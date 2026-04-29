# -*- coding: utf-8 -*-
"""
Meta-Cognition Post-Task Hook (后置钩子)

触发时机：执行任何任务后自动调用
功能：记录任务执行结果，更新调度日志，生成统计信息
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

sys.path.insert(0, str(Path(__file__).parent.parent))

from .utils import (
    load_log, save_log, get_current_timestamp,
    calculate_duration_ms, filter_sensitive_info,
    truncate_text, rotate_log_if_needed, backup_log,
    generate_session_id
)
from ..config.config import CONFIG


def update_session(
    session_id: str,
    result: str,
    agents_used: Optional[List[str]] = None,
    error: Optional[str] = None,
    response_preview: Optional[str] = None,
    duration_ms: Optional[int] = None
) -> bool:
    """
    更新会话记录

    Args:
        session_id: 会话ID
        result: 执行结果
        agents_used: 使用的智能体列表
        error: 错误信息
        response_preview: 响应预览
        duration_ms: 执行耗时

    Returns:
        是否更新成功
    """
    log_data = load_log()

    session_found = False
    task_type = "normal"
    
    for session in reversed(log_data.get("sessions", [])):
        if session.get("session_id") == session_id and session.get("phase") == "pre_task":
            session["phase"] = "completed"
            session["end_timestamp"] = get_current_timestamp()
            session["result"] = result
            session["success"] = result == "success"
            session["agents_used"] = agents_used or []

            if error:
                session["error"] = filter_sensitive_info(error)
                session["error_details"] = truncate_text(filter_sensitive_info(error), 500)
            else:
                session["error"] = None
                session["error_details"] = None

            if response_preview:
                session["response_preview"] = truncate_text(
                    filter_sensitive_info(response_preview),
                    CONFIG.response_preview_length
                )

            if duration_ms is not None:
                session["duration_ms"] = duration_ms
            else:
                session["duration_ms"] = calculate_duration_ms(
                    session.get("timestamp"),
                    session.get("end_timestamp")
                )

            # 获取任务类型
            task_type = session.get("task_type", "normal")
            session_found = True
            break

    if not session_found:
        new_session = {
            "session_id": session_id,
            "phase": "completed",
            "timestamp": get_current_timestamp(),
            "end_timestamp": get_current_timestamp(),
            "result": result,
            "success": result == "success",
            "agents_used": agents_used or [],
            "error": filter_sensitive_info(error) if error else None,
            "error_details": truncate_text(filter_sensitive_info(error), 500) if error else None,
            "duration_ms": duration_ms or 0,
            "task_type": "normal"
        }
        log_data["sessions"].append(new_session)
        session_found = True

    # 维护成功和失败任务的统计
    if "task_statistics" not in log_data:
        log_data["task_statistics"] = {
            "total": 0,
            "success": 0,
            "failure": 0,
            "last_updated": get_current_timestamp()
        }
    
    log_data["task_statistics"]["total"] += 1
    if result == "success":
        log_data["task_statistics"]["success"] += 1
    else:
        log_data["task_statistics"]["failure"] += 1
    log_data["task_statistics"]["last_updated"] = get_current_timestamp()

    # 维护任务类型统计
    if "task_type_statistics" not in log_data:
        log_data["task_type_statistics"] = {}
    
    if task_type not in log_data["task_type_statistics"]:
        log_data["task_type_statistics"][task_type] = {
            "total": 0,
            "success": 0,
            "failure": 0
        }
    
    log_data["task_type_statistics"][task_type]["total"] += 1
    if result == "success":
        log_data["task_type_statistics"][task_type]["success"] += 1
    else:
        log_data["task_type_statistics"][task_type]["failure"] += 1

    # 主动学习：更新知识图谱
    if result == "success":
        try:
            from ..active_learning import update_knowledge_graph
            update_knowledge_graph()
        except ImportError:
            pass

    log_data["current_session"] = None

    if CONFIG.log.enable_rotation and rotate_log_if_needed(
        CONFIG.log.max_size_mb,
        CONFIG.log.max_age_days
    ):
        if CONFIG.log.enable_backup:
            backup_path = backup_log()
            if backup_path:
                log_data["last_backup"] = backup_path

    return save_log(log_data)


def post_task_hook(
    session_id: str,
    result: str = "success",
    agents_used: Optional[List[str]] = None,
    error: Optional[str] = None,
    response_preview: Optional[str] = None,
    duration_ms: Optional[int] = None
) -> Dict[str, Any]:
    """
    后置钩子主函数

    Args:
        session_id: 从 pre_task_hook 获取的会话ID
        result: 执行结果 (success/failure)
        agents_used: 实际使用的智能体列表
        error: 错误信息（如果有）
        response_preview: 响应的简短预览
        duration_ms: 执行耗时（毫秒）

    Returns:
        包含执行统计信息的字典
    """
    try:
        success = update_session(
            session_id=session_id or generate_session_id(),
            result=result or "success",
            agents_used=agents_used or [],
            error=error,
            response_preview=response_preview,
            duration_ms=duration_ms
        )

        return {
            "session_id": session_id or generate_session_id(),
            "result": result or "success",
            "agents_used": agents_used or [],
            "duration_ms": duration_ms or 0,
            "logged": success
        }
    except Exception as e:
        print(f"[ERROR] 后置钩子执行失败: {e}")
        # 返回默认值，确保系统不会崩溃
        return {
            "session_id": session_id or generate_session_id(),
            "result": result or "failure",
            "agents_used": agents_used or [],
            "duration_ms": duration_ms or 0,
            "logged": False
        }


def get_statistics() -> Dict[str, Any]:
    """
    获取调度统计信息

    Returns:
        包含各种统计指标的字典
    """
    if not CONFIG.enable_statistics:
        return {"enabled": False, "message": "Statistics are disabled"}

    log_data = load_log()
    sessions = log_data.get("sessions", [])
    completed = [s for s in sessions if s.get("phase") == "completed"]

    if not completed:
        return {
            "total_tasks": 0,
            "success_rate": 0.0,
            "avg_duration_ms": 0,
            "mode_distribution": {},
            "agent_usage": {},
            "game_theory_usage_rate": 0.0,
            "success_count": 0,
            "failure_count": 0
        }

    total = len(completed)
    success = len([s for s in completed if s.get("result") == "success"])
    total_duration = sum(s.get("duration_ms", 0) for s in completed)

    mode_dist = {}
    for s in completed:
        mode = s.get("detected_mode", "unknown")
        mode_dist[mode] = mode_dist.get(mode, 0) + 1

    agent_usage = {}
    for s in completed:
        for agent in s.get("agents_used", []):
            agent_usage[agent] = agent_usage.get(agent, 0) + 1

    game_theory_modes = ["game_theory_mode1", "game_theory_mode2", "game_theory_mode3"]
    gt_count = sum(mode_dist.get(k, 0) for k in game_theory_modes)

    return {
        "total_tasks": total,
        "success_rate": round(success / total * 100, 2) if total > 0 else 0,
        "avg_duration_ms": round(total_duration / total) if total > 0 else 0,
        "mode_distribution": mode_dist,
        "agent_usage": agent_usage,
        "game_theory_usage_rate": round(gt_count / total * 100, 2) if total > 0 else 0,
        "success_count": success,
        "failure_count": total - success,
        "task_statistics": log_data.get("task_statistics", {})
    }


def get_task_statistics() -> Dict[str, Any]:
    """
    获取任务执行统计信息

    Returns:
        包含任务执行统计的字典
    """
    log_data = load_log()
    task_stats = log_data.get("task_statistics", {
        "total": 0,
        "success": 0,
        "failure": 0,
        "last_updated": get_current_timestamp()
    })

    # 计算成功率
    total = task_stats.get("total", 0)
    success = task_stats.get("success", 0)
    success_rate = round(success / total * 100, 2) if total > 0 else 0

    return {
        **task_stats,
        "success_rate": success_rate,
        "failure_rate": 100 - success_rate
    }


def get_recent_sessions(limit: int = 10) -> List[Dict[str, Any]]:
    """
    获取最近的会话记录

    Args:
        limit: 返回记录数量限制

    Returns:
        会话记录列表
    """
    log_data = load_log()
    sessions = log_data.get("sessions", [])
    completed = [s for s in sessions if s.get("phase") == "completed"]
    return sorted(completed, key=lambda x: x.get("timestamp", ""), reverse=True)[:limit]


def get_session_by_id(session_id: str) -> Optional[Dict[str, Any]]:
    """
    根据ID获取会话详情

    Args:
        session_id: 会话ID

    Returns:
        会话记录或None
    """
    log_data = load_log()
    for session in log_data.get("sessions", []):
        if session.get("session_id") == session_id:
            return session
    return None


def export_sessions(filter_result: Optional[str] = None, filter_mode: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    导出会话记录（支持过滤）

    Args:
        filter_result: 按结果过滤 (success/failure)
        filter_mode: 按模式过滤

    Returns:
        过滤后的会话列表
    """
    log_data = load_log()
    sessions = log_data.get("sessions", [])

    if filter_result:
        sessions = [s for s in sessions if s.get("result") == filter_result]

    if filter_mode:
        sessions = [s for s in sessions if s.get("detected_mode") == filter_mode]

    return sessions


if __name__ == "__main__":
    print("=== Post-Task Hook 测试 ===\n")

    from pre_task_hook import pre_task_hook
    import time

    test_task = "请帮我优化这段代码，提升性能"
    print(f"测试任务: {test_task}")

    pre_result = pre_task_hook(test_task)
    print(f"Pre-Task Result: {pre_result['session_id']}")

    time.sleep(0.1)

    post_result = post_task_hook(
        session_id=pre_result["session_id"],
        result="success",
        agents_used=["code_executor_agent", "editor_agent", "writer_agent"],
        response_preview="优化建议已完成，应用了XYZ技术来提升性能...",
        duration_ms=1500
    )
    print(f"Post-Task Result: {post_result}")

    print("\n=== 调度统计 ===")
    stats = get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n=== 最近会话 ===")
    recent = get_recent_sessions(limit=3)
    for session in recent:
        print(f"  - {session.get('session_id')}: {session.get('result')} ({session.get('duration_ms')}ms)")

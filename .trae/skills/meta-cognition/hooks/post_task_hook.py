"""
Meta-Cognition Post-Task Hook (写入钩子)

触发时机：执行任何任务后自动调用
功能：记录任务执行结果，更新调度日志
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

LOG_FILE = Path(__file__).parent.parent / "logs" / "meta_cognition.json"


def load_log() -> Dict[str, Any]:
    """加载现有日志"""
    if LOG_FILE.exists():
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"sessions": [], "current_session": None}


def save_log(data: Dict[str, Any]) -> None:
    """保存日志到文件"""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def calculate_duration_ms(start_time: Optional[str] = None, end_time: Optional[str] = None) -> int:
    """计算执行耗时（毫秒）"""
    if not start_time:
        return 0
    try:
        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time) if end_time else datetime.now()
        return int((end - start).total_seconds() * 1000)
    except (ValueError, TypeError):
        return 0


def post_task_hook(
    session_id: str,
    result: str = "success",
    agents_used: Optional[list] = None,
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

    log_data = load_log()

    session_found = False
    for session in reversed(log_data.get("sessions", [])):
        if session.get("session_id") == session_id and session.get("phase") == "pre_task":
            session["phase"] = "completed"
            session["end_timestamp"] = datetime.now().isoformat()
            session["result"] = result
            session["agents_used"] = agents_used or []
            session["error"] = error
            session["response_preview"] = (response_preview or "")[:200] if response_preview else None

            if duration_ms is not None:
                session["duration_ms"] = duration_ms
            else:
                session["duration_ms"] = calculate_duration_ms(
                    session.get("timestamp"),
                    session.get("end_timestamp")
                )

            session_found = True
            break

    if not session_found:
        session = {
            "session_id": session_id,
            "phase": "completed",
            "timestamp": datetime.now().isoformat(),
            "end_timestamp": datetime.now().isoformat(),
            "result": result,
            "agents_used": agents_used or [],
            "error": error,
            "duration_ms": duration_ms or 0
        }
        log_data["sessions"].append(session)

    log_data["current_session"] = None
    save_log(log_data)

    stats = {
        "session_id": session_id,
        "result": result,
        "agents_used": agents_used or [],
        "duration_ms": duration_ms or 0,
        "logged": True
    }

    return stats


def get_statistics() -> Dict[str, Any]:
    """
    获取调度统计信息

    Returns:
        包含各种统计指标的字典
    """
    log_data = load_log()

    sessions = log_data.get("sessions", [])
    completed = [s for s in sessions if s.get("phase") == "completed"]

    if not completed:
        return {
            "total_tasks": 0,
            "success_rate": 0.0,
            "avg_duration_ms": 0,
            "mode_distribution": {},
            "agent_usage": {}
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

    return {
        "total_tasks": total,
        "success_rate": round(success / total * 100, 2) if total > 0 else 0,
        "avg_duration_ms": round(total_duration / total) if total > 0 else 0,
        "mode_distribution": mode_dist,
        "agent_usage": agent_usage,
        "game_theory_usage_rate": round(
            sum(mode_dist.get(k, 0) for k in ["game_theory_mode1", "game_theory_mode2"]) / total * 100, 2
        ) if total > 0 else 0
    }


if __name__ == "__main__":
    print("=== Post-Task Hook 测试 ===")

    import time

    pre_result = {
        "session_id": "test-session-001",
        "mode": "game_theory_mode2",
        "decision": {"mode": "降维打击模式"}
    }

    time.sleep(0.1)

    post_result = post_task_hook(
        session_id=pre_result["session_id"],
        result="success",
        agents_used=["code_executor_agent", "editor_agent", "writer_agent"],
        response_preview="这是一个测试响应的预览...",
        duration_ms=1500
    )
    print(json.dumps(post_result, ensure_ascii=False, indent=2))

    print("\n=== 调度统计 ===")
    stats = get_statistics()
    print(json.dumps(stats, ensure_ascii=False, indent=2))
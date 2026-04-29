# -*- coding: utf-8 -*-
"""
Meta-Cognition 自动分析模块

实现定时分析日志文件并生成报告的功能
"""

import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List

from .hooks.utils import load_log, save_log, get_current_timestamp
from .config.config import CONFIG


LOGS_DIR = Path(__file__).parent / "logs"
REPORT_DIR = LOGS_DIR / "reports"
REPORT_DIR.mkdir(exist_ok=True)


def analyze_logs() -> Dict[str, Any]:
    """
    分析日志文件，生成分析报告
    
    Returns:
        分析结果
    """
    log_data = load_log()
    sessions = log_data.get("sessions", [])
    
    # 统计信息
    total_tasks = len(sessions)
    completed_tasks = [s for s in sessions if s.get("phase") == "completed"]
    completed_count = len(completed_tasks)
    
    # 成功/失败统计
    success_count = len([s for s in completed_tasks if s.get("success")])
    failure_count = completed_count - success_count
    
    # 模式分布
    mode_distribution = {}
    for session in completed_tasks:
        mode = session.get("detected_mode", "unknown")
        mode_distribution[mode] = mode_distribution.get(mode, 0) + 1
    
    # 智能体使用情况
    agent_usage = {}
    for session in completed_tasks:
        for agent in session.get("agents_used", []):
            agent_usage[agent] = agent_usage.get(agent, 0) + 1
    
    # 时间分析
    time_stats = {
        "total_duration": 0,
        "avg_duration": 0,
        "min_duration": float('inf'),
        "max_duration": 0
    }
    
    for session in completed_tasks:
        duration = session.get("duration_ms", 0)
        time_stats["total_duration"] += duration
        if duration < time_stats["min_duration"]:
            time_stats["min_duration"] = duration
        if duration > time_stats["max_duration"]:
            time_stats["max_duration"] = duration
    
    if completed_count > 0:
        time_stats["avg_duration"] = time_stats["total_duration"] / completed_count
    else:
        time_stats["min_duration"] = 0
    
    # 任务类型分析
    task_types = {
        "optimization": 0,  # 优化类
        "design": 0,        # 设计类
        "debate": 0,        # 辩论类
        "normal": 0,        # 常规类
        "other": 0          # 其他
    }
    
    for session in completed_tasks:
        task_desc = session.get("task_description", "").lower()
        detected_mode = session.get("detected_mode", "normal")
        
        if detected_mode == "game_theory_mode1":
            task_types["debate"] += 1
        elif detected_mode == "game_theory_mode2":
            task_types["optimization"] += 1
        elif detected_mode == "game_theory_mode3":
            task_types["design"] += 1
        elif detected_mode == "normal":
            task_types["normal"] += 1
        else:
            task_types["other"] += 1
    
    # 生成分析报告
    analysis = {
        "timestamp": get_current_timestamp(),
        "total_tasks": total_tasks,
        "completed_tasks": completed_count,
        "success_count": success_count,
        "failure_count": failure_count,
        "success_rate": success_count / completed_count * 100 if completed_count > 0 else 0,
        "mode_distribution": mode_distribution,
        "agent_usage": agent_usage,
        "time_stats": time_stats,
        "task_types": task_types,
        "last_updated": log_data.get("task_statistics", {}).get("last_updated", "")
    }
    
    return analysis


def generate_report() -> str:
    """
    生成分析报告文件
    
    Returns:
        报告文件路径
    """
    analysis = analyze_logs()
    
    # 生成报告文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = REPORT_DIR / f"analysis_report_{timestamp}.json"
    
    # 保存报告
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    
    # 生成摘要报告
    summary_file = REPORT_DIR / f"analysis_summary_{timestamp}.md"
    summary_content = generate_summary(analysis)
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary_content)
    
    return str(report_file)


def generate_summary(analysis: Dict[str, Any]) -> str:
    """
    生成报告摘要
    
    Args:
        analysis: 分析结果
    
    Returns:
        摘要内容
    """
    summary = f"# Meta-Cognition 技能分析报告\n"
    summary += f"\n## 基本统计\n"
    summary += f"- 总任务数: {analysis['total_tasks']}\n"
    summary += f"- 已完成任务: {analysis['completed_tasks']}\n"
    summary += f"- 成功任务: {analysis['success_count']}\n"
    summary += f"- 失败任务: {analysis['failure_count']}\n"
    summary += f"- 成功率: {analysis['success_rate']:.2f}%\n"
    
    summary += f"\n## 模式分布\n"
    for mode, count in analysis['mode_distribution'].items():
        percentage = count / analysis['completed_tasks'] * 100 if analysis['completed_tasks'] > 0 else 0
        summary += f"- {mode}: {count} ({percentage:.2f}%)\n"
    
    summary += f"\n## 任务类型分布\n"
    for task_type, count in analysis['task_types'].items():
        percentage = count / analysis['completed_tasks'] * 100 if analysis['completed_tasks'] > 0 else 0
        summary += f"- {task_type}: {count} ({percentage:.2f}%)\n"
    
    summary += f"\n## 智能体使用情况\n"
    for agent, count in analysis['agent_usage'].items():
        summary += f"- {agent}: {count}\n"
    
    summary += f"\n## 时间统计\n"
    summary += f"- 总执行时间: {analysis['time_stats']['total_duration']:.2f} ms\n"
    summary += f"- 平均执行时间: {analysis['time_stats']['avg_duration']:.2f} ms\n"
    summary += f"- 最短执行时间: {analysis['time_stats']['min_duration']:.2f} ms\n"
    summary += f"- 最长执行时间: {analysis['time_stats']['max_duration']:.2f} ms\n"
    
    summary += f"\n## 分析时间\n"
    summary += f"{analysis['timestamp']}\n"
    
    return summary


def check_and_analyze() -> Dict[str, Any]:
    """
    检查并分析日志
    
    Returns:
        分析结果
    """
    log_data = load_log()
    
    # 检查是否需要分析
    last_analysis = log_data.get("last_analysis", {})
    last_analysis_time = last_analysis.get("timestamp", 0)
    
    # 每24小时分析一次
    current_time = time.time()
    if current_time - float(last_analysis_time) > 24 * 60 * 60:
        report_path = generate_report()
        
        # 更新分析记录
        log_data["last_analysis"] = {
            "timestamp": str(current_time),
            "time": get_current_timestamp(),
            "report_path": report_path
        }
        
        save_log(log_data)
        
        return {
            "analyzed": True,
            "report_path": report_path,
            "message": "分析完成并生成报告"
        }
    
    return {
        "analyzed": False,
        "message": "未到分析时间"
    }


def get_recent_reports(limit: int = 5) -> List[str]:
    """
    获取最近的报告
    
    Args:
        limit: 限制数量
    
    Returns:
        报告文件路径列表
    """
    reports = list(REPORT_DIR.glob("analysis_report_*.json"))
    reports.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    return [str(report) for report in reports[:limit]]


def get_analysis_status() -> Dict[str, Any]:
    """
    获取分析状态
    
    Returns:
        分析状态信息
    """
    log_data = load_log()
    last_analysis = log_data.get("last_analysis", {})
    
    return {
        "last_analysis": last_analysis,
        "reports_count": len(list(REPORT_DIR.glob("analysis_report_*.json"))),
        "reports_dir": str(REPORT_DIR),
        "recent_reports": get_recent_reports(3)
    }


if __name__ == "__main__":
    print("=== 自动分析模块测试 ===")
    
    # 生成报告
    report_path = generate_report()
    print(f"报告生成路径: {report_path}")
    
    # 检查分析状态
    status = get_analysis_status()
    print(f"分析状态: {status}")
    
    # 执行检查和分析
    result = check_and_analyze()
    print(f"检查和分析结果: {result}")

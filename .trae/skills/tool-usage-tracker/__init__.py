"""
工具调用追踪技能实现模块
提供追踪、统计和报告功能
"""

import sys
import os

# 添加上层目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from tool_usage_tracker import (
    get_tracker,
    track_mcp_call,
    track_skill_call,
    ToolUsageTracker
)


def initialize_tracker():
    """初始化追踪器"""
    return get_tracker()


def record_mcp_call(tool_name: str, action: str, status: str, duration_ms: float,
                    error: str = None, metadata: dict = None) -> str:
    """记录 MCP 调用"""
    return track_mcp_call(tool_name, action, status, duration_ms, error, metadata)


def record_skill_call(tool_name: str, action: str, status: str, duration_ms: float,
                      error: str = None, metadata: dict = None) -> str:
    """记录 Skill 调用"""
    return track_skill_call(tool_name, action, status, duration_ms, error, metadata)


def generate_daily_report(date: str = None) -> str:
    """生成每日报告"""
    tracker = get_tracker()
    return tracker.generate_daily_report(date)


def get_daily_stats() -> dict:
    """获取今日统计"""
    tracker = get_tracker()
    return tracker.get_today_stats()


def list_all_reports() -> list:
    """列出所有报告"""
    tracker = get_tracker()
    return tracker.list_available_reports()


def get_report_path(date: str = None) -> str:
    """获取报告路径"""
    tracker = get_tracker()
    return str(tracker._get_report_path(date))


def get_log_path(date: str = None) -> str:
    """获取日志路径"""
    tracker = get_tracker()
    if date:
        return str(tracker.LOGS_DIR / f"tool_calls_{date}.json")
    return str(tracker._get_today_log_path())


def get_summary() -> str:
    """获取简洁的今日摘要"""
    stats = get_daily_stats()
    
    if stats["total_calls"] == 0:
        return "今日暂无工具调用记录"
    
    summary = [
        f"📊 今日工具调用统计",
        f"  ├─ 总调用: {stats['total_calls']}次",
        f"  ├─ MCP: {stats['mcp_calls']}次",
        f"  ├─ Skill: {stats['skill_calls']}次",
        f"  ├─ 成功率: {stats['success_rate']:.1f}%",
        f"  └─ 平均耗时: {stats['avg_duration_ms']:.2f}ms"
    ]
    
    return "\n".join(summary)


# 技能注册信息
SKILL_INFO = {
    "name": "tool-usage-tracker",
    "version": "1.0.0",
    "description": "工具调用追踪技能",
    "author": "TRAE System",
    "functions": [
        {"name": "record_mcp_call", "description": "记录 MCP 调用"},
        {"name": "record_skill_call", "description": "记录 Skill 调用"},
        {"name": "generate_daily_report", "description": "生成每日报告"},
        {"name": "get_daily_stats", "description": "获取今日统计"},
        {"name": "list_all_reports", "description": "列出所有报告"},
        {"name": "get_summary", "description": "获取今日摘要"}
    ]
}


if __name__ == "__main__":
    print("工具调用追踪技能")
    print("=" * 50)
    
    stats = get_daily_stats()
    print(f"今日调用次数: {stats['total_calls']}")
    
    if stats['total_calls'] > 0:
        print(get_summary())
        report = generate_daily_report()
        print(f"\n报告已生成: {get_report_path()}")
    else:
        print("暂无调用记录，请先调用 MCP 或 Skills")

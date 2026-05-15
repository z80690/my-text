"""
工具调用追踪技能实现模块 v2.0
提供追踪、统计和报告功能
"""

import sys
import os

# 添加上层目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from tool_usage_tracker_v2 import (
    get_tracker,
    track_mcp_call,
    track_skill_call,
    get_recent_calls,
    get_summary,
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


def get_recent_calls_summary(count: int = 10) -> list:
    """获取最近N次调用摘要"""
    return get_recent_calls(count)


def check_logs() -> dict:
    """检查日志状态"""
    tracker = get_tracker()
    records = tracker.read_log()
    
    return {
        "log_exists": len(records) > 0,
        "record_count": len(records),
        "log_path": str(tracker._get_today_log_path()),
        "message": f"找到 {len(records)} 条记录" if records else "暂无工具调用记录"
    }


# 技能注册信息
SKILL_INFO = {
    "name": "tool-usage-tracker",
    "version": "2.0.0",
    "description": "工具调用追踪技能 - 自动记录和读取真实工具调用日志",
    "author": "TRAE System",
    "functions": [
        {"name": "record_mcp_call", "description": "记录 MCP 调用"},
        {"name": "record_skill_call", "description": "记录 Skill 调用"},
        {"name": "generate_daily_report", "description": "生成每日报告"},
        {"name": "get_daily_stats", "description": "获取今日统计"},
        {"name": "list_all_reports", "description": "列出所有报告"},
        {"name": "get_summary", "description": "获取今日摘要"},
        {"name": "get_recent_calls_summary", "description": "获取最近调用摘要"},
        {"name": "check_logs", "description": "检查日志状态"}
    ]
}


if __name__ == "__main__":
    print("工具调用追踪技能 v2.0")
    print("=" * 50)
    
    # 检查日志状态
    log_status = check_logs()
    print(f"\n📁 日志路径: {log_status['log_path']}")
    print(f"📊 记录数量: {log_status['record_count']}")
    print(f"💬 状态: {log_status['message']}")
    
    if log_status['log_exists']:
        print("\n" + get_summary())
        recent = get_recent_calls_summary(10)
        print(f"\n📋 最近{len(recent)}次调用:")
        for i, r in enumerate(recent, 1):
            print(f"  {i}. [{r['timestamp']}] {r['tool_type']}: {r['tool_name']} -> {r['action']}")
    else:
        print("\n⚠️ 提示: 暂无工具调用记录")
        print("   系统将自动记录未来的工具调用")
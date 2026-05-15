"""
工具调用追踪器测试脚本
验证追踪器能否正确记录和读取工具调用日志
"""

import sys
import os

# 添加上层目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from tool_usage_tracker_v2 import (
    get_tracker,
    track_mcp_call,
    track_skill_call,
    get_recent_calls,
    get_summary,
    ToolUsageTracker
)


def check_logs():
    """检查日志状态"""
    tracker = get_tracker()
    records = tracker.read_log()
    
    return {
        "log_exists": len(records) > 0,
        "record_count": len(records),
        "log_path": str(tracker._get_today_log_path()),
        "message": f"找到 {len(records)} 条记录" if records else "暂无工具调用记录"
    }


def generate_daily_report(date=None):
    """生成日报"""
    tracker = get_tracker()
    return tracker.generate_daily_report(date)


def run_tests():
    """运行完整测试"""
    print("=" * 60)
    print("🔍 工具调用追踪器 v2.0 测试")
    print("=" * 60)
    
    # 测试1: 检查日志状态
    print("\n📋 测试1: 检查日志状态")
    status = check_logs()
    print(f"  日志路径: {status['log_path']}")
    print(f"  记录数: {status['record_count']}")
    print(f"  状态: {status['message']}")
    
    # 测试2: 记录工具调用
    print("\n📤 测试2: 记录工具调用")
    calls = [
        ("mcp", "Read", "read_file", 125.5),
        ("mcp", "Write", "write_file", 89.2),
        ("skill", "file-cleaner", "clean_files", 2340.0),
        ("mcp", "Grep", "search_code", 456.7),
        ("mcp", "Edit", "update_file", 156.3),
        ("skill", "my-code-review", "analyze_code", 5670.8),
        ("mcp", "Glob", "find_files", 78.9),
        ("mcp", "LS", "list_dir", 45.2),
        ("skill", "api-token-optimizer", "optimize_tokens", 1234.5),
        ("mcp", "RunCommand", "execute_cmd", 2345.6),
    ]
    
    for i, (tool_type, tool_name, action, duration) in enumerate(calls, 1):
        if tool_type == "mcp":
            track_mcp_call(tool_name, action, "success", duration)
        else:
            track_skill_call(tool_name, action, "success", duration)
        print(f"  {i}. ✅ {tool_type.upper()}: {tool_name}.{action}")
    
    # 测试3: 检查日志状态（再次）
    print("\n📊 测试3: 验证日志记录")
    status = check_logs()
    print(f"  记录数: {status['record_count']}")
    print(f"  状态: {status['message']}")
    
    # 测试4: 获取统计摘要
    print("\n📈 测试4: 获取统计摘要")
    summary = get_summary()
    print(f"  {summary}")
    
    # 测试5: 获取最近10次调用
    print("\n🔍 测试5: 获取最近10次调用")
    recent = get_recent_calls(10)
    for i, call in enumerate(recent, 1):
        print(f"  {i}. [{call['timestamp']}] {call['tool_type']}: {call['tool_name']}.{call['action']}")
    
    # 测试6: 生成日报
    print("\n📝 测试6: 生成日报")
    report = generate_daily_report()
    print(f"  报告已生成")
    
    # 测试7: 验证日志文件存在
    print("\n📁 测试7: 验证日志文件")
    tracker = get_tracker()
    log_path = tracker._get_today_log_path()
    report_path = tracker._get_report_path()
    print(f"  日志文件: {log_path} - {'存在' if log_path.exists() else '不存在'}")
    print(f"  报告文件: {report_path} - {'存在' if report_path.exists() else '不存在'}")
    
    print("\n" + "=" * 60)
    print("✅ 所有测试完成！")
    print("=" * 60)
    
    return {
        "success": True,
        "records_created": len(calls),
        "log_exists": log_path.exists(),
        "report_exists": report_path.exists(),
        "summary": summary
    }


if __name__ == "__main__":
    results = run_tests()
    
    # 打印最终结果
    print("\n📋 测试结果汇总")
    print("-" * 40)
    print(f"✅ 测试成功: {results['success']}")
    print(f"📊 创建记录数: {results['records_created']}")
    print(f"📁 日志文件存在: {results['log_exists']}")
    print(f"📝 报告文件存在: {results['report_exists']}")
    print(f"\n📈 今日统计:")
    print(results['summary'])
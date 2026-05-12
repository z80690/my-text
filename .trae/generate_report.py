"""
工具调用报告生成器
快速生成每日工具调用报告
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))
from tool_usage_tracker import get_tracker


def generate_today_report():
    tracker = get_tracker()
    report = tracker.generate_daily_report()
    print(report)
    print(f"\n✅ 报告已保存到: {tracker.REPORTS_DIR}")
    return report


def generate_report_for_date(date_str: str):
    tracker = get_tracker()
    report = tracker.generate_daily_report(date_str)
    print(report)
    print(f"\n✅ 报告已保存到: {tracker.REPORTS_DIR}")
    return report


def list_reports():
    tracker = get_tracker()
    reports = tracker.list_available_reports()
    print("📋 可用报告列表:")
    for r in reports:
        print(f"  - {r}")
    return reports


def show_stats():
    tracker = get_tracker()
    stats = tracker.get_today_stats()
    print("📊 今日统计:")
    print(f"  总调用次数: {stats['total_calls']}")
    print(f"  MCP 调用: {stats['mcp_calls']}")
    print(f"  Skill 调用: {stats['skill_calls']}")
    print(f"  成功率: {stats['success_rate']:.1f}%")
    print(f"  平均耗时: {stats['avg_duration_ms']:.2f}ms")
    return stats


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="工具调用报告生成器")
    parser.add_argument("--today", action="store_true", help="生成今日报告")
    parser.add_argument("--date", type=str, help="生成指定日期的报告 (YYYY-MM-DD)")
    parser.add_argument("--list", action="store_true", help="列出所有可用报告")
    parser.add_argument("--stats", action="store_true", help="显示今日统计")
    parser.add_argument("--yesterday", action="store_true", help="生成昨日报告")
    
    args = parser.parse_args()
    
    if args.today:
        generate_today_report()
    elif args.date:
        generate_report_for_date(args.date)
    elif args.yesterday:
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        generate_report_for_date(yesterday)
    elif args.list:
        list_reports()
    elif args.stats:
        show_stats()
    else:
        generate_today_report()

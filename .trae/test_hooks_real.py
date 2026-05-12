# -*- coding: utf-8 -*-
"""
真实测试脚本 - 验证所有 Skills 自动触发钩子
"""

import sys
import json
from pathlib import Path
from datetime import datetime

print("="*70)
print("🚀 真实测试 - Skills 自动触发钩子验证")
print("="*70)

from skill_runner import (
    get_runner, show_all_skills, quick_debug, quick_hook,
    quick_doc, quick_refactor, quick_privacy, quick_tracker,
    get_today_summary
)

from auto_hook_system import get_hook_system

def check_hook_events(skill_id: str) -> dict:
    """检查钩子事件日志"""
    hook_log = Path(__file__).parent / "logs" / f"hook_events_{datetime.now().strftime('%Y-%m-%d')}.json"
    if not hook_log.exists():
        return {"found": False}

    with open(hook_log, 'r', encoding='utf-8') as f:
        events = json.load(f)

    skill_events = [e for e in events if e.get('skill_id') == skill_id]
    return {"found": len(skill_events) > 0, "count": len(skill_events), "events": skill_events[-3:]}

def check_tracker_logs(skill_id: str) -> dict:
    """检查追踪日志"""
    tracker_log = Path(__file__).parent / "logs" / f"tool_calls_{datetime.now().strftime('%Y-%m-%d')}.json"
    if not tracker_log.exists():
        return {"found": False}

    with open(tracker_log, 'r', encoding='utf-8') as f:
        records = json.load(f)

    skill_records = [r for r in records if r.get('tool_name') == skill_id]
    return {"found": len(skill_records) > 0, "count": len(skill_records)}

def test_skill(name: str, func, *args, **kwargs):
    """测试单个Skill"""
    print(f"\n{'='*70}")
    print(f"🧪 测试: {name}")
    print("="*70)

    result = func(*args, **kwargs)
    print(f"\n📤 返回结果: {result}")

    skill_id = name.split()[0].lower()
    hook_info = check_hook_events(skill_id)
    tracker_info = check_tracker_logs(skill_id)

    print(f"\n🔗 钩子触发检查:")
    print(f"   ├─ 钩子事件记录: {'✅' if hook_info['found'] else '⚠️ 暂无记录'}")
    if hook_info['found']:
        print(f"   │   └─ 事件数: {hook_info['count']}")

    print(f"   └─ 追踪日志记录: {'✅' if tracker_info['found'] else '⚠️ 暂无记录'}")
    if tracker_info['found']:
        print(f"       └─ 记录数: {tracker_info['count']}")

    return result

print("\n📋 显示所有可用 Skills:")
print(show_all_skills())

print("\n" + "="*70)
print("开始真实测试 5 个 Skills...")
print("="*70)

test_skill("auto-debug", quick_debug, "TypeError: 'NoneType' object is not callable")
test_skill("auto-hook", quick_hook, "post_save", "auto_format")
test_skill("auto-doc", quick_doc, "test-project")
test_skill("auto-refactor", quick_refactor, "oldFunc", "new_func")
test_skill("local-privacy", quick_privacy, "/path/to/local/file")

print("\n" + "="*70)
print("查看统计报告:")
print("="*70)
print(get_today_summary())

print("\n" + "="*70)
print("钩子系统状态:")
print("="*70)
hook_system = get_hook_system()
stats = hook_system.get_hook_stats()
print(f"总钩子数: {stats['total_hooks']}")
print(f"今日事件: {stats['events_today']}")
for trigger, count in stats['by_trigger'].items():
    print(f"  - {trigger}: {count} 个钩子")

print("\n" + "="*70)
print("✅ 测试完成!")
print("="*70)

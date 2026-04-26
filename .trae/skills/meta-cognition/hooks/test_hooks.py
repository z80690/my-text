#!/usr/bin/env python3
"""
Meta-Cognition Hooks 测试脚本
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from pre_task_hook import pre_task_hook, load_log
from post_task_hook import post_task_hook, get_statistics
import json

def test_pre_task_hook():
    print("=" * 50)
    print("测试 Pre-Task Hook (读取钩子)")
    print("=" * 50)

    test_cases = [
        ("请帮我优化这段代码，提升性能", "game_theory_mode2"),
        ("请对比敏捷开发和瀑布模型的优缺点", "game_theory_mode1"),
        ("帮我写一个用户登录功能", "normal"),
        ("分析一下这个项目的风险", "game_theory_mode1"),
    ]

    results = []
    for task, expected_mode in test_cases:
        print(f"\n输入: {task}")
        print(f"预期模式: {expected_mode}")
        result = pre_task_hook(task)
        print(f"实际模式: {result['mode']}")
        print(f"调度决策: {result['decision']['mode']}")
        results.append((result['mode'] == expected_mode, result))

    return results

def test_post_task_hook():
    print("\n" + "=" * 50)
    print("测试 Post-Task Hook (写入钩子)")
    print("=" * 50)

    log_data = load_log()
    if log_data["sessions"]:
        last_session = log_data["sessions"][-1]
        session_id = last_session.get("session_id")

        print(f"\n使用 session_id: {session_id}")
        result = post_task_hook(
            session_id=session_id,
            result="success",
            agents_used=["assistant_agent", "editor_agent"],
            response_preview="测试响应内容...",
            duration_ms=1500
        )
        print(f"写入结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return True
    else:
        print("没有找到可用的 session")
        return False

def test_statistics():
    print("\n" + "=" * 50)
    print("测试统计功能")
    print("=" * 50)

    stats = get_statistics()
    print(f"\n统计结果: {json.dumps(stats, ensure_ascii=False, indent=2)}")
    return stats

def test_full_flow():
    print("\n" + "=" * 50)
    print("测试完整流程")
    print("=" * 50)

    task = "请帮我重构用户认证模块，提升其安全性"
    print(f"\n任务: {task}")

    print("\n[Step 1] Pre-Task Hook")
    pre_result = pre_task_hook(task)
    print(f"Session ID: {pre_result['session_id']}")
    print(f"Detected Mode: {pre_result['mode']}")

    print("\n[Step 2] 模拟任务执行...")
    print("执行中...")

    print("\n[Step 3] Post-Task Hook")
    post_result = post_task_hook(
        session_id=pre_result['session_id'],
        result="success",
        agents_used=["code_executor_agent", "message_filter_agent", "writer_agent"],
        response_preview="最终优化方案已完成...",
        duration_ms=3500
    )
    print(f"Post Result: {post_result}")

    print("\n[Step 4] 获取统计")
    stats = get_statistics()
    print(f"Stats: {json.dumps(stats, ensure_ascii=False, indent=2)}")

    return pre_result['session_id']

if __name__ == "__main__":
    print("\n" + "#" * 60)
    print("# Meta-Cognition Hooks 测试套件")
    print("#" * 60)

    try:
        test_pre_task_hook()
        test_post_task_hook()
        test_statistics()
        test_full_flow()

        print("\n" + "#" * 60)
        print("# 所有测试完成!")
        print("#" * 60)

        log_data = load_log()
        print(f"\n日志文件位置: {os.path.abspath('meta_cognition.json')}")
        print(f"总记录数: {len(log_data.get('sessions', []))}")

    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
# -*- coding: utf-8 -*-
"""
测试Meta-Cognition技能的重构效果
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

try:
    from .trae.skills.meta-cognition.hooks.pre_task_hook import pre_task_hook, detect_task_mode
    from .trae.skills.meta-cognition.hooks.post_task_hook import post_task_hook, get_statistics, get_task_statistics
    from .trae.skills.meta-cognition.self_update import check_and_update, get_update_status
    from .trae.skills.meta-cognition.config import CONFIG
    
    print("=== Meta-Cognition 技能测试 ===")
    print(f"自我更新功能: {'启用' if CONFIG.enable_self_update else '禁用'}")
    print(f"博弈逻辑功能: {'启用' if CONFIG.enable_game_theory else '禁用'}")
    print(f"统计功能: {'启用' if CONFIG.enable_statistics else '禁用'}")
    
    # 测试自我更新
    print("\n=== 测试自我更新 ===")
    update_status = get_update_status()
    print(f"更新状态: {update_status}")
    check_and_update()
    print("自我更新检查完成")
    
    # 测试任务模式检测
    print("\n=== 测试任务模式检测 ===")
    test_tasks = [
        ("请帮我优化这段代码，提升性能", "game_theory_mode2"),
        ("请对比敏捷开发和瀑布模型的优缺点", "game_theory_mode1"),
        ("帮我设计一个用户认证系统", "game_theory_mode3"),
        ("1+1等于几？", "normal"),
        ("现在几点了", "normal"),
        ("这个代码报错了，帮我修复一下", "game_theory_mode2"),
        ("看看这个方案有什么问题", "game_theory_mode2"),
    ]
    
    for task, expected_mode in test_tasks:
        detected_mode = detect_task_mode(task)
        status = "✓" if detected_mode == expected_mode else "✗"
        print(f"{status} 任务: {task}")
        print(f"  预期: {expected_mode} -> 实际: {detected_mode}")
    
    # 测试前置钩子
    print("\n=== 测试前置钩子 ===")
    test_task = "请帮我优化这段代码，提升性能"
    pre_result = pre_task_hook(test_task)
    print(f"任务: {test_task}")
    print(f"会话ID: {pre_result['session_id']}")
    print(f"检测模式: {pre_result['mode']}")
    print(f"工作流输出: {pre_result['workflow_output'][:200]}...")
    
    # 测试后置钩子
    print("\n=== 测试后置钩子 ===")
    post_result = post_task_hook(
        session_id=pre_result["session_id"],
        result="success",
        agents_used=["code_executor_agent", "editor_agent"],
        response_preview="优化建议已完成，应用了XYZ技术来提升性能...",
        duration_ms=1500
    )
    print(f"后置钩子结果: {post_result}")
    
    # 测试统计信息
    print("\n=== 测试统计信息 ===")
    stats = get_statistics()
    print(f"总任务数: {stats.get('total_tasks', 0)}")
    print(f"成功率: {stats.get('success_rate', 0)}%")
    print(f"博弈逻辑使用率: {stats.get('game_theory_usage_rate', 0)}%")
    
    task_stats = get_task_statistics()
    print(f"\n任务执行统计:")
    print(f"总任务: {task_stats.get('total', 0)}")
    print(f"成功任务: {task_stats.get('success', 0)}")
    print(f"失败任务: {task_stats.get('failure', 0)}")
    print(f"成功率: {task_stats.get('success_rate', 0)}%")
    
    print("\n=== 测试完成 ===")
    
except Exception as e:
    print(f"测试失败: {e}")
    import traceback
    traceback.print_exc()

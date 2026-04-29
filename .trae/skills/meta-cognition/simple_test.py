# -*- coding: utf-8 -*-
"""
简单测试脚本，验证Meta-Cognition插件的基本功能
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from hooks.pre_task_hook import pre_task_hook
    from hooks.post_task_hook import post_task_hook, get_statistics
    from config.config import CONFIG
    
    print("=== Meta-Cognition 插件测试 ===")
    print(f"博弈逻辑功能: {'启用' if CONFIG.enable_game_theory else '禁用'}")
    print(f"统计功能: {'启用' if CONFIG.enable_statistics else '禁用'}")
    
    # 测试前置钩子
    print("\n=== 测试前置钩子 ===")
    test_task = "请帮我优化这段代码，提升性能"
    pre_result = pre_task_hook(test_task)
    print(f"任务: {test_task}")
    print(f"会话ID: {pre_result['session_id']}")
    print(f"检测模式: {pre_result['mode']}")
    print(f"工作流输出: {pre_result['workflow_output'][:100]}...")
    
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
    
    print("\n=== 测试完成 ===")
    print("插件功能正常，已成功修复！")
    
except Exception as e:
    print(f"测试失败: {e}")
    import traceback
    traceback.print_exc()

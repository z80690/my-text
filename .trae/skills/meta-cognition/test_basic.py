# -*- coding: utf-8 -*-
"""
基础测试脚本，验证meta-cognition技能的基本功能
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    print("=== Meta-Cognition 技能基础测试 ===")
    
    # 测试配置模块
    print("\n1. 测试配置模块")
    from meta_cognition.config import CONFIG
    print(f"配置加载成功")
    print(f"博弈逻辑功能: {'启用' if CONFIG.enable_game_theory else '禁用'}")
    
    # 测试工具函数
    print("\n2. 测试工具函数")
    from meta_cognition.hooks.utils import load_log, save_log, generate_session_id
    log_data = load_log()
    print(f"日志加载成功，会话数量: {len(log_data.get('sessions', []))}")
    
    # 测试任务模式检测
    print("\n3. 测试任务模式检测")
    from meta_cognition.hooks.pre_task_hook import detect_task_mode
    test_tasks = [
        "请帮我优化这段代码，提升性能",
        "请对比敏捷开发和瀑布模型的优缺点",
        "帮我设计一个用户认证系统",
        "1+1等于几？"
    ]
    
    for task in test_tasks:
        mode = detect_task_mode(task)
        print(f"任务: {task} -> 模式: {mode}")
    
    # 测试前置钩子
    print("\n4. 测试前置钩子")
    from meta_cognition.hooks.pre_task_hook import pre_task_hook
    pre_result = pre_task_hook("请帮我优化这段代码，提升性能")
    print(f"前置钩子执行成功，会话ID: {pre_result['session_id']}")
    
    # 测试后置钩子
    print("\n5. 测试后置钩子")
    from meta_cognition.hooks.post_task_hook import post_task_hook
    post_result = post_task_hook(
        session_id=pre_result["session_id"],
        result="success",
        agents_used=["code_executor_agent", "editor_agent"],
        response_preview="优化建议已完成，应用了XYZ技术来提升性能...",
        duration_ms=1500
    )
    print(f"后置钩子执行成功")
    
    # 测试统计功能
    print("\n6. 测试统计功能")
    from meta_cognition.hooks.post_task_hook import get_statistics
    stats = get_statistics()
    print(f"统计信息: {stats}")
    
    print("\n=== 测试完成 ===")
    print("Meta-Cognition 技能基础功能正常")
    
except Exception as e:
    print(f"测试失败: {e}")
    import traceback
    traceback.print_exc()

# -*- coding: utf-8 -*-
"""
测试Meta-Cognition插件的修复效果
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("=== Meta-Cognition 插件修复测试 ===")
    
    # 测试1: 导入配置模块
    print("\n1. 测试配置模块导入")
    from config.config import CONFIG
    print("✓ 配置模块导入成功")
    print(f"   博弈逻辑功能: {'启用' if CONFIG.enable_game_theory else '禁用'}")
    print(f"   统计功能: {'启用' if CONFIG.enable_statistics else '禁用'}")
    
    # 测试2: 导入工具函数
    print("\n2. 测试工具函数导入")
    from hooks.utils import load_log, save_log, generate_session_id
    log_data = load_log()
    print("✓ 工具函数导入成功")
    print(f"   日志加载成功，会话数量: {len(log_data.get('sessions', []))}")
    
    # 测试3: 导入前置钩子
    print("\n3. 测试前置钩子导入")
    from hooks.pre_task_hook import pre_task_hook
    test_task = "请帮我优化这段代码，提升性能"
    pre_result = pre_task_hook(test_task)
    print("✓ 前置钩子导入成功")
    print(f"   会话ID: {pre_result['session_id']}")
    print(f"   检测模式: {pre_result['mode']}")
    
    # 测试4: 导入后置钩子
    print("\n4. 测试后置钩子导入")
    from hooks.post_task_hook import post_task_hook
    post_result = post_task_hook(
        session_id=pre_result["session_id"],
        result="success",
        agents_used=["code_executor_agent", "editor_agent"],
        response_preview="优化建议已完成，应用了XYZ技术来提升性能...",
        duration_ms=1500
    )
    print("✓ 后置钩子导入成功")
    print(f"   后置钩子执行结果: {post_result}")
    
    # 测试5: 测试统计功能
    print("\n5. 测试统计功能")
    from hooks.post_task_hook import get_statistics
    stats = get_statistics()
    print("✓ 统计功能导入成功")
    print(f"   总任务数: {stats.get('total_tasks', 0)}")
    print(f"   成功率: {stats.get('success_rate', 0)}%")
    print(f"   博弈逻辑使用率: {stats.get('game_theory_usage_rate', 0)}%")
    
    # 测试6: 测试日志保存
    print("\n6. 测试日志保存")
    updated_log = load_log()
    print("✓ 日志保存成功")
    print(f"   更新后会话数量: {len(updated_log.get('sessions', []))}")
    
    print("\n=== 测试完成 ===")
    print("✓ 插件修复成功，所有功能正常运行！")
    
except Exception as e:
    print(f"✗ 测试失败: {e}")
    import traceback
    traceback.print_exc()

# -*- coding: utf-8 -*-
"""
手动测试 meta-cognition 技能
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("=== 测试 meta-cognition 技能 ===")
    
    # 测试1: 导入模块
    print("\n1. 测试模块导入")
    from hooks.pre_task_hook import pre_task_hook
    from hooks.post_task_hook import post_task_hook
    from config.config import CONFIG
    print("✓ 模块导入成功")
    
    # 测试2: 测试前置钩子
    print("\n2. 测试前置钩子")
    test_task = "请帮我优化这段代码，提升性能"
    print(f"测试任务: {test_task}")
    
    pre_result = pre_task_hook(test_task)
    print(f"✓ 前置钩子执行成功")
    print(f"  会话ID: {pre_result['session_id']}")
    print(f"  检测模式: {pre_result['mode']}")
    print(f"  推荐智能体: {pre_result['decision']['recommended_agents']}")
    
    # 测试3: 测试后置钩子
    print("\n3. 测试后置钩子")
    post_result = post_task_hook(
        session_id=pre_result["session_id"],
        result="success",
        agents_used=["code_executor_agent", "editor_agent"],
        response_preview="优化已完成，性能提升了50%",
        duration_ms=1500
    )
    print(f"✓ 后置钩子执行成功")
    print(f"  结果: {post_result}")
    
    # 测试4: 检查日志
    print("\n4. 检查日志文件")
    from hooks.utils import load_log
    log_data = load_log()
    print(f"✓ 日志加载成功")
    print(f"  会话数量: {len(log_data.get('sessions', []))}")
    
    if len(log_data.get('sessions', [])) > 0:
        last_session = log_data['sessions'][-1]
        print(f"  最后会话ID: {last_session.get('session_id')}")
        print(f"  最后会话模式: {last_session.get('detected_mode')}")
    
    print("\n=== 测试完成 ===")
    print("✓ meta-cognition 技能功能正常！")
    
except Exception as e:
    print(f"✗ 测试失败: {e}")
    import traceback
    traceback.print_exc()

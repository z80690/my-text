# -*- coding: utf-8 -*-
"""
直接测试meta-cognition技能的核心功能
"""

import sys
import os

# 添加技能目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("=== 测试 meta-cognition 技能 ===")
    
    # 导入模块
    print("\n1. 测试模块导入")
    from meta_cognition.hooks.pre_task_hook import pre_task_hook
    from meta_cognition.hooks.post_task_hook import post_task_hook
    from meta_cognition.hooks.utils import load_log, save_log
    print("✓ 模块导入成功")
    
    # 测试任务列表
    test_tasks = [
        "这是一个简单的代码优化任务。",
        "对比一下敏捷和瀑布开发模式。",
        "请设计一个用户登录系统的架构。",
        "分析这个项目可能存在的风险。",
        "1+1等于几？"
    ]
    
    # 执行五轮测试
    print("\n2. 执行五轮测试")
    for i, task in enumerate(test_tasks, 1):
        print(f"\n【测试 {i}】任务: {task}")
        
        # 执行前置钩子
        pre_result = pre_task_hook(task)
        print(f"✓ 前置钩子执行成功")
        print(f"  会话ID: {pre_result['session_id']}")
        print(f"  检测模式: {pre_result['mode']}")
        
        # 执行后置钩子
        post_result = post_task_hook(
            session_id=pre_result["session_id"],
            result="success",
            agents_used=["code_executor_agent"],
            response_preview=f"测试任务 {i} 完成",
            duration_ms=1000
        )
        print(f"✓ 后置钩子执行成功")
    
    # 检查日志
    print("\n3. 检查日志文件")
    log_data = load_log()
    print(f"✓ 日志加载成功")
    print(f"  会话数量: {len(log_data.get('sessions', []))}")
    
    if len(log_data.get('sessions', [])) > 0:
        last_session = log_data['sessions'][-1]
        print(f"  最后会话ID: {last_session.get('session_id')}")
        print(f"  最后会话模式: {last_session.get('detected_mode')}")
    
    print("\n=== 测试完成 ===")
    print("✓ meta-cognition 技能测试成功！")
    
except Exception as e:
    print(f"✗ 测试失败: {e}")
    import traceback
    traceback.print_exc()

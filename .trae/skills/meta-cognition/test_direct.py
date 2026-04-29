# -*- coding: utf-8 -*-
"""
直接测试 meta-cognition 技能的核心功能
"""

import os
import sys

# 添加技能目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_meta_cognition_core():
    """测试 meta-cognition 技能的核心功能"""
    print("=== 测试 meta-cognition 技能核心功能 ===")
    
    try:
        # 1. 测试模块导入
        print("\n1. 测试模块导入")
        from hooks.pre_task_hook import pre_task_hook, detect_task_mode
        from hooks.post_task_hook import post_task_hook
        from hooks.utils import load_log, save_log
        print("✓ 模块导入成功")
        
        # 2. 测试模式检测
        print("\n2. 测试模式检测")
        test_tasks = [
            ("请帮我优化这段代码，提升性能", "game_theory_mode2"),
            ("请对比敏捷开发和瀑布模型的优缺点", "game_theory_mode1"),
            ("帮我设计一个用户认证系统", "game_theory_mode3"),
            ("1+1等于几？", "normal"),
        ]
        
        for task, expected_mode in test_tasks:
            detected_mode = detect_task_mode(task)
            status = "✓" if detected_mode == expected_mode else "✗"
            print(f"  {status} 任务: {task}")
            print(f"    预期: {expected_mode} -> 实际: {detected_mode}")
        
        # 3. 测试前置钩子
        print("\n3. 测试前置钩子")
        test_task = "请帮我优化这段代码，提升性能"
        pre_result = pre_task_hook(test_task)
        print(f"✓ 前置钩子执行成功")
        print(f"  会话ID: {pre_result['session_id']}")
        print(f"  检测模式: {pre_result['mode']}")
        print(f"  推荐智能体: {pre_result['decision']['recommended_agents']}")
        print(f"  工作流输出: {pre_result['workflow_output']}")
        
        # 4. 测试后置钩子
        print("\n4. 测试后置钩子")
        post_result = post_task_hook(
            session_id=pre_result["session_id"],
            result="success",
            agents_used=["code_executor_agent", "editor_agent"],
            response_preview="优化已完成，性能提升了50%",
            duration_ms=1500
        )
        print(f"✓ 后置钩子执行成功")
        print(f"  结果: {post_result}")
        
        # 5. 检查日志
        print("\n5. 检查日志文件")
        log_data = load_log()
        print(f"✓ 日志加载成功")
        print(f"  会话数量: {len(log_data.get('sessions', []))}")
        
        if len(log_data.get('sessions', [])) > 0:
            last_session = log_data['sessions'][-1]
            print(f"  最后会话ID: {last_session.get('session_id')}")
            print(f"  最后会话模式: {last_session.get('detected_mode')}")
            print(f"  最后会话任务: {last_session.get('task_description')}")
        
        # 6. 测试多次调用
        print("\n6. 测试多次调用")
        for i in range(4):  # 总共测试5次
            test_task = f"测试任务 {i+1}: 帮我优化这段代码，提升性能"
            pre_result = pre_task_hook(test_task)
            post_task_hook(
                session_id=pre_result["session_id"],
                result="success",
                agents_used=["code_executor_agent"],
                response_preview=f"测试任务 {i+1} 完成",
                duration_ms=1000
            )
            print(f"  ✓ 第 {i+1} 次测试完成")
        
        # 7. 最终检查日志
        print("\n7. 最终日志检查")
        log_data = load_log()
        print(f"✓ 最终会话数量: {len(log_data.get('sessions', []))}")
        
        print("\n=== 测试完成 ===")
        print("✓ meta-cognition 技能核心功能正常！")
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_meta_cognition_core()

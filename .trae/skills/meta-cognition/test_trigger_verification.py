# -*- coding: utf-8 -*-
"""
测试验证脚本 - 验证增强后的触发逻辑是否正确
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from integration_config import execute_with_hooks, complete_with_hooks

# 测试用例
test_cases = [
    {
        "task": "帮我优化这段代码",
        "expected_mode": "game_theory_mode2",
        "description": "优化类任务 - 降维打击模式"
    },
    {
        "task": "对比一下微服务和单体架构",
        "expected_mode": "game_theory_mode1", 
        "description": "对比类任务 - 辩论模式"
    },
    {
        "task": "设计一个用户管理系统",
        "expected_mode": "game_theory_mode3",
        "description": "设计类任务 - 深度设计模式"
    },
    {
        "task": "@调度员 帮我规划项目",
        "expected_mode": "game_theory_mode3",
        "description": "显式调用 + 规划 - 深度设计模式"
    },
    {
        "task": "你好",
        "expected_mode": "normal",
        "description": "简单问候 - 常规模式"
    },
    {
        "task": "1+1等于几",
        "expected_mode": "normal", 
        "description": "简单计算 - 常规模式"
    },
    {
        "task": "重构项目结构",
        "expected_mode": "game_theory_mode2",
        "description": "重构类任务 - 降维打击模式"
    },
    {
        "task": "分析这个方案的优缺点",
        "expected_mode": "game_theory_mode1",
        "description": "优缺点分析 - 辩论模式"
    }
]

print("="*60)
print("🚀 智能体调度员触发逻辑测试")
print("="*60)

success_count = 0
failure_count = 0

for i, test_case in enumerate(test_cases, 1):
    print(f"\n--- 测试用例 {i}: {test_case['description']} ---")
    print(f"任务描述: {test_case['task']}")
    
    # 执行前置钩子
    result = execute_with_hooks(test_case['task'])
    detected_mode = result.get('mode')
    session_id = result.get('session_id')
    
    print(f"检测模式: {detected_mode}")
    print(f"预期模式: {test_case['expected_mode']}")
    
    # 判断是否符合预期
    if detected_mode == test_case['expected_mode']:
        print("✅ 触发正确!")
        success_count += 1
    else:
        print("❌ 触发错误!")
        failure_count += 1
    
    # 执行后置钩子
    complete_with_hooks(
        result='success' if detected_mode == test_case['expected_mode'] else 'failure',
        response_preview=f"测试用例{i}完成"
    )

print("\n" + "="*60)
print(f"📊 测试结果: {success_count}/{len(test_cases)} 通过")
print("="*60)

if failure_count > 0:
    print("\n⚠️ 需要优化的触发规则:")
    for i, test_case in enumerate(test_cases, 1):
        result = execute_with_hooks(test_case['task'])
        detected_mode = result.get('mode')
        if detected_mode != test_case['expected_mode']:
            print(f"  • 任务: '{test_case['task']}'")
            print(f"    - 实际: {detected_mode}")
            print(f"    - 预期: {test_case['expected_mode']}")

# -*- coding: utf-8 -*-
"""
测试钩子函数是否正常工作
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from integration_config import execute_with_hooks, complete_with_hooks

# 测试1: 执行前置钩子
print("=== 测试1: 执行前置钩子 ===")
result = execute_with_hooks('测试任务：分析代码优化需求')
print(f"会话ID: {result.get('session_id')}")
print(f"检测模式: {result.get('mode')}")
print(f"任务类型: {result.get('task_type')}")

# 测试2: 执行后置钩子
print("\n=== 测试2: 执行后置钩子 ===")
complete_result = complete_with_hooks(
    result='success', 
    agents_used=['code_executor_agent', 'editor_agent'],
    response_preview='测试完成，代码已优化',
    duration_ms=1500
)
print(f"完成状态: {complete_result.get('status')}")

# 测试3: 测试另一个任务
print("\n=== 测试3: 测试设计任务 ===")
result2 = execute_with_hooks('设计一个微服务架构')
print(f"会话ID: {result2.get('session_id')}")
print(f"检测模式: {result2.get('mode')}")
complete_with_hooks(result='success', response_preview='架构设计完成')

print("\n=== 测试完成 ===")

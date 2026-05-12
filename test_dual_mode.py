# -*- coding: utf-8 -*-
"""
双模式执行测试
"""

import sys
sys.path.insert(0, r"c:\Users\Administrator\Desktop\my-text\trae-core")

print("=" * 60)
print("  双模式执行测试")
print("=" * 60)

from agents.base import AgentConfig
from agents.implementations_v2 import DispatcherAgent

# 创建调度器
config = AgentConfig(
    id="dispatcher",
    name="测试调度",
    type="coordinator",
    capabilities=[]
)
dispatcher = DispatcherAgent(config)

# 测试1: 同步模式（默认）
print("\n[测试1] 同步模式（默认）")
result1 = dispatcher._default_execute("优化这段代码", {})
print(f"  执行模式: {result1['result']['execution_mode']}")
print(f"  状态: {result1['status']}")

# 测试2: 切换到异步模式
print("\n[测试2] 切换到异步模式")
ok = dispatcher.set_execution_mode("async")
print(f"  切换结果: {'成功' if ok else '失败'}")

# 测试3: 异步模式执行
print("\n[测试3] 异步模式执行")
result2 = dispatcher._default_execute("优化这段代码", {})
print(f"  执行模式: {result2['result']['execution_mode']}")
print(f"  状态: {result2['status']}")

# 测试4: 切换回同步模式
print("\n[测试4] 切换回同步模式")
ok = dispatcher.set_execution_mode("sync")
print(f"  切换结果: {'成功' if ok else '失败'}")

# 测试5: 同步模式再次执行
print("\n[测试5] 同步模式再次执行")
result3 = dispatcher._default_execute("设计系统架构", {})
print(f"  执行模式: {result3['result']['execution_mode']}")
print(f"  博弈模式: {result3['result']['game_mode']}")
print(f"  参与智能体: {result3['result']['participating_agents']}")

print("\n" + "=" * 60)
print("  测试完成")
print("=" * 60)

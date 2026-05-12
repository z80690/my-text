# -*- coding: utf-8 -*-
"""
中央调度引擎完整测试 - 强耦合模式
测试DispatcherAgent与TRAE注册中心、消息总线的强耦合
"""

import sys
sys.path.insert(0, r"c:\Users\Administrator\Desktop\my-text\trae-core")

print("=" * 70)
print("  中央调度引擎 - 强耦合模式测试")
print("=" * 70)

# 测试1: 导入和初始化
print("\n[测试1] 初始化调度智能体")
try:
    from agents.base import AgentConfig
    from agents.implementations_v2 import DispatcherAgent
    
    config = AgentConfig(
        id="dispatcher",
        name="测试调度",
        type="coordinator",
        capabilities=[]
    )
    dispatcher = DispatcherAgent(config)
    print("  ✅ 调度智能体初始化成功")
    
    # 检查强耦合组件
    print(f"  - 注册中心: {'已连接' if dispatcher._registry else '未连接'}")
    print(f"  - 调用接口: {'已连接' if dispatcher._call_interface else '未连接'}")
    print(f"  - 消息总线: {'已连接' if dispatcher._message_bus else '未连接'}")
    
except Exception as e:
    print(f"  ❌ 初始化失败: {e}")
    sys.exit(1)

# 测试2: 同步模式执行
print("\n[测试2] 同步模式执行（默认）")
try:
    result = dispatcher._default_execute("设计系统架构方案", {})
    print(f"  ✅ 执行成功")
    print(f"  - 执行模式: {result['result']['execution_mode']}")
    print(f"  - 博弈模式: {result['result']['game_mode']}")
    print(f"  - 参与智能体: {result['result']['participating_agents']}")
    print(f"  - 总线状态: {result['result']['bus_status']}")
    print(f"  - 注册状态: {result['result']['registry_status']}")
except Exception as e:
    print(f"  ❌ 同步模式执行失败: {e}")

# 测试3: 切换到异步模式
print("\n[测试3] 切换到异步模式")
try:
    ok = dispatcher.set_execution_mode("async")
    print(f"  ✅ 模式切换成功" if ok else "  ❌ 模式切换失败")
    print(f"  - 当前模式: {dispatcher.get_execution_mode()}")
except Exception as e:
    print(f"  ❌ 切换失败: {e}")

# 测试4: 异步模式执行
print("\n[测试4] 异步模式执行（消息总线）")
try:
    result = dispatcher._default_execute("优化代码性能", {})
    print(f"  ✅ 执行成功")
    print(f"  - 执行模式: {result['result']['execution_mode']}")
    print(f"  - 博弈模式: {result['result']['game_mode']}")
    print(f"  - 参与智能体: {result['result']['participating_agents']}")
except Exception as e:
    print(f"  ❌ 异步模式执行失败: {e}")

# 测试5: 测试5种博弈模式
print("\n[测试5] 测试5种博弈模式")
game_tasks = [
    ("对比两种方案的优缺点", "debate"),
    ("改进系统性能", "optimization"),
    ("设计分布式架构", "design"),
    ("协商项目优先级", "negotiation"),
    ("分配计算资源", "auction")
]

for task, expected_mode in game_tasks:
    try:
        result = dispatcher._default_execute(task, {})
        actual_mode = result['result']['game_mode']
        status = "✅" if actual_mode == expected_mode else "⚠️"
        print(f"  {status} {task[:20]}... -> {actual_mode}")
    except Exception as e:
        print(f"  ❌ {task[:20]}... -> {e}")

# 测试6: 切换回同步模式
print("\n[测试6] 切换回同步模式")
try:
    ok = dispatcher.set_execution_mode("sync")
    print(f"  ✅ 模式切换成功" if ok else "  ❌ 模式切换失败")
    print(f"  - 当前模式: {dispatcher.get_execution_mode()}")
except Exception as e:
    print(f"  ❌ 切换失败: {e}")

# 测试7: 验证消息总线功能
print("\n[测试7] 消息总线功能验证")
try:
    if dispatcher._message_bus:
        # 检查注册的端点
        endpoints = list(dispatcher._message_bus._endpoints.keys())
        print(f"  ✅ 消息总线已注册 {len(endpoints)} 个端点")
        print(f"  - 端点示例: {endpoints[:5]}...") if len(endpoints) > 5 else print(f"  - 端点: {endpoints}")
    else:
        print("  ❌ 消息总线未初始化")
except Exception as e:
    print(f"  ❌ 消息总线验证失败: {e}")

# 测试8: 验证注册中心功能
print("\n[测试8] 注册中心功能验证")
try:
    if dispatcher._registry:
        agent_ids = dispatcher._registry.get_agent_ids()
        print(f"  ✅ 注册中心已加载 {len(agent_ids)} 个智能体")
        print(f"  - 智能体示例: {agent_ids[:5]}...") if len(agent_ids) > 5 else print(f"  - 智能体: {agent_ids}")
    else:
        print("  ❌ 注册中心未初始化")
except Exception as e:
    print(f"  ❌ 注册中心验证失败: {e}")

print("\n" + "=" * 70)
print("  测试完成")
print("=" * 70)

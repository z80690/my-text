# -*- coding: utf-8 -*-
"""
智能体测试执行日志 v2
记录每个智能体调用
"""

import sys
import os
import asyncio
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.trae'))

from agents.registry import AgentRegistry

def log_agent_call(agent_id: str, task: str, result: dict):
    """记录智能体调用"""
    print(f"\n{'='*70}")
    print(f"📌 智能体调用日志")
    print(f"{'='*70}")
    print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🤖 调用的智能体: {agent_id}")
    print(f"📋 任务: {task}")
    print(f"✅ 执行状态: {result.get('status', 'unknown')}")
    if 'result' in result:
        print(f"📤 返回结果: {str(result['result'])[:200]}...")
    print(f"{'='*70}\n")

async def main():
    """主测试流程"""
    print("\n" + "🎯"*35)
    print("🎯 智能体调度测试开始")
    print("🎯"*35)

    # 初始化注册中心（全局共享）
    print("\n[步骤0] 初始化注册中心...")
    registry = AgentRegistry()
    registry.initialize(".trae")
    print(f"✅ 已加载 {len(registry.get_agent_ids())} 个智能体")

    results = []

    # ========== 测试1: 代码执行智能体 ==========
    print("\n" + "="*70)
    print("🧪 测试1 - 代码执行智能体 (code_executor_agent)")
    print("="*70)

    task1 = "写一个Python函数，计算斐波那契数列第n项"
    print(f"📋 任务内容: {task1}")

    agent1 = registry.create_agent_instance("code_executor_agent")
    if agent1:
        result1 = await agent1.execute(task1, {})
        log_agent_call("code_executor_agent", task1, result1)
        results.append(("code_executor_agent", result1))
    else:
        results.append(("code_executor_agent", {"status": "error", "message": "创建失败"}))

    # ========== 测试2: 通用助手智能体 ==========
    print("\n" + "="*70)
    print("🧪 测试2 - 通用助手智能体 (assistant_agent)")
    print("="*70)

    task2 = "解释什么是人工智能"
    print(f"📋 任务内容: {task2}")

    agent2 = registry.create_agent_instance("assistant_agent")
    if agent2:
        result2 = await agent2.execute(task2, {})
        log_agent_call("assistant_agent", task2, result2)
        results.append(("assistant_agent", result2))
    else:
        results.append(("assistant_agent", {"status": "error", "message": "创建失败"}))

    # ========== 测试3: 心智社会智能体 ==========
    print("\n" + "="*70)
    print("🧪 测试3 - 心智社会智能体 (society_of_mind_agent)")
    print("="*70)

    task3 = "分析人工智能的优缺点"
    print(f"📋 任务内容: {task3}")

    agent3 = registry.create_agent_instance("society_of_mind_agent")
    if agent3:
        result3 = await agent3.execute(task3, {})
        log_agent_call("society_of_mind_agent", task3, result3)
        results.append(("society_of_mind_agent", result3))
    else:
        results.append(("society_of_mind_agent", {"status": "error", "message": "创建失败"}))

    # ========== 测试4: 调度员智能体 ==========
    print("\n" + "="*70)
    print("🧪 测试4 - 调度员智能体 (dispatcher_agent)")
    print("="*70)

    task4 = "协调多个子智能体完成一个复杂任务"
    print(f"📋 任务内容: {task4}")

    agent4 = registry.create_agent_instance("dispatcher_agent")
    if agent4:
        result4 = await agent4.execute(task4, {})
        log_agent_call("dispatcher_agent", task4, result4)
        results.append(("dispatcher_agent", result4))
    else:
        results.append(("dispatcher_agent", {"status": "error", "message": "创建失败"}))

    # 汇总报告
    print("\n" + "="*70)
    print("📊 测试汇总报告")
    print("="*70)
    print(f"总共调用智能体: {len(results)} 个\n")

    for agent_id, result in results:
        status = "✅ 成功" if result.get('status') == 'success' else "❌ 失败"
        print(f"  {status} - {agent_id}")

    print("\n" + "🎯"*35)
    print("🎯 智能体调度测试完成")
    print("🎯"*35)

if __name__ == "__main__":
    asyncio.run(main())

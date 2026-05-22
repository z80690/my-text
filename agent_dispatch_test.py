# -*- coding: utf-8 -*-
"""
智能体测试执行日志
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

async def test_code_executor():
    """测试代码执行智能体"""
    print("\n" + "="*70)
    print("🧪 智能体调度测试 - 代码执行智能体")
    print("="*70)

    # 初始化注册中心
    print("\n[步骤1] 初始化注册中心...")
    registry = AgentRegistry()
    registry.initialize(".trae")
    print(f"✅ 已加载 {len(registry.get_agent_ids())} 个智能体")

    # 测试代码执行智能体
    task = "写一个Python函数，计算斐波那契数列第n项"

    print(f"\n[步骤2] 调用代码执行智能体...")
    print(f"📋 任务内容: {task}")

    agent = registry.create_agent_instance("code_executor_agent")
    if agent:
        result = await agent.execute(task, {})
        log_agent_call("code_executor_agent", task, result)
        return result
    else:
        return {"status": "error", "message": "智能体创建失败"}

async def test_assistant():
    """测试通用助手智能体"""
    print("\n" + "="*70)
    print("🧪 智能体调度测试 - 通用助手智能体")
    print("="*70)

    task = "解释什么是人工智能"

    print(f"\n[步骤2] 调用通用助手智能体...")
    print(f"📋 任务内容: {task}")

    agent = registry.create_agent_instance("assistant_agent")
    if agent:
        result = await agent.execute(task, {})
        log_agent_call("assistant_agent", task, result)
        return result
    else:
        return {"status": "error", "message": "智能体创建失败"}

async def test_society_of_mind():
    """测试心智社会智能体"""
    print("\n" + "="*70)
    print("🧪 智能体调度测试 - 心智社会智能体")
    print("="*70)

    task = "分析人工智能的优缺点"

    print(f"\n[步骤2] 调用心智社会智能体...")
    print(f"📋 任务内容: {task}")

    agent = registry.create_agent_instance("society_of_mind_agent")
    if agent:
        result = await agent.execute(task, {})
        log_agent_call("society_of_mind_agent", task, result)
        return result
    else:
        return {"status": "error", "message": "智能体创建失败"}

async def main():
    """主测试流程"""
    print("\n" + "🎯"*35)
    print("🎯 智能体调度测试开始")
    print("🎯"*35)

    # 按顺序测试3个智能体
    results = []

    # 测试1: 代码执行智能体
    result1 = await test_code_executor()
    results.append(("code_executor_agent", result1))

    # 测试2: 通用助手智能体
    result2 = await test_assistant()
    results.append(("assistant_agent", result2))

    # 测试3: 心智社会智能体
    result3 = await test_society_of_mind()
    results.append(("society_of_mind_agent", result3))

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

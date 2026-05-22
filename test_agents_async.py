# -*- coding: utf-8 -*-
"""异步智能体测试脚本"""

import sys
import os
import asyncio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.trae'))

from agents.registry import AgentRegistry

async def test_agent_execution():
    """测试异步执行智能体"""
    print("=" * 60)
    print("测试异步智能体调用")
    print("=" * 60)
    
    registry = AgentRegistry()
    registry.initialize(".trae")
    
    # 测试多个智能体
    test_cases = [
        ("assistant_agent", "请解释什么是人工智能"),
        ("code_executor_agent", "写一个Python打印Hello World的代码"),
        ("society_of_mind_agent", "分析人工智能的优缺点")
    ]
    
    for agent_id, task in test_cases:
        try:
            agent = registry.create_agent_instance(agent_id)
            if agent:
                result = await agent.execute(task, {})
                print(f"✅ {agent_id}")
                print(f"   任务: {task}")
                print(f"   结果: {result}")
        except Exception as e:
            print(f"❌ {agent_id} 失败: {e}")
        print()

if __name__ == "__main__":
    asyncio.run(test_agent_execution())

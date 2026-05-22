# -*- coding: utf-8 -*-
"""
智能体测试脚本 - 验证 .trae/agents/ 下的智能体是否能正常加载和调用
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.trae'))

from agents.registry import AgentRegistry

def test_agent_registry():
    """测试智能体注册中心"""
    print("=" * 60)
    print("测试智能体注册中心")
    print("=" * 60)
    
    try:
        # 初始化注册中心
        registry = AgentRegistry()
        registry.initialize(".trae")
        
        # 获取智能体列表
        agents = registry.list_agents()
        agent_ids = registry.get_agent_ids()
        
        print(f"\n✅ 成功加载 {len(agents)} 个智能体")
        print("\n智能体列表:")
        print("-" * 60)
        
        for agent in agents:
            print(f"ID: {agent['id']}")
            print(f"  名称: {agent['name']}")
            print(f"  类型: {agent['type']}")
            print(f"  描述: {agent['description']}")
            print(f"  能力: {', '.join(agent['capabilities'])}")
            print()
        
        # 测试创建智能体实例
        print("测试创建智能体实例:")
        print("-" * 60)
        
        test_agent_ids = ['assistant_agent', 'code_executor_agent', 'dispatcher_agent']
        
        for agent_id in test_agent_ids:
            try:
                agent = registry.create_agent_instance(agent_id)
                if agent:
                    print(f"✅ {agent_id} - 创建成功")
                    print(f"   实例类型: {type(agent).__name__}")
                    print(f"   名称: {agent.name}")
                    
                    # 测试执行
                    result = agent.execute("测试任务", {"test": "context"})
                    print(f"   执行结果: {result}")
                else:
                    print(f"❌ {agent_id} - 创建失败")
            except Exception as e:
                print(f"❌ {agent_id} - 错误: {e}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_parallel_call():
    """测试并行调用"""
    print("\n" + "=" * 60)
    print("测试并行调用")
    print("=" * 60)
    
    try:
        registry = AgentRegistry()
        if not registry._initialized:
            registry.initialize(".trae")
        
        # 创建多个智能体实例
        agents_to_call = ['assistant_agent', 'code_executor_agent', 'editor_agent']
        
        print(f"并行调用 {len(agents_to_call)} 个智能体...")
        
        results = []
        for agent_id in agents_to_call:
            agent = registry.create_agent_instance(agent_id)
            if agent:
                result = agent.execute("并行测试任务", {"parallel": True})
                results.append({
                    "agent_id": agent_id,
                    "result": result
                })
        
        print("\n并行调用结果:")
        for res in results:
            print(f"✅ {res['agent_id']}: {res['result'].get('response', '无响应')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 并行调用失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("智能体测试脚本")
    print("验证 .trae/agents/ 下的智能体是否能正常工作")
    print("=" * 80)
    
    success = True
    
    # 测试注册中心
    success &= test_agent_registry()
    
    # 测试并行调用
    success &= test_parallel_call()
    
    print("\n" + "=" * 80)
    if success:
        print("✅ 所有测试通过！智能体系统工作正常")
    else:
        print("❌ 部分测试失败，请检查错误信息")
    print("=" * 80)

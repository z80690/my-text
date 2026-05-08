# -*- coding: utf-8 -*-
"""
简化版智能体测试
"""

import sys
import os

# 添加路径
base_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, base_path)
agents_path = os.path.join(base_path, '.trae', 'agents')
sys.path.insert(0, agents_path)

print("=" * 80)
print("智能体系统测试 - 简化版")
print("=" * 80)
print()

# 导入基础模块
print("【1】导入测试")
try:
    from base import BaseAgent, AgentConfig, ModuleRegistry
    from registry import AgentRegistry
    print("  ✓ 基础模块导入成功")
except Exception as e:
    print(f"  ✗ 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# 初始化
print("【2】初始化注册中心")
try:
    registry = AgentRegistry()
    registry.initialize('.trae')
    print("  ✓ 注册中心初始化成功")
    
    agent_ids = registry.get_agent_ids()
    print(f"  ✓ 发现 {len(agent_ids)} 个智能体")
except Exception as e:
    print(f"  ✗ 初始化失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# 测试实例化和执行
print("【3】智能体测试")
print("-" * 40)

instances = {}
success = 0
fail = 0

for agent_id in agent_ids:
    try:
        print(f"\n  测试: {agent_id}")
        
        # 实例化
        agent = registry.create_agent_instance(agent_id)
        if not agent:
            print(f"    ✗ 实例化失败")
            fail += 1
            continue
        
        instances[agent_id] = agent
        print(f"    ✓ 实例化成功: {agent.name}")
        
        # 执行测试
        result = agent._default_execute(f"测试{agent.name}", {})
        if result.get('status') == 'success':
            print(f"    ✓ 执行成功")
            success += 1
        else:
            print(f"    ✗ 执行失败")
            fail += 1
            
    except Exception as e:
        print(f"    ✗ 异常: {e}")
        fail += 1

print()
print("=" * 80)
print("测试总结")
print("=" * 80)
print(f"  总数: {len(agent_ids)}")
print(f"  成功: {success}")
print(f"  失败: {fail}")
print()

if fail == 0:
    print("  ✓ 所有测试通过！")
else:
    print("  ✗ 部分测试失败")
    
print()
print("智能体列表:")
for aid in agent_ids:
    config = registry.get_config(aid)
    status = "✓" if aid in instances else "✗"
    print(f"  {status} {config['name']} ({aid})")

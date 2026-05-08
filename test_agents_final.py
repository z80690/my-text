# -*- coding: utf-8 -*-
"""
最终版智能体测试
"""

import sys
import os

# 路径设置
base_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, base_path)
agents_dir = os.path.join(base_path, '.trae', 'agents')
sys.path.insert(0, agents_dir)
os.chdir(base_path)

print("=" * 80)
print("智能体系统完整测试")
print("=" * 80)
print()

# 导入
print("【阶段1】模块导入")
try:
    sys.path.insert(0, os.path.join(base_path, '.trae'))
    from agents.registry import AgentRegistry
    from agents.base import BaseAgent, AgentConfig
    from agents.implementations_v2 import *
    print("  ✓ 模块导入成功")
except Exception as e:
    print(f"  ✗ 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# 初始化
print("【阶段2】初始化注册中心")
try:
    registry = AgentRegistry()
    registry.initialize('.trae')
    print("  ✓ 注册中心初始化成功")
    
    agent_ids = registry.get_agent_ids()
    print(f"  ✓ 发现 {len(agent_ids)} 个智能体:")
    for aid in agent_ids:
        cfg = registry.get_config(aid)
        print(f"      - {cfg['name']} ({aid})")
except Exception as e:
    print(f"  ✗ 初始化失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# 测试
print("【阶段3】智能体实例化和执行")
print("-" * 40)

instances = {}
success = 0
fail = 0

for agent_id in agent_ids:
    print(f"\n  【{agent_id}】")
    try:
        # 实例化
        agent = registry.create_agent_instance(agent_id)
        if agent:
            instances[agent_id] = agent
            print(f"    ✓ 实例化成功: {agent.name}")
            
            # 执行
            result = agent._default_execute(f"测试{agent.name}", {})
            if result.get('status') == 'success':
                print(f"    ✓ 执行成功")
                print(f"      响应: {result.get('result', {}).get('response', 'N/A')}")
                success += 1
            else:
                print(f"    ✗ 执行失败")
                fail += 1
        else:
            print(f"    ✗ 实例化失败")
            fail += 1
            
    except Exception as e:
        print(f"    ✗ 异常: {e}")
        import traceback
        traceback.print_exc()
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
    sys.exit(1)

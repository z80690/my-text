# -*- coding: utf-8 -*-
"""
验证智能体注册情况
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from agent.agents.registry import get_registry
    
    registry = get_registry()
    agents = registry.list_agents()
    
    print(f"已注册智能体数量: {len(agents)}")
    print("\n智能体列表:")
    for i, agent in enumerate(agents, 1):
        print(f"{i}. {agent['name']} ({agent['id']})")
        print(f"   描述: {agent['description']}")
        print()
    
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()

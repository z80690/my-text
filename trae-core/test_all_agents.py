# -*- coding: utf-8 -*-
"""
测试所有20个智能体
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from agent.agents.registry import get_registry
    
    registry = get_registry()
    agents = registry.list_agents()
    
    print(f"开始测试 {len(agents)} 个智能体...\n")
    
    success_count = 0
    total_count = len(agents)
    
    for agent in agents:
        agent_id = agent['id']
        agent_name = agent['name']
        
        try:
            result = registry.execute(agent_id, "test")
            if result.get('status') == 'success':
                print(f"[成功] {agent_name}")
                success_count += 1
            else:
                print(f"[失败] {agent_name}: {result.get('message', '未知错误')}")
        except Exception as e:
            print(f"[错误] {agent_name}: {e}")
    
    print(f"\n总计: {success_count}/{total_count} 智能体运行正常")
    
    if success_count == total_count:
        print("所有智能体测试通过！")
    else:
        print("部分智能体测试失败！")
    
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()

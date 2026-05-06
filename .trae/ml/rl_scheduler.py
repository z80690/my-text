# -*- coding: utf-8 -*-
"""强化学习调度器 - 异步版本"""

import random
import numpy as np
import asyncio
from typing import List, Dict, Any

class RLBasedScheduler:
    """基于强化学习的调度器"""
    
    def __init__(self, num_agents: int, num_tasks: int):
        self.num_agents = num_agents
        self.num_tasks = num_tasks
        
        self.q_table = {}
        
        self.alpha = 0.1
        self.gamma = 0.9
        self.epsilon = 0.1
    
    def _get_state(self, task_type: int, agent_loads: List[int]) -> str:
        """获取状态表示"""
        load_levels = [min(l // 10, 5) for l in agent_loads]
        return f"{task_type}:{','.join(map(str, load_levels))}"
    
    async def select_action(self, state: str, agent_ids: List[int]) -> int:
        """异步选择动作"""
        loop = asyncio.get_event_loop()
        
        def _select():
            if random.random() < self.epsilon:
                return random.choice(agent_ids)
            
            if state not in self.q_table:
                self.q_table[state] = {aid: 0.0 for aid in agent_ids}
            
            q_values = self.q_table[state]
            return max(q_values, key=q_values.get)
        
        return await loop.run_in_executor(None, _select)
    
    async def update_q_value(self, state: str, action: int, reward: float, next_state: str):
        """异步更新Q值"""
        loop = asyncio.get_event_loop()
        
        def _update():
            if state not in self.q_table:
                self.q_table[state] = {action: 0.0}
            
            old_q = self.q_table[state].get(action, 0.0)
            
            if next_state in self.q_table:
                max_next_q = max(self.q_table[next_state].values())
            else:
                max_next_q = 0.0
            
            new_q = old_q + self.alpha * (reward + self.gamma * max_next_q - old_q)
            self.q_table[state][action] = new_q
        
        await loop.run_in_executor(None, _update)
    
    async def schedule(self, task_type: int, agent_ids: List[int], agent_loads: List[int]) -> int:
        """异步调度任务"""
        state = self._get_state(task_type, agent_loads)
        action = await self.select_action(state, agent_ids)
        
        avg_load = sum(agent_loads) / len(agent_loads)
        action_idx = agent_ids.index(action)
        reward = 1.0 - abs(agent_loads[action_idx] - avg_load) / max(agent_loads)
        
        new_loads = agent_loads.copy()
        new_loads[action_idx] += 1
        next_state = self._get_state(task_type, new_loads)
        
        await self.update_q_value(state, action, reward, next_state)
        
        return action
# -*- coding: utf-8 -*-
"""智能体专用缓存 - 异步版本"""

import asyncio
from typing import Dict, Any
from .lru_cache import LRUCache

class AgentCache:
    """智能体执行结果缓存"""
    
    def __init__(self, max_size: int = 10000):
        self.cache = LRUCache(capacity=max_size)
        self.agent_stats: Dict[str, int] = {}
    
    async def get(self, agent_id: str, task_hash: str) -> Any:
        """异步获取智能体执行结果"""
        loop = asyncio.get_event_loop()
        key = f"{agent_id}:{task_hash}"
        result = await loop.run_in_executor(None, self.cache.get, key)
        
        if result:
            self.agent_stats[agent_id] = self.agent_stats.get(agent_id, 0) + 1
        
        return result
    
    async def put(self, agent_id: str, task_hash: str, result: Any):
        """异步缓存智能体执行结果"""
        loop = asyncio.get_event_loop()
        key = f"{agent_id}:{task_hash}"
        await loop.run_in_executor(None, self.cache.put, key, result)
    
    async def invalidate_agent(self, agent_id: str):
        """异步失效指定智能体的所有缓存"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.cache.invalidate, f"{agent_id}:")
    
    def get_stats(self) -> Dict[str, int]:
        """获取缓存统计"""
        return self.agent_stats.copy()
    
    async def clear(self):
        """异步清空缓存"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.cache.clear)
        self.agent_stats.clear()
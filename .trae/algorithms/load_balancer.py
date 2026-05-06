# -*- coding: utf-8 -*-
"""负载均衡器 - 异步版本"""

import random
import hashlib
import yaml
import asyncio
from pathlib import Path
from typing import Dict, List, Any

class WeightedLoadBalancer:
    """加权负载均衡器"""
    
    def __init__(self):
        self.weights: Dict[str, float] = {}
        self.counters: Dict[str, int] = {}
    
    async def initialize(self):
        """异步初始化 - 自动加载权重"""
        config_path = Path('.trae/agents.yaml')
        
        if config_path.exists():
            loop = asyncio.get_event_loop()
            with open(config_path, 'r', encoding='utf-8') as f:
                config = await loop.run_in_executor(None, yaml.safe_load, f)
                
                qos_weights = {'critical': 3.0, 'high': 2.0, 'normal': 1.0, 'low': 0.5}
                
                for agent in config.get('agents', []):
                    agent_id = agent['id']
                    qos_level = agent.get('qos_level', 'normal')
                    self.weights[agent_id] = qos_weights.get(qos_level, 1.0)
                    self.counters[agent_id] = 0
    
    def set_weights(self, agent_weights: Dict[str, float]):
        """设置智能体权重"""
        self.weights = agent_weights
        self.counters = {agent_id: 0 for agent_id in agent_weights}
    
    async def select_agent(self, agent_ids: List[str]) -> str:
        """异步选择智能体"""
        if not agent_ids:
            raise ValueError("智能体列表为空")
        
        for agent_id in agent_ids:
            if agent_id not in self.weights:
                self.weights[agent_id] = 1.0
            if agent_id not in self.counters:
                self.counters[agent_id] = 0
        
        max_diff = -1
        selected = agent_ids[0]
        
        for agent_id in agent_ids:
            weight = self.weights.get(agent_id, 1.0)
            current = self.counters[agent_id]
            diff = weight - current
            
            if diff > max_diff:
                max_diff = diff
                selected = agent_id
        
        self.counters[selected] += 1
        
        if all(self.counters.get(aid, 0) >= self.weights.get(aid, 1.0) for aid in agent_ids):
            self.counters = {aid: 0 for aid in agent_ids}
        
        return selected

class ConsistentHashing:
    """一致性哈希实现"""
    
    def __init__(self, replicas: int = 100):
        self.replicas = replicas
        self.ring = {}
    
    async def initialize(self):
        """异步初始化 - 自动注册智能体"""
        config_path = Path('.trae/agents.yaml')
        
        if config_path.exists():
            loop = asyncio.get_event_loop()
            with open(config_path, 'r', encoding='utf-8') as f:
                config = await loop.run_in_executor(None, yaml.safe_load, f)
                
                for agent in config.get('agents', []):
                    self.add_agent(agent['id'])
    
    def _hash(self, key: str) -> int:
        """计算哈希值"""
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
    
    def add_agent(self, agent_id: str):
        """添加智能体到哈希环"""
        for i in range(self.replicas):
            key = f"{agent_id}:{i}"
            hash_val = self._hash(key)
            self.ring[hash_val] = agent_id
    
    def remove_agent(self, agent_id: str):
        """从哈希环移除智能体"""
        for i in range(self.replicas):
            key = f"{agent_id}:{i}"
            hash_val = self._hash(key)
            if hash_val in self.ring:
                del self.ring[hash_val]
    
    async def get_agent(self, task_id: str) -> str:
        """异步获取任务对应的智能体"""
        if not self.ring:
            raise ValueError("哈希环为空")
        
        hash_val = self._hash(task_id)
        keys = sorted(self.ring.keys())
        
        for key in keys:
            if key >= hash_val:
                return self.ring[key]
        
        return self.ring[keys[0]]
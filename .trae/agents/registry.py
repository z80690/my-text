# -*- coding: utf-8 -*-
"""智能体注册中心 - 自动启用"""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional

class AgentRegistry:
    """智能体注册中心"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._agents = {}
            cls._instance._initialized = False
        return cls._instance
    
    async def initialize(self):
        """初始化注册中心"""
        if self._initialized:
            return
        
        # 从YAML配置加载智能体
        config_path = Path('.trae/agents.yaml')
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                
                for agent_data in config.get('agents', []):
                    self._agents[agent_data['id']] = agent_data
        
        self._initialized = True
    
    def get(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """获取智能体"""
        return self._agents.get(agent_id)
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """列出所有智能体"""
        return list(self._agents.values())
    
    def get_agent_ids(self) -> List[str]:
        """获取所有智能体ID"""
        return list(self._agents.keys())
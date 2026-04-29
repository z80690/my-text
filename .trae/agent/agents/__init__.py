# -*- coding: utf-8 -*-
"""
智能体模块初始化
"""

from .base import BaseAgent, AgentConfig
from .registry import get_registry
from .implementations import load_all_agents

# 自动加载所有智能体
load_all_agents()

__all__ = [
    'BaseAgent',
    'AgentConfig',
    'get_registry',
    'load_all_agents'
]

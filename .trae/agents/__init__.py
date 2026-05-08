# -*- coding: utf-8 -*-
"""
智能体模块初始化 - V2
"""

from .base import BaseAgent, AgentConfig, ModuleRegistry, get_registry
from .registry import AgentRegistry, get_registry as get_agent_registry
from .implementations_v2 import *

__all__ = [
    'BaseAgent',
    'AgentConfig',
    'ModuleRegistry',
    'AgentRegistry',
    'get_registry',
    'get_agent_registry',
]

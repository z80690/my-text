# -*- coding: utf-8 -*-
"""缓存模块 - 自动加载"""

from .cache_manager import CacheManager
from .lru_cache import LRUCache
from .lfu_cache import LFUCache
from .ttl_cache import TTLCache
from .agent_cache import AgentCache

__all__ = [
    'CacheManager',
    'LRUCache',
    'LFUCache',
    'TTLCache',
    'AgentCache'
]
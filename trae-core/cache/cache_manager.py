# -*- coding: utf-8 -*-
"""缓存管理器 - 异步版本"""

import asyncio
from typing import Dict, Any, Optional

class CacheManager:
    """缓存管理器"""
    
    def __init__(self):
        self.caches: Dict[str, Any] = {}
    
    def create_cache(self, name: str, cache_type: str, **kwargs):
        """创建缓存实例"""
        if cache_type == 'lru':
            from .lru_cache import LRUCache
            self.caches[name] = LRUCache(**kwargs)
        elif cache_type == 'lfu':
            from .lfu_cache import LFUCache
            self.caches[name] = LFUCache(**kwargs)
        elif cache_type == 'ttl':
            from .ttl_cache import TTLCache
            self.caches[name] = TTLCache(**kwargs)
    
    def get_cache(self, name: str) -> Any:
        """获取缓存实例"""
        return self.caches.get(name)
    
    async def get(self, cache_name: str, key: str) -> Any:
        """异步获取缓存值"""
        loop = asyncio.get_event_loop()
        cache = self.get_cache(cache_name)
        if not cache:
            return None
        return await loop.run_in_executor(None, cache.get, key)
    
    async def put(self, cache_name: str, key: str, value: Any, **kwargs):
        """异步设置缓存值"""
        loop = asyncio.get_event_loop()
        cache = self.get_cache(cache_name)
        if cache:
            await loop.run_in_executor(None, cache.put, key, value)
    
    async def invalidate(self, cache_name: str, pattern: str = None):
        """异步失效缓存"""
        loop = asyncio.get_event_loop()
        cache = self.get_cache(cache_name)
        if cache:
            if pattern:
                await loop.run_in_executor(None, cache.invalidate, pattern)
            else:
                await loop.run_in_executor(None, cache.clear)
    
    async def clear_all(self):
        """异步清空所有缓存"""
        loop = asyncio.get_event_loop()
        for cache in self.caches.values():
            await loop.run_in_executor(None, cache.clear)
# -*- coding: utf-8 -*-
"""LRU缓存 - 自动启用"""

from collections import OrderedDict
from typing import Any

class LRUCache:
    """LRU缓存实现"""
    
    def __init__(self, capacity: int = 1000):
        self.cache = OrderedDict()
        self.capacity = capacity
    
    def get(self, key: str) -> Any:
        """获取缓存"""
        if key not in self.cache:
            return None
        
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def put(self, key: str, value: Any):
        """设置缓存"""
        if key in self.cache:
            self.cache.move_to_end(key)
        elif len(self.cache) >= self.capacity:
            self.cache.popitem(last=False)
        
        self.cache[key] = value
    
    def invalidate(self, pattern: str):
        """按模式失效缓存"""
        keys_to_remove = [k for k in self.cache if pattern in k]
        for key in keys_to_remove:
            del self.cache[key]
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
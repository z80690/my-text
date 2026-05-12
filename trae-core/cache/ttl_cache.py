# -*- coding: utf-8 -*-
"""TTL缓存 - 自动启用"""

import time
from typing import Dict, Any, Optional

class TTLCache:
    """TTL缓存实现"""
    
    def __init__(self, default_ttl: int = 3600):
        self.cache: Dict[str, Tuple[Any, float]] = {}
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Any:
        """获取缓存"""
        item = self.cache.get(key)
        if item is None:
            return None
        
        value, expire_time = item
        
        if time.time() > expire_time:
            del self.cache[key]
            return None
        
        return value
    
    def put(self, key: str, value: Any, ttl: Optional[int] = None):
        """设置缓存"""
        expire_time = time.time() + (ttl or self.default_ttl)
        self.cache[key] = (value, expire_time)
    
    def invalidate(self, pattern: str):
        """按模式失效缓存"""
        keys_to_remove = [k for k in self.cache if pattern in k]
        for key in keys_to_remove:
            del self.cache[key]
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
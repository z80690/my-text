# -*- coding: utf-8 -*-
"""LFU缓存 - 自动启用"""

from collections import defaultdict
from typing import Any

class LFUCache:
    """LFU缓存实现"""
    
    def __init__(self, capacity: int = 500):
        self.capacity = capacity
        self.cache = {}
        self.freq_map = defaultdict(set)
        self.min_freq = 0
    
    def get(self, key: str) -> Any:
        """获取缓存"""
        if key not in self.cache:
            return None
        
        value, freq = self.cache[key]
        
        self.freq_map[freq].remove(key)
        if not self.freq_map[freq] and self.min_freq == freq:
            self.min_freq += 1
        
        freq += 1
        self.cache[key] = (value, freq)
        self.freq_map[freq].add(key)
        
        return value
    
    def put(self, key: str, value: Any):
        """设置缓存"""
        if self.capacity == 0:
            return
        
        if key in self.cache:
            _, freq = self.cache[key]
            self.freq_map[freq].remove(key)
            if not self.freq_map[freq] and self.min_freq == freq:
                self.min_freq += 1
            
            freq += 1
            self.cache[key] = (value, freq)
            self.freq_map[freq].add(key)
        else:
            if len(self.cache) >= self.capacity:
                keys = self.freq_map[self.min_freq]
                key_to_remove = keys.pop()
                del self.cache[key_to_remove]
            
            self.cache[key] = (value, 1)
            self.freq_map[1].add(key)
            self.min_freq = 1
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
        self.freq_map.clear()
        self.min_freq = 0
# -*- coding: utf-8 -*-
"""漏桶算法 - 自动启用"""

import time
from threading import Lock

class LeakyBucket:
    """漏桶限流算法"""
    
    def __init__(self, capacity: int, leak_rate: int):
        self.capacity = capacity
        self.leak_rate = leak_rate
        self.water = 0
        self.last_leak_time = time.time()
        self.lock = Lock()
    
    def _leak(self):
        """漏水"""
        now = time.time()
        time_passed = now - self.last_leak_time
        
        leaked = time_passed * self.leak_rate / 1000
        self.water = max(0, self.water - leaked)
        self.last_leak_time = now
    
    def allow(self) -> bool:
        """是否允许请求"""
        with self.lock:
            self._leak()
            
            if self.water < self.capacity:
                self.water += 1
                return True
            
            return False
    
    def get_level(self) -> float:
        """获取当前水位"""
        with self.lock:
            self._leak()
            return self.water
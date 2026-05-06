# -*- coding: utf-8 -*-
"""令牌桶算法 - 自动启用"""

import time
from threading import Lock

class TokenBucket:
    """令牌桶限流算法"""
    
    def __init__(self, capacity: int, refill_rate: int):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill_time = time.time()
        self.lock = Lock()
    
    def _refill(self):
        """补充令牌"""
        now = time.time()
        time_passed = now - self.last_refill_time
        
        new_tokens = time_passed * self.refill_rate / 1000
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill_time = now
    
    def allow(self, tokens: int = 1) -> bool:
        """是否允许请求"""
        with self.lock:
            self._refill()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            
            return False
    
    def get_remaining(self) -> float:
        """获取剩余令牌数"""
        with self.lock:
            self._refill()
            return self.tokens
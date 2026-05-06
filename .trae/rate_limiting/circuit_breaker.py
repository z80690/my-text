# -*- coding: utf-8 -*-
"""熔断器模式 - 异步版本"""

import time
import asyncio
from enum import Enum
from typing import Callable, Any, Dict

class CircuitBreakerState(Enum):
    """熔断器状态"""
    CLOSED = 'closed'
    OPEN = 'open'
    HALF_OPEN = 'half_open'

class CircuitBreaker:
    """熔断器实现"""
    
    def __init__(self, failure_threshold: int = 5, 
                recovery_timeout: int = 30,
                success_threshold: int = 3):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
    
    def _should_allow(self) -> bool:
        """是否允许调用"""
        if self.state == CircuitBreakerState.CLOSED:
            return True
        
        if self.state == CircuitBreakerState.OPEN:
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = CircuitBreakerState.HALF_OPEN
                return True
            return False
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            return True
        
        return False
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """异步执行受保护的调用"""
        if not self._should_allow():
            raise Exception("Circuit breaker is open")
        
        try:
            # 使用异步执行
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, func, *args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """成功处理"""
        self.success_count += 1
        self.failure_count = 0
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            if self.success_count >= self.success_threshold:
                self.state = CircuitBreakerState.CLOSED
                self.success_count = 0
    
    def _on_failure(self):
        """失败处理"""
        self.failure_count += 1
        self.success_count = 0
        
        if self.state == CircuitBreakerState.CLOSED:
            if self.failure_count >= self.failure_threshold:
                self._open_circuit()
        elif self.state == CircuitBreakerState.HALF_OPEN:
            self._open_circuit()
    
    def _open_circuit(self):
        """打开熔断器"""
        self.state = CircuitBreakerState.OPEN
        self.last_failure_time = time.time()

class CircuitBreakerManager:
    """熔断器管理器"""
    
    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {}
    
    def create_breaker(self, name: str, **kwargs):
        """创建熔断器"""
        self.breakers[name] = CircuitBreaker(**kwargs)
    
    def get_breaker(self, name: str) -> CircuitBreaker:
        """获取熔断器"""
        return self.breakers.get(name)
    
    async def call(self, breaker_name: str, func: Callable, *args, **kwargs) -> Any:
        """异步通过熔断器调用函数"""
        breaker = self.get_breaker(breaker_name)
        if not breaker:
            # 如果没有熔断器，直接异步执行
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, func, *args, **kwargs)
        
        return await breaker.call(func, *args, **kwargs)
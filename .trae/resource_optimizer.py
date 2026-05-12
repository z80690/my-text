"""
资源优化管理器 - 自动调优系统资源

特性：
- CPU 占用自动优化
- 内存自动管理
- 智能缓存策略
- 自适应并发控制
"""

import os
import time
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from collections import OrderedDict


@dataclass
class OptimizationConfig:
    """优化配置"""
    target_cpu_usage: float = 70.0
    target_memory_mb: float = 512.0
    min_concurrent_tasks: int = 5
    max_concurrent_tasks: int = 100
    cache_ttl_seconds: int = 300
    gc_interval_seconds: int = 60


class LRUCache:
    """LRU 缓存 - 内存优化"""

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 300):
        self.cache = OrderedDict()
        self.ttl = ttl_seconds
        self.max_size = max_size
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        async with self._lock:
            if key not in self.cache:
                return None

            item, timestamp = self.cache[key]

            if time.time() - timestamp > self.ttl:
                del self.cache[key]
                return None

            self.cache.move_to_end(key)
            return item

    async def set(self, key: str, value: Any):
        """设置缓存"""
        async with self._lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            elif len(self.cache) >= self.max_size:
                self.cache.popitem(last=False)

            self.cache[key] = (value, time.time())

    async def clear(self):
        """清空缓存"""
        async with self._lock:
            self.cache.clear()

    async def cleanup_expired(self):
        """清理过期缓存"""
        async with self._lock:
            expired_keys = []
            current_time = time.time()

            for key, (_, timestamp) in self.cache.items():
                if current_time - timestamp > self.ttl:
                    expired_keys.append(key)

            for key in expired_keys:
                del self.cache[key]

            return len(expired_keys)

    async def size(self) -> int:
        """获取缓存大小"""
        async with self._lock:
            return len(self.cache)


class ResourceMonitor:
    """资源监控器"""

    def __init__(self, config: OptimizationConfig, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.cpu_history = []
        self.memory_history = []
        self._lock = asyncio.Lock()

    async def get_cpu_usage(self) -> float:
        """获取 CPU 使用率"""
        try:
            import psutil
            return psutil.cpu_percent(interval=0.1)
        except (ImportError, Exception):
            return 0.0

    async def get_memory_usage(self) -> float:
        """获取内存使用（MB）"""
        try:
            import psutil
            return psutil.Process().memory_info().rss / 1024 / 1024
        except (ImportError, Exception):
            return 0.0

    async def record_samples(self):
        """记录资源使用样本"""
        cpu = await self.get_cpu_usage()
        memory = await self.get_memory_usage()

        async with self._lock:
            self.cpu_history.append(cpu)
            self.memory_history.append(memory)

            if len(self.cpu_history) > 60:
                self.cpu_history = self.cpu_history[-60:]
            if len(self.memory_history) > 60:
                self.memory_history = self.memory_history[-60:]

        return cpu, memory

    async def get_average_usage(self, window_seconds: int = 30) -> Dict[str, float]:
        """获取平均资源使用"""
        async with self._lock:
            if not self.cpu_history:
                return {'cpu': 0.0, 'memory': 0.0}

            samples = min(len(self.cpu_history), window_seconds)

            return {
                'cpu': sum(self.cpu_history[-samples:]) / samples,
                'memory': sum(self.memory_history[-samples:]) / samples
            }


class AdaptiveConcurrencyController:
    """自适应并发控制器"""

    def __init__(self, config: OptimizationConfig, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.current_concurrency = config.min_concurrent_tasks
        self._lock = asyncio.Lock()

    async def adjust_concurrency(self, cpu_usage: float, memory_usage: float) -> int:
        """根据资源使用调整并发数"""
        async with self._lock:
            cpu_ratio = cpu_usage / self.config.target_cpu_usage
            memory_ratio = memory_usage / self.config.target_memory_mb

            if cpu_ratio > 0.9 or memory_ratio > 0.9:
                adjustment = -max(1, int(self.current_concurrency * 0.1))
            elif cpu_ratio < 0.5 and memory_ratio < 0.5:
                adjustment = max(1, int(self.current_concurrency * 0.2))
            else:
                adjustment = 0

            old_concurrency = self.current_concurrency
            self.current_concurrency += adjustment
            self.current_concurrency = max(self.config.min_concurrent_tasks,
                                           min(self.current_concurrency,
                                               self.config.max_concurrent_tasks))

            if adjustment != 0:
                self.logger.info(
                    f"[并发控制器] 并发数调整: {old_concurrency} -> {self.current_concurrency} "
                    f"(CPU: {cpu_usage:.1f}%, Memory: {memory_usage:.1f}MB)"
                )

            return self.current_concurrency

    async def get_current_concurrency(self) -> int:
        """获取当前并发数"""
        async with self._lock:
            return self.current_concurrency


class GarbageCollectorOptimizer:
    """垃圾回收优化器"""

    def __init__(self, config: OptimizationConfig, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.last_gc_time = 0.0
        self._gc_counts = {0: 0, 1: 0, 2: 0}

    async def smart_collect(self, memory_usage: float):
        """智能垃圾回收"""
        current_time = time.time()

        if current_time - self.last_gc_time < self.config.gc_interval_seconds:
            return False

        import gc

        memory_ratio = memory_usage / self.config.target_memory_mb

        if memory_ratio > 0.8:
            gc.collect(generation=2)
            self._gc_counts[2] += 1
            self.logger.debug("[GC] Full GC (generation 2)")
        elif memory_ratio > 0.6:
            gc.collect(generation=1)
            self._gc_counts[1] += 1
            self.logger.debug("[GC] Medium GC (generation 1)")
        elif memory_ratio > 0.4:
            gc.collect(generation=0)
            self._gc_counts[0] += 1
            self.logger.debug("[GC] Light GC (generation 0)")

        self.last_gc_time = current_time
        return True

    def get_gc_stats(self) -> Dict[str, int]:
        """获取 GC 统计"""
        return self._gc_counts.copy()


class ResourceOptimizationManager:
    """资源优化管理器"""

    def __init__(self, config: Optional[OptimizationConfig] = None,
                 logger: Optional[logging.Logger] = None):
        self.config = config or OptimizationConfig()
        self.logger = logger or self._setup_default_logger()

        self.cache = LRUCache(
            max_size=1000,
            ttl_seconds=self.config.cache_ttl_seconds
        )

        self.resource_monitor = ResourceMonitor(self.config, self.logger)
        self.concurrency_controller = AdaptiveConcurrencyController(
            self.config, self.logger
        )
        self.gc_optimizer = GarbageCollectorOptimizer(self.config, self.logger)

        self._background_task = None
        self._running = False

    def _setup_default_logger(self) -> logging.Logger:
        """设置默认日志"""
        logger = logging.getLogger("resource_optimizer")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    async def start(self):
        """启动优化器"""
        if self._running:
            return

        self._running = True
        self._background_task = asyncio.create_task(self._optimization_loop())
        self.logger.info("[资源优化器] 已启动")

    async def stop(self):
        """停止优化器"""
        self._running = False
        if self._background_task:
            self._background_task.cancel()
            try:
                await self._background_task
            except asyncio.CancelledError:
                pass
        self.logger.info("[资源优化器] 已停止")

    async def _optimization_loop(self):
        """优化循环"""
        while self._running:
            try:
                cpu, memory = await self.resource_monitor.record_samples()

                avg_usage = await self.resource_monitor.get_average_usage()

                await self.concurrency_controller.adjust_concurrency(
                    avg_usage['cpu'], avg_usage['memory']
                )

                await self.gc_optimizer.smart_collect(memory)

                await self.cache.cleanup_expired()

                await asyncio.sleep(2.0)

            except Exception as e:
                self.logger.error(f"优化循环错误: {e}")
                await asyncio.sleep(1.0)

    async def get_optimization_stats(self) -> Dict[str, Any]:
        """获取优化统计"""
        avg_usage = await self.resource_monitor.get_average_usage()
        current_concurrency = await self.concurrency_controller.get_current_concurrency()

        return {
            'average_cpu_percent': round(avg_usage['cpu'], 1),
            'average_memory_mb': round(avg_usage['memory'], 1),
            'current_concurrency': current_concurrency,
            'cache_size': await self.cache.size(),
            'gc_stats': self.gc_optimizer.get_gc_stats(),
            'config': {
                'target_cpu_percent': self.config.target_cpu_usage,
                'target_memory_mb': self.config.target_memory_mb
            }
        }

    async def cached_exec(self, key: str, func: Callable, *args, **kwargs) -> Any:
        """带缓存的执行"""
        cached = await self.cache.get(key)
        if cached is not None:
            return cached

        result = func(*args, **kwargs)
        if asyncio.iscoroutine(result):
            result = await result

        await self.cache.set(key, result)
        return result


_optimizer_instance: Optional[ResourceOptimizationManager] = None


def get_resource_optimizer(config: Optional[OptimizationConfig] = None,
                           logger: Optional[logging.Logger] = None) -> ResourceOptimizationManager:
    """获取资源优化器单例"""
    global _optimizer_instance
    if _optimizer_instance is None:
        _optimizer_instance = ResourceOptimizationManager(config, logger)
    return _optimizer_instance


# 使用示例
async def main():
    print("=== 资源优化管理器测试 ===")

    optimizer = get_resource_optimizer()
    await optimizer.start()

    print("\n--- 运行中（10秒）---")
    await asyncio.sleep(10.0)

    print("\n--- 优化统计 ---")
    stats = await optimizer.get_optimization_stats()
    import json
    print(json.dumps(stats, indent=2, ensure_ascii=False))

    await optimizer.stop()


if __name__ == "__main__":
    asyncio.run(main())

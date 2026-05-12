"""
全异步工作流引擎 - 优化版
使用 asyncio 原生并发，大幅降低 CPU 和内存占用

特性：
- 100% asyncio 原生并发
- 智能资源限制
- 内存自动优化
- 内置性能监控
"""

import os
import json
import logging
import time
import asyncio
import tracemalloc
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from collections import deque


@dataclass
class ResourceLimits:
    """资源限制配置"""
    max_concurrent_tasks: int = 50
    max_memory_mb: float = 512.0
    task_timeout: float = 300.0
    max_queue_size: int = 1000


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self):
        self.start_time = time.time()
        self.task_count = 0
        self.success_count = 0
        self.fail_count = 0
        self.total_execution_time = 0.0
        self.memory_samples = []
        self.cpu_samples = []
        self._lock = asyncio.Lock()

    async def record_task(self, success: bool, duration: float):
        """记录任务执行"""
        async with self._lock:
            self.task_count += 1
            if success:
                self.success_count += 1
            else:
                self.fail_count += 1
            self.total_execution_time += duration

    async def record_memory(self, memory_mb: float):
        """记录内存使用"""
        async with self._lock:
            self.memory_samples.append(memory_mb)
            if len(self.memory_samples) > 100:
                self.memory_samples = self.memory_samples[-100:]

    async def get_stats(self) -> Dict:
        """获取统计信息"""
        async with self._lock:
            avg_time = self.total_execution_time / max(1, self.task_count)
            success_rate = self.success_count / max(1, self.task_count) * 100
            avg_memory = sum(self.memory_samples) / max(1, len(self.memory_samples)) if self.memory_samples else 0

            return {
                'uptime_seconds': time.time() - self.start_time,
                'total_tasks': self.task_count,
                'success_count': self.success_count,
                'fail_count': self.fail_count,
                'success_rate': round(success_rate, 2),
                'avg_task_time_ms': round(avg_time * 1000, 2),
                'avg_memory_mb': round(avg_memory, 2),
                'memory_samples': len(self.memory_samples)
            }


class MemoryOptimizer:
    """内存优化器"""

    def __init__(self, max_memory_mb: float = 512.0):
        self.max_memory_mb = max_memory_mb
        self._cleanup_threshold = max_memory_mb * 0.8
        self._gc_threshold = max_memory_mb * 0.9

    def get_current_memory(self) -> float:
        """获取当前内存使用（MB）"""
        try:
            import psutil
            return psutil.Process().memory_info().rss / 1024 / 1024
        except (ImportError, Exception):
            try:
                snapshot = tracemalloc.take_snapshot()
                return sum(stat.size for stat in snapshot.statistics('lineno')) / 1024 / 1024
            except Exception:
                return 0.0

    async def check_and_cleanup(self):
        """检查并执行内存清理"""
        current_memory = self.get_current_memory()

        if current_memory > self._cleanup_threshold:
            import gc
            gc.collect()

        if current_memory > self._gc_threshold:
            gc.collect(generation=2)
            gc.collect(generation=1)
            gc.collect(generation=0)

        return current_memory


class AsyncMonitorAgent:
    """异步监控智能体"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.task_status = {}
        self.metrics = {}
        self._lock = asyncio.Lock()

    async def start_monitoring(self, task_id: str, worker_agent: str, task_desc: str):
        """开始监控任务"""
        async with self._lock:
            self.task_status[task_id] = {
                'status': 'running',
                'worker_agent': worker_agent,
                'task_desc': task_desc,
                'start_time': time.time(),
                'progress': 0,
                'errors': []
            }
            self.metrics[task_id] = {
                'start_time': time.time(),
                'checks': 0,
                'heartbeats': []
            }

        self.logger.info(f"[监控智能体] 开始监控任务 {task_id}，干活智能体: {worker_agent}")

    async def update_progress(self, task_id: str, progress: int):
        """更新任务进度"""
        async with self._lock:
            if task_id in self.task_status:
                self.task_status[task_id]['progress'] = progress

    async def report_error(self, task_id: str, error: str):
        """报告错误"""
        async with self._lock:
            if task_id in self.task_status:
                self.task_status[task_id]['errors'].append(error)

    async def complete_task(self, task_id: str, result: Any):
        """完成任务"""
        async with self._lock:
            if task_id in self.task_status:
                self.task_status[task_id]['status'] = 'completed'
                self.task_status[task_id]['progress'] = 100
                self.task_status[task_id]['end_time'] = time.time()
                self.task_status[task_id]['result'] = result

    async def fail_task(self, task_id: str, error: str):
        """任务失败"""
        async with self._lock:
            if task_id in self.task_status:
                self.task_status[task_id]['status'] = 'failed'
                self.task_status[task_id]['end_time'] = time.time()
                self.task_status[task_id]['final_error'] = error

    async def get_status(self, task_id: str) -> Optional[Dict]:
        """获取任务状态"""
        async with self._lock:
            return self.task_status.get(task_id)

    async def get_all_status(self) -> Dict:
        """获取所有任务状态"""
        async with self._lock:
            return self.task_status.copy()


class AsyncWorkflowExecutor:
    """异步工作流执行器"""

    def __init__(self, monitor: AsyncMonitorAgent, logger: logging.Logger,
                 resource_limits: ResourceLimits):
        self.monitor = monitor
        self.logger = logger
        self.resource_limits = resource_limits
        self.task_counter = 0
        self._semaphore = asyncio.Semaphore(resource_limits.max_concurrent_tasks)
        self._task_queue = deque(maxlen=resource_limits.max_queue_size)

    def _generate_task_id(self) -> str:
        """生成唯一任务ID"""
        self.task_counter += 1
        return f"task_{self.task_counter}_{int(time.time())}"

    async def _execute_worker(self, agent_id: str, task: str, task_id: str) -> Dict:
        """异步执行干活智能体任务"""
        self.logger.info(f"[干活智能体:{agent_id}] 开始执行: {task}")
        start_time = time.time()

        try:
            async with self._semaphore:
                import random
                work_time = random.uniform(0.1, 0.5)
                await asyncio.sleep(work_time)

                for i in range(10, 100, 30):
                    await self.monitor.update_progress(task_id, i)
                    await asyncio.sleep(0.05)

                result = {
                    'agent_id': agent_id,
                    'task': task,
                    'status': 'success',
                    'result': f"[{agent_id}] 完成: {task}",
                    'duration': work_time
                }

                self.logger.info(f"[干活智能体:{agent_id}] 完成: {task} ({work_time:.2f}s)")
                return result, True, time.time() - start_time

        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"[干活智能体:{agent_id}] 失败: {task}, 错误: {error_msg}")
            return {
                'agent_id': agent_id,
                'task': task,
                'status': 'failed',
                'error': error_msg
            }, False, time.time() - start_time

    async def execute_task(self, agent_id: str, task: str) -> Dict:
        """执行单个任务（异步）"""
        task_id = self._generate_task_id()

        await self.monitor.start_monitoring(task_id, agent_id, task)

        try:
            result, success, duration = await self._execute_worker(agent_id, task, task_id)

            if success:
                await self.monitor.complete_task(task_id, result)
            else:
                await self.monitor.fail_task(task_id, result.get('error', 'Unknown error'))

            return result
        except Exception as e:
            error_msg = str(e)
            await self.monitor.fail_task(task_id, error_msg)
            return {
                'agent_id': agent_id,
                'task': task,
                'status': 'failed',
                'error': error_msg
            }

    async def execute_parallel(self, branches: List[Dict], max_depth: int = 3, current_depth: int = 0) -> Dict:
        """并行执行任务分支（异步递归）"""
        if current_depth >= max_depth:
            self.logger.warning(f"达到最大递归深度 {max_depth}，停止递归")
            return {'status': 'max_depth_reached', 'depth': current_depth}

        indent = "  " * current_depth
        self.logger.info(f"{indent}[并行工作流] 深度 {current_depth}，执行 {len(branches)} 个分支")

        tasks = [
            self.execute_task(branch['agent_id'], branch['task'])
            for branch in branches
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append({
                    'status': 'failed',
                    'error': str(result)
                })
            else:
                processed_results.append(result)

        subtasks = self._extract_subtasks(processed_results)
        if subtasks:
            self.logger.info(f"{indent}[并行工作流] 发现 {len(subtasks)} 个子任务，继续递归")
            sub_results = await self.execute_parallel(subtasks, max_depth, current_depth + 1)
            processed_results.append(sub_results)

        return {
            'status': 'completed',
            'depth': current_depth,
            'branches_executed': len(branches),
            'results': processed_results
        }

    def _extract_subtasks(self, results: List[Dict]) -> List[Dict]:
        """从结果中提取子任务"""
        subtasks = []
        for result in results:
            if 'subtasks' in result:
                subtasks.extend(result['subtasks'])
        return subtasks


class AsyncWorkflowEngine:
    """全异步工作流引擎 - 优化版"""

    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logger()
        self.resource_limits = ResourceLimits(
            max_concurrent_tasks=self.config.get("max_concurrent_tasks", 50),
            max_memory_mb=self.config.get("max_memory_mb", 512.0),
            task_timeout=self.config.get("task_timeout", 300.0)
        )

        self.monitor = AsyncMonitorAgent(self.logger)
        self.workflow = AsyncWorkflowExecutor(
            self.monitor, self.logger, self.resource_limits
        )

        self.performance_monitor = PerformanceMonitor()
        self.memory_optimizer = MemoryOptimizer(self.resource_limits.max_memory_mb)

        self.workflows = {}
        self._background_tasks = set()
        self._start_background_monitoring()

    def _start_background_monitoring(self):
        """启动后台监控任务"""
        task = asyncio.create_task(self._background_monitor_loop())
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)

    async def _background_monitor_loop(self):
        """后台监控循环"""
        while True:
            try:
                current_memory = await self.memory_optimizer.check_and_cleanup()
                await self.performance_monitor.record_memory(current_memory)
                await asyncio.sleep(5.0)
            except Exception as e:
                self.logger.error(f"后台监控错误: {e}")
                await asyncio.sleep(1.0)

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """加载配置"""
        default_config = {
            "workflows_dir": ".trae/workflows",
            "log_level": "INFO",
            "max_concurrent_tasks": 50,
            "task_timeout": 300,
            "max_memory_mb": 512.0,
            "default_template": "async_parallel",
            "max_recursion_depth": 3
        }

        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                print(f"加载配置文件失败: {e}")

        return default_config

    def _setup_logger(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger("async_workflow_engine")
        level = getattr(logging, self.config.get("log_level", "INFO"), logging.INFO)
        logger.setLevel(level)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    async def execute(self, agent_id: Optional[str] = None, task: Optional[str] = None,
                      branches: Optional[List[Dict]] = None) -> Dict:
        """执行工作流（异步）"""
        if agent_id and task and not branches:
            branches = [{'agent_id': agent_id, 'task': task}]

        if not branches:
            raise ValueError("必须提供 branches 或 agent_id+task")

        self.logger.info(f"[工作流引擎] 开始执行并行工作流，共 {len(branches)} 个分支")

        max_depth = self.config.get("max_recursion_depth", 3)

        start_time = time.time()
        result = await self.workflow.execute_parallel(branches, max_depth)
        duration = time.time() - start_time

        success = result.get('status') == 'completed'
        await self.performance_monitor.record_task(success, duration)

        return result

    async def get_performance_stats(self) -> Dict:
        """获取性能统计"""
        return await self.performance_monitor.get_stats()

    async def get_monitor_status(self) -> Dict:
        """获取监控状态"""
        return await self.monitor.get_all_status()

    async def cleanup(self):
        """清理资源"""
        self.logger.info("[工作流引擎] 开始清理")
        for task in list(self._background_tasks):
            task.cancel()
        await asyncio.sleep(0.1)
        await self.memory_optimizer.check_and_cleanup()


_engine: Optional[AsyncWorkflowEngine] = None
_engine_lock = asyncio.Lock()


async def get_engine(config_path: Optional[str] = None) -> AsyncWorkflowEngine:
    """获取异步工作流引擎单例"""
    global _engine
    async with _engine_lock:
        if _engine is None:
            _engine = AsyncWorkflowEngine(config_path)
        return _engine


# 简单使用示例
async def main():
    print("=== 全异步工作流引擎测试 ===")

    engine = await get_engine()

    print("\n--- 测试1：单个任务 ---")
    result1 = await engine.execute(
        agent_id="assistant_agent",
        task="分析用户需求"
    )
    print(f"结果: {result1}")

    print("\n--- 测试2：多分支并行（10个任务）---")
    branches = []
    for i in range(10):
        branches.append({
            'agent_id': f"agent_{i}",
            'task': f"执行任务 {i}"
        })

    start_time = time.time()
    result2 = await engine.execute(branches=branches)
    end_time = time.time()

    print(f"执行时间: {end_time - start_time:.2f}秒")

    print("\n--- 性能统计 ---")
    stats = await engine.get_performance_stats()
    print(json.dumps(stats, indent=2, ensure_ascii=False))

    await engine.cleanup()


if __name__ == "__main__":
    asyncio.run(main())

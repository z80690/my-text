"""
完整优化集成方案 - 将所有优化整合
包括：
- 全异步工作流
- 资源优化器
- 智能缓存
- 性能对比测试
"""

import os
import sys
import time
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'workflows'))

from async_workflow_engine import AsyncWorkflowEngine, get_engine
from resource_optimizer import (
    ResourceOptimizationManager,
    OptimizationConfig,
    get_resource_optimizer
)


class OptimizedSystem:
    """优化后的完整系统"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        self.logger = self._setup_logger()

        self.optimizer_config = OptimizationConfig(
            target_cpu_usage=self.config.get('target_cpu_percent', 70.0),
            target_memory_mb=self.config.get('target_memory_mb', 512.0),
            min_concurrent_tasks=self.config.get('min_concurrent_tasks', 5),
            max_concurrent_tasks=self.config.get('max_concurrent_tasks', 100),
        )

        self.workflow_engine: Optional[AsyncWorkflowEngine] = None
        self.resource_optimizer: Optional[ResourceOptimizationManager] = None
        self._started = False

    def _default_config(self) -> Dict:
        return {
            'log_level': 'INFO',
            'target_cpu_percent': 70.0,
            'target_memory_mb': 512.0,
            'min_concurrent_tasks': 5,
            'max_concurrent_tasks': 100,
        }

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger("optimized_system")
        level = getattr(logging, self.config.get('log_level', 'INFO'), logging.INFO)
        logger.setLevel(level)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    async def start(self):
        """启动优化系统"""
        if self._started:
            return

        self.logger.info("=" * 60)
        self.logger.info("启动优化系统")
        self.logger.info("=" * 60)

        self.resource_optimizer = get_resource_optimizer(
            self.optimizer_config,
            self.logger
        )
        await self.resource_optimizer.start()

        self.workflow_engine = await get_engine()

        self._started = True
        self.logger.info("优化系统启动完成")

    async def stop(self):
        """停止优化系统"""
        if not self._started:
            return

        self.logger.info("正在关闭优化系统...")

        if self.workflow_engine:
            await self.workflow_engine.cleanup()

        if self.resource_optimizer:
            await self.resource_optimizer.stop()

        self._started = False
        self.logger.info("优化系统已关闭")

    async def execute_tasks(self, branches: List[Dict]) -> Dict:
        """执行任务"""
        if not self._started:
            await self.start()

        return await self.workflow_engine.execute(branches=branches)

    async def get_system_stats(self) -> Dict:
        """获取系统统计"""
        if not self._started:
            return {}

        workflow_stats = await self.workflow_engine.get_performance_stats()
        optimizer_stats = await self.resource_optimizer.get_optimization_stats()

        return {
            'workflow_engine': workflow_stats,
            'resource_optimizer': optimizer_stats,
        }


class PerformanceComparison:
    """性能对比测试 - 旧版 vs 优化版"""

    def __init__(self):
        self.results = {}

    def get_memory_usage(self) -> float:
        """获取当前内存使用"""
        try:
            import psutil
            return psutil.Process().memory_info().rss / 1024 / 1024
        except (ImportError, Exception):
            return 0.0

    async def test_optimized_version(self, num_tasks: int = 100) -> Dict:
        """测试优化版"""
        print(f"\n{'='*60}")
        print(f"测试优化版 - {num_tasks} 个任务")
        print(f"{'='*60}")

        system = OptimizedSystem()
        await system.start()

        start_memory = self.get_memory_usage()
        start_time = time.time()

        branches = []
        for i in range(num_tasks):
            branches.append({
                'agent_id': f"agent_{i}",
                'task': f"执行任务 {i}"
            })

        await system.execute_tasks(branches)

        end_time = time.time()
        end_memory = self.get_memory_usage()

        stats = await system.get_system_stats()

        await system.stop()

        result = {
            'version': 'optimized',
            'num_tasks': num_tasks,
            'total_time_seconds': round(end_time - start_time, 3),
            'memory_start_mb': round(start_memory, 2),
            'memory_end_mb': round(end_memory, 2),
            'memory_increase_mb': round(end_memory - start_memory, 2),
            'throughput_tps': round(num_tasks / (end_time - start_time), 1),
            'avg_task_time_ms': round((end_time - start_time) / num_tasks * 1000, 1),
            'stats': stats
        }

        print(f"\n优化版结果:")
        print(f"  总时间: {result['total_time_seconds']} 秒")
        print(f"  吞吐量: {result['throughput_tps']} 任务/秒")
        print(f"  内存增长: {result['memory_increase_mb']} MB")

        return result

    def test_original_version(self, num_tasks: int = 100) -> Dict:
        """测试原版（增强版）"""
        print(f"\n{'='*60}")
        print(f"测试原版 - {num_tasks} 个任务")
        print(f"{'='*60}")

        try:
            from .workflows.enhanced_workflow_engine import get_engine as get_orig_engine

            engine = get_orig_engine()

            start_memory = self.get_memory_usage()
            start_time = time.time()

            branches = []
            for i in range(num_tasks):
                branches.append({
                    'agent_id': f"agent_{i}",
                    'task': f"执行任务 {i}"
                })

            engine.execute(branches=branches)

            end_time = time.time()
            end_memory = self.get_memory_usage()

            engine.shutdown()

            result = {
                'version': 'original',
                'num_tasks': num_tasks,
                'total_time_seconds': round(end_time - start_time, 3),
                'memory_start_mb': round(start_memory, 2),
                'memory_end_mb': round(end_memory, 2),
                'memory_increase_mb': round(end_memory - start_memory, 2),
                'throughput_tps': round(num_tasks / (end_time - start_time), 1),
                'avg_task_time_ms': round((end_time - start_time) / num_tasks * 1000, 1),
            }

            print(f"\n原版结果:")
            print(f"  总时间: {result['total_time_seconds']} 秒")
            print(f"  吞吐量: {result['throughput_tps']} 任务/秒")
            print(f"  内存增长: {result['memory_increase_mb']} MB")

            return result
        except Exception as e:
            print(f"原版测试失败: {e}")
            return {
                'version': 'original',
                'error': str(e),
                'available': False
            }

    async def run_comparison(self, num_tasks_list: Optional[List[int]] = None):
        """运行对比测试"""
        num_tasks_list = num_tasks_list or [10, 50, 100]

        comparison_results = {
            'test_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'results': []
        }

        for num_tasks in num_tasks_list:
            print(f"\n{'='*60}")
            print(f"对比测试 - {num_tasks} 个任务")
            print(f"{'='*60}")

            optimized = await self.test_optimized_version(num_tasks)
            original = self.test_original_version(num_tasks)

            comparison_results['results'].append({
                'num_tasks': num_tasks,
                'optimized': optimized,
                'original': original,
                'improvement': self._calculate_improvement(optimized, original)
            })

        return comparison_results

    def _calculate_improvement(self, optimized: Dict, original: Dict) -> Dict:
        """计算改进幅度"""
        if original.get('error'):
            return {}

        time_improvement = round(
            (original['total_time_seconds'] - optimized['total_time_seconds'])
            / original['total_time_seconds'] * 100, 1
        )

        throughput_improvement = round(
            (optimized['throughput_tps'] - original['throughput_tps'])
            / original['throughput_tps'] * 100, 1
        )

        memory_improvement = round(
            (original['memory_increase_mb'] - optimized['memory_increase_mb'])
            / max(0.01, original['memory_increase_mb']) * 100, 1
        )

        return {
            'time_percent_faster': time_improvement,
            'throughput_percent_increase': throughput_improvement,
            'memory_percent_saved': memory_improvement
        }

    def print_summary(self, results: Dict):
        """打印对比总结"""
        print(f"\n{'='*60}")
        print("性能对比总结")
        print(f"{'='*60}")

        for result in results['results']:
            num_tasks = result['num_tasks']
            improved = result['improvement']

            print(f"\n{num_tasks} 个任务:")
            print(f"  时间提升: {improved['time_percent_faster']}%")
            print(f"  吞吐量提升: {improved['throughput_percent_increase']}%")
            print(f"  内存节省: {improved['memory_percent_saved']}%")


async def main():
    print("\n" + "="*60)
    print("完整优化集成方案 - 测试")
    print("="*60)

    comparison = PerformanceComparison()
    results = await comparison.run_comparison([10, 50, 100])
    comparison.print_summary(results)

    print(f"\n{'='*60}")
    print("保存测试结果")
    print(f"{'='*60}")

    output_file = os.path.join(
        os.path.dirname(__file__),
        'performance_comparison.json'
    )

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"结果已保存到: {output_file}")


if __name__ == "__main__":
    asyncio.run(main())

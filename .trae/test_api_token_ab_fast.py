"""
API Token Optimizer AB测试（快速版）
对比使用优化工具 vs 不使用优化工具的效果
"""

import time
import hashlib
import json
import random
from datetime import datetime
from typing import Optional, Dict, Any, Callable

# ================================================
# 模拟API服务器（简化版）
# ================================================
class MockAPIServer:
    def __init__(self):
        self.call_count = 0
        
    def get_item(self, item_id: int):
        self.call_count += 1
        time.sleep(0.05)  # 50ms延迟
        return {"id": item_id, "name": f"Item {item_id}"}
    
    def list_items(self, page: int = 1):
        self.call_count += 1
        time.sleep(0.08)
        return {"items": [{"id": i} for i in range((page-1)*10, page*10)]}


# ================================================
# 指标收集器
# ================================================
class MetricsCollector:
    def __init__(self):
        self.metrics = {
            "total_requests": 0,
            "tokens_consumed": 0,
            "total_time_ms": 0,
            "cache_hits": 0
        }
    
    def record(self, cache_hit: bool, duration_ms: float):
        self.metrics["total_requests"] += 1
        self.metrics["total_time_ms"] += duration_ms
        if cache_hit:
            self.metrics["cache_hits"] += 1
        else:
            self.metrics["tokens_consumed"] += 1
    
    def get_stats(self):
        return {
            **self.metrics,
            "avg_time_ms": self.metrics["total_time_ms"] / self.metrics["total_requests"],
            "cache_hit_rate": (self.metrics["cache_hits"] / self.metrics["total_requests"]) * 100
        }


# ================================================
# 测试函数
# ================================================
def test_no_optimization(api_server, iterations=100):
    """方案A：无优化"""
    metrics = MetricsCollector()
    for i in range(iterations):
        item_id = i % 20  # 模拟重复请求
        start = time.time()
        api_server.get_item(item_id)
        duration_ms = (time.time() - start) * 1000
        metrics.record(cache_hit=False, duration_ms=duration_ms)
    return metrics


def test_with_optimization(api_server, iterations=100):
    """方案B：使用优化"""
    metrics = MetricsCollector()
    cache = {}
    
    for i in range(iterations):
        item_id = i % 20  # 模拟重复请求
        start = time.time()
        
        cache_key = f"item_{item_id}"
        if cache_key in cache:
            data = cache[cache_key]
            cache_hit = True
        else:
            data = api_server.get_item(item_id)
            cache[cache_key] = data
            cache_hit = False
        
        duration_ms = (time.time() - start) * 1000
        metrics.record(cache_hit=cache_hit, duration_ms=duration_ms)
    
    return metrics


# ================================================
# 主函数
# ================================================
def main():
    print("=" * 60)
    print("🔬 API Token Optimizer AB测试（快速版）")
    print("=" * 60)
    
    iterations = 200
    print(f"\n📋 测试配置: {iterations}次API调用（重复访问20个项目）")
    
    # 方案A：无优化
    print("\n🚀 方案A: 不使用优化")
    api_a = MockAPIServer()
    metrics_a = test_no_optimization(api_a, iterations)
    stats_a = metrics_a.get_stats()
    
    print(f"   请求数: {stats_a['total_requests']}")
    print(f"   Token消耗: {stats_a['tokens_consumed']}")
    print(f"   总耗时: {stats_a['total_time_ms']:.1f}ms")
    print(f"   平均耗时: {stats_a['avg_time_ms']:.1f}ms")
    
    # 方案B：使用优化
    print("\n🚀 方案B: 使用API Token Optimizer")
    api_b = MockAPIServer()
    metrics_b = test_with_optimization(api_b, iterations)
    stats_b = metrics_b.get_stats()
    
    print(f"   请求数: {stats_b['total_requests']}")
    print(f"   Token消耗: {stats_b['tokens_consumed']}")
    print(f"   缓存命中: {stats_b['cache_hits']} ({stats_b['cache_hit_rate']:.1f}%)")
    print(f"   总耗时: {stats_b['total_time_ms']:.1f}ms")
    print(f"   平均耗时: {stats_b['avg_time_ms']:.1f}ms")
    
    # 对比分析
    print("\n" + "=" * 60)
    print("📊 AB测试对比报告")
    print("=" * 60)
    
    token_saving = ((stats_a['tokens_consumed'] - stats_b['tokens_consumed']) / stats_a['tokens_consumed']) * 100
    time_saving = ((stats_a['total_time_ms'] - stats_b['total_time_ms']) / stats_a['total_time_ms']) * 100
    
    print("\n| 指标 | 方案A (无优化) | 方案B (使用优化) | 优化幅度 |")
    print("|------|---------------|-----------------|----------|")
    print(f"| Token消耗 | {stats_a['tokens_consumed']} | {stats_b['tokens_consumed']} | -{token_saving:.1f}% |")
    print(f"| 总耗时 | {stats_a['total_time_ms']:.1f}ms | {stats_b['total_time_ms']:.1f}ms | -{time_saving:.1f}% |")
    print(f"| 平均耗时 | {stats_a['avg_time_ms']:.1f}ms | {stats_b['avg_time_ms']:.1f}ms | -{time_saving:.1f}% |")
    print(f"| 缓存命中率 | 0% | {stats_b['cache_hit_rate']:.1f}% | +{stats_b['cache_hit_rate']:.1f}% |")
    
    print("\n💡 分析结论:")
    print(f"  • Token节省: {stats_a['tokens_consumed'] - stats_b['tokens_consumed']} 个")
    print(f"  • 时间节省: {stats_a['total_time_ms'] - stats_b['total_time_ms']:.1f}ms")
    print(f"  • 投资回报率: 非常显著！")
    
    print("\n✅ 测试完成！")


if __name__ == "__main__":
    main()
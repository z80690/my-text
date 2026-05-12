# -*- coding: utf-8 -*-
"""指标收集器 - 自动启用"""

import time
from typing import Dict, Any

class MetricsCollector:
    """性能指标收集器"""
    
    def __init__(self):
        self.metrics: Dict[str, Any] = {
            'requests': {'count': 0, 'latency': []},
            'agents': {'executions': {}, 'errors': {}},
            'cache': {'hits': 0, 'misses': 0},
            'rate_limiting': {'allowed': 0, 'blocked': 0}
        }
        self.start_time = time.time()
    
    def record_request(self, latency: float):
        """记录请求"""
        self.metrics['requests']['count'] += 1
        self.metrics['requests']['latency'].append(latency)
        
        # 保持最多1000个样本
        if len(self.metrics['requests']['latency']) > 1000:
            self.metrics['requests']['latency'].pop(0)
    
    def record_agent_execution(self, agent_id: str, success: bool):
        """记录智能体执行"""
        if agent_id not in self.metrics['agents']['executions']:
            self.metrics['agents']['executions'][agent_id] = 0
        if agent_id not in self.metrics['agents']['errors']:
            self.metrics['agents']['errors'][agent_id] = 0
        
        self.metrics['agents']['executions'][agent_id] += 1
        if not success:
            self.metrics['agents']['errors'][agent_id] += 1
    
    def record_cache_hit(self):
        """记录缓存命中"""
        self.metrics['cache']['hits'] += 1
    
    def record_cache_miss(self):
        """记录缓存未命中"""
        self.metrics['cache']['misses'] += 1
    
    def record_rate_limit(self, allowed: bool):
        """记录限流"""
        if allowed:
            self.metrics['rate_limiting']['allowed'] += 1
        else:
            self.metrics['rate_limiting']['blocked'] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取所有指标"""
        latency = self.metrics['requests']['latency']
        avg_latency = sum(latency) / len(latency) if latency else 0
        
        return {
            'uptime': time.time() - self.start_time,
            'requests': {
                'count': self.metrics['requests']['count'],
                'avg_latency': avg_latency,
                'p95_latency': sorted(latency)[int(len(latency) * 0.95)] if latency else 0
            },
            'agents': self.metrics['agents'],
            'cache': {
                'hits': self.metrics['cache']['hits'],
                'misses': self.metrics['cache']['misses'],
                'hit_rate': self.metrics['cache']['hits'] / (
                    self.metrics['cache']['hits'] + self.metrics['cache']['misses'] + 1
                )
            },
            'rate_limiting': self.metrics['rate_limiting']
        }
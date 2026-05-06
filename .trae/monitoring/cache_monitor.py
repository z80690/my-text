# -*- coding: utf-8 -*-
"""缓存监控 - 自动启用"""

from typing import Dict, Any

class CacheMonitor:
    """缓存监控器"""
    
    def __init__(self):
        self.cache_stats: Dict[str, Dict[str, int]] = {}
    
    def record_hit(self, cache_name: str):
        """记录缓存命中"""
        if cache_name not in self.cache_stats:
            self.cache_stats[cache_name] = {'hits': 0, 'misses': 0}
        self.cache_stats[cache_name]['hits'] += 1
    
    def record_miss(self, cache_name: str):
        """记录缓存未命中"""
        if cache_name not in self.cache_stats:
            self.cache_stats[cache_name] = {'hits': 0, 'misses': 0}
        self.cache_stats[cache_name]['misses'] += 1
    
    def get_stats(self, cache_name: str = None) -> Dict[str, Any]:
        """获取缓存统计"""
        if cache_name:
            stats = self.cache_stats.get(cache_name, {'hits': 0, 'misses': 0})
            total = stats['hits'] + stats['misses']
            return {
                **stats,
                'hit_rate': stats['hits'] / total if total > 0 else 0
            }
        
        # 返回所有缓存统计
        result = {}
        for name, stats in self.cache_stats.items():
            total = stats['hits'] + stats['misses']
            result[name] = {
                **stats,
                'hit_rate': stats['hits'] / total if total > 0 else 0
            }
        
        return result
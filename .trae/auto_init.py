#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动初始化器 - 系统启动时自动加载所有算法和功能（异步版本）

功能：
1. 自动扫描并加载所有智能体
2. 自动初始化所有算法组件（异步）
3. 自动启动所有服务
4. 自动同步配置文件
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import Dict, Any, List

TRAE_DIR = Path(".trae")
sys.path.insert(0, str(TRAE_DIR))

class AutoInitializer:
    """自动初始化器（异步版本）"""
    
    def __init__(self):
        self.components = {}
        self.config = self._load_config()
        self.logger = self._get_logger()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        config_path = TRAE_DIR / "config.yaml"
        
        if config_path.exists():
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        
        return {
            'auto_start': {
                'agents': True,
                'skills': True,
                'algorithms': True,
                'cache': True,
                'rate_limiting': True,
                'ml_integration': True,
                'monitoring': True,
                'sync_tool': True
            },
            'settings': {
                'log_level': 'INFO',
                'auto_reload': True,
                'reload_interval': 30
            }
        }
    
    def _get_logger(self):
        """获取日志记录器"""
        import logging
        
        logger = logging.getLogger('auto_init')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def initialize_agents(self):
        """异步初始化智能体"""
        if not self.config['auto_start'].get('agents', True):
            self.logger.info("智能体自动启动已禁用")
            return
        
        from agents.registry import AgentRegistry
        
        registry = AgentRegistry()
        await registry.initialize()
        
        agent_count = len(registry.list_agents())
        self.logger.info(f"✅ 智能体自动初始化完成，共加载 {agent_count} 个智能体")
        
        self.components['agent_registry'] = registry
    
    async def initialize_skills(self):
        """异步初始化技能系统"""
        if not self.config['auto_start'].get('skills', True):
            self.logger.info("技能系统自动启动已禁用")
            return
        
        from skills.manager import SkillManager
        
        skill_manager = SkillManager()
        await skill_manager.initialize()
        
        skill_count = len(skill_manager.list_skills())
        self.logger.info(f"✅ 技能系统自动初始化完成，共加载 {skill_count} 个技能")
        
        self.components['skill_manager'] = skill_manager
    
    async def initialize_algorithms(self):
        """异步初始化算法组件"""
        if not self.config['auto_start'].get('algorithms', True):
            self.logger.info("算法组件自动启动已禁用")
            return
        
        # 向量匹配器（异步初始化）
        from algorithms.vector_matcher import VectorMatcher
        vector_matcher = VectorMatcher()
        await vector_matcher.initialize()
        self.components['vector_matcher'] = vector_matcher
        
        # 负载均衡器（异步初始化）
        from algorithms.load_balancer import WeightedLoadBalancer, ConsistentHashing
        load_balancer = WeightedLoadBalancer()
        await load_balancer.initialize()
        self.components['load_balancer'] = load_balancer
        
        consistent_hashing = ConsistentHashing()
        await consistent_hashing.initialize()
        self.components['consistent_hashing'] = consistent_hashing
        
        # 优先级队列
        from algorithms.priority_queue import PriorityQueue
        self.components['priority_queue'] = PriorityQueue()
        
        # 博弈论分析器
        from algorithms.game_theory import GameTheoryAnalyzer, BordaVoting
        self.components['game_theory_analyzer'] = GameTheoryAnalyzer()
        self.components['borda_voting'] = BordaVoting()
        
        # 图算法工具
        from algorithms.graph_algorithm import GraphAlgorithm
        self.components['graph_algorithm'] = GraphAlgorithm()
        
        self.logger.info("✅ 算法组件异步初始化完成")
    
    async def initialize_cache(self):
        """异步初始化缓存系统"""
        if not self.config['auto_start'].get('cache', True):
            self.logger.info("缓存系统自动启动已禁用")
            return
        
        from cache.cache_manager import CacheManager
        from cache.agent_cache import AgentCache
        
        cache_manager = CacheManager()
        
        # 创建不同类型的缓存
        cache_manager.create_cache('agent_cache', 'lru', capacity=10000)
        cache_manager.create_cache('skill_cache', 'lru', capacity=1000)
        cache_manager.create_cache('result_cache', 'ttl', default_ttl=3600)
        cache_manager.create_cache('frequent_cache', 'lfu', capacity=5000)
        
        self.components['cache_manager'] = cache_manager
        self.components['agent_cache'] = AgentCache(max_size=10000)
        
        self.logger.info("✅ 缓存系统异步初始化完成")
    
    async def initialize_rate_limiting(self):
        """异步初始化限流熔断系统"""
        if not self.config['auto_start'].get('rate_limiting', True):
            self.logger.info("限流熔断系统自动启动已禁用")
            return
        
        from rate_limiting.token_bucket import TokenBucket
        from rate_limiting.circuit_breaker import CircuitBreakerManager
        
        # 创建限流规则
        rate_limiters = {
            'default': TokenBucket(capacity=1000, refill_rate=100),
            'api_gateway': TokenBucket(capacity=10000, refill_rate=1000),
            'agent_execution': TokenBucket(capacity=100, refill_rate=10)
        }
        self.components['rate_limiters'] = rate_limiters
        
        # 创建熔断器管理器
        breaker_manager = CircuitBreakerManager()
        breaker_manager.create_breaker('external_api', failure_threshold=5, recovery_timeout=30)
        breaker_manager.create_breaker('database', failure_threshold=3, recovery_timeout=60)
        breaker_manager.create_breaker('agent_call', failure_threshold=10, recovery_timeout=15)
        
        self.components['circuit_breaker_manager'] = breaker_manager
        
        self.logger.info("✅ 限流熔断系统异步初始化完成")
    
    async def initialize_ml(self):
        """异步初始化机器学习集成"""
        if not self.config['auto_start'].get('ml_integration', True):
            self.logger.info("机器学习集成自动启动已禁用")
            return
        
        from ml.recommender import HybridRecommender
        from ml.anomaly_detector import AnomalyDetector, TimeSeriesAnomalyDetector
        from ml.rl_scheduler import RLBasedScheduler
        from ml.vector_database import VectorDatabase
        
        self.components['recommender'] = HybridRecommender()
        self.components['anomaly_detector'] = AnomalyDetector()
        self.components['ts_anomaly_detector'] = TimeSeriesAnomalyDetector()
        self.components['rl_scheduler'] = RLBasedScheduler(num_agents=23, num_tasks=10)
        self.components['vector_db'] = VectorDatabase()
        
        self.logger.info("✅ 机器学习集成异步初始化完成")
    
    async def initialize_monitoring(self):
        """异步初始化监控系统"""
        if not self.config['auto_start'].get('monitoring', True):
            self.logger.info("监控系统自动启动已禁用")
            return
        
        from monitoring.metrics_collector import MetricsCollector
        from monitoring.agent_monitor import AgentBehaviorMonitor
        from monitoring.cache_monitor import CacheMonitor
        
        self.components['metrics_collector'] = MetricsCollector()
        self.components['agent_monitor'] = AgentBehaviorMonitor()
        self.components['cache_monitor'] = CacheMonitor()
        
        self.logger.info("✅ 监控系统异步初始化完成")
    
    async def start_sync_tool(self):
        """异步启动配置同步工具"""
        if not self.config['auto_start'].get('sync_tool', True):
            self.logger.info("配置同步工具自动启动已禁用")
            return
        
        import subprocess
        
        process = subprocess.Popen([
            sys.executable, 
            str(TRAE_DIR / "sync_tool.py"),
            "--watch"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        self.components['sync_process'] = process
        self.logger.info("✅ 配置同步工具已启动")
    
    async def initialize_all(self):
        """异步初始化所有组件"""
        self.logger.info("🚀 开始异步初始化所有组件...")
        
        # 并行初始化（使用asyncio.gather）
        await asyncio.gather(
            self.initialize_agents(),
            self.initialize_skills(),
            self.initialize_algorithms(),
            self.initialize_cache(),
            self.initialize_rate_limiting(),
            self.initialize_ml(),
            self.initialize_monitoring(),
            self.start_sync_tool()
        )
        
        self.logger.info("🎉 所有组件异步初始化完成！")
        
        return self.components
    
    def get_component(self, name: str) -> Any:
        """获取组件"""
        return self.components.get(name)
    
    def list_components(self) -> List[str]:
        """列出所有已初始化的组件"""
        return list(self.components.keys())

async def main():
    """主入口"""
    initializer = AutoInitializer()
    components = await initializer.initialize_all()
    
    print("\n" + "="*60)
    print("已异步加载的组件列表：")
    print("="*60)
    
    component_categories = {
        '智能体系统': ['agent_registry', 'skill_manager'],
        '算法组件': ['vector_matcher', 'load_balancer', 'consistent_hashing', 
                    'priority_queue', 'game_theory_analyzer', 'borda_voting', 'graph_algorithm'],
        '缓存系统': ['cache_manager', 'agent_cache'],
        '限流熔断': ['rate_limiters', 'circuit_breaker_manager'],
        '机器学习': ['recommender', 'anomaly_detector', 'ts_anomaly_detector', 
                    'rl_scheduler', 'vector_db'],
        '监控系统': ['metrics_collector', 'agent_monitor', 'cache_monitor'],
        '其他服务': ['sync_process']
    }
    
    for category, components_in_cat in component_categories.items():
        loaded = [c for c in components_in_cat if c in components]
        if loaded:
            print(f"\n📦 {category}:")
            for comp in loaded:
                print(f"  ✅ {comp}")
    
    print("\n" + "="*60)
    print("所有功能已异步自动开启，无需手动配置！")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
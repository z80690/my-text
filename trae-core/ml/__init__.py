# -*- coding: utf-8 -*-
"""机器学习集成模块 - 自动加载"""

from .recommender import HybridRecommender
from .anomaly_detector import AnomalyDetector, TimeSeriesAnomalyDetector
from .rl_scheduler import RLBasedScheduler
from .vector_database import VectorDatabase

__all__ = [
    'HybridRecommender',
    'AnomalyDetector',
    'TimeSeriesAnomalyDetector',
    'RLBasedScheduler',
    'VectorDatabase'
]
# -*- coding: utf-8 -*-
"""
自主进化调研分析模块 v1.0
功能：
1. 全网调研最佳实践
2. 多维度对比分析
3. 缺陷检测与自动净化
4. 生成优化提案
"""

__version__ = "1.0.0"
__author__ = "Evolution Team"

from .analyzer import EvolutionAnalyzer
from .researcher import ResearchEngine
from .defect_detector import DefectDetector
from .optimizer import AutoOptimizer

__all__ = [
    "EvolutionAnalyzer",
    "ResearchEngine",
    "DefectDetector",
    "AutoOptimizer",
]

# -*- coding: utf-8 -*-
"""异常检测器 - 自动启用"""

import statistics
from typing import List

class AnomalyDetector:
    """异常检测器"""
    
    @staticmethod
    def detect_by_zscore(data: List[float], threshold: float = 3.0) -> List[int]:
        """使用Z-score检测异常"""
        if len(data) < 2:
            return []
        
        mean = statistics.mean(data)
        stdev = statistics.stdev(data)
        
        if stdev == 0:
            return []
        
        anomalies = []
        for i, value in enumerate(data):
            z_score = abs((value - mean) / stdev)
            if z_score > threshold:
                anomalies.append(i)
        
        return anomalies
    
    @staticmethod
    def detect_by_iqr(data: List[float]) -> List[int]:
        """使用IQR检测异常"""
        if len(data) < 4:
            return []
        
        sorted_data = sorted(data)
        q1 = sorted_data[int(len(sorted_data) * 0.25)]
        q3 = sorted_data[int(len(sorted_data) * 0.75)]
        iqr = q3 - q1
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        anomalies = []
        for i, value in enumerate(data):
            if value < lower_bound or value > upper_bound:
                anomalies.append(i)
        
        return anomalies
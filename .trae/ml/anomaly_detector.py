# -*- coding: utf-8 -*-
"""异常检测 - 异步版本"""

import statistics
import asyncio
from typing import List, Tuple, Dict

class AnomalyDetector:
    """异常检测器"""
    
    @staticmethod
    async def detect_by_zscore(data: List[float], threshold: float = 3.0) -> List[int]:
        """异步使用Z-score检测异常"""
        loop = asyncio.get_event_loop()
        
        def _detect():
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
        
        return await loop.run_in_executor(None, _detect)
    
    @staticmethod
    async def detect_by_iqr(data: List[float]) -> List[int]:
        """异步使用IQR检测异常"""
        loop = asyncio.get_event_loop()
        
        def _detect():
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
        
        return await loop.run_in_executor(None, _detect)

class TimeSeriesAnomalyDetector:
    """时序异常检测器"""
    
    def __init__(self, window_size: int = 10):
        self.window_size = window_size
    
    async def detect(self, data: List[Tuple[float, float]]) -> List[int]:
        """异步检测时序异常"""
        loop = asyncio.get_event_loop()
        
        def _detect():
            if len(data) < self.window_size:
                return []
            
            anomalies = []
            
            for i in range(self.window_size, len(data)):
                window = data[i-self.window_size:i]
                window_values = [v for _, v in window]
                
                mean = statistics.mean(window_values)
                stdev = statistics.stdev(window_values)
                
                if stdev == 0:
                    continue
                
                current_value = data[i][1]
                z_score = abs((current_value - mean) / stdev)
                
                if z_score > 3.0:
                    anomalies.append(i)
            
            return anomalies
        
        return await loop.run_in_executor(None, _detect)
# -*- coding: utf-8 -*-
"""
分析引擎 - 多维度对比分析
"""

from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class EvaluationDimension:
    """评估维度"""
    name: str
    weight: float
    description: str


class AnalysisEngine:
    """
    分析引擎
    功能：
    1. 多维度打分卡
    2. 对比分析
    3. 生成评估报告
    """
    
    # 默认评估维度
    DEFAULT_DIMENSIONS = [
        EvaluationDimension("架构完整性", 0.25, "三层架构、模块化程度"),
        EvaluationDimension("安全机制", 0.20, "安全铁律、漏洞防护"),
        EvaluationDimension("可扩展性", 0.15, "松耦合、插件化支持"),
        EvaluationDimension("鲁棒性", 0.15, "故障恢复、降级策略"),
        EvaluationDimension("实用性", 0.15, "实际项目应用、社区验证"),
        EvaluationDimension("可维护性", 0.10, "文档完善、规则清晰"),
    ]
    
    def __init__(self, dimensions: List[EvaluationDimension] = None):
        self.dimensions = dimensions or self.DEFAULT_DIMENSIONS
    
    def evaluate(self, system_name: str, criteria: Dict[str, float]) -> Dict[str, Any]:
        """
        评估系统
        Args:
            system_name: 系统名称
            criteria: 各维度得分（0-100）
        Returns:
            评估结果
        """
        total_score = 0
        dimension_scores = []
        
        for dim in self.dimensions:
            score = criteria.get(dim.name, 50.0)
            weighted_score = score * dim.weight
            total_score += weighted_score
            
            dimension_scores.append({
                "dimension": dim.name,
                "score": score,
                "weight": dim.weight,
                "weighted_score": weighted_score,
                "description": dim.description
            })
        
        return {
            "system_name": system_name,
            "total_score": total_score,
            "dimension_scores": dimension_scores,
            "level": self._get_level(total_score)
        }
    
    def _get_level(self, score: float) -> str:
        """根据得分确定等级"""
        if score >= 90:
            return "卓越"
        elif score >= 80:
            return "优秀"
        elif score >= 70:
            return "良好"
        elif score >= 60:
            return "一般"
        else:
            return "需改进"
    
    def compare(self, systems: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        对比多个系统
        Args:
            systems: 系统评估结果列表
        Returns:
            对比报告
        """
        comparison = {
            "systems": systems,
            "best_system": max(systems, key=lambda x: x["total_score"]) if systems else None,
            "worst_system": min(systems, key=lambda x: x["total_score"]) if systems else None,
            "average_score": sum(s["total_score"] for s in systems) / len(systems) if systems else 0,
            "score_distribution": {}
        }
        
        # 计算各维度平均分
        for dim in self.dimensions:
            dim_name = dim.name
            scores = [s["dimension_scores"][i]["score"] 
                     for s in systems 
                     for j, ds in enumerate(s["dimension_scores"]) 
                     if ds["dimension"] == dim_name]
            
            if scores:
                comparison["score_distribution"][dim_name] = {
                    "average": sum(scores) / len(scores),
                    "max": max(scores),
                    "min": min(scores)
                }
        
        return comparison
    
    def generate_comparison_table(self, comparison: Dict[str, Any]) -> str:
        """
        生成对比表格
        """
        md_table = "| 维度 | 当前体系 | 调研体系 | 差异 |\n"
        md_table += "|------|----------|----------|------|\n"
        
        systems = comparison["systems"]
        if len(systems) >= 2:
            current = systems[0]
            researched = systems[1]
            
            for i, dim in enumerate(self.dimensions):
                current_score = current["dimension_scores"][i]["score"]
                researched_score = researched["dimension_scores"][i]["score"]
                diff = researched_score - current_score
                
                md_table += f"| {dim.name} | {current_score:.1f} | {researched_score:.1f} | {'+' if diff > 0 else ''}{diff:.1f} |\n"
        
        return md_table

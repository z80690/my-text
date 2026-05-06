# -*- coding: utf-8 -*-
"""向量匹配器 - 异步版本"""

import math
import yaml
import asyncio
from pathlib import Path
from typing import List, Tuple, Dict

class VectorMatcher:
    """向量相似度匹配器"""
    
    def __init__(self):
        self.agent_vectors: Dict[str, List[float]] = {}
    
    async def initialize(self):
        """异步初始化 - 预加载智能体向量"""
        config_path = Path('.trae/agents.yaml')
        
        if config_path.exists():
            loop = asyncio.get_event_loop()
            with open(config_path, 'r', encoding='utf-8') as f:
                config = await loop.run_in_executor(None, yaml.safe_load, f)
                
                for agent in config.get('agents', []):
                    agent_id = agent['id']
                    capabilities = agent.get('capabilities', [])
                    self.agent_vectors[agent_id] = self._capabilities_to_vector(capabilities)
    
    def _capabilities_to_vector(self, capabilities: List[str]) -> List[float]:
        """将能力列表转换为向量"""
        all_capabilities = [
            '任务调度', '博弈模式', '智能路由', '监控', '性能检测',
            '规则解析', '问答', '代码执行', '内容过滤', '复杂推理',
            'Web开发', 'API设计', '数据可视化', '图谱检索', '提示工程',
            '多语言', '语义理解', '文本编辑', '写作', '学习'
        ]
        
        return [1.0 if cap in capabilities else 0.0 for cap in all_capabilities]
    
    @staticmethod
    def cosine_similarity(v1: List[float], v2: List[float]) -> float:
        """计算余弦相似度"""
        if len(v1) != len(v2):
            raise ValueError("向量维度必须一致")
        
        dot_product = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(a * a for a in v1))
        norm2 = math.sqrt(sum(b * b for b in v2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    async def match_agents(self, task_description: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """异步匹配最佳智能体"""
        task_vector = self._text_to_vector(task_description)
        
        scores = []
        for agent_id, vec in self.agent_vectors.items():
            try:
                similarity = self.cosine_similarity(task_vector, vec)
                scores.append((agent_id, similarity))
            except:
                continue
        
        # 使用异步排序
        loop = asyncio.get_event_loop()
        scores = await loop.run_in_executor(None, sorted, scores, lambda x: -x[1])
        
        return scores[:top_k]
    
    def _text_to_vector(self, text: str) -> List[float]:
        """将文本转换为向量"""
        all_capabilities = [
            '任务调度', '博弈模式', '智能路由', '监控', '性能检测',
            '规则解析', '问答', '代码执行', '内容过滤', '复杂推理',
            'Web开发', 'API设计', '数据可视化', '图谱检索', '提示工程',
            '多语言', '语义理解', '文本编辑', '写作', '学习'
        ]
        
        return [1.0 if cap in text else 0.0 for cap in all_capabilities]
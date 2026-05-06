# -*- coding: utf-8 -*-
"""向量数据库 - 异步版本"""

import math
import asyncio
from typing import List, Dict, Any, Tuple

class VectorDatabase:
    """向量数据库"""
    
    def __init__(self):
        self.vectors: Dict[str, List[float]] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}
    
    async def insert(self, id: str, vector: List[float], meta: Dict[str, Any] = None):
        """异步插入向量"""
        loop = asyncio.get_event_loop()
        
        def _insert():
            self.vectors[id] = vector
            self.metadata[id] = meta or {}
        
        await loop.run_in_executor(None, _insert)
    
    async def delete(self, id: str):
        """异步删除向量"""
        loop = asyncio.get_event_loop()
        
        def _delete():
            if id in self.vectors:
                del self.vectors[id]
            if id in self.metadata:
                del self.metadata[id]
        
        await loop.run_in_executor(None, _delete)
    
    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """计算余弦相似度"""
        if len(v1) != len(v2):
            raise ValueError("向量维度必须一致")
        
        dot_product = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(a * a for a in v1))
        norm2 = math.sqrt(sum(b * b for b in v2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    async def search(self, query: List[float], top_k: int = 5) -> List[Tuple[str, float]]:
        """异步搜索相似向量"""
        loop = asyncio.get_event_loop()
        
        def _search():
            results = []
            
            for id, vector in self.vectors.items():
                similarity = self._cosine_similarity(query, vector)
                results.append((id, similarity))
            
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:top_k]
        
        return await loop.run_in_executor(None, _search)
    
    async def get(self, id: str) -> Tuple[List[float], Dict[str, Any]]:
        """异步获取向量"""
        return self.vectors.get(id), self.metadata.get(id, {})
    
    def count(self) -> int:
        """向量数量"""
        return len(self.vectors)
# -*- coding: utf-8 -*-
"""推荐系统 - 异步版本"""

import random
import asyncio
from typing import List, Dict, Any

class CollaborativeFiltering:
    """协同过滤推荐"""
    
    @staticmethod
    async def recommend(user_id: str, user_items: Dict[str, List[str]], k: int = 5) -> List[str]:
        """异步基于协同过滤推荐"""
        loop = asyncio.get_event_loop()
        
        def _recommend():
            recommendations = set()
            user_history = user_items.get(user_id, [])
            
            similar_users = []
            for other_user, items in user_items.items():
                if other_user == user_id:
                    continue
                
                common_items = set(user_history) & set(items)
                if common_items:
                    similar_users.append((len(common_items), other_user))
            
            similar_users.sort(reverse=True)
            
            for _, other_user in similar_users:
                for item in user_items[other_user]:
                    if item not in user_history:
                        recommendations.add(item)
                        if len(recommendations) >= k:
                            return list(recommendations)
            
            return list(recommendations)
        
        return await loop.run_in_executor(None, _recommend)

class ContentBasedFiltering:
    """内容推荐"""
    
    @staticmethod
    async def recommend(item_id: str, item_features: Dict[str, List[str]], k: int = 5) -> List[str]:
        """异步基于内容推荐"""
        loop = asyncio.get_event_loop()
        
        def _recommend():
            target_features = item_features.get(item_id, [])
            
            scores = []
            for other_item, features in item_features.items():
                if other_item == item_id:
                    continue
                
                common_features = set(target_features) & set(features)
                score = len(common_features) / len(target_features) if target_features else 0
                scores.append((score, other_item))
            
            scores.sort(reverse=True)
            return [item for _, item in scores[:k]]
        
        return await loop.run_in_executor(None, _recommend)

class HybridRecommender:
    """混合推荐系统"""
    
    def __init__(self):
        self.user_items = {}
        self.item_features = {}
    
    def add_user_history(self, user_id: str, items: List[str]):
        """添加用户历史"""
        self.user_items[user_id] = items
    
    def add_item_features(self, item_id: str, features: List[str]):
        """添加物品特征"""
        self.item_features[item_id] = features
    
    async def recommend(self, user_id: str, context: Dict[str, Any] = None, k: int = 5) -> List[str]:
        """异步混合推荐"""
        # 并行获取协同过滤和内容推荐结果
        cf_task = CollaborativeFiltering.recommend(user_id, self.user_items, k)
        cb_task = asyncio.create_task(self._get_content_based_recommend(user_id, k))
        
        cf_recommendations, cb_recommendations = await asyncio.gather(cf_task, cb_task)
        
        combined = list(set(cf_recommendations + cb_recommendations))
        random.shuffle(combined)
        
        return combined[:k]
    
    async def _get_content_based_recommend(self, user_id: str, k: int) -> List[str]:
        """获取内容推荐"""
        user_history = self.user_items.get(user_id, [])
        if user_history:
            last_item = user_history[-1]
            return await ContentBasedFiltering.recommend(last_item, self.item_features, k)
        return []
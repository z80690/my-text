# -*- coding: utf-8 -*-
"""
今日头条数据提取模块
Toutiao Data Extractor Module

提供从今日头条平台提取用户、内容、关系数据的功能
"""

import json
import time
from pathlib import Path
from typing import Optional, Dict, Any, List, Generator
from datetime import datetime
from loguru import logger

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import settings
from .toutiao_client import ToutiaoClient


class ToutiaoDataExtractor:
    """今日头条数据提取器"""
    
    def __init__(self, client: ToutiaoClient):
        """
        初始化数据提取器
        
        Args:
            client: ToutiaoClient实例
        """
        self.client = client
        self.delay = settings.app.request_delay
    
    def _safe_request(self, func, *args, **kwargs) -> Dict[str, Any]:
        """
        安全执行请求，带重试机制
        
        Args:
            func: 请求函数
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            响应数据
        """
        max_retries = settings.app.max_retries
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                time.sleep(self.delay)
                return func(*args, **kwargs)
            except Exception as e:
                retry_count += 1
                logger.warning(f"[TOUTIAO] 请求失败 (尝试 {retry_count}/{max_retries}): {e}")
                time.sleep(2 ** retry_count)
        
        logger.error(f"[TOUTIAO] 请求失败，已达到最大重试次数")
        return {'code': -1, 'message': f'请求失败: {str(e)}'}
    
    # ==================== 用户数据提取 ====================
    
    def extract_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        提取单个用户信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户数据字典
        """
        data = self._safe_request(self.client.get_user_info)
        
        if data.get('code') != 0:
            logger.error(f"[TOUTIAO] 获取用户信息失败: {data.get('message')}")
            return None
        
        user_data = data.get('data', {}).get('user', {})
        
        # 提取关键字段
        user = {
            'external_user_id': str(user_id),
            'username': user_data.get('name'),
            'display_name': user_data.get('screen_name'),
            'avatar_url': user_data.get('avatar_url'),
            'bio': user_data.get('description'),
            'is_verified': user_data.get('verified') == True,
            'verification_type': user_data.get('verified_reason'),
            'profile_url': f"https://www.toutiao.com/c/user/{user_id}/",
            'follower_count': user_data.get('followers_count', 0),
            'following_count': user_data.get('friends_count', 0),
            'raw_data': user_data,
        }
        
        logger.info(f"[TOUTIAO] 提取用户: {user.get('display_name', user_id)}")
        return user
    
    def extract_user_articles(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        提取用户文章列表
        
        Args:
            user_id: 用户ID
            limit: 最大数量
            
        Returns:
            文章列表
        """
        articles = []
        page = 1
        page_size = 20
        
        while len(articles) < limit:
            data = self._safe_request(
                self.client.get_user_articles,
                user_id,
                page=page,
                page_size=page_size
            )
            
            if data.get('code') != 0:
                break
            
            article_list = data.get('data', {}).get('articles', [])
            if not article_list:
                break
            
            for article in article_list:
                articles.append(self._parse_article_info(article))
            
            if len(article_list) < page_size:
                break
            
            page += 1
        
        logger.info(f"[TOUTIAO] 提取用户 {user_id} 的文章: {len(articles)} 篇")
        return articles[:limit]
    
    def _parse_article_info(self, article_data: Dict) -> Dict[str, Any]:
        """
        解析文章信息
        
        Args:
            article_data: 原始文章数据
            
        Returns:
            解析后的文章数据
        """
        return {
            'external_content_id': str(article_data.get('group_id', article_data.get('id'))),
            'content_type': 'article',
            'title': article_data.get('title'),
            'description': article_data.get('abstract'),
            'content_text': article_data.get('content'),
            'cover_url': article_data.get('image_url'),
            'view_count': article_data.get('detail_play_count', article_data.get('view_count', 0)),
            'like_count': article_data.get('digg_count', 0),
            'comment_count': article_data.get('comment_count', 0),
            'share_count': article_data.get('share_count', 0),
            'collect_count': article_data.get('collect_count', 0),
            'author_id': str(article_data.get('user_id')),
            'published_at': datetime.fromtimestamp(article_data.get('publish_time', 0)),
            'tags': article_data.get('keywords', '').split(',') if article_data.get('keywords') else [],
            'raw_data': article_data,
        }
    
    def extract_followings(
        self,
        user_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        提取用户关注列表
        
        Args:
            user_id: 用户ID
            limit: 最大数量
            
        Returns:
            关注列表
        """
        followings = []
        page = 1
        page_size = 20
        
        while len(followings) < limit:
            data = self._safe_request(
                self.client.get_user_followings,
                user_id,
                page=page,
                page_size=page_size
            )
            
            if data.get('code') != 0:
                break
            
            list_data = data.get('data', {}).get('followings', [])
            if not list_data:
                break
            
            for item in list_data:
                followings.append({
                    'external_user_id': str(item.get('user_id')),
                    'username': item.get('name'),
                    'display_name': item.get('screen_name'),
                    'avatar_url': item.get('avatar_url'),
                })
            
            if len(list_data) < page_size:
                break
            
            page += 1
        
        logger.info(f"[TOUTIAO] 提取用户 {user_id} 的关注列表: {len(followings)} 人")
        return followings[:limit]
    
    def extract_followers(
        self,
        user_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        提取用户粉丝列表
        
        Args:
            user_id: 用户ID
            limit: 最大数量
            
        Returns:
            粉丝列表
        """
        followers = []
        page = 1
        page_size = 20
        
        while len(followers) < limit:
            data = self._safe_request(
                self.client.get_user_followers,
                user_id,
                page=page,
                page_size=page_size
            )
            
            if data.get('code') != 0:
                break
            
            list_data = data.get('data', {}).get('fans', [])
            if not list_data:
                break
            
            for item in list_data:
                followers.append({
                    'external_user_id': str(item.get('user_id')),
                    'username': item.get('name'),
                    'display_name': item.get('screen_name'),
                    'avatar_url': item.get('avatar_url'),
                })
            
            if len(list_data) < page_size:
                break
            
            page += 1
        
        logger.info(f"[TOUTIAO] 提取用户 {user_id} 的粉丝列表: {len(followers)} 人")
        return followers[:limit]
    
    # ==================== 内容数据提取 ====================
    
    def extract_article(self, group_id: str) -> Optional[Dict[str, Any]]:
        """
        提取文章详情
        
        Args:
            group_id: 文章ID
            
        Returns:
            文章数据
        """
        data = self._safe_request(self.client.get_article_detail, group_id)
        
        if data.get('code') != 0:
            logger.error(f"[TOUTIAO] 获取文章详情失败: {data.get('message')}")
            return None
        
        article_data = data.get('data', {}).get('article', {})
        
        parsed = {
            'external_content_id': str(group_id),
            'content_type': 'article',
            'title': article_data.get('title'),
            'description': article_data.get('abstract'),
            'content_html': article_data.get('content'),
            'content_text': article_data.get('content'),
            'cover_url': article_data.get('image_url'),
            'view_count': article_data.get('detail_play_count', 0),
            'like_count': article_data.get('digg_count', 0),
            'comment_count': article_data.get('comment_count', 0),
            'share_count': article_data.get('share_count', 0),
            'collect_count': article_data.get('bury_count', 0),
            'author_id': str(article_data.get('user', {}).get('user_id')),
            'author_name': article_data.get('user', {}).get('name'),
            'category_name': article_data.get('category_name'),
            'tags': [tag['name'] for tag in article_data.get('tag', [])],
            'published_at': datetime.fromtimestamp(article_data.get('publish_time', 0)),
            'raw_data': article_data,
        }
        
        logger.info(f"[TOUTIAO] 提取文章: {parsed.get('title', group_id)}")
        return parsed
    
    def extract_article_comments(
        self,
        group_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        提取文章评论
        
        Args:
            group_id: 文章ID
            limit: 最大数量
            
        Returns:
            评论列表
        """
        comments = []
        page = 1
        page_size = 20
        
        while len(comments) < limit:
            data = self._safe_request(
                self.client.get_article_comments,
                group_id,
                page=page,
                page_size=page_size
            )
            
            if data.get('code') != 0:
                break
            
            comment_list = data.get('data', {}).get('comments', [])
            if not comment_list:
                break
            
            for comment in comment_list:
                comments.append({
                    'external_comment_id': str(comment.get('id')),
                    'content': comment.get('text'),
                    'author_id': str(comment.get('user', {}).get('user_id')),
                    'author_name': comment.get('user', {}).get('name'),
                    'like_count': comment.get('digg_count', 0),
                    'timestamp': datetime.fromtimestamp(comment.get('create_time', 0)),
                    'raw_data': comment,
                })
            
            if len(comment_list) < page_size:
                break
            
            page += 1
        
        logger.info(f"[TOUTIAO] 提取文章 {group_id} 的评论: {len(comments)} 条")
        return comments[:limit]
    
    def extract_feed(
        self,
        category: str = 'all',
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        提取推荐内容流
        
        Args:
            category: 分类
            limit: 最大数量
            
        Returns:
            内容列表
        """
        contents = []
        page = 1
        page_size = 20
        
        while len(contents) < limit:
            data = self._safe_request(
                self.client.get_feed,
                category=category,
                page=page,
                page_size=page_size
            )
            
            if data.get('code') != 0:
                break
            
            feed_list = data.get('data', [])
            if not feed_list:
                break
            
            for item in feed_list:
                contents.append({
                    'external_content_id': str(item.get('group_id', item.get('id'))),
                    'content_type': item.get('content_type', 'article'),
                    'title': item.get('title'),
                    'description': item.get('abstract'),
                    'cover_url': item.get('image_url'),
                    'view_count': item.get('detail_play_count', item.get('view_count', 0)),
                    'like_count': item.get('digg_count', 0),
                    'comment_count': item.get('comment_count', 0),
                    'share_count': item.get('share_count', 0),
                    'author_id': str(item.get('user_id')),
                    'author_name': item.get('source'),
                    'published_at': datetime.fromtimestamp(item.get('publish_time', 0)),
                    'tags': item.get('keywords', '').split(',') if item.get('keywords') else [],
                    'raw_data': item,
                })
            
            if len(feed_list) < page_size:
                break
            
            page += 1
        
        logger.info(f"[TOUTIAO] 提取内容流: {len(contents)} 条")
        return contents[:limit]
    
    def search_articles(
        self,
        keyword: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        搜索文章
        
        Args:
            keyword: 搜索关键词
            limit: 最大数量
            
        Returns:
            文章列表
        """
        articles = []
        page = 1
        page_size = 20
        
        while len(articles) < limit:
            data = self._safe_request(
                self.client.search_feed,
                keyword,
                page=page,
                page_size=page_size
            )
            
            if data.get('code') != 0:
                break
            
            result_list = data.get('data', [])
            if not result_list:
                break
            
            for result in result_list:
                articles.append({
                    'external_content_id': str(result.get('group_id', result.get('id'))),
                    'content_type': 'article',
                    'title': result.get('title'),
                    'description': result.get('abstract'),
                    'cover_url': result.get('image_url'),
                    'view_count': result.get('detail_play_count', 0),
                    'like_count': result.get('digg_count', 0),
                    'author_id': str(result.get('user_id')),
                    'published_at': datetime.fromtimestamp(result.get('publish_time', 0)),
                })
            
            page += 1
        
        logger.info(f"[TOUTIAO] 搜索文章 '{keyword}': {len(articles)} 个结果")
        return articles[:limit]
    
    def extract_hot_search(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        提取热搜榜
        
        Args:
            limit: 最大数量
            
        Returns:
            热搜列表
        """
        data = self._safe_request(self.client.get_hot_search)
        
        if data.get('code') != 0:
            return []
        
        hot_list = data.get('data', {}).get('hot_search', [])[:limit]
        
        result = []
        for item in hot_list:
            result.append({
                'keyword': item.get('keyword'),
                'heat': item.get('heat'),
                'url': item.get('url'),
                'platform': item.get('platform'),
            })
        
        logger.info(f"[TOUTIAO] 提取热搜榜: {len(result)} 条")
        return result
    
    # ==================== 批量提取 ====================
    
    def batch_extract_users(
        self,
        user_ids: List[str]
    ) -> List[Dict[str, Any]]:
        """
        批量提取用户信息
        
        Args:
            user_ids: 用户ID列表
            
        Returns:
            用户数据列表
        """
        users = []
        
        for user_id in user_ids:
            try:
                user = self.extract_user(user_id)
                if user:
                    users.append(user)
                    
            except Exception as e:
                logger.error(f"[TOUTIAO] 提取用户 {user_id} 失败: {e}")
        
        return users
    
    def crawl_user_network(
        self,
        seed_user_id: str,
        max_users: int = 100,
        depth: int = 2
    ) -> Dict[str, Any]:
        """
        爬取用户关系网络
        
        Args:
            seed_user_id: 种子用户ID
            max_users: 最大用户数
            depth: 爬取深度
            
        Returns:
            关系网络数据
        """
        network = {
            'users': [],
            'relations': [],
            'seed_user': seed_user_id,
        }
        
        visited = set()
        to_visit = [seed_user_id]
        current_depth = 0
        
        while to_visit and len(visited) < max_users and current_depth <= depth:
            batch = to_visit[:10]
            to_visit = to_visit[10:]
            
            for user_id in batch:
                if user_id in visited:
                    continue
                
                visited.add(user_id)
                
                # 提取用户
                user = self.extract_user(user_id)
                if user:
                    network['users'].append(user)
                
                # 提取关注和粉丝
                if current_depth < depth:
                    followings = self.extract_followings(user_id, limit=20)
                    followers = self.extract_followers(user_id, limit=20)
                    
                    for following in followings:
                        network['relations'].append({
                            'from': user_id,
                            'to': following['external_user_id'],
                            'type': 'follows',
                        })
                        if following['external_user_id'] not in visited:
                            to_visit.append(following['external_user_id'])
                    
                    for follower in followers:
                        network['relations'].append({
                            'from': follower['external_user_id'],
                            'to': user_id,
                            'type': 'follows',
                        })
                        if follower['external_user_id'] not in visited:
                            to_visit.append(follower['external_user_id'])
            
            current_depth += 1
        
        logger.info(f"[TOUTIAO] 爬取用户网络完成: {len(network['users'])} 用户, {len(network['relations'])} 关系")
        return network

# -*- coding: utf-8 -*-
"""
哔哩哔哩数据提取模块
Bilibili Data Extractor Module

提供从哔哩哔哩平台提取用户、内容、关系数据的功能
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
from .bilibili_client import BilibiliClient


class BilibiliDataExtractor:
    """哔哩哔哩数据提取器"""
    
    def __init__(self, client: BilibiliClient):
        """
        初始化数据提取器
        
        Args:
            client: BilibiliClient实例
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
                logger.warning(f"[BILI] 请求失败 (尝试 {retry_count}/{max_retries}): {e}")
                time.sleep(2 ** retry_count)  # 指数退避
        
        logger.error(f"[BILI] 请求失败，已达到最大重试次数")
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
        data = self._safe_request(self.client.get_user_info, user_id)
        
        if data.get('code') != 0:
            logger.error(f"[BILI] 获取用户信息失败: {data.get('message')}")
            return None
        
        user_data = data.get('data', {})
        
        # 提取关键字段
        user = {
            'external_user_id': str(user_id),
            'username': user_data.get('name'),
            'display_name': user_data.get('uname'),
            'avatar_url': user_data.get('face'),
            'bio': user_data.get('sign'),
            'gender': user_data.get('sex'),
            'is_verified': user_data.get('vip', {}).get('type') > 0,
            'level': user_data.get('level'),
            'profile_url': f"https://space.bilibili.com/{user_id}",
            'raw_data': user_data,
        }
        
        # 获取统计数据
        stats_data = self._safe_request(self.client.get_user_stats, user_id)
        if stats_data.get('code') == 0:
            stats = stats_data.get('data', {})
            user['follower_count'] = stats.get('follower', 0)
            user['following_count'] = stats.get('following', 0)
        
        logger.info(f"[BILI] 提取用户: {user.get('display_name', user_id)}")
        return user
    
    def extract_user_with_contents(
        self,
        user_id: str,
        max_videos: int = 100,
        max_articles: int = 50
    ) -> Dict[str, Any]:
        """
        提取用户完整信息（含内容）
        
        Args:
            user_id: 用户ID
            max_videos: 最大视频数
            max_articles: 最大文章数
            
        Returns:
            用户完整数据
        """
        # 提取基本信息
        user = self.extract_user(user_id)
        if not user:
            return {}
        
        # 提取视频列表
        videos = []
        page = 1
        while len(videos) < max_videos:
            data = self._safe_request(
                self.client.get_user_videos,
                user_id,
                page=page,
                page_size=30
            )
            
            if data.get('code') != 0:
                break
            
            video_list = data.get('data', {}).get('list', {}).get('vlist', [])
            if not video_list:
                break
            
            for video in video_list:
                videos.append(self._parse_video_info(video))
            
            page += 1
        
        user['videos'] = videos[:max_videos]
        
        # 提取文章列表
        articles = []
        page = 1
        while len(articles) < max_articles:
            data = self._safe_request(self.client.get_user_articles, user_id, page=page)
            
            if data.get('code') != 0:
                break
            
            article_list = data.get('data', {}).get('articles', [])
            if not article_list:
                break
            
            for article in article_list:
                articles.append(self._parse_article_info(article))
            
            page += 1
        
        user['articles'] = articles[:max_articles]
        
        # 提取动态
        dynamics = self._extract_user_dynamics(user_id, limit=20)
        user['dynamics'] = dynamics
        
        return user
    
    def _extract_user_dynamics(
        self,
        user_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        提取用户动态
        
        Args:
            user_id: 用户ID
            limit: 最大数量
            
        Returns:
            动态列表
        """
        data = self._safe_request(self.client.get_user_dynamics, user_id)
        
        if data.get('code') != 0:
            return []
        
        items = data.get('data', {}).get('items', [])[:limit]
        
        dynamics = []
        for item in items:
            dynamic = {
                'external_id': str(item.get('id')),
                'type': item.get('type'),
                'content': item.get('modules', {}).get('module_dynamic', {}).get('desc', {}).get('text'),
                'timestamp': item.get('modules', {}).get('module_author', {}).get('pub_time'),
                'raw_data': item,
            }
            dynamics.append(dynamic)
        
        return dynamics
    
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
            
            list_data = data.get('data', {}).get('list', [])
            if not list_data:
                break
            
            for item in list_data:
                followings.append({
                    'external_user_id': str(item.get('mid')),
                    'username': item.get('uname'),
                    'display_name': item.get('uname'),
                    'avatar_url': item.get('face'),
                })
            
            if len(list_data) < page_size:
                break
            
            page += 1
        
        logger.info(f"[BILI] 提取用户 {user_id} 的关注列表: {len(followings)} 人")
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
            
            list_data = data.get('data', {}).get('list', [])
            if not list_data:
                break
            
            for item in list_data:
                followers.append({
                    'external_user_id': str(item.get('mid')),
                    'username': item.get('uname'),
                    'display_name': item.get('uname'),
                    'avatar_url': item.get('face'),
                })
            
            if len(list_data) < page_size:
                break
            
            page += 1
        
        logger.info(f"[BILI] 提取用户 {user_id} 的粉丝列表: {len(followers)} 人")
        return followers[:limit]
    
    # ==================== 内容数据提取 ====================
    
    def _parse_video_info(self, video_data: Dict) -> Dict[str, Any]:
        """
        解析视频信息
        
        Args:
            video_data: 原始视频数据
            
        Returns:
            解析后的视频数据
        """
        return {
            'external_content_id': video_data.get('bvid'),
            'content_type': 'video',
            'title': video_data.get('title'),
            'description': video_data.get('description'),
            'cover_url': video_data.get('pic'),
            'view_count': video_data.get('play'),
            'like_count': video_data.get('like'),
            'comment_count': video_data.get('comment'),
            'duration': video_data.get('length'),
            'author_id': str(video_data.get('mid')),
            'published_at': datetime.fromtimestamp(video_data.get('created', 0)),
            'tags': video_data.get('tags', '').split(',') if video_data.get('tags') else [],
            'raw_data': video_data,
        }
    
    def _parse_article_info(self, article_data: Dict) -> Dict[str, Any]:
        """
        解析专栏文章信息
        
        Args:
            article_data: 原始文章数据
            
        Returns:
            解析后的文章数据
        """
        return {
            'external_content_id': str(article_data.get('id')),
            'content_type': 'article',
            'title': article_data.get('title'),
            'description': article_data.get('summary'),
            'content_html': article_data.get('content'),
            'cover_url': article_data.get('image_urls', [{}])[0].get('url') if article_data.get('image_urls') else None,
            'view_count': article_data.get('stats', {}).get('view', 0),
            'like_count': article_data.get('stats', {}).get('like', 0),
            'comment_count': article_data.get('stats', {}).get('reply', 0),
            'author_id': str(article_data.get('author', {}).get('mid')),
            'published_at': datetime.fromtimestamp(article_data.get('publish_time', 0)),
            'raw_data': article_data,
        }
    
    def extract_video(self, bvid: str) -> Optional[Dict[str, Any]]:
        """
        提取视频详情
        
        Args:
            bvid: B站视频ID
            
        Returns:
            视频数据
        """
        data = self._safe_request(self.client.get_video_info, bvid)
        
        if data.get('code') != 0:
            logger.error(f"[BILI] 获取视频信息失败: {data.get('message')}")
            return None
        
        video_data = data.get('data', {})
        
        parsed = {
            'external_content_id': video_data.get('bvid'),
            'content_type': 'video',
            'title': video_data.get('title'),
            'description': video_data.get('desc'),
            'content_text': video_data.get('desc'),
            'cover_url': video_data.get('pic'),
            'video_url': video_data.get('link'),
            'duration': video_data.get('duration'),
            'view_count': video_data.get('stat', {}).get('view', 0),
            'like_count': video_data.get('stat', {}).get('like', 0),
            'dislike_count': video_data.get('stat', {}).get('dislike', 0),
            'comment_count': video_data.get('stat', {}).get('reply', 0),
            'share_count': video_data.get('stat', {}).get('share', 0),
            'collect_count': video_data.get('stat', {}).get('coin', 0),
            'danmaku_count': video_data.get('stat', {}).get('danmaku', 0),
            'author_id': str(video_data.get('owner', {}).get('mid')),
            'category_id': str(video_data.get('cid', '')),
            'category_name': video_data.get('tname', ''),
            'tags': [tag['tag_name'] for tag in video_data.get('tags', [])],
            'published_at': datetime.fromtimestamp(video_data.get('pubdate', 0)),
            'raw_data': video_data,
        }
        
        logger.info(f"[BILI] 提取视频: {parsed.get('title', bvid)}")
        return parsed
    
    def extract_video_comments(
        self,
        bvid: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        提取视频评论
        
        Args:
            bvid: B站视频ID
            limit: 最大数量
            
        Returns:
            评论列表
        """
        comments = []
        page = 1
        page_size = 20
        
        while len(comments) < limit:
            data = self._safe_request(
                self.client.get_video_comments,
                bvid,
                page=page,
                page_size=page_size
            )
            
            if data.get('code') != 0:
                break
            
            reply_list = data.get('data', {}).get('replies', [])
            if not reply_list:
                break
            
            for reply in reply_list:
                comments.append({
                    'external_comment_id': str(reply.get('rpid')),
                    'content': reply.get('content', {}).get('message'),
                    'author_id': str(reply.get('member', {}).get('mid')),
                    'like_count': reply.get('like', 0),
                    'timestamp': datetime.fromtimestamp(reply.get('ctime', 0)),
                    'raw_data': reply,
                })
            
            if len(reply_list) < page_size:
                break
            
            page += 1
        
        logger.info(f"[BILI] 提取视频 {bvid} 的评论: {len(comments)} 条")
        return comments[:limit]
    
    def extract_popular_videos(
        self,
        limit: int = 50,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        提取热门视频
        
        Args:
            limit: 最大数量
            category: 分区（可选）
            
        Returns:
            视频列表
        """
        videos = []
        page = 1
        
        while len(videos) < limit:
            data = self._safe_request(self.client.get_popular_videos, page=page)
            
            if data.get('code') != 0:
                break
            
            video_list = data.get('data', {}).get('list', [])
            if not video_list:
                break
            
            for video in video_list:
                videos.append(self._parse_video_info(video))
            
            page += 1
        
        logger.info(f"[BILI] 提取热门视频: {len(videos)} 个")
        return videos[:limit]
    
    def search_videos(
        self,
        keyword: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        搜索视频
        
        Args:
            keyword: 搜索关键词
            limit: 最大数量
            
        Returns:
            视频列表
        """
        videos = []
        page = 1
        
        while len(videos) < limit:
            data = self._safe_request(
                self.client.search,
                keyword,
                page=page,
                page_size=20,
                search_type='video'
            )
            
            if data.get('code') != 0:
                break
            
            result_list = data.get('data', {}).get('result', [])
            if not result_list:
                break
            
            for result in result_list:
                videos.append({
                    'external_content_id': result.get('bvid'),
                    'content_type': 'video',
                    'title': result.get('title'),
                    'description': result.get('description'),
                    'cover_url': result.get('pic'),
                    'view_count': result.get('play'),
                    'like_count': result.get('like'),
                    'author_id': str(result.get('mid')),
                    'author_name': result.get('author'),
                    'duration': result.get('duration'),
                    'published_at': result.get('pubdate'),
                })
            
            page += 1
        
        logger.info(f"[BILI] 搜索视频 '{keyword}': {len(videos)} 个结果")
        return videos[:limit]
    
    # ==================== 批量提取 ====================
    
    def batch_extract_users(
        self,
        user_ids: List[str],
        include_contents: bool = False
    ) -> List[Dict[str, Any]]:
        """
        批量提取用户信息
        
        Args:
            user_ids: 用户ID列表
            include_contents: 是否包含内容
            
        Returns:
            用户数据列表
        """
        users = []
        
        for user_id in user_ids:
            try:
                if include_contents:
                    user = self.extract_user_with_contents(user_id)
                else:
                    user = self.extract_user(user_id)
                
                if user:
                    users.append(user)
                    
            except Exception as e:
                logger.error(f"[BILI] 提取用户 {user_id} 失败: {e}")
        
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
        
        logger.info(f"[BILI] 爬取用户网络完成: {len(network['users'])} 用户, {len(network['relations'])} 关系")
        return network

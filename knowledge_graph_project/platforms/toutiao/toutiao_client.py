# -*- coding: utf-8 -*-
"""
今日头条API客户端
Toutiao API Client

提供今日头条API请求功能，支持登录状态自动管理
"""

import json
import time
import hashlib
import uuid
from typing import Optional, Dict, Any, List
from pathlib import Path
import requests
from loguru import logger

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import settings


class ToutiaoClient:
    """今日头条API客户端"""
    
    # API配置
    API_BASE = "https://www.toutiao.com"
    API_V2 = "https://www.toutiao.com/api"
    TOUTIAO_API = "https://www.toutiao.com/api/pc/feed"
    
    # 必要的Cookie字段
    REQUIRED_COOKIES = ['tt_webid', 'csrftoken', 'sessionid']
    
    def __init__(self, cookies: Optional[Dict[str, str]] = None):
        """
        初始化客户端
        
        Args:
            cookies: Cookie字典，可选
        """
        self.session = requests.Session()
        self.cookies = cookies or {}
        
        # 设置默认请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.toutiao.com/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })
    
    def set_cookies(self, cookies: Dict[str, str]) -> None:
        """
        设置Cookie
        
        Args:
            cookies: Cookie字典
        """
        self.cookies.update(cookies)
        self.session.cookies.update(cookies)
        logger.info(f"[TOUTIAO] Cookies已更新")
    
    def get_cookies(self) -> Dict[str, str]:
        """
        获取当前Cookie
        
        Returns:
            Cookie字典
        """
        return {k: v for k, v in self.cookies.items()}
    
    def is_logged_in(self) -> bool:
        """
        检查是否已登录
        
        Returns:
            是否已登录
        """
        # 检查必要的Cookie字段
        if not all(k in self.cookies for k in self.REQUIRED_COOKIES):
            return False
        
        # 尝试获取用户信息验证
        try:
            response = self.get_user_info()
            return response is not None and response.get('code') == 0
        except Exception:
            return False
    
    def _make_request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        发起API请求
        
        Args:
            method: HTTP方法
            url: 请求URL
            params: URL参数
            data: 表单数据
            json_data: JSON数据
            **kwargs: 其他参数
            
        Returns:
            响应数据
        """
        # 发送请求
        response = self.session.request(
            method=method,
            url=url,
            params=params,
            data=data,
            json=json_data,
            **kwargs
        )
        
        # 解析响应
        try:
            return response.json()
        except json.JSONDecodeError:
            logger.error(f"[TOUTIAO] JSON解析失败: {response.text[:200]}")
            return {'code': -1, 'message': 'JSON解析失败'}
    
    # ==================== 用户相关API ====================
    
    def get_user_info(self) -> Dict[str, Any]:
        """
        获取当前登录用户信息
        
        Returns:
            用户信息
        """
        url = f"{self.API_BASE}/user/profile/info/v2/"
        params = {
            'channel': 'pc',
            'aid': '4912',
            '_signature': self._generate_signature(),
        }
        return self._make_request('GET', url, params)
    
    def get_user_articles(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        获取用户文章列表
        
        Args:
            user_id: 用户ID
            page: 页码
            page_size: 每页数量
            
        Returns:
            文章列表
        """
        url = f"{self.API_BASE}/api/pc/user/profile/articles/"
        params = {
            'user_id': user_id,
            'page': page,
            'page_size': page_size,
            'sort': 'time',
            'aid': '4912',
            '_signature': self._generate_signature(),
        }
        return self._make_request('GET', url, params)
    
    def get_user_followers(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        获取用户粉丝列表
        
        Args:
            user_id: 用户ID
            page: 页码
            page_size: 每页数量
            
        Returns:
            粉丝列表
        """
        url = f"{self.API_BASE}/user/profile/fans/"
        params = {
            'user_id': user_id,
            'page': page,
            'page_size': page_size,
            'aid': '4912',
        }
        return self._make_request('GET', url, params)
    
    def get_user_followings(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        获取用户关注列表
        
        Args:
            user_id: 用户ID
            page: 页码
            page_size: 每页数量
            
        Returns:
            关注列表
        """
        url = f"{self.API_BASE}/user/profile/followers/"
        params = {
            'user_id': user_id,
            'page': page,
            'page_size': page_size,
            'aid': '4912',
        }
        return self._make_request('GET', url, params)
    
    # ==================== 内容相关API ====================
    
    def get_article_detail(self, group_id: str) -> Dict[str, Any]:
        """
        获取文章详情
        
        Args:
            group_id: 文章ID
            
        Returns:
            文章详情
        """
        url = f"{self.API_BASE}/api/pc/article/detail/"
        params = {
            'group_id': group_id,
            'aid': '4912',
        }
        return self._make_request('GET', url, params)
    
    def get_article_comments(
        self,
        group_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        获取文章评论
        
        Args:
            group_id: 文章ID
            page: 页码
            page_size: 每页数量
            
        Returns:
            评论列表
        """
        url = f"{self.API_BASE}/api/pc/article/detail/comments/"
        params = {
            'group_id': group_id,
            'page': page,
            'page_size': page_size,
            'aid': '4912',
        }
        return self._make_request('GET', url, params)
    
    # ==================== 推荐和搜索API ====================
    
    def get_feed(
        self,
        category: str = 'all',
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        获取推荐内容流
        
        Args:
            category: 分类
            page: 页码
            page_size: 每页数量
            
        Returns:
            内容流
        """
        url = f"{self.TOUTIAO_API}/feed/"
        params = {
            'category': category,
            'page': page,
            'page_size': page_size,
            'aid': '4912',
            '_signature': self._generate_signature(),
        }
        return self._make_request('GET', url, params)
    
    def search(
        self,
        keyword: str,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        搜索内容
        
        Args:
            keyword: 搜索关键词
            page: 页码
            page_size: 每页数量
            
        Returns:
            搜索结果
        """
        url = f"{self.API_BASE}/api/pc/search/suggest/"
        params = {
            'keyword': keyword,
            'page': page,
            'page_size': page_size,
            'aid': '4912',
        }
        return self._make_request('GET', url, params)
    
    def search_feed(
        self,
        keyword: str,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        搜索内容流
        
        Args:
            keyword: 搜索关键词
            page: 页码
            page_size: 每页数量
            
        Returns:
            搜索结果
        """
        url = f"{self.API_BASE}/api/pc/search/feed/"
        params = {
            'keyword': keyword,
            'page': page,
            'page_size': page_size,
            'aid': '4912',
        }
        return self._make_request('GET', url, params)
    
    # ==================== 热搜榜API ====================
    
    def get_hot_search(self) -> Dict[str, Any]:
        """
        获取热搜榜
        
        Returns:
            热搜列表
        """
        url = f"{self.API_BASE}/api/pc/hot-search/list/"
        params = {
            'aid': '4912',
        }
        return self._make_request('GET', url, params)
    
    # ==================== 工具方法 ====================
    
    def _generate_signature(self) -> str:
        """
        生成签名
        
        Returns:
            签名字符串
        """
        # 今日头条使用特定算法生成签名
        timestamp = str(int(time.time()))
        nonce = str(uuid.uuid4())[:8]
        
        # 简化签名（实际需要根据具体算法）
        sig_input = f"{timestamp}{nonce}{self.cookies.get('tt_webid', '')}"
        signature = hashlib.md5(sig_input.encode()).hexdigest()
        
        return signature
    
    # ==================== 问答相关API ====================
    
    def get_question_detail(self, question_id: str) -> Dict[str, Any]:
        """
        获取问答详情
        
        Args:
            question_id: 问答ID
            
        Returns:
            问答详情
        """
        url = f"{self.API_BASE}/qa/question/{question_id}/"
        params = {
            'aid': '4912',
        }
        return self._make_request('GET', url, params)
    
    def get_question_answers(
        self,
        question_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        获取问答回答列表
        
        Args:
            question_id: 问答ID
            page: 页码
            page_size: 每页数量
            
        Returns:
            回答列表
        """
        url = f"{self.API_BASE}/qa/question/{question_id}/answers/"
        params = {
            'page': page,
            'page_size': page_size,
            'aid': '4912',
        }
        return self._make_request('GET', url, params)

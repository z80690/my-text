# -*- coding: utf-8 -*-
"""
哔哩哔哩API客户端
Bilibili API Client

提供哔哩哔哩API请求功能，支持登录状态自动管理
"""

import json
import time
import hashlib
import re
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
import requests
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64
from loguru import logger

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import settings


class BilibiliClient:
    """哔哩哔哩API客户端"""
    
    # API配置
    API_BASE = "https://api.bilibili.com"
    PASSPORT_API = "https://passport.bilibili.com"
    LIVE_API = "https://live.bilibili.com"
    
    # 必要的Cookie字段
    REQUIRED_COOKIES = ['SESSDATA', 'bili_jct', 'DedeUserID', 'DedeUserID__ckMd5', 'sid']
    
    def __init__(self, cookies: Optional[Dict[str, str]] = None):
        """
        初始化客户端
        
        Args:
            cookies: Cookie字典，可选
        """
        self.session = requests.Session()
        self.cookies = cookies or {}
        self.wbi_mixin_key = None
        
        # 设置默认请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.bilibili.com/',
            'Accept': 'application/json, text/plain, */*',
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
        logger.info("[BILI] Cookies已更新")
    
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
    
    def _get_wbi_sign(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        获取WBI签名
        
        Args:
            params: 请求参数
            
        Returns:
            带签名的参数
        """
        if not self.wbi_mixin_key:
            self._fetch_wbi_key()
        
        # 排序参数
        sorted_params = sorted(params.items())
        query = '&'.join(f'{k}={v}' for k, v in sorted_params if v)
        
        # 计算签名
        md5 = hashlib.md5()
        md5.update((query + self.wbi_mixin_key).encode())
        w_rid = md5.hexdigest()
        
        params['w_rid'] = w_rid
        params['wts'] = int(time.time())
        
        return params
    
    def _fetch_wbi_key(self) -> None:
        """获取WBI密钥"""
        try:
            url = f"{self.API_BASE}/x/web-interface/nav"
            response = self.session.get(url)
            data = response.json()
            
            if data.get('code') == 0:
                wbi_img = data.get('data', {}).get('wbi_img', {})
                self.wbi_mixin_key = self._get_mixin_key(wbi_img.get('img_url', ''))
        except Exception as e:
            logger.error(f"[BILI] 获取WBI密钥失败: {e}")
    
    def _get_mixin_key(self, img_url: str) -> str:
        """
        从图片URL提取mixin_key
        
        Args:
            img_url: 图片URL
            
        Returns:
            mixin_key
        """
        match = re.search(r'mixin_key=([^&]+)', img_url)
        if match:
            return match.group(1)
        return ""
    
    def _encrypt_password(self, password: str) -> Tuple[str, str]:
        """
        加密密码
        
        Args:
            password: 原始密码
            
        Returns:
            (加密后的密码, hash)
        """
        # 获取公钥
        url = f"{self.PASSPORT_API}/x/passport-login/web/key"
        response = self.session.get(url)
        data = response.json()
        
        if data.get('code') != 0:
            raise Exception(f"获取公钥失败: {data.get('message')}")
        
        key_data = data['data']
        pub_key = RSA.import_key(key_data['key'])
        hash_str = key_data['hash']
        
        # 加密密码
        cipher = PKCS1_v1_5.new(pub_key)
        encrypted = cipher.encrypt((hash_str + password).encode())
        encrypted_password = base64.b64encode(encrypted).decode()
        
        return encrypted_password, hash_str
    
    def _make_request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        use_wbi: bool = False,
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
            use_wbi: 是否使用WBI签名
            **kwargs: 其他参数
            
        Returns:
            响应数据
        """
        # 添加认证参数
        if use_wbi and self.cookies.get('SESSDATA'):
            params = params or {}
            params = self._get_wbi_sign(params)
        
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
            logger.error(f"[BILI] JSON解析失败: {response.text[:200]}")
            return {'code': -1, 'message': 'JSON解析失败'}
    
    # ==================== 用户相关API ====================
    
    def get_user_info(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        获取用户信息
        
        Args:
            user_id: 用户ID，为空获取当前登录用户
            
        Returns:
            用户信息
        """
        if user_id:
            url = f"{self.API_BASE}/x/space/wbi/acc/info"
            params = {'mid': user_id, 'jsonp': 'jsonp'}
            return self._make_request('GET', url, params, use_wbi=True)
        else:
            url = f"{self.API_BASE}/x/web-interface/nav"
            return self._make_request('GET', url)
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户统计数据
        
        Args:
            user_id: 用户ID
            
        Returns:
            统计数据
        """
        url = f"{self.API_BASE}/x/relation/stat"
        params = {'vmid': user_id, 'jsonp': 'jsonp'}
        return self._make_request('GET', url, params)
    
    def get_user_videos(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 30,
        order: str = 'pubdate'  # pubdate, click, stow
    ) -> Dict[str, Any]:
        """
        获取用户视频列表
        
        Args:
            user_id: 用户ID
            page: 页码
            page_size: 每页数量
            order: 排序方式
            
        Returns:
            视频列表
        """
        url = f"{self.API_BASE}/x/space/wbi/arc/search"
        params = {
            'mid': user_id,
            'pn': page,
            'ps': page_size,
            'order': order,
            'jsonp': 'jsonp'
        }
        return self._make_request('GET', url, params, use_wbi=True)
    
    def get_user_articles(self, user_id: str, page: int = 1) -> Dict[str, Any]:
        """
        获取用户专栏文章
        
        Args:
            user_id: 用户ID
            page: 页码
            
        Returns:
            文章列表
        """
        url = f"{self.API_BASE}/x/space/article"
        params = {'mid': user_id, 'pn': page, 'ps': 10, 'sort': 'publish_time'}
        return self._make_request('GET', url, params)
    
    def get_user_dynamics(
        self,
        user_id: str,
        offset: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取用户动态
        
        Args:
            user_id: 用户ID
            offset: 分页偏移
            
        Returns:
            动态列表
        """
        url = f"{self.API_BASE}/x/polymer/web-dynamic/v1/feed/space"
        params = {'host_mid': user_id}
        if offset:
            params['offset'] = offset
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
        url = f"{self.API_BASE}/x/relation/followings"
        params = {
            'vmid': user_id,
            'pn': page,
            'ps': page_size,
            'order': 'desc',
            'jsonp': 'jsonp'
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
        url = f"{self.API_BASE}/x/relation/followers"
        params = {
            'vmid': user_id,
            'pn': page,
            'ps': page_size,
            'order': 'desc',
            'jsonp': 'jsonp'
        }
        return self._make_request('GET', url, params)
    
    # ==================== 内容相关API ====================
    
    def get_video_info(self, bvid: str) -> Dict[str, Any]:
        """
        获取视频详情
        
        Args:
            bvid: B站视频ID (BV号)
            
        Returns:
            视频详情
        """
        url = f"{self.API_BASE}/x/web-interface/view"
        params = {'bvid': bvid}
        return self._make_request('GET', url, params)
    
    def get_video_stat(self, bvid: str) -> Dict[str, Any]:
        """
        获取视频统计数据
        
        Args:
            bvid: B站视频ID
            
        Returns:
            统计数据
        """
        url = f"{self.API_BASE}/x/web-interface/view/stat"
        params = {'bvid': bvid}
        return self._make_request('GET', url, params)
    
    def get_video_comments(
        self,
        bvid: str,
        page: int = 1,
        page_size: int = 20,
        sort: str = '2'  # 0:按时间, 1:按热门, 2:按推荐
    ) -> Dict[str, Any]:
        """
        获取视频评论
        
        Args:
            bvid: 视频BVID
            page: 页码
            page_size: 每页数量
            sort: 排序方式
            
        Returns:
            评论列表
        """
        # 先获取视频对应的oid
        video_info = self.get_video_info(bvid)
        if video_info.get('code') != 0:
            return video_info
        
        aid = video_info['data']['aid']
        
        url = f"{self.API_BASE}/x/v2/reply"
        params = {
            'type': 1,
            'oid': aid,
            'pn': page,
            'ps': page_size,
            'sort': sort
        }
        return self._make_request('GET', url, params)
    
    def get_article_info(self, article_id: str) -> Dict[str, Any]:
        """
        获取专栏文章详情
        
        Args:
            article_id: 文章ID
            
        Returns:
            文章详情
        """
        url = f"{self.API_BASE}/x/article/view"
        params = {'id': article_id}
        return self._make_request('GET', url, params)
    
    def get_article_comments(
        self,
        article_id: str,
        page: int = 1
    ) -> Dict[str, Any]:
        """
        获取文章评论
        
        Args:
            article_id: 文章ID
            page: 页码
            
        Returns:
            评论列表
        """
        url = f"{self.API_BASE}/x/v2/reply"
        params = {
            'type': 12,
            'oid': article_id,
            'pn': page,
            'ps': 20
        }
        return self._make_request('GET', url, params)
    
    # ==================== 推荐和搜索API ====================
    
    def get_popular_videos(self, page: int = 1) -> Dict[str, Any]:
        """
        获取热门视频
        
        Args:
            page: 页码
            
        Returns:
            热门视频列表
        """
        url = f"{self.API_BASE}/x/web-interface/popular"
        params = {'pn': page, 'ps': 20}
        return self._make_request('GET', url, params)
    
    def get_recommend_videos(self) -> Dict[str, Any]:
        """
        获取推荐视频
        
        Returns:
            推荐视频列表
        """
        url = f"{self.API_BASE}/x/web-interface/index/feed/zone"
        return self._make_request('GET', url)
    
    def search(
        self,
        keyword: str,
        page: int = 1,
        page_size: int = 20,
        search_type: str = 'video'  # video, article, user, live
    ) -> Dict[str, Any]:
        """
        搜索内容
        
        Args:
            keyword: 搜索关键词
            page: 页码
            page_size: 每页数量
            search_type: 搜索类型
            
        Returns:
            搜索结果
        """
        url = f"{self.API_BASE}/x/web-interface/search/type"
        params = {
            'search_type': search_type,
            'keyword': keyword,
            'page': page,
            'page_size': page_size
        }
        return self._make_request('GET', url, params)
    
    # ==================== 排行榜API ====================
    
    def get_ranking(
        self,
        rid: int = 0,  # 0:全站, 1:动画, 3:音乐, 4:游戏等
        day: int = 3  # 1:日榜, 3:三日榜, 7:周榜
    ) -> Dict[str, Any]:
        """
        获取排行榜
        
        Args:
            rid: 分区ID
            day: 排行周期
            
        Returns:
            排行榜数据
        """
        url = f"{self.API_BASE}/x/web-interface/ranking/region"
        params = {'rid': rid, 'day': day}
        return self._make_request('GET', url, params)
    
    def get_bangumi_timeline(self) -> Dict[str, Any]:
        """
        获取番剧时间线
        
        Returns:
            番剧时间线
        """
        url = f"{self.API_BASE}/x/pgc/web/timeline"
        return self._make_request('GET', url)
    
    # ==================== 话题相关API ====================
    
    def get_topic_info(self, topic_id: str) -> Dict[str, Any]:
        """
        获取话题信息
        
        Args:
            topic_id: 话题ID
            
        Returns:
            话题信息
        """
        url = f"{self.API_BASE}/x/topic/pc/feed"
        params = {'topic_id': topic_id}
        return self._make_request('GET', url, params)
    
    # ==================== 直播相关API ====================
    
    def get_live_info(self, room_id: str) -> Dict[str, Any]:
        """
        获取直播间信息
        
        Args:
            room_id: 直播间ID
            
        Returns:
            直播间信息
        """
        url = f"{self.LIVE_API}/room/v1/Room/getRoomInfoOld"
        params = {'mid': room_id}
        return self._make_request('GET', url, params)
    
    def get_live_room_info(self, room_id: str) -> Dict[str, Any]:
        """
        获取直播间详情
        
        Args:
            room_id: 直播间ID
            
        Returns:
            直播间详情
        """
        url = f"{self.LIVE_API}/xlive/web-room/v1/index/getInfoByRoom"
        params = {'room_id': room_id}
        return self._make_request('GET', url, params)

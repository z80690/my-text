# -*- coding: utf-8 -*-
"""
Cookie管理模块
Cookie Management Module

提供Cookie的加密存储、自动刷新、有效性检测功能
"""

import json
import time
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from loguru import logger

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import settings


class CookieManager:
    """Cookie管理器"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        初始化Cookie管理器
        
        Args:
            encryption_key: 加密密钥，为空则使用配置中的密钥
        """
        key = encryption_key or settings.app.encryption_key

        # 直接使用密钥，Fernet会自动验证格式
        self.fernet = Fernet(key.encode())
        self.cookies_dir = Path("data/cookies")
        self.cookies_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("[COOKIE] Cookie管理器已初始化")
    
    def encrypt_cookies(self, cookies: Dict[str, str]) -> str:
        """
        加密Cookie
        
        Args:
            cookies: Cookie字典
            
        Returns:
            加密后的字符串
        """
        json_data = json.dumps(cookies, ensure_ascii=False)
        encrypted = self.fernet.encrypt(json_data.encode())
        return encrypted.decode()
    
    def decrypt_cookies(self, encrypted_data: str) -> Optional[Dict[str, str]]:
        """
        解密Cookie
        
        Args:
            encrypted_data: 加密数据
            
        Returns:
            解密后的Cookie字典，失败返回None
        """
        try:
            decrypted = self.fernet.decrypt(encrypted_data.encode())
            return json.loads(decrypted.decode())
        except Exception as e:
            logger.error(f"[COOKIE] Cookie解密失败: {e}")
            return None
    
    def save_cookies(
        self,
        platform: str,
        cookies: Dict[str, str],
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        保存Cookie到文件
        
        Args:
            platform: 平台标识
            cookies: Cookie字典
            user_id: 绑定的用户ID（可选）
            metadata: 元数据
            
        Returns:
            是否保存成功
        """
        try:
            # 准备数据
            data = {
                'platform': platform,
                'cookies': self.encrypt_cookies(cookies),
                'user_id': user_id,
                'metadata': metadata or {},
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'checksum': self._generate_checksum(cookies),
            }
            
            # 保存到文件
            file_path = self.cookies_dir / f"{platform}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"[COOKIE] Cookie已保存: {platform}")
            return True
            
        except Exception as e:
            logger.error(f"[COOKIE] 保存Cookie失败: {e}")
            return False
    
    def load_cookies(self, platform: str) -> Optional[Dict[str, str]]:
        """
        加载Cookie
        
        Args:
            platform: 平台标识
            
        Returns:
            Cookie字典，失败返回None
        """
        try:
            file_path = self.cookies_dir / f"{platform}.json"
            
            if not file_path.exists():
                logger.warning(f"[COOKIE] Cookie文件不存在: {platform}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 解密Cookie
            cookies = self.decrypt_cookies(data['cookies'])
            
            if cookies:
                # 更新使用时间
                data['updated_at'] = datetime.now().isoformat()
                data['last_used_at'] = datetime.now().isoformat()
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            
            return cookies
            
        except Exception as e:
            logger.error(f"[COOKIE] 加载Cookie失败: {e}")
            return None
    
    def get_cookie_info(self, platform: str) -> Optional[Dict[str, Any]]:
        """
        获取Cookie信息
        
        Args:
            platform: 平台标识
            
        Returns:
            Cookie信息字典
        """
        try:
            file_path = self.cookies_dir / f"{platform}.json"
            
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 解密并验证
            cookies = self.decrypt_cookies(data['cookies'])
            is_valid = cookies is not None and self._verify_checksum(cookies, data['checksum'])
            
            return {
                'platform': data['platform'],
                'user_id': data.get('user_id'),
                'metadata': data.get('metadata', {}),
                'created_at': data.get('created_at'),
                'updated_at': data.get('updated_at'),
                'last_used_at': data.get('last_used_at'),
                'is_valid': is_valid,
                'cookie_count': len(cookies) if cookies else 0,
            }
            
        except Exception as e:
            logger.error(f"[COOKIE] 获取Cookie信息失败: {e}")
            return None
    
    def delete_cookies(self, platform: str) -> bool:
        """
        删除Cookie
        
        Args:
            platform: 平台标识
            
        Returns:
            是否成功
        """
        try:
            file_path = self.cookies_dir / f"{platform}.json"
            
            if file_path.exists():
                file_path.unlink()
                logger.info(f"[COOKIE] Cookie已删除: {platform}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"[COOKIE] 删除Cookie失败: {e}")
            return False
    
    def list_cookies(self) -> List[Dict[str, Any]]:
        """
        列出所有保存的Cookie
        
        Returns:
            Cookie信息列表
        """
        cookies_list = []
        
        for file_path in self.cookies_dir.glob("*.json"):
            platform = file_path.stem
            info = self.get_cookie_info(platform)
            if info:
                cookies_list.append(info)
        
        return cookies_list
    
    def validate_cookies(
        self,
        platform: str,
        validator: callable
    ) -> bool:
        """
        验证Cookie有效性
        
        Args:
            platform: 平台标识
            validator: 验证函数，接收cookies字典，返回是否有效
            
        Returns:
            是否有效
        """
        cookies = self.load_cookies(platform)
        
        if not cookies:
            return False
        
        return validator(cookies)
    
    def refresh_cookies(
        self,
        platform: str,
        refresh_func: callable
    ) -> bool:
        """
        刷新Cookie
        
        Args:
            platform: 平台标识
            refresh_func: 刷新函数，返回新的Cookie字典
            
        Returns:
            是否刷新成功
        """
        try:
            new_cookies = refresh_func()
            
            if new_cookies:
                self.save_cookies(platform, new_cookies)
                logger.info(f"[COOKIE] Cookie已刷新: {platform}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"[COOKIE] 刷新Cookie失败: {e}")
            return False
    
    def get_all_platforms(self) -> List[str]:
        """
        获取所有已保存的平台
        
        Returns:
            平台列表
        """
        return [f.stem for f in self.cookies_dir.glob("*.json")]
    
    def _generate_checksum(self, cookies: Dict[str, str]) -> str:
        """
        生成Cookie校验和
        
        Args:
            cookies: Cookie字典
            
        Returns:
            校验和
        """
        cookie_str = json.dumps(cookies, sort_keys=True)
        return hashlib.md5(cookie_str.encode()).hexdigest()
    
    def _verify_checksum(
        self,
        cookies: Dict[str, str],
        checksum: str
    ) -> bool:
        """
        验证Cookie校验和
        
        Args:
            cookies: Cookie字典
            checksum: 校验和
            
        Returns:
            是否匹配
        """
        return self._generate_checksum(cookies) == checksum
    
    def merge_cookies(
        self,
        primary: Dict[str, str],
        secondary: Dict[str, str]
    ) -> Dict[str, str]:
        """
        合并Cookie
        
        Args:
            primary: 主Cookie
            secondary: 次Cookie
            
        Returns:
            合并后的Cookie
        """
        merged = primary.copy()
        merged.update(secondary)
        return merged
    
    def extract_cookies(
        self,
        raw_cookies: str,
        required_keys: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """
        从原始字符串提取Cookie
        
        Args:
            raw_cookies: 原始Cookie字符串（如 "key1=value1; key2=value2"）
            required_keys: 必需的Cookie键
            
        Returns:
            Cookie字典
        """
        cookies = {}
        
        for item in raw_cookies.split(';'):
            item = item.strip()
            if '=' in item:
                key, value = item.split('=', 1)
                cookies[key.strip()] = value.strip()
        
        # 如果指定了必需键，过滤
        if required_keys:
            cookies = {k: v for k, v in cookies.items() if k in required_keys}
        
        return cookies
    
    def export_cookies(
        self,
        platform: str,
        format: str = 'json'  # json, netscape, plain
    ) -> str:
        """
        导出Cookie
        
        Args:
            platform: 平台标识
            format: 导出格式
            
        Returns:
            格式化后的Cookie字符串
        """
        cookies = self.load_cookies(platform)
        
        if not cookies:
            return ""
        
        if format == 'json':
            return json.dumps(cookies, ensure_ascii=False, indent=2)
        
        elif format == 'netscape':
            lines = ["# Netscape HTTP Cookie File"]
            for key, value in cookies.items():
                lines.append(f"\t".join([
                    'FALSE', '/', 'FALSE', '0', key, value
                ]))
            return "\n".join(lines)
        
        elif format == 'plain':
            return '; '.join(f"{k}={v}" for k, v in cookies.items())
        
        else:
            return json.dumps(cookies)


class SessionManager:
    """会话管理器"""
    
    def __init__(self):
        """初始化会话管理器"""
        self.sessions_dir = Path("data/sessions")
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        
        self.cookie_manager = CookieManager()
        
        logger.info("[SESSION] 会话管理器已初始化")
    
    def create_session(
        self,
        platform: str,
        session_name: str,
        cookies: Dict[str, str],
        local_storage: Optional[Dict[str, str]] = None,
        session_storage: Optional[Dict[str, str]] = None,
        user_agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        创建会话
        
        Args:
            platform: 平台标识
            session_name: 会话名称
            cookies: Cookie字典
            local_storage: Local Storage数据
            session_storage: Session Storage数据
            user_agent: User-Agent
            metadata: 元数据
            
        Returns:
            是否成功
        """
        session_data = {
            'platform': platform,
            'session_name': session_name,
            'cookies': self.cookie_manager.encrypt_cookies(cookies),
            'local_storage': local_storage or {},
            'session_storage': session_storage or {},
            'user_agent': user_agent,
            'metadata': metadata or {},
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(hours=settings.app.session_expire_hours)).isoformat(),
            'is_valid': True,
        }
        
        try:
            file_path = self.sessions_dir / f"{platform}_{session_name}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"[SESSION] 会话已创建: {platform}/{session_name}")
            return True
            
        except Exception as e:
            logger.error(f"[SESSION] 创建会话失败: {e}")
            return False
    
    def load_session(
        self,
        platform: str,
        session_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        加载会话
        
        Args:
            platform: 平台标识
            session_name: 会话名称
            
        Returns:
            会话数据，失败返回None
        """
        try:
            file_path = self.sessions_dir / f"{platform}_{session_name}.json"
            
            if not file_path.exists():
                logger.warning(f"[SESSION] 会话文件不存在: {platform}/{session_name}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # 检查是否过期
            expires_at = datetime.fromisoformat(session_data['expires_at'])
            if expires_at < datetime.now():
                logger.warning(f"[SESSION] 会话已过期: {platform}/{session_name}")
                session_data['is_valid'] = False
                return session_data
            
            # 解密Cookie
            cookies = self.cookie_manager.decrypt_cookies(session_data['cookies'])
            session_data['decrypted_cookies'] = cookies
            
            return session_data
            
        except Exception as e:
            logger.error(f"[SESSION] 加载会话失败: {e}")
            return None
    
    def delete_session(self, platform: str, session_name: str) -> bool:
        """
        删除会话
        
        Args:
            platform: 平台标识
            session_name: 会话名称
            
        Returns:
            是否成功
        """
        try:
            file_path = self.sessions_dir / f"{platform}_{session_name}.json"
            
            if file_path.exists():
                file_path.unlink()
                logger.info(f"[SESSION] 会话已删除: {platform}/{session_name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"[SESSION] 删除会话失败: {e}")
            return False
    
    def list_sessions(self, platform: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        列出所有会话
        
        Args:
            platform: 平台筛选（可选）
            
        Returns:
            会话信息列表
        """
        sessions = []
        
        for file_path in self.sessions_dir.glob("*.json"):
            info = self.get_session_info(file_path.stem)
            if info and (platform is None or info['platform'] == platform):
                sessions.append(info)
        
        return sessions
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        获取会话信息
        
        Args:
            session_id: 会话ID (platform_sessionname)
            
        Returns:
            会话信息
        """
        try:
            file_path = self.sessions_dir / f"{session_id}.json"
            
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 检查有效期
            expires_at = datetime.fromisoformat(data['expires_at'])
            is_valid = data['is_valid'] and expires_at > datetime.now()
            
            return {
                'session_id': session_id,
                'platform': data['platform'],
                'session_name': data['session_name'],
                'user_agent': data.get('user_agent'),
                'metadata': data.get('metadata', {}),
                'created_at': data.get('created_at'),
                'expires_at': data.get('expires_at'),
                'is_valid': is_valid,
                'cookie_count': len(data.get('local_storage', {})) + len(data.get('session_storage', {})),
            }
            
        except Exception as e:
            logger.error(f"[SESSION] 获取会话信息失败: {e}")
            return None
    
    def cleanup_expired_sessions(self) -> int:
        """
        清理过期会话
        
        Returns:
            清理的会话数量
        """
        count = 0
        
        for file_path in self.sessions_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                expires_at = datetime.fromisoformat(data['expires_at'])
                
                if expires_at < datetime.now():
                    file_path.unlink()
                    count += 1
                    
            except Exception:
                continue
        
        logger.info(f"[SESSION] 清理了 {count} 个过期会话")
        return count

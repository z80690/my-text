# -*- coding: utf-8 -*-
"""
项目配置模块
Project Configuration Module

负责加载和管理所有配置项
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field


class DatabaseConfig(BaseModel):
    """数据库配置"""
    supabase_url: str = ""
    supabase_key: str = ""
    supabase_service_key: str = ""
    supabase_jwt_secret: str = ""
    
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = ""


class BilibiliConfig(BaseModel):
    """哔哩哔哩配置"""
    cookies_file: str = "data/bilibili_cookies.json"
    login_method: str = "qrcode"  # qrcode, password, sms
    save_path: str = "data/bilibili/"
    api_base: str = "https://api.bilibili.com"
    passport_api: str = "https://passport.bilibili.com"
    proxy: Optional[str] = None


class ToutiaoConfig(BaseModel):
    """今日头条配置"""
    cookies_file: str = "data/toutiao_cookies.json"
    login_method: str = "qrcode"
    save_path: str = "data/toutiao/"
    api_base: str = "https://www.toutiao.com"
    api_v2: str = "https://www.toutiao.com/api"
    proxy: Optional[str] = None


class AppConfig(BaseModel):
    """应用配置"""
    host: str = "0.0.0.0"
    port: int = 8080
    environment: str = "development"
    debug: bool = True
    
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    
    session_secret: str = "your-session-secret-key-change-in-production"
    session_expire_hours: int = 24
    
    encryption_key: str = "your-encryption-key-32-chars"
    
    http_proxy: Optional[str] = None
    https_proxy: Optional[str] = None
    
    request_delay: float = 1.0
    max_retries: int = 3
    timeout: int = 30
    
    captcha_api_key: Optional[str] = None
    captcha_api_url: Optional[str] = None


class Settings:
    """全局配置单例"""
    
    _instance: Optional['Settings'] = None
    _loaded: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._loaded:
            self._load_config()
            Settings._loaded = True
    
    def _load_config(self):
        """加载配置文件"""
        # 加载环境变量
        env_path = Path(__file__).parent.parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)
        
        # 数据库配置
        self.database = DatabaseConfig(
            supabase_url=os.getenv("SUPABASE_URL", ""),
            supabase_key=os.getenv("SUPABASE_KEY", ""),
            supabase_service_key=os.getenv("SUPABASE_SERVICE_KEY", ""),
            supabase_jwt_secret=os.getenv("SUPABASE_JWT_SECRET", ""),
            neo4j_uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            neo4j_user=os.getenv("NEO4J_USER", "neo4j"),
            neo4j_password=os.getenv("NEO4J_PASSWORD", ""),
        )
        
        # 哔哩哔哩配置
        self.bilibili = BilibiliConfig(
            cookies_file=os.getenv("BILIBILI_COOKIES_FILE", "data/bilibili_cookies.json"),
            login_method=os.getenv("BILIBILI_LOGIN_METHOD", "qrcode"),
            save_path=os.getenv("BILIBILI_SAVE_PATH", "data/bilibili/"),
            api_base=os.getenv("BILIBILI_API_BASE", "https://api.bilibili.com"),
            passport_api=os.getenv("BILIBILI_PASSPORT_API", "https://passport.bilibili.com"),
            proxy=os.getenv("BILIBILI_PROXY"),
        )
        
        # 今日头条配置
        self.toutiao = ToutiaoConfig(
            cookies_file=os.getenv("TOUTIAO_COOKIES_FILE", "data/toutiao_cookies.json"),
            login_method=os.getenv("TOUTIAO_LOGIN_METHOD", "qrcode"),
            save_path=os.getenv("TOUTIAO_SAVE_PATH", "data/toutiao/"),
            api_base=os.getenv("TOUTIAO_API_BASE", "https://www.toutiao.com"),
            api_v2=os.getenv("TOUTIAO_API_V2", "https://www.toutiao.com/api"),
            proxy=os.getenv("TOUTIAO_PROXY"),
        )
        
        # 应用配置
        self.app = AppConfig(
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", 8080)),
            environment=os.getenv("ENVIRONMENT", "development"),
            debug=os.getenv("DEBUG", "True").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_file=os.getenv("LOG_FILE", "logs/app.log"),
            session_secret=os.getenv("SESSION_SECRET", "your-session-secret-key-change-in-production"),
            session_expire_hours=int(os.getenv("SESSION_EXPIRE_HOURS", 24)),
            encryption_key=os.getenv("ENCRYPTION_KEY", "your-encryption-key-32-chars"),
            http_proxy=os.getenv("HTTP_PROXY"),
            https_proxy=os.getenv("HTTPS_PROXY"),
            request_delay=float(os.getenv("REQUEST_DELAY", 1.0)),
            max_retries=int(os.getenv("MAX_RETRIES", 3)),
            timeout=int(os.getenv("TIMEOUT", 30)),
            captcha_api_key=os.getenv("CAPTCHA_API_KEY"),
            captcha_api_url=os.getenv("CAPTCHA_API_URL"),
        )
    
    def validate(self) -> bool:
        """验证配置是否完整"""
        required_fields = [
            (self.database.supabase_url, "SUPABASE_URL"),
            (self.database.supabase_key, "SUPABASE_KEY"),
        ]
        
        missing = []
        for value, name in required_fields:
            if not value or value.startswith("your-"):
                missing.append(name)
        
        if missing:
            print(f"[WARNING] 缺少配置: {', '.join(missing)}")
            return False
        return True


# 全局配置实例
settings = Settings()

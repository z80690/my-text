# -*- coding: utf-8 -*-
"""
今日头条登录模块
Toutiao Login Module

提供多种登录方式：扫码登录、密码登录
"""

import json
import time
import qrcode
from pathlib import Path
from typing import Optional, Dict, Any, Callable, Tuple
from io import BytesIO
import base64
from PIL import Image
from loguru import logger

from playwright.sync_api import sync_playwright, Playwright, Browser, BrowserContext, Page

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import settings
from .toutiao_client import ToutiaoClient


class ToutiaoLogin:
    """今日头条登录管理器"""
    
    # 登录URL
    LOGIN_URL = "https://www.toutiao.com/login/"
    QRCODE_URL = "https://www.toutiao.com/login/qrcode/"
    
    def __init__(
        self,
        cookies_file: Optional[str] = None,
        headless: bool = True,
        browser_type: str = 'chromium'
    ):
        """
        初始化登录管理器
        
        Args:
            cookies_file: Cookie保存文件路径
            headless: 是否headless模式运行
            browser_type: 浏览器类型 (chromium, firefox, webkit)
        """
        self.cookies_file = cookies_file or settings.toutiao.cookies_file
        self.headless = headless
        self.browser_type = browser_type
        
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        self.client = ToutiaoClient()
        
        # 确保目录存在
        Path(self.cookies_file).parent.mkdir(parents=True, exist_ok=True)
    
    def __enter__(self):
        """上下文管理器入口"""
        self.init_browser()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
    
    def init_browser(self) -> None:
        """初始化浏览器"""
        self.playwright = sync_playwright().start()
        
        if self.browser_type == 'chromium':
            self.browser = self.playwright.chromium.launch(headless=self.headless)
        elif self.browser_type == 'firefox':
            self.browser = self.playwright.firefox.launch(headless=self.headless)
        elif self.browser_type == 'webkit':
            self.browser = self.playwright.webkit.launch(headless=self.headless)
        else:
            raise ValueError(f"不支持的浏览器类型: {self.browser_type}")
        
        # 创建浏览器上下文
        self.context = self.browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='zh-CN',
        )
        
        self.page = self.context.new_page()
        logger.info(f"[TOUTIAO] 浏览器已初始化: {self.browser_type}")
    
    def close(self) -> None:
        """关闭浏览器"""
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        
        self.context = None
        self.browser = None
        self.playwright = None
        self.page = None
        logger.info("[TOUTIAO] 浏览器已关闭")
    
    # ==================== Cookie管理 ====================
    
    def save_cookies(self, cookies: Optional[Dict[str, str]] = None) -> bool:
        """
        保存Cookie到文件
        
        Args:
            cookies: Cookie字典，为空则使用当前cookies
            
        Returns:
            是否保存成功
        """
        try:
            cookies_to_save = cookies or self.get_cookies()
            
            # 提取关键Cookie
            essential_cookies = {}
            for key in ToutiaoClient.REQUIRED_COOKIES:
                if key in cookies_to_save:
                    essential_cookies[key] = cookies_to_save[key]
            
            with open(self.cookies_file, 'w', encoding='utf-8') as f:
                json.dump(essential_cookies, f, ensure_ascii=False, indent=2)
            
            logger.info(f"[TOUTIAO] Cookie已保存到: {self.cookies_file}")
            return True
        except Exception as e:
            logger.error(f"[TOUTIAO] 保存Cookie失败: {e}")
            return False
    
    def load_cookies(self) -> Optional[Dict[str, str]]:
        """
        从文件加载Cookie
        
        Returns:
            Cookie字典，加载失败返回None
        """
        try:
            if not Path(self.cookies_file).exists():
                logger.warning(f"[TOUTIAO] Cookie文件不存在: {self.cookies_file}")
                return None
            
            with open(self.cookies_file, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            logger.info(f"[TOUTIAO] Cookie已从文件加载")
            return cookies
        except Exception as e:
            logger.error(f"[TOUTIAO] 加载Cookie失败: {e}")
            return None
    
    def get_cookies(self) -> Dict[str, str]:
        """
        获取当前浏览器Cookie
        
        Returns:
            Cookie字典
        """
        if not self.context:
            return {}
        
        cookies = self.context.cookies()
        return {c['name']: c['value'] for c in cookies}
    
    # ==================== 扫码登录 ====================
    
    def login_with_qrcode(
        self,
        show_qrcode: bool = True,
        timeout: int = 120,
        callback: Optional[Callable[[str], None]] = None
    ) -> Tuple[bool, Dict[str, str]]:
        """
        扫码登录
        
        Args:
            show_qrcode: 是否显示二维码(控制台打印base64)
            timeout: 超时时间(秒)
            callback: 回调函数，用于自定义二维码显示
            
        Returns:
            (是否成功, Cookie字典)
        """
        logger.info("[TOUTIAO] 开始扫码登录...")
        
        try:
            # 访问登录页面
            self.page.goto(self.LOGIN_URL)
            time.sleep(2)
            
            # 点击切换到扫码登录
            qrcode_tab = self.page.locator('text=扫码登录')
            if qrcode_tab.count() > 0:
                qrcode_tab.click()
                time.sleep(1)
            
            # 获取二维码图片
            qrcode_element = self.page.locator('.qrcode-img img, .qrcode img')
            
            if qrcode_element.count() > 0:
                qrcode_src = qrcode_element.get_attribute('src')
                logger.info("[TOUTIAO] 已显示二维码，请使用头条App扫描")
                
                if show_qrcode or callback:
                    self._display_qrcode(qrcode_src, callback)
                
                # 等待登录成功
                try:
                    self.page.wait_for_url('**/www.toutiao.com/**', timeout=timeout*1000)
                except Exception as e:
                    logger.warning(f"[TOUTIAO] 等待登录超时: {e}")
                
                cookies = self.get_cookies()
                self.save_cookies(cookies)
                
                logger.info("[TOUTIAO] 扫码登录成功!")
                return True, cookies
            else:
                logger.error("[TOUTIAO] 未找到二维码元素")
                return False, {}
                
        except Exception as e:
            logger.error(f"[TOUTIAO] 扫码登录失败: {e}")
            return False, {}
    
    def _display_qrcode(
        self,
        url: str,
        callback: Optional[Callable[[str], None]] = None
    ) -> None:
        """
        显示二维码
        
        Args:
            url: 二维码URL
            callback: 回调函数
        """
        try:
            # 如果是相对URL，添加前缀
            if url.startswith('//'):
                url = 'https:' + url
            
            # 生成二维码
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # 转换为base64
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            qrcode_b64 = base64.b64encode(buffered.getvalue()).decode()
            
            if callback:
                callback(qrcode_b64)
            else:
                # 控制台打印
                print("\n" + "="*50)
                print("请扫描下方二维码进行登录:")
                print("="*50)
                print(f"\n[二维码Base64长度: {len(qrcode_b64)}]\n")
                
        except Exception as e:
            logger.error(f"[TOUTIAO] 生成二维码失败: {e}")
    
    # ==================== 密码登录 ====================
    
    def login_with_password(
        self,
        username: str,
        password: str,
        timeout: int = 60
    ) -> Tuple[bool, Dict[str, str]]:
        """
        密码登录
        
        Args:
            username: 用户名(手机号)
            password: 密码
            timeout: 超时时间(秒)
            
        Returns:
            (是否成功, Cookie字典)
        """
        logger.info("[TOUTIAO] 开始密码登录...")
        
        try:
            self.page.goto(self.LOGIN_URL)
            time.sleep(1)
            
            # 切换到密码登录
            password_tab = self.page.locator('text=密码登录')
            if password_tab.count() > 0:
                password_tab.click()
                time.sleep(0.5)
            
            # 输入手机号
            self.page.fill('input[type="text"], input[type="tel"]', username)
            time.sleep(0.5)
            
            # 输入密码
            self.page.fill('input[type="password"]', password)
            time.sleep(0.5)
            
            # 点击登录按钮
            login_button = self.page.locator('button[type="submit"], .login-btn')
            if login_button.count() > 0:
                login_button.click()
                time.sleep(2)
            
            # 等待登录完成
            try:
                self.page.wait_for_url('**/www.toutiao.com/**', timeout=timeout*1000)
            except:
                # 检查是否登录失败
                error_elements = self.page.locator('.error-message, .error-tip')
                if error_elements.count() > 0:
                    error_msg = error_elements.text_content()
                    logger.error(f"[TOUTIAO] 登录失败: {error_msg}")
            
            cookies = self.get_cookies()
            self.save_cookies(cookies)
            
            logger.info("[TOUTIAO] 密码登录成功!")
            return True, cookies
            
        except Exception as e:
            logger.error(f"[TOUTIAO] 密码登录失败: {e}")
            return False, {}
    
    # ==================== 快捷登录方法 ====================
    
    def auto_login(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        method: str = 'auto'
    ) -> Tuple[bool, Dict[str, str]]:
        """
        自动登录
        
        Args:
            username: 用户名（密码登录时需要）
            password: 密码（密码登录时需要）
            method: 登录方式 ('qrcode', 'password', 'auto', 'cookie')
            
        Returns:
            (是否成功, Cookie字典)
        """
        # 1. 尝试加载已保存的Cookie
        if method in ['auto', 'cookie']:
            cookies = self.load_cookies()
            if cookies:
                self.client.set_cookies(cookies)
                if self.client.is_logged_in():
                    logger.info("[TOUTIAO] Cookie登录成功")
                    return True, cookies
        
        # 2. 确保浏览器已初始化
        if not self.browser:
            self.init_browser()
        
        # 3. 根据方法登录
        if method == 'qrcode':
            return self.login_with_qrcode()
        elif method == 'password':
            if not username or not password:
                logger.error("[TOUTIAO] 密码登录需要提供用户名和密码")
                return False, {}
            return self.login_with_password(username, password)
        elif method == 'auto':
            # 优先尝试扫码登录
            success, cookies = self.login_with_qrcode(timeout=60)
            if not success:
                # 扫码失败，尝试密码登录
                if username and password:
                    success, cookies = self.login_with_password(username, password)
            return success, cookies
        else:
            logger.error(f"[TOUTIAO] 不支持的登录方式: {method}")
            return False, {}
    
    def logout(self) -> bool:
        """
        退出登录
        
        Returns:
            是否成功
        """
        try:
            # 清除Cookie
            if self.context:
                self.context.clear_cookies()
            
            # 删除Cookie文件
            if Path(self.cookies_file).exists():
                Path(self.cookies_file).unlink()
                logger.info("[TOUTIAO] 已退出登录")
            
            return True
        except Exception as e:
            logger.error(f"[TOUTIAO] 退出登录失败: {e}")
            return False
    
    def get_client(self) -> ToutiaoClient:
        """
        获取已登录的API客户端
        
        Returns:
            ToutiaoClient实例
        """
        cookies = self.load_cookies()
        if cookies:
            self.client.set_cookies(cookies)
        return self.client


# ==================== 便捷函数 ====================

def login(
    cookies_file: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    method: str = 'auto'
) -> ToutiaoClient:
    """
    便捷登录函数
    
    Args:
        cookies_file: Cookie文件路径
        username: 用户名
        password: 密码
        method: 登录方式
        
    Returns:
        ToutiaoClient实例
    """
    login_manager = ToutiaoLogin(cookies_file=cookies_file, headless=False)
    success, _ = login_manager.auto_login(username, password, method)
    
    if success:
        return login_manager.get_client()
    else:
        raise Exception("登录失败")

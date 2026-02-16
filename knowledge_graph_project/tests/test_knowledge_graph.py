# -*- coding: utf-8 -*-
"""
知识图谱数据库项目测试
Knowledge Graph Database Project Tests

测试用例和验证脚本
"""

import json
import sys
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings


# ==================== 测试配置 ====================

class TestConfig:
    """配置测试"""
    
    @staticmethod
    def test_settings_loading():
        """测试配置加载"""
        print("[TEST] 测试配置加载...")
        
        assert settings is not None
        assert settings.app is not None
        assert settings.database is not None
        assert settings.bilibili is not None
        assert settings.toutiao is not None
        
        print("[PASS] 配置加载正常")
        return True
    
    @staticmethod
    def test_settings_validation():
        """测试配置验证"""
        print("[TEST] 测试配置验证...")
        
        # 检查关键配置
        assert settings.database.supabase_url is not None
        assert settings.database.supabase_key is not None
        
        print("[PASS] 配置验证通过")
        return True


# ==================== 测试Cookie管理 ====================

class TestCookieManager:
    """Cookie管理器测试"""
    
    @staticmethod
    def test_cookie_manager_init():
        """测试Cookie管理器初始化"""
        print("[TEST] 测试Cookie管理器初始化...")
        
        from auth.cookie_manager import CookieManager
        
        manager = CookieManager()
        assert manager is not None
        assert manager.fernet is not None
        
        print("[PASS] Cookie管理器初始化正常")
        return True
    
    @staticmethod
    def test_cookie_encrypt_decrypt():
        """测试Cookie加密解密"""
        print("[TEST] 测试Cookie加密解密...")
        
        from auth.cookie_manager import CookieManager
        
        manager = CookieManager()
        
        # 测试数据
        test_cookies = {
            'SESSDATA': 'test_sessdata',
            'bili_jct': 'test_bili_jct',
            'DedeUserID': '123456',
            'DedeUserID__ckMd5': 'abcdef',
            'sid': 'session123'
        }
        
        # 加密
        encrypted = manager.encrypt_cookies(test_cookies)
        assert encrypted is not None
        assert encrypted != json.dumps(test_cookies)
        
        # 解密
        decrypted = manager.decrypt_cookies(encrypted)
        assert decrypted == test_cookies
        
        print("[PASS] Cookie加密解密正常")
        return True
    
    @staticmethod
    def test_cookie_save_load():
        """测试Cookie保存加载"""
        print("[TEST] 测试Cookie保存加载...")
        
        from auth.cookie_manager import CookieManager
        
        manager = CookieManager()
        
        test_cookies = {
            'test_key': 'test_value',
            'session': 'session_value'
        }
        
        # 保存
        save_result = manager.save_cookies('test_platform', test_cookies)
        assert save_result is True
        
        # 加载
        loaded_cookies = manager.load_cookies('test_platform')
        assert loaded_cookies == test_cookies
        
        # 清理
        manager.delete_cookies('test_platform')
        
        print("[PASS] Cookie保存加载正常")
        return True
    
    @staticmethod
    def test_checksum():
        """测试校验和"""
        print("[TEST] 测试校验和...")
        
        from auth.cookie_manager import CookieManager
        
        manager = CookieManager()
        
        cookies1 = {'key': 'value'}
        cookies2 = {'key': 'value'}
        cookies3 = {'key': 'different'}
        
        checksum1 = manager._generate_checksum(cookies1)
        checksum2 = manager._generate_checksum(cookies2)
        checksum3 = manager._generate_checksum(cookies3)
        
        assert checksum1 == checksum2
        assert checksum1 != checksum3
        
        assert manager._verify_checksum(cookies1, checksum1) is True
        assert manager._verify_checksum(cookies3, checksum1) is False
        
        print("[PASS] 校验和功能正常")
        return True


# ==================== 测试平台客户端 ====================

class TestPlatformClients:
    """平台客户端测试"""
    
    @staticmethod
    def test_bilibili_client_init():
        """测试B站客户端初始化"""
        print("[TEST] 测试B站客户端初始化...")
        
        from platforms.bilibili import BilibiliClient
        
        # 无Cookie初始化
        client = BilibiliClient()
        assert client is not None
        assert client.session is not None
        
        # 带Cookie初始化
        cookies = {'SESSDATA': 'test', 'bili_jct': 'test'}
        client = BilibiliClient(cookies=cookies)
        assert client.cookies == cookies
        
        print("[PASS] B站客户端初始化正常")
        return True
    
    @staticmethod
    def test_bilibili_cookies():
        """测试B站Cookie管理"""
        print("[TEST] 测试B站Cookie管理...")
        
        from platforms.bilibili import BilibiliClient
        
        client = BilibiliClient()
        
        # 设置Cookie
        test_cookies = {'SESSDATA': 'test123', 'bili_jct': 'abc'}
        client.set_cookies(test_cookies)
        
        # 获取Cookie
        cookies = client.get_cookies()
        assert cookies['SESSDATA'] == 'test123'
        assert cookies['bili_jct'] == 'abc'
        
        # 检查必要字段
        assert all(k in client.REQUIRED_COOKIES for k in client.REQUIRED_COOKIES)
        
        print("[PASS] B站Cookie管理正常")
        return True
    
    @staticmethod
    def test_toutiao_client_init():
        """测试头条客户端初始化"""
        print("[TEST] 测试头条客户端初始化...")
        
        from platforms.toutiao import ToutiaoClient
        
        # 无Cookie初始化
        client = ToutiaoClient()
        assert client is not None
        assert client.session is not None
        
        # 带Cookie初始化
        cookies = {'tt_webid': 'test', 'csrftoken': 'test'}
        client = ToutiaoClient(cookies=cookies)
        assert client.cookies == cookies
        
        print("[PASS] 头条客户端初始化正常")
        return True
    
    @staticmethod
    def test_toutiao_cookies():
        """测试头条Cookie管理"""
        print("[TEST] 测试头条Cookie管理...")
        
        from platforms.toutiao import ToutiaoClient
        
        client = ToutiaoClient()
        
        # 设置Cookie
        test_cookies = {'tt_webid': 'test123', 'csrftoken': 'abc'}
        client.set_cookies(test_cookies)
        
        # 获取Cookie
        cookies = client.get_cookies()
        assert cookies['tt_webid'] == 'test123'
        assert cookies['csrftoken'] == 'abc'
        
        print("[PASS] 头条Cookie管理正常")
        return True


# ==================== 测试数据模型 ====================

class TestDataModels:
    """数据模型测试"""
    
    @staticmethod
    def test_user_model():
        """测试用户模型"""
        print("[TEST] 测试用户模型...")
        
        from database.models import User, UserCreate, UserStatus
        
        # 创建用户
        user_data = {
            'external_user_id': '123456',
            'username': 'testuser',
            'display_name': '测试用户',
            'avatar_url': 'https://example.com/avatar.jpg',
            'bio': '这是测试用户',
            'is_verified': False,
            'level': 5,
            'follower_count': 1000,
            'following_count': 500,
        }
        
        user = User(**user_data)
        assert user.external_user_id == '123456'
        assert user.username == 'testuser'
        assert user.status == UserStatus.ACTIVE
        
        print("[PASS] 用户模型正常")
        return True
    
    @staticmethod
    def test_content_model():
        """测试内容模型"""
        print("[TEST] 测试内容模型...")
        
        from database.models import Content, ContentType
        
        content_data = {
            'external_content_id': 'BV123456',
            'content_type': ContentType.VIDEO,
            'title': '测试视频',
            'description': '这是一个测试视频',
            'view_count': 10000,
            'like_count': 500,
            'comment_count': 100,
            'tags': ['测试', '科技', '编程'],
        }
        
        content = Content(**content_data)
        assert content.external_content_id == 'BV123456'
        assert content.content_type == ContentType.VIDEO
        assert len(content.tags) == 3
        
        print("[PASS] 内容模型正常")
        return True
    
    @staticmethod
    def test_relation_model():
        """测试关系模型"""
        print("[TEST] 测试关系模型...")
        
        from database.models import Relation, RelationType
        from uuid import uuid4
        
        source_id = uuid4()
        target_id = uuid4()
        
        relation_data = {
            'relation_type': RelationType.FOLLOWS,
            'source_entity_type': 'user',
            'source_entity_id': source_id,
            'target_entity_type': 'user',
            'target_entity_id': target_id,
            'weight': 1.0,
        }
        
        relation = Relation(**relation_data)
        assert relation.relation_type == RelationType.FOLLOWS
        assert relation.weight == 1.0
        
        print("[PASS] 关系模型正常")
        return True
    
    @staticmethod
    def test_platform_enum():
        """测试平台枚举"""
        print("[TEST] 测试平台枚举...")
        
        from database.models import PlatformType
        
        assert PlatformType.BILIBILI.value == 'bilibili'
        assert PlatformType.TOUTIAO.value == 'toutiao'
        assert PlatformType.OTHER.value == 'other'
        
        print("[PASS] 平台枚举正常")
        return True


# ==================== 测试会话管理 ====================

class TestSessionManager:
    """会话管理器测试"""
    
    @staticmethod
    def test_session_manager_init():
        """测试会话管理器初始化"""
        print("[TEST] 测试会话管理器初始化...")
        
        from auth.cookie_manager import SessionManager
        
        manager = SessionManager()
        assert manager is not None
        assert manager.cookie_manager is not None
        
        print("[PASS] 会话管理器初始化正常")
        return True
    
    @staticmethod
    def test_session_create_load():
        """测试会话创建加载"""
        print("[TEST] 测试会话创建加载...")
        
        from auth.cookie_manager import SessionManager
        
        manager = SessionManager()
        
        # 创建会话
        test_cookies = {'session': 'test123'}
        result = manager.create_session(
            platform='test',
            session_name='test_session',
            cookies=test_cookies,
            user_agent='Test User Agent',
            metadata={'note': 'test'}
        )
        assert result is True
        
        # 加载会话
        session = manager.load_session('test', 'test_session')
        assert session is not None
        assert session['decrypted_cookies'] == test_cookies
        assert session['user_agent'] == 'Test User Agent'
        
        # 清理
        manager.delete_session('test', 'test_session')
        
        print("[PASS] 会话创建加载正常")
        return True


# ==================== 测试运行器 ====================

def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("知识图谱数据库项目 - 测试套件")
    print("=" * 60 + "\n")
    
    test_classes = [
        TestConfig,
        TestCookieManager,
        TestPlatformClients,
        TestDataModels,
        TestSessionManager,
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    for test_class in test_classes:
        print(f"\n{'='*40}")
        print(f"测试类: {test_class.__name__}")
        print(f"{'='*40}")
        
        methods = [m for m in dir(test_class) if m.startswith('test_')]
        
        for method_name in methods:
            total_tests += 1
            try:
                method = getattr(test_class, method_name)
                method()
                passed_tests += 1
                print(f"  ✓ {method_name}")
            except Exception as e:
                failed_tests += 1
                print(f"  ✗ {method_name}")
                print(f"    错误: {e}")
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    print(f"总计: {total_tests} 个测试")
    print(f"通过: {passed_tests} 个")
    print(f"失败: {failed_tests} 个")
    print(f"通过率: {passed_tests/total_tests*100:.1f}%")
    print("=" * 60 + "\n")
    
    return failed_tests == 0


# ==================== 主函数 ====================

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

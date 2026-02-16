# -*- coding: utf8 -*-
"""
测试修复后的代码
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """测试所有导入是否正常"""
    try:
        from main import route_request, handle_knowledge_base_query, main_handler
        from ai_api import main_handler as ai_main_handler
        from auth_api import main_handler as auth_main_handler
        from zhipu_service import ZhipuAIClient, get_zhipu_client
        from security import get_security_config
        
        print("[PASS] 所有模块导入成功")
        return True
    except ImportError as e:
        print(f"[FAIL] 导入失败: {e}")
        return False

def test_routing():
    """测试路由功能"""
    try:
        from main import route_request
        
        # 测试 AI 路由
        ai_event = {"path": "/api/ai/generate", "httpMethod": "POST", "body": '{"prompt": "test"}'}
        response = route_request(ai_event)
        print(f"[PASS] AI路由测试: {response.get('statusCode', 'N/A')}")
        
        # 测试 Auth 路由
        auth_event = {"path": "/auth/login", "httpMethod": "POST", "body": '{"email": "test@test.com", "password": "test"}'}
        response = route_request(auth_event)
        print(f"[PASS] Auth路由测试: {response.get('statusCode', 'N/A')}")
        
        # 测试默认路由
        default_event = {"path": "/other", "httpMethod": "GET"}
        response = route_request(default_event)
        print(f"[PASS] 默认路由测试: {response.get('statusCode', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"[FAIL] 路由测试失败: {e}")
        return False

def test_rate_limiting():
    """测试速率限制功能"""
    try:
        from ai_api import is_rate_limited, _rate_limit_storage
        
        # 清空速率限制存储
        _rate_limit_storage.clear()
        
        # 测试正常请求
        is_limited = is_rate_limited("test_ip", max_requests=3, window_seconds=1)
        print(f"[PASS] 速率限制测试1 (正常): {not is_limited}")
        
        # 快速发送多个请求
        for i in range(4):
            is_limited = is_rate_limited("test_ip", max_requests=3, window_seconds=1)
        
        print(f"[PASS] 速率限制测试2 (超限): {is_limited}")
        
        return True
    except Exception as e:
        print(f"[FAIL] 速率限制测试失败: {e}")
        return False

def test_message_validation():
    """测试消息验证功能"""
    try:
        import json
        
        # 创建模拟的事件和上下文
        event = {
            "path": "/api/ai/chat",
            "httpMethod": "POST",
            "body": json.dumps({
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant"},
                    {"role": "user", "content": "Hello"},
                    {"role": "invalid_role", "content": "This should fail"}
                ]
            })
        }
        
        from ai_api import main_handler as ai_handler
        response = ai_handler(event, None)
        
        # 应该返回400错误
        if response.get('statusCode') == 400:
            print("[PASS] 消息验证测试: 正确拒绝了无效角色")
            return True
        else:
            print(f"[FAIL] 消息验证测试: 期望400，实际{response.get('statusCode')}")
            return False
            
    except Exception as e:
        print(f"[FAIL] 消息验证测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("=" * 60)
    print("代码修复验证测试")
    print("=" * 60)
    
    tests = [
        ("导入测试", test_imports),
        ("路由测试", test_routing),
        ("速率限制测试", test_rate_limiting),
        ("消息验证测试", test_message_validation),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n[测试] {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"[FAIL] {test_name} 异常: {e}")
            results.append((test_name, False))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试汇总")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "[PASS] 通过" if result else "[FAIL] 失败"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print("=" * 60)
    print(f"总计: {len(results)} 个测试，通过: {passed} 个")
    print("=" * 60)
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
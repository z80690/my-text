# -*- coding: utf-8 -*-
"""
认证系统测试脚本

测试用户注册、登录、令牌刷新等功能
"""

import os
import sys
import json
from typing import Dict, Any, Optional
from supabase import create_client, Client


def get_supabase_client() -> Optional[Client]:
    """获取 Supabase 客户端"""
    try:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            print("[ERROR] SUPABASE_URL 或 SUPABASE_KEY 未设置")
            return None
        return create_client(url, key)
    except Exception as e:
        print(f"[ERROR] 无法创建 Supabase 客户端: {str(e)}")
        return None


def test_user_registration(supabase: Client, email: str, password: str) -> Dict[str, Any]:
    """
    测试用户注册

    参数:
        supabase: Supabase 客户端
        email: 测试邮箱
        password: 测试密码

    返回:
        测试结果
    """
    print("\n[TEST] 用户注册")
    print(f"邮箱: {email}")

    try:
        # 尝试注册
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "display_name": "Test User"
                }
            }
        })

        if auth_response.user:
            print(f"✅ 注册成功，用户 ID: {auth_response.user.id}")
            return {
                "test": "user_registration",
                "status": "PASSED",
                "message": "用户注册成功",
                "user_id": auth_response.user.id
            }
        else:
            print("❌ 注册失败: 用户未创建")
            return {
                "test": "user_registration",
                "status": "FAILED",
                "message": "用户创建失败"
            }

    except Exception as e:
        error_msg = str(e)

        # 如果用户已存在，跳过此测试
        if "User already registered" in error_msg:
            print("⚠️  用户已注册，跳过注册测试")
            return {
                "test": "user_registration",
                "status": "SKIPPED",
                "message": "用户已存在"
            }

        print(f"❌ 注册失败: {error_msg}")
        return {
            "test": "user_registration",
            "status": "FAILED",
            "message": error_msg
        }


def test_user_login(supabase: Client, email: str, password: str) -> Dict[str, Any]:
    """
    测试用户登录

    参数:
        supabase: Supabase 客户端
        email: 测试邮箱
        password: 测试密码

    返回:
        测试结果
    """
    print("\n[TEST] 用户登录")
    print(f"邮箱: {email}")

    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        if auth_response.user and auth_response.session:
            access_token = auth_response.session.access_token
            refresh_token = auth_response.session.refresh_token

            print(f"✅ 登录成功，用户 ID: {auth_response.user.id}")
            print(f"访问令牌: {access_token[:30]}...")
            print(f"刷新令牌: {refresh_token[:30]}...")

            return {
                "test": "user_login",
                "status": "PASSED",
                "message": "用户登录成功",
                "user_id": auth_response.user.id,
                "access_token": access_token,
                "refresh_token": refresh_token
            }
        else:
            print("❌ 登录失败")
            return {
                "test": "user_login",
                "status": "FAILED",
                "message": "登录失败"
            }

    except Exception as e:
        print(f"❌ 登录失败: {str(e)}")
        return {
            "test": "user_login",
            "status": "FAILED",
            "message": str(e)
        }


def test_token_refresh(supabase: Client, refresh_token: str) -> Dict[str, Any]:
    """
    测试令牌刷新

    参数:
        supabase: Supabase 客户端
        refresh_token: 刷新令牌

    返回:
        测试结果
    """
    print("\n[TEST] 令牌刷新")
    print(f"刷新令牌: {refresh_token[:30]}...")

    try:
        auth_response = supabase.auth.refresh_session(refresh_token)

        if auth_response.session:
            new_access_token = auth_response.session.access_token
            new_refresh_token = auth_response.session.refresh_token

            print(f"✅ 令牌刷新成功")
            print(f"新访问令牌: {new_access_token[:30]}...")
            print(f"新刷新令牌: {new_refresh_token[:30]}...")

            return {
                "test": "token_refresh",
                "status": "PASSED",
                "message": "令牌刷新成功",
                "new_access_token": new_access_token,
                "new_refresh_token": new_refresh_token
            }
        else:
            print("❌ 令牌刷新失败")
            return {
                "test": "token_refresh",
                "status": "FAILED",
                "message": "令牌刷新失败"
            }

    except Exception as e:
        print(f"❌ 令牌刷新失败: {str(e)}")
        return {
            "test": "token_refresh",
            "status": "FAILED",
            "message": str(e)
        }


def test_user_profile(supabase: Client, user_id: str) -> Dict[str, Any]:
    """
    测试用户资料查询

    参数:
        supabase: Supabase 客户端
        user_id: 用户 ID

    返回:
        测试结果
    """
    print("\n[TEST] 用户资料查询")
    print(f"用户 ID: {user_id}")

    try:
        response = supabase.table("user_profiles").select("*").eq("id", user_id).single().execute()

        if response.data:
            print(f"✅ 资料查询成功")
            print(f"显示名称: {response.data.get('display_name', '')}")
            print(f"创建时间: {response.data.get('created_at')}")

            return {
                "test": "user_profile",
                "status": "PASSED",
                "message": "用户资料查询成功",
                "data": response.data
            }
        else:
            print("❌ 资料查询失败: 未找到用户资料")
            return {
                "test": "user_profile",
                "status": "FAILED",
                "message": "用户资料不存在"
            }

    except Exception as e:
        print(f"❌ 资料查询失败: {str(e)}")
        return {
            "test": "user_profile",
            "status": "FAILED",
            "message": str(e)
        }


def run_auth_tests(test_email: str = "test@example.com", test_password: str = "TestPass123"):
    """
    运行所有认证测试

    参数:
        test_email: 测试邮箱
        test_password: 测试密码

    返回:
        测试结果汇总
    """
    print("=" * 60)
    print("认证系统测试")
    print("=" * 60)

    # 获取 Supabase 客户端
    supabase = get_supabase_client()
    if not supabase:
        return {
            "all_tests_passed": False,
            "message": "无法连接到 Supabase",
            "results": []
        }

    # 运行测试
    test_results = []

    # 测试 1: 用户注册
    result = test_user_registration(supabase, test_email, test_password)
    test_results.append(result)

    # 测试 2: 用户登录
    result = test_user_login(supabase, test_email, test_password)
    test_results.append(result)

    # 如果登录成功，继续其他测试
    if result.get("status") == "PASSED":
        user_id = result.get("user_id")
        refresh_token = result.get("refresh_token")

        # 测试 3: 令牌刷新
        if refresh_token:
            result = test_token_refresh(supabase, refresh_token)
            test_results.append(result)

        # 测试 4: 用户资料查询
        if user_id:
            result = test_user_profile(supabase, user_id)
            test_results.append(result)

    # 计算结果
    passed_count = sum(1 for r in test_results if r.get("status") == "PASSED")
    skipped_count = sum(1 for r in test_results if r.get("status") == "SKIPPED")
    failed_count = sum(1 for r in test_results if r.get("status") == "FAILED")

    # 输出结果
    print("\n" + "=" * 60)
    print("测试汇总")
    print("=" * 60)
    for result in test_results:
        icon = "✅" if result["status"] == "PASSED" else ("⚠️ " if result["status"] == "SKIPPED" else "❌")
        print(f"{icon} {result['test']}: {result['message']}")

    print("=" * 60)
    print(f"总计: {len(test_results)} 个测试")
    print(f"通过: {passed_count}")
    print(f"跳过: {skipped_count}")
    print(f"失败: {failed_count}")
    print("=" * 60)

    all_passed = passed_count > 0 and failed_count == 0
    print(f"总体状态: {'✅ 全部通过' if all_passed else '❌ 存在失败'}")
    print("=" * 60)

    return {
        "all_tests_passed": all_passed,
        "passed_count": passed_count,
        "skipped_count": skipped_count,
        "failed_count": failed_count,
        "total_tests": len(test_results),
        "results": test_results
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='运行认证系统测试')
    parser.add_argument('--email', help='测试邮箱', default='test@example.com')
    parser.add_argument('--password', help='测试密码', default='TestPass123')
    args = parser.parse_args()

    result = run_auth_tests(args.email, args.password)
    sys.exit(0 if result["all_tests_passed"] else 1)

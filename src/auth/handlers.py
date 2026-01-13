# -*- coding: utf-8 -*-
"""
认证端点处理器

提供用户注册、登录、令牌刷新等认证相关的端点处理函数
"""

import os
import json
from typing import Dict, Any
from supabase import create_client, Client
from .utils import (
    validate_password_strength,
    generate_jwt_token,
    verify_jwt_token,
    format_auth_response,
    format_error_response,
    get_token_from_header
)


def get_supabase_client() -> Client:
    """获取 Supabase 客户端"""
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY", "")
    if not url or not key:
        raise ValueError("Supabase URL 或 Key 未配置")
    return create_client(url, key)


def get_jwt_secret() -> str:
    """获取 JWT 密钥"""
    return os.getenv("SUPABASE_JWT_SECRET", "")


def handle_register(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理用户注册

    请求体:
        - email: 邮箱地址
        - password: 密码
        - display_name: 显示名称（可选）

    返回:
        注册结果响应
    """
    try:
        body = json.loads(event.get("body", "{}"))
        email = body.get("email")
        password = body.get("password")
        display_name = body.get("display_name", "")

        # 验证输入
        if not email or not password:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    format_error_response("邮箱和密码不能为空"),
                    ensure_ascii=False
                )
            }

        # 验证邮箱格式
        if "@" not in email or "." not in email:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    format_error_response("邮箱格式无效"),
                    ensure_ascii=False
                )
            }

        # 验证密码强度
        min_length = int(os.getenv("MIN_PASSWORD_LENGTH", "8"))
        valid, msg = validate_password_strength(password, min_length)
        if not valid:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    format_error_response(msg),
                    ensure_ascii=False
                )
            }

        # 创建用户（使用 Supabase Auth）
        supabase = get_supabase_client()
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "display_name": display_name
                }
            }
        })

        if auth_response.user:
            user_id = auth_response.user.id

            return {
                "statusCode": 201,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    {
                        "success": True,
                        "message": "注册成功，请查收验证邮件",
                        "user_id": user_id
                    },
                    ensure_ascii=False
                )
            }
        else:
            raise Exception("用户创建失败")

    except Exception as e:
        error_msg = str(e)

        # 处理已存在的邮箱错误
        if "User already registered" in error_msg or "duplicate" in error_msg.lower():
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    format_error_response("该邮箱已被注册"),
                    ensure_ascii=False
                )
            }

        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                format_error_response(f"注册失败: {error_msg}"),
                ensure_ascii=False
            )
        }


def handle_login(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理用户登录

    请求体:
        - email: 邮箱地址
        - password: 密码

    返回:
        登录结果响应（包含访问令牌和刷新令牌）
    """
    try:
        body = json.loads(event.get("body", "{}"))
        email = body.get("email")
        password = body.get("password")

        # 验证输入
        if not email or not password:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    format_error_response("邮箱和密码不能为空"),
                    ensure_ascii=False
                )
            }

        # 使用 Supabase Auth 登录
        supabase = get_supabase_client()
        auth_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        if auth_response.user and auth_response.session:
            user_id = auth_response.user.id
            access_token = auth_response.session.access_token
            refresh_token = auth_response.session.refresh_token

            # 获取用户资料
            profile_response = supabase.table("user_profiles").select("*").eq("id", user_id).single().execute()

            user_data = {
                "id": user_id,
                "email": auth_response.user.email,
                "display_name": profile_response.data.get("display_name", "") if profile_response.data else ""
            }

            # 更新最后登录时间（通过 RPC 调用）
            try:
                supabase.rpc("update_last_login", {"user_id": user_id}).execute()
            except Exception:
                pass  # 忽略更新失败

            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    format_auth_response(
                        user_id=user_id,
                        access_token=access_token,
                        refresh_token=refresh_token,
                        user_data=user_data
                    ),
                    ensure_ascii=False
                )
            }
        else:
            raise Exception("登录失败")

    except Exception as e:
        error_msg = str(e)

        # 处理认证失败
        if "Invalid login credentials" in error_msg or "email_not_confirmed" in error_msg:
            return {
                "statusCode": 401,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    format_error_response("邮箱或密码错误"),
                    ensure_ascii=False
                )
            }

        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                format_error_response(f"登录失败: {error_msg}"),
                ensure_ascii=False
            )
        }


def handle_refresh_token(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理令牌刷新

    请求体:
        - refresh_token: 刷新令牌

    返回:
        新的访问令牌和刷新令牌
    """
    try:
        body = json.loads(event.get("body", "{}"))
        refresh_token = body.get("refresh_token")

        if not refresh_token:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    format_error_response("缺少刷新令牌"),
                    ensure_ascii=False
                )
            }

        # 使用 Supabase Auth 刷新令牌
        supabase = get_supabase_client()
        auth_response = supabase.auth.refresh_session(refresh_token)

        if auth_response.session:
            user_id = auth_response.session.user.id
            access_token = auth_response.session.access_token
            new_refresh_token = auth_response.session.refresh_token

            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    format_auth_response(
                        user_id=user_id,
                        access_token=access_token,
                        refresh_token=new_refresh_token
                    ),
                    ensure_ascii=False
                )
            }
        else:
            raise Exception("令牌刷新失败")

    except Exception as e:
        return {
            "statusCode": 401,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                format_error_response("刷新令牌无效或已过期"),
                ensure_ascii=False
            )
        }


def handle_logout(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理用户登出

    请求体:
        - refresh_token: 刷新令牌（用于撤销）

    返回:
        登出结果
    """
    try:
        body = json.loads(event.get("body", "{}"))
        refresh_token = body.get("refresh_token")

        if refresh_token:
            # 撤销刷新令牌
            supabase = get_supabase_client()
            supabase.auth.sign_out()

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {
                    "success": True,
                    "message": "登出成功"
                },
                ensure_ascii=False
            )
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                format_error_response(f"登出失败: {str(e)}"),
                ensure_ascii=False
            )
        }


def handle_password_reset_request(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理密码重置请求

    请求体:
        - email: 邮箱地址

    返回:
        密码重置请求结果
    """
    try:
        body = json.loads(event.get("body", "{}"))
        email = body.get("email")

        if not email:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    format_error_response("邮箱不能为空"),
                    ensure_ascii=False
                )
            }

        # 发送密码重置邮件（使用 Supabase Auth）
        supabase = get_supabase_client()
        supabase.auth.reset_password_email(email)

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {
                    "success": True,
                    "message": "如果该邮箱已注册，您将收到密码重置邮件"
                },
                ensure_ascii=False
            )
        }

    except Exception as e:
        # 不暴露邮箱是否存在的信息
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {
                    "success": True,
                    "message": "如果该邮箱已注册，您将收到密码重置邮件"
                },
                ensure_ascii=False
            )
        }


def handle_password_reset_confirm(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理密码重置确认

    请求体:
        - token: 重置令牌
        - new_password: 新密码

    返回:
        密码重置结果
    """
    try:
        body = json.loads(event.get("body", "{}"))
        token = body.get("token")
        new_password = body.get("new_password")

        if not token or not new_password:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    format_error_response("令牌和新密码不能为空"),
                    ensure_ascii=False
                )
            }

        # 验证新密码强度
        min_length = int(os.getenv("MIN_PASSWORD_LENGTH", "8"))
        valid, msg = validate_password_strength(new_password, min_length)
        if not valid:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    format_error_response(msg),
                    ensure_ascii=False
                )
            }

        # 使用 Supabase Auth 更新密码
        supabase = get_supabase_client()
        supabase.auth.update_user({
            "password": new_password
        })

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {
                    "success": True,
                    "message": "密码重置成功"
                },
                ensure_ascii=False
            )
        }

    except Exception as e:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                format_error_response("令牌无效或已过期"),
                ensure_ascii=False
            )
        }

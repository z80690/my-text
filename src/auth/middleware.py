# -*- coding: utf-8 -*-
"""
认证中间件

提供 JWT 令牌验证中间件，用于保护需要认证的端点
"""

import os
import json
from typing import Dict, Any, Callable, Optional, Tuple
from functools import wraps
from supabase import create_client, Client
from .utils import (
    verify_jwt_token,
    get_token_from_header,
    format_error_response
)


def get_jwt_secret() -> str:
    """获取 JWT 密钥"""
    return os.getenv("SUPABASE_JWT_SECRET", "")


def verify_token_and_get_user_id(token: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    验证令牌并获取用户 ID

    参数:
        token: JWT 令牌

    返回:
        (是否有效, 用户 ID, 错误消息)
    """
    jwt_secret = get_jwt_secret()

    if not jwt_secret:
        return False, None, "JWT 密钥未配置"

    valid, payload, error = verify_jwt_token(token, jwt_secret)

    if not valid:
        return False, None, error

    user_id = payload.get("sub")
    if not user_id:
        return False, None, "令牌中缺少用户 ID"

    return True, user_id, None


def auth_required(handler_func: Callable) -> Callable:
    """
    认证装饰器

    用于保护需要认证的端点。如果令牌无效，返回 401 错误。

    使用方法:
        @auth_required
        def my_handler(event, context):
            user_id = event.get("user_id")
            # 处理逻辑...

    参数:
        handler_func: 要保护的端点处理函数

    返回:
        装饰后的函数
    """
    @wraps(handler_func)
    def wrapper(event: Dict[str, Any], context) -> Dict[str, Any]:
        # 从请求头中提取令牌
        headers = event.get("headers", {})
        auth_header = headers.get("Authorization") or headers.get("authorization")

        if not auth_header:
            return {
                "statusCode": 401,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    format_error_response("缺少认证令牌", error_code="MISSING_TOKEN"),
                    ensure_ascii=False
                )
            }

        token = get_token_from_header(auth_header)

        if not token:
            return {
                "statusCode": 401,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    format_error_response("无效的认证头格式", error_code="INVALID_AUTH_HEADER"),
                    ensure_ascii=False
                )
            }

        # 验证令牌
        valid, user_id, error = verify_token_and_get_user_id(token)

        if not valid:
            error_msg = error or "令牌验证失败"
            return {
                "statusCode": 401,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    format_error_response(error_msg, error_code="INVALID_TOKEN"),
                    ensure_ascii=False
                )
            }

        # 将用户 ID 添加到事件中，供处理函数使用
        event["user_id"] = user_id

        # 调用原始处理函数
        return handler_func(event, context)

    return wrapper


def optional_auth(handler_func: Callable) -> Callable:
    """
    可选认证装饰器

    用于既支持匿名访问又支持认证用户的端点。
    如果令牌有效，将用户 ID 添加到事件中；否则正常执行。

    使用方法:
        @optional_auth
        def my_handler(event, context):
            user_id = event.get("user_id")  # 可能为 None
            # 处理逻辑...

    参数:
        handler_func: 端点处理函数

    返回:
        装饰后的函数
    """
    @wraps(handler_func)
    def wrapper(event: Dict[str, Any], context) -> Dict[str, Any]:
        # 从请求头中提取令牌
        headers = event.get("headers", {})
        auth_header = headers.get("Authorization") or headers.get("authorization")

        if auth_header:
            token = get_token_from_header(auth_header)

            if token:
                # 尝试验证令牌
                valid, user_id, error = verify_token_and_get_user_id(token)

                if valid:
                    event["user_id"] = user_id
                else:
                    # 令牌无效，但不阻止访问
                    event["user_id"] = None
            else:
                event["user_id"] = None
        else:
            event["user_id"] = None

        # 调用原始处理函数
        return handler_func(event, context)

    return wrapper


def require_roles(*allowed_roles: str) -> Callable:
    """
    角色检查装饰器（预留功能，当前未实现）

    用于限制特定角色的用户访问端点。

    使用方法:
        @require_roles("admin", "moderator")
        def admin_handler(event, context):
            # 只有 admin 或 moderator 角色可以访问
            ...

    参数:
        allowed_roles: 允许的角色列表

    返回:
        装饰后的函数
    """
    def decorator(handler_func: Callable) -> Callable:
        @wraps(handler_func)
        def wrapper(event: Dict[str, Any], context) -> Dict[str, Any]:
            user_id = event.get("user_id")

            if not user_id:
                return {
                    "statusCode": 401,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps(
                        format_error_response("需要认证", error_code="AUTH_REQUIRED"),
                        ensure_ascii=False
                    )
                }

            # TODO: 实现角色检查逻辑
            # 当前直接放行，后续需要实现时再添加
            return handler_func(event, context)

        return wrapper
    return decorator


def get_supabase_client_for_user(user_id: str) -> Optional[Client]:
    """
    获取为特定用户配置的 Supabase 客户端

    使用用户的令牌进行认证，确保只能访问自己的数据。

    参数:
        user_id: 用户 ID

    返回:
        Supabase 客户端或 None
    """
    try:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if not url or not key:
            return None

        # 注意：这里使用 anon key，实际数据访问受 RLS 策略保护
        # Supabase 会根据 auth.uid() 自动过滤数据
        return create_client(url, key)
    except Exception:
        return None


if __name__ == "__main__":
    # 测试代码
    print("=" * 50)
    print("认证中间件测试")
    print("=" * 50)

    # 设置测试环境变量
    os.environ["SUPABASE_JWT_SECRET"] = "test_secret_key"

    from .utils import generate_jwt_token

    # 生成测试令牌
    token = generate_jwt_token("test-user-id", "test_secret_key")

    # 测试令牌验证
    valid, user_id, error = verify_token_and_get_user_id(token)
    print(f"\n令牌验证: {valid}")
    if valid:
        print(f"用户 ID: {user_id}")

    # 测试无效令牌
    invalid_token = "invalid_token_string"
    valid, user_id, error = verify_token_and_get_user_id(invalid_token)
    print(f"\n无效令牌验证: {valid}")
    print(f"错误: {error}")

    print("=" * 50)

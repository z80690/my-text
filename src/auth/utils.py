# -*- coding: utf-8 -*-
"""
认证工具模块

提供密码验证、JWT 令牌生成和验证等认证相关工具函数
"""

import re
import hashlib
import secrets
import jwt
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from supabase import Client


def validate_password_strength(password: str, min_length: int = 8) -> Tuple[bool, str]:
    """
    验证密码强度

    参数:
        password: 要验证的密码
        min_length: 密码最小长度（默认8）

    返回:
        (是否有效, 错误消息)
    """
    if not password:
        return False, "密码不能为空"

    if len(password) < min_length:
        return False, f"密码长度至少需要 {min_length} 个字符"

    # 可选的复杂度检查（当前仅检查长度）
    # 如果需要更严格的策略，可以取消注释以下代码

    # if not re.search(r'[A-Z]', password):
    #     return False, "密码必须包含至少一个大写字母"

    # if not re.search(r'[a-z]', password):
    #     return False, "密码必须包含至少一个小写字母"

    # if not re.search(r'\d', password):
    #     return False, "密码必须包含至少一个数字"

    # if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
    #     return False, "密码必须包含至少一个特殊字符"

    return True, "密码强度验证通过"


def hash_password(password: str) -> str:
    """
    对密码进行哈希处理（注意：Supabase Auth 会自动处理密码哈希）
    此函数主要用于本地测试或自定义实现

    参数:
        password: 原始密码

    返回:
        哈希后的密码（SHA256 + salt）
    """
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${password_hash}"


def verify_password(password: str, hashed: str) -> bool:
    """
    验证密码（注意：Supabase Auth 会自动处理密码验证）
    此函数主要用于本地测试或自定义实现

    参数:
        password: 原始密码
        hashed: 哈希后的密码

    返回:
        密码是否匹配
    """
    try:
        salt, password_hash = hashed.split('$')
        computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return secrets.compare_digest(computed_hash, password_hash)
    except (ValueError, AttributeError):
        return False


def generate_jwt_token(
    user_id: str,
    jwt_secret: str,
    expiry_seconds: int = 3600,
    additional_claims: Optional[Dict[str, Any]] = None
) -> str:
    """
    生成 JWT 令牌

    参数:
        user_id: 用户 ID
        jwt_secret: JWT 密钥
        expiry_seconds: 令牌过期时间（秒）
        additional_claims: 额外的声明

    返回:
        JWT 令牌字符串
    """
    now = datetime.utcnow()
    payload = {
        "sub": user_id,           # Subject: 用户 ID
        "iat": now,              # Issued At: 签发时间
        "exp": now + timedelta(seconds=expiry_seconds),  # Expiration: 过期时间
        "type": "access"         # Token Type: 令牌类型
    }

    if additional_claims:
        payload.update(additional_claims)

    token = jwt.encode(payload, jwt_secret, algorithm="HS256")
    return token


def verify_jwt_token(token: str, jwt_secret: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """
    验证 JWT 令牌

    参数:
        token: JWT 令牌字符串
        jwt_secret: JWT 密钥

    返回:
        (是否有效, 声明数据, 错误消息)
    """
    try:
        payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
        return True, payload, None
    except jwt.ExpiredSignatureError:
        return False, None, "令牌已过期"
    except jwt.InvalidTokenError as e:
        return False, None, f"无效的令牌: {str(e)}"
    except Exception as e:
        return False, None, f"令牌验证失败: {str(e)}"


def extract_user_id_from_token(token: str) -> Optional[str]:
    """
    从 JWT 令牌中提取用户 ID（不验证签名，仅用于调试）

    参数:
        token: JWT 令牌字符串

    返回:
        用户 ID 或 None
    """
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload.get("sub")
    except Exception:
        return None


def format_auth_response(
    user_id: str,
    access_token: str,
    refresh_token: Optional[str] = None,
    user_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    格式化认证响应

    参数:
        user_id: 用户 ID
        access_token: 访问令牌
        refresh_token: 刷新令牌（可选）
        user_data: 用户数据（可选）

    返回:
        标准化的认证响应
    """
    response = {
        "success": True,
        "user_id": user_id,
        "access_token": access_token,
        "token_type": "Bearer"
    }

    if refresh_token:
        response["refresh_token"] = refresh_token

    if user_data:
        response["user"] = user_data

    return response


def format_error_response(message: str, status_code: int = 400, error_code: Optional[str] = None) -> Dict[str, Any]:
    """
    格式化错误响应

    参数:
        message: 错误消息
        status_code: HTTP 状态码
        error_code: 错误代码（可选）

    返回:
        标准化的错误响应
    """
    error_response = {
        "success": False,
        "error": message
    }

    if error_code:
        error_response["error_code"] = error_code

    return error_response


def get_token_from_header(auth_header: Optional[str]) -> Optional[str]:
    """
    从 Authorization 头中提取令牌

    参数:
        auth_header: Authorization 头的值（例如："Bearer eyJhbGciOi..."）

    返回:
        令牌字符串或 None
    """
    if not auth_header:
        return None

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    return parts[1]


def is_refresh_token(token: str) -> bool:
    """
    检查令牌是否为刷新令牌

    参数:
        token: JWT 令牌字符串

    返回:
        是否为刷新令牌
    """
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload.get("type") == "refresh"
    except Exception:
        return False


if __name__ == "__main__":
    # 测试代码
    print("=" * 50)
    print("认证工具测试")
    print("=" * 50)

    # 测试密码验证
    password = "testpass123"
    valid, msg = validate_password_strength(password)
    print(f"\n密码验证: {valid} - {msg}")

    # 测试令牌生成
    jwt_secret = "test_secret_key"
    user_id = "test-user-id"
    token = generate_jwt_token(user_id, jwt_secret)
    print(f"\n生成的令牌: {token[:50]}...")

    # 测试令牌验证
    valid, payload, error = verify_jwt_token(token, jwt_secret)
    print(f"\n令牌验证: {valid}")
    if valid and payload:
        print(f"用户 ID: {payload.get('sub')}")

    print("=" * 50)

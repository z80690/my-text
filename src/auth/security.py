# -*- coding: utf-8 -*-
"""
安全增强模块

提供密码验证、速率限制、令牌黑名单等安全功能
"""

import os
import json
import hashlib
import time
from typing import Dict, Any, Set, Tuple
from collections import defaultdict


def validate_password_complexity(password: str, min_length: int = 8) -> Tuple[bool, str]:
    """
    验证密码复杂度

    参数:
        password: 要验证的密码
        min_length: 密码最小长度

    返回:
        (是否有效, 错误消息)
    """
    if not password:
        return False, "密码不能为空"

    if len(password) < min_length:
        return False, f"密码长度至少需要 {min_length} 个字符"

    # 基本复杂度检查
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)

    if not (has_lower or has_upper):
        return False, "密码必须包含字母"

    if not has_digit:
        return False, "密码必须包含数字"

    # 检查常见弱密码
    weak_passwords = ["password", "12345678", "qwerty", "abc123", "password123"]
    if password.lower() in weak_passwords:
        return False, "密码过于常见，请选择更强的密码"

    return True, "密码复杂度验证通过"


class RateLimiter:
    """
    简单的内存速率限制器

    使用内存存储请求计数，适用于单实例部署。
    对于生产环境，建议使用 Redis 或类似服务。
    """

    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        """
        初始化速率限制器

        参数:
            max_requests: 时间窗口内最大请求数
            window_seconds: 时间窗口长度（秒）
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = defaultdict(list)

    def is_allowed(self, identifier: str) -> Tuple[bool, Dict[str, Any]]:
        """
        检查请求是否允许

        参数:
            identifier: 唯一标识符（如 IP 地址、用户 ID）

        返回:
            (是否允许, 限制信息字典)
        """
        current_time = time.time()
        window_start = current_time - self.window_seconds

        # 清理过期的请求记录
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > window_start
        ]

        # 检查是否超过限制
        request_count = len(self.requests[identifier])

        if request_count >= self.max_requests:
            # 计算重置时间
            oldest_request = min(self.requests[identifier])
            reset_time = oldest_request + self.window_seconds

            return False, {
                "allowed": False,
                "limit": self.max_requests,
                "remaining": 0,
                "reset": int(reset_time)
            }

        # 记录此次请求
        self.requests[identifier].append(current_time)

        return True, {
            "allowed": True,
            "limit": self.max_requests,
            "remaining": self.max_requests - request_count - 1,
            "reset": int(current_time + self.window_seconds)
        }

    def get_identifier_from_event(self, event: Dict[str, Any]) -> str:
        """
        从事件中提取标识符

        参数:
            event: AWS Lambda 事件对象

        返回:
            标识符字符串
        """
        # 优先使用用户 ID（如果已认证）
        if "user_id" in event:
            return f"user:{event['user_id']}"

        # 否则使用 IP 地址
        headers = event.get("headers", {})
        ip_address = headers.get("X-Forwarded-For") or headers.get("X-Real-IP") or headers.get("CF-Connecting-IP")

        if ip_address:
            return f"ip:{ip_address}"

        # 如果没有 IP，使用默认标识符
        return "unknown"


class TokenBlacklist:
    """
    令牌黑名单

    存储已撤销的刷新令牌，用于防止已登出的令牌被使用。
    """

    def __init__(self):
        """初始化令牌黑名单"""
        self.blacklisted_tokens: Set[str] = set()

    def blacklist_token(self, token: str) -> bool:
        """
        将令牌加入黑名单

        参数:
            token: 要加入黑名单的令牌

        返回:
            是否成功加入
        """
        try:
            # 使用令牌的哈希值而不是原始令牌
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            self.blacklisted_tokens.add(token_hash)
            return True
        except Exception:
            return False

    def is_blacklisted(self, token: str) -> bool:
        """
        检查令牌是否在黑名单中

        参数:
            token: 要检查的令牌

        返回:
            是否在黑名单中
        """
        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            return token_hash in self.blacklisted_tokens
        except Exception:
            return False

    def remove_token(self, token: str) -> bool:
        """
        从黑名单中移除令牌

        参数:
            token: 要移除的令牌

        返回:
            是否成功移除
        """
        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            if token_hash in self.blacklisted_tokens:
                self.blacklisted_tokens.remove(token_hash)
                return True
            return False
        except Exception:
            return False

    def clear_all(self) -> None:
        """清空黑名单"""
        self.blacklisted_tokens.clear()


# 全局实例
_rate_limiter = None
_token_blacklist = None


def get_rate_limiter() -> RateLimiter:
    """获取全局速率限制器实例"""
    global _rate_limiter
    if _rate_limiter is None:
        max_requests = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
        _rate_limiter = RateLimiter(max_requests=max_requests, window_seconds=60)
    return _rate_limiter


def get_token_blacklist() -> TokenBlacklist:
    """获取全局令牌黑名单实例"""
    global _token_blacklist
    if _token_blacklist is None:
        _token_blacklist = TokenBlacklist()
    return _token_blacklist


if __name__ == "__main__":
    # 测试代码
    print("=" * 50)
    print("安全增强模块测试")
    print("=" * 50)

    # 测试密码复杂度验证
    passwords = ["123", "password", "Passw0rd", "abc123"]
    for pwd in passwords:
        valid, msg = validate_password_complexity(pwd)
        print(f"\n密码 '{pwd}': {valid} - {msg}")

    # 测试速率限制
    print("\n" + "=" * 50)
    print("速率限制测试")
    print("=" * 50)

    limiter = RateLimiter(max_requests=3, window_seconds=60)
    identifier = "test-user"

    for i in range(5):
        allowed, info = limiter.is_allowed(identifier)
        print(f"\n请求 {i + 1}: {'允许' if allowed else '拒绝'}")
        print(f"剩余: {info['remaining']}/{info['limit']}")

    # 测试令牌黑名单
    print("\n" + "=" * 50)
    print("令牌黑名单测试")
    print("=" * 50)

    blacklist = TokenBlacklist()
    test_token = "test_token_12345"

    print(f"\n令牌是否在黑名单中: {blacklist.is_blacklisted(test_token)}")
    blacklist.blacklist_token(test_token)
    print(f"添加后，令牌是否在黑名单中: {blacklist.is_blacklisted(test_token)}")
    blacklist.remove_token(test_token)
    print(f"移除后，令牌是否在黑名单中: {blacklist.is_blacklisted(test_token)}")

    print("=" * 50)

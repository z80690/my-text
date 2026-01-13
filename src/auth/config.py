# -*- coding: utf-8 -*-
"""
Supabase 认证配置模块

该模块提供 Supabase Auth 客户端的配置和初始化功能。
"""

import os
from typing import Dict, Any
from supabase import create_client, Client


def get_supabase_auth_config() -> Dict[str, str | None]:
    """
    获取 Supabase 认证配置

    返回:
        包含 Supabase URL、密钥和JWT密钥的字典

    异常:
        ValueError: 当环境变量未设置时抛出
    """
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    jwt_secret = os.getenv("SUPABASE_JWT_SECRET")

    if not supabase_url:
        raise ValueError("SUPABASE_URL 环境变量未设置")

    if not supabase_key:
        raise ValueError("SUPABASE_KEY 环境变量未设置")

    return {
        "url": supabase_url,
        "key": supabase_key,
        "jwt_secret": jwt_secret
    }


def create_supabase_client() -> Client:
    """
    创建并返回 Supabase 客户端实例

    返回:
        Supabase Client 实例

    异常:
        ValueError: 当配置无效时抛出
    """
    config = get_supabase_auth_config()
    if not config["url"] or not config["key"]:
        raise ValueError("Supabase URL 或 Key 无效")
    supabase: Client = create_client(config["url"], config["key"])
    return supabase


def validate_config() -> Dict[str, Any]:
    """
    验证 Supabase 配置是否有效

    返回:
        包含验证结果的字典:
        - valid: 配置是否有效
        - message: 验证消息
        - config: 配置信息（敏感信息已脱敏）
    """
    try:
        config = get_supabase_auth_config()

        # 验证 URL 格式
        if not config["url"] or not config["url"].startswith(("http://", "https://")):
            return {
                "valid": False,
                "message": "SUPABASE_URL 必须以 http:// 或 https:// 开头",
                "config": None
            }

        # 验证密钥格式（Supabase anon key 通常以 eyJ 开头）
        if not config["key"]:
            return {
                "valid": False,
                "message": "SUPABASE_KEY 不能为空",
                "config": None
            }

        # 脱敏输出
        safe_config = {
            "url": config["url"],
            "key": f"{config['key'][:8]}...{config['key'][-8:]}",
            "jwt_secret": "***" if config["jwt_secret"] else "未设置"
        }

        return {
            "valid": True,
            "message": "Supabase 配置验证成功",
            "config": safe_config
        }

    except ValueError as e:
        return {
            "valid": False,
            "message": str(e),
            "config": None
        }
    except Exception as e:
        return {
            "valid": False,
            "message": f"配置验证失败: {str(e)}",
            "config": None
        }


if __name__ == "__main__":
    # 测试配置验证
    print("=" * 50)
    print("Supabase 认证配置验证")
    print("=" * 50)

    result = validate_config()

    if result["valid"]:
        print("✅ 配置有效")
        print(f"配置: {result['config']}")
    else:
        print(f"❌ 配置无效: {result['message']}")

    print("=" * 50)

# -*- coding: utf-8 -*-
"""
用户资料端点处理器

提供用户资料的查看和更新功能
"""

import os
import json
from typing import Dict, Any
from supabase import create_client, Client
from .utils import format_auth_response, format_error_response


def get_supabase_client() -> Client:
    """获取 Supabase 客户端"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("Supabase URL 或 Key 未配置")
    return create_client(url, key)


def handle_get_profile(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    获取用户资料

    参数:
        event: AWS Lambda 事件对象（应包含 user_id）

    返回:
        用户资料数据
    """
    try:
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

        supabase = get_supabase_client()

        # 查询用户资料
        response = supabase.table("user_profiles").select("*").eq("id", user_id).single().execute()

        if response.data:
            profile_data = {
                "id": response.data["id"],
                "display_name": response.data.get("display_name", ""),
                "avatar_url": response.data.get("avatar_url"),
                "bio": response.data.get("bio"),
                "phone": response.data.get("phone"),
                "website": response.data.get("website"),
                "preferences": response.data.get("preferences", {}),
                "stats": response.data.get("stats", {}),
                "is_active": response.data["is_active"],
                "last_login_at": response.data.get("last_login_at"),
                "created_at": response.data["created_at"],
                "updated_at": response.data["updated_at"]
            }

            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    {
                        "success": True,
                        "data": profile_data
                    },
                    ensure_ascii=False
                )
            }
        else:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    format_error_response("用户资料不存在", error_code="PROFILE_NOT_FOUND"),
                    ensure_ascii=False
                )
            }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                format_error_response(f"获取资料失败: {str(e)}"),
                ensure_ascii=False
            )
        }


def handle_update_profile(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    更新用户资料

    参数:
        event: AWS Lambda 事件对象（应包含 user_id 和请求体）

    请求体:
        - display_name: 显示名称（可选）
        - avatar_url: 头像 URL（可选）
        - bio: 个人简介（可选）
        - phone: 电话号码（可选）
        - website: 个人网站（可选）
        - preferences: 用户偏好（可选）

    返回:
        更新后的用户资料
    """
    try:
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

        body = json.loads(event.get("body", "{}"))

        # 允许更新的字段（email 不允许更新）
        allowed_fields = [
            "display_name",
            "avatar_url",
            "bio",
            "phone",
            "website",
            "preferences"
        ]

        # 过滤并只保留允许更新的字段
        update_data = {}
        for field in allowed_fields:
            if field in body:
                update_data[field] = body[field]

        if not update_data:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    format_error_response("没有提供有效的更新字段"),
                    ensure_ascii=False
                )
            }

        supabase = get_supabase_client()

        # 更新用户资料
        response = supabase.table("user_profiles").update(update_data).eq("id", user_id).execute()

        if response.data:
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    {
                        "success": True,
                        "message": "资料更新成功",
                        "data": response.data[0]
                    },
                    ensure_ascii=False
                )
            }
        else:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    format_error_response("用户资料不存在", error_code="PROFILE_NOT_FOUND"),
                    ensure_ascii=False
                )
            }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                format_error_response(f"更新资料失败: {str(e)}"),
                ensure_ascii=False
            )
        }

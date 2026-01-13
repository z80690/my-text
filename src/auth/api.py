# -*- coding: utf-8 -*-
"""
API 路由处理器

根据 HTTP 方法和路径路由到相应的处理函数
"""

import json
from typing import Dict, Any
from .handlers import (
    handle_register,
    handle_login,
    handle_refresh_token,
    handle_logout,
    handle_password_reset_request,
    handle_password_reset_confirm
)
from .profile import handle_get_profile, handle_update_profile
from .middleware import auth_required
from src.index import main_handler as knowledge_base_handler


def route_request(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    路由 API 请求到相应的处理函数

    参数:
        event: AWS Lambda 事件对象

    返回:
        HTTP 响应字典
    """
    path = event.get("path", "").lower()
    method = event.get("httpMethod", "").upper()

    # 确保路径以 / 开头
    if not path.startswith("/"):
        path = f"/{path}"

    # 认证端点路由
    if path == "/auth/register" and method == "POST":
        return handle_register(event)

    elif path == "/auth/login" and method == "POST":
        return handle_login(event)

    elif path == "/auth/refresh" and method == "POST":
        return handle_refresh_token(event)

    elif path == "/auth/logout" and method == "POST":
        return handle_logout(event)

    elif path == "/auth/password/reset" and method == "POST":
        return handle_password_reset_request(event)

    elif path == "/auth/password/reset/confirm" and method == "POST":
        return handle_password_reset_confirm(event)

    # 用户资料端点路由（需要认证）
    elif path == "/auth/profile" and method == "GET":
        return auth_required(handle_get_profile)(event, None)

    elif path == "/auth/profile" and method == "PUT":
        return auth_required(handle_update_profile)(event, None)

    # Knowledge Base 端点路由（可选认证）
    elif path == "/api/knowledge" and method == "GET":
        return knowledge_base_handler(event, None)

    # 404 Not Found
    else:
        return {
            "statusCode": 404,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {
                    "success": False,
                    "error": "未找到请求的端点"
                },
                ensure_ascii=False
            )
        }


def main_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    API 网关主处理函数

    路由所有请求到相应的处理函数

    参数:
        event: AWS Lambda 事件对象
        context: AWS Lambda 上下文

    返回:
        HTTP 响应字典
    """
    # 添加 CORS 头
    cors_headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": os.getenv("CORS_ORIGINS", "*"),
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
        "Access-Control-Max-Age": "3600"
    }

    # 处理 OPTIONS 请求（CORS 预检）
    method = event.get("httpMethod", "").upper()
    if method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": cors_headers,
            "body": ""
        }

    # 路由请求
    response = route_request(event)

    # 添加 CORS 头
    response["headers"] = {**response.get("headers", {}), **cors_headers}

    return response


# 导入 os 以获取 CORS 配置
import os

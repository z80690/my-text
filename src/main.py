# -*- coding: utf8 -*-
"""
主 API 网关处理器

路由所有 API 请求到相应的处理函数
"""

import os
import json
from typing import Dict, Any
from auth.api import main_handler as auth_api_handler
from src.auth.profile import handle_get_profile, handle_update_profile
from src.auth.middleware import auth_required


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

    # 如果是 /api/* 或 /auth/* 路径，使用认证 API 处理器
    if path.startswith("/api/") or path.startswith("/auth/"):
        return auth_api_handler(event, None)

    # 默认：knowledge base 查询
    return handle_knowledge_base_query(event)


def handle_knowledge_base_query(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理 Knowledge Base 查询（向后兼容）

    参数:
        event: AWS Lambda 事件对象

    返回:
        HTTP 响应字典
    """
    result = {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': ''
    }

    try:
        # 1. 从环境变量读取配置
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        # 验证环境变量
        if not supabase_url or not supabase_key:
            error_msg = "Error: SUPABASE_URL or SUPABASE_KEY is not set in environment variables"
            print(error_msg)
            result['statusCode'] = 400
            result['body'] = json.dumps({'error': error_msg})
            return result

        # 2. 创建 Supabase 客户端
        from supabase import create_client, Client
        supabase: Client = create_client(supabase_url, supabase_key)
        print("Supabase client initialized successfully.")

        # 3. 执行查询（从 knowledge_base 表查询前 5 条数据）
        response = supabase.table("knowledge_base").select("*").limit(5).execute()

        # 4. 处理查询结果
        print(f"Query executed successfully. Found {len(response.data)} records.")

        result['body'] = json.dumps({
            'success': True,
            'message': 'Query successful',
            'data': response.data,
            'count': len(response.data)
        }, ensure_ascii=False)

    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(error_msg)
        result['statusCode'] = 500
        result['body'] = json.dumps({'error': error_msg})

    print("Supabase handler execution complete")
    return result


def main_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    API 网关主处理函数

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

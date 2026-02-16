# -*- coding: utf-8 -*-
"""
Main Application Entry Point

Local development server entry point
Routes requests to appropriate handlers
"""

import os
import json
from typing import Dict, Any

# Import API handlers
from .ai_api import main_handler as ai_handler
from .auth.api import main_handler as auth_handler


def route_request(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Route request to appropriate handler based on path
    
    Args:
        event: Lambda event or HTTP request dict
        
    Returns:
        HTTP response dict
    """
    path = event.get("path", "").lower()
    method = event.get("httpMethod", "").upper()
    
    # Ensure path starts with /
    if not path.startswith("/"):
        path = f"/{path}"
    
    # Route to AI API
    if path.startswith("/api/ai"):
        return ai_handler(event, None)
    
    # Route to Auth API
    elif path.startswith("/auth"):
        return auth_handler(event, None)
    
    # Default: knowledge base query
    elif path == "/" and method == "GET":
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "My Text API",
                "version": "1.0.0",
                "endpoints": {
                    "ai": "/api/ai/*",
                    "auth": "/auth/*"
                }
            })
        }
    
    # 404 Not Found
    else:
        return {
            "statusCode": 404,
            "body": json.dumps({
                "success": False,
                "error": "Not found"
            })
        }


def main_handler(event: Dict[str, Any], context=None) -> Dict[str, Any]:
    """
    Main request handler for cloud functions
    
    Routes all requests to appropriate handlers
    
    Args:
        event: AWS Lambda event object
        context: AWS Lambda context object
        
    Returns:
        HTTP response dictionary
    """
    # Add CORS headers
    cors_headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": os.getenv("CORS_ORIGINS", "*"),
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization"
    }
    
    # Handle OPTIONS preflight requests
    method = event.get("httpMethod", "").upper()
    if method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": cors_headers,
            "body": ""
        }
    
    # Route request
    response = route_request(event)
    
    # Add CORS headers to response
    response["headers"] = {**response.get("headers", {}), **cors_headers}
    
    return response


if __name__ == "__main__":
    port = int(os.getenv("PORT") or "9000")
    print(f"[INFO] Starting My Text API server on port {port}")
    print("[INFO] Available endpoints:")
    print("  - GET  /                    - API info")
    print("  - POST /api/ai/chat         - AI chat with function calling")
    print("  - POST /api/ai/text         - Text generation")
    print("  - GET  /api/ai/tools        - List available tools")
    print("  - POST /api/ai/execute      - Execute function directly")
    print("  - GET  /api/ai/status       - AI service status")
    print("  - POST /auth/register       - User registration")
    print("  - POST /auth/login          - User login")
    # Note: For local development, use a WSGI server like gunicorn
    # This is just a placeholder for the entry point

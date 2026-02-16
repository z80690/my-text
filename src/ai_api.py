# -*- coding: utf-8 -*-
"""
AI API Endpoint

Handles AI-related requests including text generation, chat completion, and function calling
"""

import os
import json
import logging
from typing import Dict, Any
from supabase import create_client, Client

# Import agent services
from .skill_handler import FunctionRegistry, get_all_tools


class DefaultSecurityConfig:
    """Default security configuration for AI API"""
    
    RATE_LIMIT = 60  # requests per minute
    RATE_WINDOW = 60  # seconds
    MAX_TOKENS = 4000
    TEMPERATURE = 0.7


def get_supabase_client() -> Client:
    """Get Supabase client"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL or SUPABASE_KEY is not set")
    return create_client(supabase_url, supabase_key)


def is_rate_limited(client: Client, identifier: str, limit: int, window: int) -> bool:
    """Check if identifier is rate limited"""
    return False


def handle_ai_chat(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle AI chat completion with optional function calling
    
    POST /api/ai/chat
    
    Body:
    {
        "messages": [
            {"role": "user", "content": "Hello"}
        ],
        "use_functions": true,  // optional, defaults to true
        "stream": false,        // optional
        "temperature": 0.7      // optional
    }
    """
    try:
        body = json.loads(event.get("body", "{}"))
        messages = body.get("messages", [])
        use_functions = body.get("use_functions", True)
        stream = body.get("stream", False)
        temperature = body.get("temperature", DefaultSecurityConfig.TEMPERATURE)
        
        if not messages:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "success": False,
                    "error": "No messages provided"
                })
            }
        
        # Model not configured
        return {
            "statusCode": 404,
            "body": json.dumps({
                "success": False,
                "error": "AI model not configured"
            })
        }
        
        # Get tools if function calling is enabled
        tools = None
        if use_functions:
            tools = get_all_tools()
            logging.info("[INFO] Using %d tools for function calling", len(tools))
        
        # Check for rate limiting
        try:
            supabase_client = get_supabase_client()
            # In production, implement proper rate limiting
            if not is_rate_limited(supabase_client, "default", DefaultSecurityConfig.RATE_LIMIT, DefaultSecurityConfig.RATE_WINDOW):
                pass  # Rate limit check passed
        except Exception:
            pass  # Skip rate limiting if Supabase is not available
        
        # Execute chat with or without function calling
        if use_functions and tools:
            result = client.chat_with_functions(
                messages=messages,
                tools=tools
            )
        else:
            result = client.chat(
                messages=messages,
                temperature=temperature,
                stream=stream
            )
        
        if result.get("success"):
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "success": True,
                    "content": result.get("content"),
                    "tool_calls": result.get("tool_calls", []),
                    "usage": result.get("usage")
                })
            }
        
        return {
            "statusCode": 500,
            "body": json.dumps({
                "success": False,
                "error": result.get("error", "Unknown error")
            })
        }
    
    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "success": False,
                "error": "Invalid JSON in request body"
            })
        }
    except Exception as e:
        logging.error("[ERROR] AI chat failed: %s", e)
        return {
            "statusCode": 500,
            "body": json.dumps({
                "success": False,
                "error": str(e)
            })
        }


def handle_list_tools(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    List all available tools/functions
    
    GET /api/ai/tools
    """
    try:
        tools = get_all_tools()
        return {
            "statusCode": 200,
            "body": json.dumps({
                "success": True,
                "tools_count": len(tools),
                "tools": tools
            })
        }
    except Exception as e:
        logging.error("[ERROR] List tools failed: %s", e)
        return {
            "statusCode": 500,
            "body": json.dumps({
                "success": False,
                "error": str(e)
            })
        }


def handle_execute_function(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a function directly
    
    POST /api/ai/execute
    
    Body:
    {
        "function_name": "query_knowledge_base",
        "arguments": {
            "query": "How to use the API",
            "limit": 5
        },
        "validate": true  # optional
    }
    """
    try:
        body = json.loads(event.get("body", "{}"))
        function_name = body.get("function_name")
        arguments = body.get("arguments", {})
        validate = body.get("validate", True)
        
        if not function_name:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "success": False,
                    "error": "Function name is required"
                })
            }
        
        result = FunctionRegistry.execute(
            name=function_name,
            arguments=arguments,
            validate=validate
        )
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "success": result.get("success", False),
                "result": result.get("result"),
                "error": result.get("error"),
                "function": function_name
            })
        }
    
    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "success": False,
                "error": "Invalid JSON in request body"
            })
        }
    except Exception as e:
        logging.error("[ERROR] Execute function failed: %s", e)
        return {
            "statusCode": 500,
            "body": json.dumps({
                "success": False,
                "error": str(e)
            })
        }


def handle_text_generation(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle simple text generation
    
    POST /api/ai/text
    
    Body:
    {
        "prompt": "Write a poem about...",
        "max_tokens": 500,
        "temperature": 0.8
    }
    """
    try:
        body = json.loads(event.get("body", "{}"))
        prompt = body.get("prompt", "")
        max_tokens = body.get("max_tokens", 1000)
        temperature = body.get("temperature", DefaultSecurityConfig.TEMPERATURE)
        
        if not prompt:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "success": False,
                    "error": "Prompt is required"
                })
            }
        
        return {
            "statusCode": 404,
            "body": json.dumps({
                "success": False,
                "error": "AI model not configured"
            })
        }
        # client = get_zhipu_client()
        # messages = [{"role": "user", "content": prompt}]
        
        result = client.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        if result.get("success"):
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "success": True,
                    "generated_text": result.get("content")
                })
            }
        
        return {
            "statusCode": 500,
            "body": json.dumps({
                "success": False,
                "error": result.get("error", "Unknown error")
            })
        }
    
    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "success": False,
                "error": "Invalid JSON in request body"
            })
        }
    except Exception as e:
        logging.error("[ERROR] Text generation failed: %s", e)
        return {
            "statusCode": 500,
            "body": json.dumps({
                "success": False,
                "error": str(e)
            })
        }


def handle_ai_status(event: Dict[str, Any]) -> Dict[str, Any]:
    """Get AI service status"""
    try:
        # AI model not configured
        available = False
        
        tools_count = len(FunctionRegistry.list_functions())
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "success": True,
                "status": {
                    "ai_available": available,
                    "model": os.getenv("ZHIPU_MODEL", "glm-4.7"),
                    "tools_registered": tools_count,
                    "functions": FunctionRegistry.list_functions()
                }
            })
        }
    except Exception as e:
        return {
            "statusCode": 200,
            "body": json.dumps({
                "success": True,
                "status": {
                    "ai_available": False,
                    "error": str(e),
                    "tools_registered": 0
                }
            })
        }


def main_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    AI API main handler
    
    Routes:
    - POST /api/ai/chat - Chat completion with function calling
    - POST /api/ai/text - Simple text generation
    - GET /api/ai/tools - List available tools
    - POST /api/ai/execute - Execute a function directly
    - GET /api/ai/status - Get AI service status
    """
    path = event.get("path", "").lower()
    method = event.get("httpMethod", "").upper()
    
    # Ensure path starts with /
    if not path.startswith("/"):
        path = f"/{path}"
    
    # Route requests
    if path == "/api/ai/chat" and method == "POST":
        return handle_ai_chat(event)
    
    if path == "/api/ai/text" and method == "POST":
        return handle_text_generation(event)
    
    if path == "/api/ai/tools" and method == "GET":
        return handle_list_tools(event)
    
    if path == "/api/ai/execute" and method == "POST":
        return handle_execute_function(event)
    
    if path == "/api/ai/status" and method == "GET":
        return handle_ai_status(event)
    
        return {
            "statusCode": 404,
            "body": json.dumps({
                "success": False,
                "error": "Not found"
            })
        }


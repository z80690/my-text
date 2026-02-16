# -*- coding: utf-8 -*-
"""
Auth API Endpoint

Handles user registration, login, token refresh and other authentication functions
"""

import os
import json
from typing import Dict, Any
from supabase import create_client, Client


def get_supabase_client() -> Client:
    """Get Supabase client"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL or SUPABASE_KEY is not set")
    return create_client(supabase_url, supabase_key)


def main_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Auth service API main handler
    
    Routes:
    - /auth/register - User registration
    - /auth/login - User login
    - /auth/refresh - Token refresh
    - /auth/logout - User logout
    """
    return {"statusCode": 200, "body": json.dumps({"message": "Auth API"})}

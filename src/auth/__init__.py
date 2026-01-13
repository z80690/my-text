# -*- coding: utf-8 -*-
"""
认证模块

提供用户认证、授权和安全功能
"""

from .config import (
    get_supabase_auth_config,
    create_supabase_client,
    validate_config
)

from .utils import (
    validate_password_strength,
    generate_jwt_token,
    verify_jwt_token,
    format_auth_response,
    format_error_response,
    get_token_from_header
)

from .handlers import (
    handle_register,
    handle_login,
    handle_refresh_token,
    handle_logout,
    handle_password_reset_request,
    handle_password_reset_confirm
)

from .profile import (
    handle_get_profile,
    handle_update_profile
)

from .middleware import (
    auth_required,
    optional_auth,
    require_roles
)

from .security import (
    validate_password_complexity,
    RateLimiter,
    TokenBlacklist,
    get_rate_limiter,
    get_token_blacklist
)

__all__ = [
    # Config
    "get_supabase_auth_config",
    "create_supabase_client",
    "validate_config",

    # Utils
    "validate_password_strength",
    "generate_jwt_token",
    "verify_jwt_token",
    "format_auth_response",
    "format_error_response",
    "get_token_from_header",

    # Handlers
    "handle_register",
    "handle_login",
    "handle_refresh_token",
    "handle_logout",
    "handle_password_reset_request",
    "handle_password_reset_confirm",

    # Profile
    "handle_get_profile",
    "handle_update_profile",

    # Middleware
    "auth_required",
    "optional_auth",
    "require_roles",

    # Security
    "validate_password_complexity",
    "RateLimiter",
    "TokenBlacklist",
    "get_rate_limiter",
    "get_token_blacklist"
]

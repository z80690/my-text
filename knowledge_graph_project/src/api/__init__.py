# -*- coding: utf-8 -*-
"""
API 响应和异常包

包含:
- responses: 标准响应模型
- exceptions: 自定义异常
- middleware: 响应包装中间件
"""

from .responses import (
    SuccessResponse,
    ErrorResponse,
    PaginatedResponse,
    ResponseFactory,
)
from .exceptions import (
    APIException,
    ErrorCode,
    ValidationException,
    NotFoundException,
    AuthenticationException,
    AuthorizationException,
    ConflictException,
    RateLimitException,
    InternalException,
    ExceptionFactory,
)
from .middleware import (
    APIResponseMiddleware,
    ResponseWrapper,
    setup_exception_handlers,
    success,
    error,
    paginated,
)

__all__ = [
    # 响应模型
    "SuccessResponse",
    "ErrorResponse",
    "PaginatedResponse",
    "ResponseFactory",
    
    # 异常
    "APIException",
    "ErrorCode",
    "ValidationException",
    "NotFoundException",
    "AuthenticationException",
    "AuthorizationException",
    "ConflictException",
    "RateLimitException",
    "InternalException",
    "ExceptionFactory",
    
    # 中间件
    "APIResponseMiddleware",
    "ResponseWrapper",
    "setup_exception_handlers",
    
    # 便捷函数
    "success",
    "error",
    "paginated",
]

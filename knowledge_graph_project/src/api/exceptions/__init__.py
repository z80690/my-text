# -*- coding: utf-8 -*-
"""
API 异常定义
API Exceptions

定义项目使用的自定义异常和错误码

版本: 1.0.0
日期: 2026-01-20
"""

from enum import Enum
from typing import Any, Dict, Optional


# ============================================
# 1. 错误码枚举
# ============================================

class ErrorCode(int, Enum):
    """业务错误码枚举"""

    # 成功
    SUCCESS = 0

    # 客户端错误 (4xxxx)
    VALIDATION_ERROR = 40001  # 请求参数验证失败
    INVALID_FORMAT = 40002    # 请求参数格式错误
    MISSING_PARAM = 40003     # 缺少必需参数

    # 认证错误 (401xx)
    UNAUTHORIZED = 40101      # 未认证
    TOKEN_EXPIRED = 40102     # Token已过期
    INVALID_TOKEN = 40103     # 无效的Token

    # 权限错误 (403xx)
    FORBIDDEN = 40301         # 无权限访问
    OPERATION_FORBIDDEN = 40302  # 禁止操作

    # 资源错误 (404xx)
    RESOURCE_NOT_FOUND = 40401   # 资源不存在
    PAGE_NOT_FOUND = 40402       # 页面不存在

    # 冲突错误 (409xx)
    RESOURCE_EXISTS = 40901      # 资源已存在
    RESOURCE_CONFLICT = 40902    # 资源冲突

    # 验证错误 (422xx)
    UNPROCESSABLE_ENTITY = 42201  # 参数验证失败

    # 频率限制 (429xx)
    RATE_LIMIT = 42901           # 请求过于频繁

    # 服务器错误 (5xxxx)
    INTERNAL_ERROR = 50001       # 服务器内部错误
    DATABASE_ERROR = 50002       # 数据库错误
    EXTERNAL_SERVICE_ERROR = 50003  # 外部服务调用失败

    # 服务不可用 (503xx)
    SERVICE_UNAVAILABLE = 50301  # 服务维护中


# ============================================
# 2. HTTP状态码映射
# ============================================

class HttpStatusCode(int, Enum):
    """HTTP状态码"""
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    TOO_MANY_REQUESTS = 429
    INTERNAL_SERVER_ERROR = 500
    SERVICE_UNAVAILABLE = 503


# ============================================
# 3. 错误码到HTTP状态的映射
# ============================================

ERROR_TO_HTTP: Dict[int, int] = {
    ErrorCode.SUCCESS: 200,
    ErrorCode.VALIDATION_ERROR: 400,
    ErrorCode.INVALID_FORMAT: 400,
    ErrorCode.MISSING_PARAM: 400,
    ErrorCode.UNAUTHORIZED: 401,
    ErrorCode.TOKEN_EXPIRED: 401,
    ErrorCode.INVALID_TOKEN: 401,
    ErrorCode.FORBIDDEN: 403,
    ErrorCode.OPERATION_FORBIDDEN: 403,
    ErrorCode.RESOURCE_NOT_FOUND: 404,
    ErrorCode.PAGE_NOT_FOUND: 404,
    ErrorCode.RESOURCE_EXISTS: 409,
    ErrorCode.RESOURCE_CONFLICT: 409,
    ErrorCode.UNPROCESSABLE_ENTITY: 422,
    ErrorCode.RATE_LIMIT: 429,
    ErrorCode.INTERNAL_ERROR: 500,
    ErrorCode.DATABASE_ERROR: 500,
    ErrorCode.EXTERNAL_SERVICE_ERROR: 500,
    ErrorCode.SERVICE_UNAVAILABLE: 503,
}


# ============================================
# 4. 自定义异常类
# ============================================

class APIException(Exception):
    """API自定义异常基类"""

    def __init__(
        self,
        code: int,
        message: str,
        http_status: Optional[int] = None,
        error_type: str = "api_error",
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ):
        self.code = code
        self.message = message
        self.http_status = http_status or ERROR_TO_HTTP.get(code, 400)
        self.error_type = error_type
        self.details = details or {}
        self.request_id = request_id
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "code": self.code,
            "message": self.message,
            "error": {
                "type": self.error_type,
                "details": self.details
            },
            "request_id": self.request_id
        }

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


class ValidationException(APIException):
    """验证异常"""

    def __init__(
        self,
        message: str = "请求参数验证失败",
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ):
        super().__init__(
            code=ErrorCode.VALIDATION_ERROR,
            message=message,
            http_status=400,
            error_type="validation_error",
            details=details,
            request_id=request_id
        )


class AuthenticationException(APIException):
    """认证异常"""

    def __init__(
        self,
        message: str = "请先登录",
        request_id: Optional[str] = None
    ):
        super().__init__(
            code=ErrorCode.UNAUTHORIZED,
            message=message,
            http_status=401,
            error_type="authentication_error",
            request_id=request_id
        )


class AuthorizationException(APIException):
    """权限异常"""

    def __init__(
        self,
        message: str = "无权访问此资源",
        request_id: Optional[str] = None
    ):
        super().__init__(
            code=ErrorCode.FORBIDDEN,
            message=message,
            http_status=403,
            error_type="authorization_error",
            request_id=request_id
        )


class NotFoundException(APIException):
    """资源不存在异常"""

    def __init__(
        self,
        resource_type: str = "资源",
        resource_id: Optional[str] = None,
        request_id: Optional[str] = None
    ):
        message = f"{resource_type}不存在"
        if resource_id:
            message = f"{resource_type} {resource_id}不存在"

        super().__init__(
            code=ErrorCode.RESOURCE_NOT_FOUND,
            message=message,
            http_status=404,
            error_type="not_found",
            details={"resource_type": resource_type, "resource_id": resource_id} if resource_id else {"resource_type": resource_type},
            request_id=request_id
        )


class ConflictException(APIException):
    """资源冲突异常"""

    def __init__(
        self,
        message: str = "资源冲突",
        field: Optional[str] = None,
        value: Optional[Any] = None,
        request_id: Optional[str] = None
    ):
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = value

        super().__init__(
            code=ErrorCode.RESOURCE_EXISTS,
            message=message,
            http_status=409,
            error_type="conflict",
            details=details if details else None,
            request_id=request_id
        )


class RateLimitException(APIException):
    """频率限制异常"""

    def __init__(
        self,
        message: str = "请求过于频繁，请稍后重试",
        retry_after: int = 60,
        request_id: Optional[str] = None
    ):
        super().__init__(
            code=ErrorCode.RATE_LIMIT,
            message=message,
            http_status=429,
            error_type="rate_limit",
            details={"retry_after": retry_after},
            request_id=request_id
        )
        self.retry_after = retry_after


class InternalException(APIException):
    """服务器内部异常"""

    def __init__(
        self,
        message: str = "服务器内部错误，请稍后重试",
        reference: Optional[str] = None,
        request_id: Optional[str] = None
    ):
        details = {}
        if reference:
            details["reference"] = reference

        super().__init__(
            code=ErrorCode.INTERNAL_ERROR,
            message=message,
            http_status=500,
            error_type="internal_error",
            details=details if details else None,
            request_id=request_id
        )


# ============================================
# 5. 异常工厂函数
# ============================================

class ExceptionFactory:
    """异常工厂类"""

    @staticmethod
    def bad_request(
        message: str = "请求参数错误",
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ) -> APIException:
        """创建400异常"""
        return APIException(
            code=ErrorCode.VALIDATION_ERROR,
            message=message,
            http_status=400,
            error_type="bad_request",
            details=details,
            request_id=request_id
        )

    @staticmethod
    def unauthorized(
        message: str = "请先登录",
        request_id: Optional[str] = None
    ) -> APIException:
        """创建401异常"""
        return AuthenticationException(message, request_id)

    @staticmethod
    def forbidden(
        message: str = "无权访问此资源",
        request_id: Optional[str] = None
    ) -> APIException:
        """创建403异常"""
        return AuthorizationException(message, request_id)

    @staticmethod
    def not_found(
        resource_type: str,
        resource_id: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> APIException:
        """创建404异常"""
        return NotFoundException(resource_type, resource_id, request_id)

    @staticmethod
    def conflict(
        message: str = "资源已存在",
        field: Optional[str] = None,
        value: Optional[Any] = None,
        request_id: Optional[str] = None
    ) -> APIException:
        """创建409异常"""
        return ConflictException(message, field, value, request_id)

    @staticmethod
    def rate_limit(
        retry_after: int = 60,
        request_id: Optional[str] = None
    ) -> APIException:
        """创建429异常"""
        return RateLimitException(retry_after=retry_after, request_id=request_id)

    @staticmethod
    def internal(
        message: str = "服务器内部错误",
        reference: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> APIException:
        """创建500异常"""
        return InternalException(message, reference, request_id)


# ============================================
# 6. 快速抛出辅助函数
# ============================================

def raise_bad_request(
    message: str = "请求参数错误",
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
) -> None:
    """抛出400异常"""
    raise ExceptionFactory.bad_request(message, details, request_id)


def raise_unauthorized(
    message: str = "请先登录",
    request_id: Optional[str] = None
) -> None:
    """抛出401异常"""
    raise ExceptionFactory.unauthorized(message, request_id)


def raise_forbidden(
    message: str = "无权访问此资源",
    request_id: Optional[str] = None
) -> None:
    """抛出403异常"""
    raise ExceptionFactory.forbidden(message, request_id)


def raise_not_found(
    resource_type: str,
    resource_id: Optional[str] = None,
    request_id: Optional[str] = None
) -> None:
    """抛出404异常"""
    raise ExceptionFactory.not_found(resource_type, resource_id, request_id)


def raise_conflict(
    message: str = "资源已存在",
    field: Optional[str] = None,
    value: Optional[Any] = None,
    request_id: Optional[str] = None
) -> None:
    """抛出409异常"""
    raise ExceptionFactory.conflict(message, field, value, request_id)


def raise_rate_limit(
    retry_after: int = 60,
    request_id: Optional[str] = None
) -> None:
    """抛出429异常"""
    raise ExceptionFactory.rate_limit(retry_after, request_id)


def raise_internal(
    message: str = "服务器内部错误",
    reference: Optional[str] = None,
    request_id: Optional[str] = None
) -> None:
    """抛出500异常"""
    raise ExceptionFactory.internal(message, reference, request_id)


# 导出
__all__ = [
    "ErrorCode",
    "HttpStatusCode",
    "ERROR_TO_HTTP",
    "APIException",
    "ValidationException",
    "AuthenticationException",
    "AuthorizationException",
    "NotFoundException",
    "ConflictException",
    "RateLimitException",
    "InternalException",
    "ExceptionFactory",
    "raise_bad_request",
    "raise_unauthorized",
    "raise_forbidden",
    "raise_not_found",
    "raise_conflict",
    "raise_rate_limit",
    "raise_internal",
]

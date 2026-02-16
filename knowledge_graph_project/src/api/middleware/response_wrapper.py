# -*- coding: utf-8 -*-
"""
API 响应包装中间件
API Response Wrapper Middleware

确保所有API响应遵守统一格式规范的中间件

版本: 1.0.0
日期: 2026-01-20
"""

import functools
import json
import uuid
from contextlib import contextmanager
from typing import Any, Callable, Dict, Optional, TypeVar, Union

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from .exceptions import APIException, ErrorCode
from .models import ResponseFactory


# ============================================
# 1. 请求上下文
# ============================================

class RequestContext:
    """请求上下文"""

    def __init__(self):
        self._request_id: Optional[str] = None
        self._start_time: Optional[float] = None
        self._extra: Dict[str, Any] = {}

    @property
    def request_id(self) -> Optional[str]:
        return self._request_id

    @request_id.setter
    def request_id(self, value: str):
        self._request_id = value

    @property
    def start_time(self) -> Optional[float]:
        return self._start_time

    @start_time.setter
    def start_time(self, value: float):
        self._start_time = value

    def set_extra(self, key: str, value: Any):
        self._extra[key] = value

    def get_extra(self, key: str, default: Any = None) -> Any:
        return self._extra.get(key, default)

    def clear(self):
        self._request_id = None
        self._start_time = None
        self._extra.clear()


# 全局请求上下文
_request_context = RequestContext()


def get_request_id() -> Optional[str]:
    """获取当前请求ID"""
    return _request_context.request_id


def set_request_id(request_id: str):
    """设置当前请求ID"""
    _request_context.request_id = request_id


def get_request_context() -> RequestContext:
    """获取请求上下文"""
    return _request_context


# ============================================
# 2. 响应包装器
# ============================================

class ResponseWrapper:
    """响应包装器"""

    @staticmethod
    def success(
        data: Any = None,
        message: str = "success",
        code: int = 0,
        meta: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """创建成功响应"""
        return ResponseFactory.success(
            data=data,
            message=message,
            code=code,
            meta=meta,
            request_id=get_request_id()
        ).dict()

    @staticmethod
    def paginated(
        data: list,
        page: int,
        limit: int,
        total: int,
        filters: Optional[Dict[str, Any]] = None,
        sort: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """创建分页响应"""
        return ResponseFactory.paginated(
            data=data,
            page=page,
            limit=limit,
            total=total,
            filters=filters,
            sort=sort,
            request_id=get_request_id()
        ).dict()

    @staticmethod
    def error(
        code: int,
        message: str,
        error_type: str = "api_error",
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """创建错误响应"""
        return ResponseFactory.error(
            code=code,
            message=message,
            error_type=error_type,
            details=details,
            request_id=get_request_id()
        ).dict()

    @staticmethod
    def created(
        data: Any,
        message: str = "创建成功"
    ) -> Dict[str, Any]:
        """创建资源成功响应"""
        return ResponseFactory.created(
            data=data,
            message=message,
            request_id=get_request_id()
        ).dict()

    @staticmethod
    def updated(
        data: Any,
        message: str = "更新成功"
    ) -> Dict[str, Any]:
        """更新资源成功响应"""
        return ResponseFactory.updated(
            data=data,
            message=message,
            request_id=get_request_id()
        ).dict()

    @staticmethod
    def deleted(
        deleted_id: str,
        message: str = "删除成功"
    ) -> Dict[str, Any]:
        """删除资源成功响应"""
        return ResponseFactory.deleted(
            deleted_id=deleted_id,
            message=message,
            request_id=get_request_id()
        ).dict()


# ============================================
# 3. FastAPI 中间件
# ============================================

class APIResponseMiddleware(BaseHTTPMiddleware):
    """API响应中间件"""

    # 排除的路径（不进行响应包装）
    EXCLUDE_PATHS = [
        "/docs",
        "/redoc",
        "/openapi.json",
        "/health",
        "/favicon.ico",
    ]

    # 排除的前缀
    EXCLUDE_PREFIXES = [
        "/static",
    ]

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint
    ) -> Response:
        """处理请求"""
        # 生成请求ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        set_request_id(request_id)
        _request_context.start_time = __import__("time").time()

        # 检查是否需要排除
        if self._should_exclude(request):
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response

        # 处理请求
        try:
            response = await call_next(request)

            # 处理成功响应
            if response.status_code < 400:
                return self._wrap_success_response(response, request_id)

            # 处理错误响应（已由异常处理器处理）
            return response

        except APIException as e:
            return self._wrap_exception(e, request_id)

        except Exception as e:
            return self._wrap_unknown_error(e, request_id)

    def _should_exclude(self, request: Request) -> bool:
        """检查是否应该排除"""
        path = request.url.path

        # 完全匹配
        if path in self.EXCLUDE_PATHS:
            return True

        # 前缀匹配
        for prefix in self.EXCLUDE_PREFIXES:
            if path.startswith(prefix):
                return True

        return False

    def _wrap_success_response(
        self,
        response: Response,
        request_id: str
    ) -> JSONResponse:
        """包装成功响应"""
        # 获取原始响应内容
        if hasattr(response, "body"):
            content = response.body
            if isinstance(content, bytes):
                content = content.decode("utf-8")
                data = json.loads(content) if content else None
            else:
                data = None
        else:
            data = None

        # 排除204 No Content
        if response.status_code == 204:
            response.headers["X-Request-ID"] = request_id
            return response

        # 创建标准响应
        wrapped = ResponseWrapper.success(
            data=data,
            request_id=request_id
        )

        return JSONResponse(
            content=wrapped,
            status_code=response.status_code,
            headers=dict(response.headers) if hasattr(response, "headers") else {}
        )

    def _wrap_exception(
        self,
        exception: APIException,
        request_id: str
    ) -> JSONResponse:
        """包装异常响应"""
        wrapped = ResponseWrapper.error(
            code=exception.code,
            message=exception.message,
            error_type=exception.error_type,
            details=exception.details
        )

        return JSONResponse(
            content=wrapped,
            status_code=exception.http_status,
            headers={"X-Request-ID": request_id}
        )

    def _wrap_unknown_error(
        self,
        exception: Exception,
        request_id: str
    ) -> JSONResponse:
        """包装未知错误"""
        # 记录错误日志
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"[{request_id}] Unknown error: {exception}", exc_info=True)

        wrapped = ResponseWrapper.error(
            code=ErrorCode.INTERNAL_ERROR,
            message="服务器内部错误，请稍后重试",
            error_type="internal_error",
            details={"reference": request_id}
        )

        return JSONResponse(
            content=wrapped,
            status_code=500,
            headers={"X-Request-ID": request_id}
        )


# ============================================
# 4. 异常处理器
# ============================================

from fastapi import FastAPI
from fastapi.responses import JSONResponse


def setup_exception_handlers(app: FastAPI):
    """设置异常处理器"""

    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException):
        """API异常处理器"""
        wrapped = ResponseWrapper.error(
            code=exc.code,
            message=exc.message,
            error_type=exc.error_type,
            details=exc.details
        )
        return JSONResponse(
            content=wrapped,
            status_code=exc.http_status,
            headers={"X-Request-ID": get_request_id() or ""}
        )

    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError):
        """验证异常处理器"""
        details = []
        for error in exc.errors():
            details.append({
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "value": error.get("input")
            })

        wrapped = ResponseWrapper.error(
            code=ErrorCode.VALIDATION_ERROR,
            message="请求参数验证失败",
            error_type="validation_error",
            details={"errors": details}
        )
        return JSONResponse(content=wrapped, status_code=422)

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """通用异常处理器"""
        import logging
        logger = logging.getLogger(__name__)
        request_id = get_request_id() or ""
        logger.error(f"[{request_id}] Unhandled exception: {exc}", exc_info=True)

        wrapped = ResponseWrapper.error(
            code=ErrorCode.INTERNAL_ERROR,
            message="服务器内部错误，请稍后重试",
            error_type="internal_error",
            details={"reference": request_id}
        )
        return JSONResponse(content=wrapped, status_code=500)


# ============================================
# 5. 路由装饰器
# ============================================

T = TypeVar("T")


def api_response(
    message: str = "success",
    code: int = 0
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """API响应装饰器

    用于自动包装函数返回值为标准响应格式
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Dict[str, Any]:
            result = await func(*args, **kwargs)
            return ResponseWrapper.success(data=result, message=message, code=code)
        return wrapper
    return decorator


# ============================================
# 6. 响应工厂便捷函数
# ============================================

# 成功响应
def success(data: Any = None, message: str = "success") -> Dict[str, Any]:
    return ResponseWrapper.success(data=data, message=message)


def created(data: Any, message: str = "创建成功") -> Dict[str, Any]:
    return ResponseWrapper.created(data=data, message=message)


def updated(data: Any, message: str = "更新成功") -> Dict[str, Any]:
    return ResponseWrapper.updated(data=data, message=message)


def deleted(deleted_id: str, message: str = "删除成功") -> Dict[str, Any]:
    return ResponseWrapper.deleted(deleted_id=deleted_id, message=message)


def paginated(
    data: list,
    page: int,
    limit: int,
    total: int,
    filters: Optional[Dict[str, Any]] = None,
    sort: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    return ResponseWrapper.paginated(
        data=data, page=page, limit=limit, total=total,
        filters=filters, sort=sort
    )


# 错误响应
def error(
    code: int,
    message: str,
    error_type: str = "api_error",
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    return ResponseWrapper.error(
        code=code, message=message,
        error_type=error_type, details=details
    )


# 导出
__all__ = [
    "RequestContext",
    "get_request_id",
    "set_request_id",
    "get_request_context",
    "ResponseWrapper",
    "APIResponseMiddleware",
    "setup_exception_handlers",
    "api_response",
    "success",
    "created",
    "updated",
    "deleted",
    "paginated",
    "error",
]

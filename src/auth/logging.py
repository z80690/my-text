# -*- coding: utf-8 -*-
"""
日志和错误处理模块

提供结构化日志和错误处理功能
"""

import os
import json
import sys
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from functools import wraps


class AuthLogger:
    """
    认证系统日志记录器
    """

    def __init__(self):
        """初始化日志记录器"""
        self.logger = logging.getLogger("auth")
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()

        # 配置日志级别
        self.logger.setLevel(getattr(logging, log_level, logging.INFO))

        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)

        # 日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)

    def log_auth_event(self, event_type: str, user_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        """
        记录认证事件

        参数:
            event_type: 事件类型（如 "login", "logout", "register", "password_reset"）
            user_id: 用户 ID（可选）
            metadata: 额外的元数据（可选）
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "metadata": metadata or {}
        }

        self.logger.info(f"AUTH_EVENT: {json.dumps(log_data, ensure_ascii=False)}")

    def log_error(self, error: str, context: Optional[Dict[str, Any]] = None):
        """
        记录错误

        参数:
            error: 错误消息
            context: 错误上下文（可选）
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "error": error,
            "context": context or {}
        }

        self.logger.error(f"AUTH_ERROR: {json.dumps(log_data, ensure_ascii=False)}")

    def log_warning(self, warning: str, context: Optional[Dict[str, Any]] = None):
        """
        记录警告

        参数:
            warning: 警告消息
            context: 警告上下文（可选）
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "warning": warning,
            "context": context or {}
        }

        self.logger.warning(f"AUTH_WARNING: {json.dumps(log_data, ensure_ascii=False)}")

    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """
        记录安全事件

        参数:
            event_type: 安全事件类型
            details: 事件详情
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "details": details
        }

        self.logger.warning(f"SECURITY_EVENT: {json.dumps(log_data, ensure_ascii=False)}")


# 全局日志记录器实例
_logger_instance: Optional[AuthLogger] = None


def get_logger() -> AuthLogger:
    """获取全局日志记录器实例"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = AuthLogger()
    return _logger_instance


def handle_errors(error_message: str = "内部服务器错误", status_code: int = 500):
    """
    错误处理装饰器

    参数:
        error_message: 默认错误消息
        status_code: 默认状态码

    返回:
        装饰器
    """
    def decorator(func):
        @wraps(func)
        def wrapper(event: Dict[str, Any], context) -> Dict[str, Any]:
            try:
                return func(event, context)
            except ValueError as e:
                logger = get_logger()
                logger.log_error(f"验证错误: {str(e)}", {"event": event})
                return {
                    "statusCode": 400,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({
                        "success": False,
                        "error": str(e) or "无效的请求"
                    }, ensure_ascii=False)
                }
            except PermissionError as e:
                logger = get_logger()
                logger.log_security_event("permission_denied", {"error": str(e)})
                return {
                    "statusCode": 403,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({
                        "success": False,
                        "error": "权限不足"
                    }, ensure_ascii=False)
                }
            except Exception as e:
                logger = get_logger()
                logger.log_error(f"未预期的错误: {str(e)}", {"event": event})
                return {
                    "statusCode": status_code,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({
                        "success": False,
                        "error": error_message
                    }, ensure_ascii=False)
                }
        return wrapper
    return decorator


class AuthenticationMetrics:
    """
    认证指标收集器

    用于收集和分析认证相关的指标
    """

    def __init__(self):
        """初始化指标收集器"""
        self.metrics: Dict[str, Any] = {
            "login_attempts": 0,
            "successful_logins": 0,
            "failed_logins": 0,
            "registrations": 0,
            "password_resets": 0,
            "token_refreshes": 0,
            "rate_limit_violations": 0
        }

    def increment(self, metric: str):
        """
        增加指标计数

        参数:
            metric: 指标名称
        """
        if metric in self.metrics:
            self.metrics[metric] += 1

    def get_metrics(self) -> Dict[str, Any]:
        """
        获取所有指标

        返回:
            指标字典
        """
        return self.metrics.copy()

    def get_success_rate(self) -> float:
        """
        获取登录成功率

        返回:
            成功率（0-1）
        """
        total = self.metrics["login_attempts"]
        if total == 0:
            return 0.0
        return self.metrics["successful_logins"] / total

    def reset(self):
        """重置所有指标"""
        for key in self.metrics:
            self.metrics[key] = 0


# 全局指标收集器实例
_metrics_instance: Optional[AuthenticationMetrics] = None


def get_metrics() -> AuthenticationMetrics:
    """获取全局指标收集器实例"""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = AuthenticationMetrics()
    return _metrics_instance


if __name__ == "__main__":
    # 测试代码
    print("=" * 50)
    print("日志和错误处理模块测试")
    print("=" * 50)

    logger = get_logger()

    # 测试日志记录
    logger.log_auth_event("login", user_id="test-user", metadata={"ip": "127.0.0.1"})
    logger.log_error("测试错误", {"context": "测试"})
    logger.log_warning("测试警告", {"context": "测试"})
    logger.log_security_event("rate_limit_exceeded", {"ip": "127.0.0.1"})

    # 测试指标收集
    metrics = get_metrics()
    metrics.increment("login_attempts")
    metrics.increment("successful_logins")
    print(f"\n指标: {json.dumps(metrics.get_metrics(), indent=2)}")
    print(f"登录成功率: {metrics.get_success_rate() * 100:.2f}%")

    print("=" * 50)

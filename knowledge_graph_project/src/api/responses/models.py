# -*- coding: utf-8 -*-
"""
API 响应模型
API Response Models

基于 REST API 响应格式规范定义的标准Pydantic模型

版本: 1.0.0
日期: 2026-01-20
"""

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field


# ============================================
# 1. 基础响应模型
# ============================================

class BaseResponse(BaseModel):
    """基础响应模型"""
    code: int = Field(..., description="状态码 (0表示成功)")
    message: str = Field(..., description="状态描述信息")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="响应时间")
    request_id: Optional[str] = Field(None, description="请求追踪ID")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat() + "Z"}


class SuccessResponse(BaseResponse):
    """成功响应模型"""
    data: Optional[Any] = Field(None, description="响应数据")
    meta: Optional[Dict[str, Any]] = Field(None, description="元数据")


class ErrorDetail(BaseModel):
    """错误详情模型"""
    field: Optional[str] = Field(None, description="字段名")
    message: str = Field(..., description="错误信息")
    value: Optional[Any] = Field(None, description="无效的值")
    type: Optional[str] = Field(None, description="错误类型")


class ErrorResponse(BaseResponse):
    """错误响应模型"""
    error: Optional[Dict[str, Any]] = Field(None, description="错误详情")


# ============================================
# 2. 分页响应模型
# ============================================

class PaginationMeta(BaseModel):
    """分页元数据"""
    page: int = Field(..., description="当前页码")
    limit: int = Field(..., description="每页数量")
    total: Optional[int] = Field(None, description="总数量")
    total_pages: Optional[int] = Field(None, description="总页数")
    has_next: bool = Field(..., description="是否有下一页")
    has_prev: bool = Field(..., description="是否有上一页")
    next_page: Optional[int] = Field(None, description="下一页页码")
    prev_page: Optional[int] = Field(None, description="上一页页码")
    cursor: Optional[str] = Field(None, description="游标分页的游标值")


class PaginationRequest(BaseModel):
    """分页请求参数"""
    page: int = Field(default=1, ge=1, description="当前页码")
    limit: int = Field(default=20, ge=1, le=100, description="每页数量")
    sort_by: Optional[str] = Field(default="created_at", description="排序字段")
    order: str = Field(default="desc", pattern="^(asc|desc)$", description="排序方向")


class SortApplied(BaseModel):
    """应用的排序"""
    field: str = Field(..., description="排序字段")
    direction: str = Field(..., description="排序方向")


class FiltersApplied(BaseModel):
    """应用的过滤器"""
    applied_filters: Dict[str, Any] = Field(default_factory=dict)


class PaginatedMeta(BaseModel):
    """分页完整元数据"""
    pagination: PaginationMeta = Field(..., description="分页信息")
    cursor: Optional[str] = Field(None, description="游标值")
    filters_applied: Dict[str, Any] = Field(default_factory=dict, description="应用的筛选")
    sort_applied: Optional[SortApplied] = Field(None, description="应用的排序")


class PaginatedResponse(BaseResponse):
    """分页响应模型"""
    data: List[Any] = Field(..., description="数据列表")
    meta: PaginatedMeta = Field(..., description="分页元数据")


# ============================================
# 3. 空响应
# ============================================

class EmptyResponse(BaseModel):
    """空响应"""
    pass


# ============================================
# 4. 批量操作响应
# ============================================

class BatchOperationItem(BaseModel):
    """批量操作项"""
    id: str = Field(..., description="资源ID")
    reason: Optional[str] = Field(None, description="失败原因")


class BatchOperationResult(BaseModel):
    """批量操作结果"""
    total_requested: int = Field(..., description="请求总数")
    total_succeeded: int = Field(..., description="成功数")
    total_failed: int = Field(..., description="失败数")
    succeeded_ids: List[str] = Field(default_factory=list, description="成功的ID列表")
    failed_items: List[BatchOperationItem] = Field(default_factory=list, description="失败的项")


class BatchResponse(SuccessResponse):
    """批量操作响应"""
    data: BatchOperationResult = Field(..., description="批量操作结果")


# ============================================
# 5. 业务响应模型
# ============================================

class UserInfo(BaseModel):
    """用户信息"""
    id: str = Field(..., description="用户ID")
    username: Optional[str] = Field(None, description="用户名")
    display_name: Optional[str] = Field(None, description="显示名称")
    email: Optional[str] = Field(None, description="邮箱")
    avatar_url: Optional[str] = Field(None, description="头像URL")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class ContentInfo(BaseModel):
    """内容信息"""
    id: str = Field(..., description="内容ID")
    external_content_id: Optional[str] = Field(None, description="外部内容ID")
    content_type: Optional[str] = Field(None, description="内容类型")
    title: Optional[str] = Field(None, description="标题")
    description: Optional[str] = Field(None, description="描述")
    cover_url: Optional[str] = Field(None, description="封面URL")
    author_id: Optional[str] = Field(None, description="作者ID")
    view_count: int = Field(default=0, description="播放/阅读数")
    like_count: int = Field(default=0, description="点赞数")
    comment_count: int = Field(default=0, description="评论数")
    published_at: Optional[datetime] = Field(None, description="发布时间")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    tags: List[str] = Field(default_factory=list, description="标签")
    topics: List[str] = Field(default_factory=list, description="话题")


class CommentInfo(BaseModel):
    """评论信息"""
    id: str = Field(..., description="评论ID")
    content_id: Optional[str] = Field(None, description="内容ID")
    author_id: Optional[str] = Field(None, description="作者ID")
    parent_id: Optional[str] = Field(None, description="父评论ID")
    root_id: Optional[str] = Field(None, description="根评论ID")
    content: Optional[str] = Field(None, description="评论内容")
    like_count: int = Field(default=0, description="点赞数")
    reply_count: int = Field(default=0, description="回复数")
    is_top: bool = Field(default=False, description="是否置顶")
    is_selected: bool = Field(default=False, description="是否精选")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class RelationInfo(BaseModel):
    """关系信息"""
    id: str = Field(..., description="关系ID")
    relation_type: str = Field(..., description="关系类型")
    source_entity_type: str = Field(..., description="源实体类型")
    source_entity_id: str = Field(..., description="源实体ID")
    target_entity_type: str = Field(..., description="目标实体类型")
    target_entity_id: str = Field(..., description="目标实体ID")
    weight: float = Field(default=1.0, description="关系权重")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="扩展属性")
    created_at: Optional[datetime] = Field(None, description="创建时间")


class TopicInfo(BaseModel):
    """话题信息"""
    id: str = Field(..., description="话题ID")
    external_topic_id: Optional[str] = Field(None, description="外部话题ID")
    name: str = Field(..., description="话题名称")
    description: Optional[str] = Field(None, description="话题描述")
    cover_url: Optional[str] = Field(None, description="封面URL")
    content_count: int = Field(default=0, description="内容数量")
    view_count: int = Field(default=0, description="浏览量")
    follower_count: int = Field(default=0, description="关注者数量")
    hot_score: float = Field(default=0.0, description="热度分数")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


# ============================================
# 6. 创建/更新响应
# ============================================

class CreateResult(BaseModel):
    """创建结果"""
    id: str = Field(..., description="创建的资源ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")


class UpdateResult(BaseModel):
    """更新结果"""
    id: str = Field(..., description="更新的资源ID")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")
    affected_rows: int = Field(default=1, description="受影响的行数")


class DeleteResult(BaseModel):
    """删除结果"""
    deleted_id: str = Field(..., description="删除的资源ID")
    deleted_count: int = Field(default=1, description="删除的数量")


# ============================================
# 7. 验证错误
# ============================================

class ValidationErrorResponse(ErrorResponse):
    """验证错误响应"""
    error: Dict[str, Any] = Field(
        ...,
        description="错误详情",
        example={
            "type": "validation_error",
            "details": [
                {"field": "email", "message": "邮箱格式不正确", "value": "invalid-email"}
            ]
        }
    )


# ============================================
# 8. 通用响应工厂函数
# ============================================

T = TypeVar("T")


class ResponseFactory:
    """响应工厂类"""

    @staticmethod
    def success(
        data: Any = None,
        message: str = "success",
        code: int = 0,
        meta: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ) -> SuccessResponse:
        """创建成功响应"""
        return SuccessResponse(
            code=code,
            message=message,
            data=data,
            meta=meta,
            request_id=request_id
        )

    @staticmethod
    def paginated(
        data: List[Any],
        page: int,
        limit: int,
        total: int,
        request_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        sort: Optional[Dict[str, str]] = None,
        cursor: Optional[str] = None
    ) -> PaginatedResponse:
        """创建分页响应"""
        total_pages = (total + limit - 1) // limit if total else None

        pagination_meta = PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages if total_pages else True,
            has_prev=page > 1,
            next_page=page + 1 if page < total_pages else None if total_pages else None,
            prev_page=page - 1 if page > 1 else None,
            cursor=cursor
        )

        paginated_meta = PaginatedMeta(
            pagination=pagination_meta,
            cursor=cursor,
            filters_applied=filters or {},
            sort_applied=SortApplied(
                field=sort.get("field", "created_at") if sort else "created_at",
                direction=sort.get("direction", "desc") if sort else "desc"
            ) if sort else None
        )

        return PaginatedResponse(
            code=0,
            message="success",
            data=data,
            meta=paginated_meta,
            request_id=request_id
        )

    @staticmethod
    def error(
        code: int,
        message: str,
        error_type: str = "api_error",
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ) -> ErrorResponse:
        """创建错误响应"""
        error_dict = {"type": error_type}
        if details:
            error_dict["details"] = details

        return ErrorResponse(
            code=code,
            message=message,
            error=error_dict,
            request_id=request_id
        )

    @staticmethod
    def validation_error(
        details: List[ErrorDetail],
        request_id: Optional[str] = None
    ) -> ValidationErrorResponse:
        """创建验证错误响应"""
        return ValidationErrorResponse(
            code=40001,
            message="请求参数验证失败",
            error={
                "type": "validation_error",
                "details": [d.dict() for d in details]
            },
            request_id=request_id
        )

    @staticmethod
    def created(
        data: Any,
        message: str = "创建成功",
        request_id: Optional[str] = None
    ) -> SuccessResponse:
        """创建资源成功响应"""
        return SuccessResponse(
            code=0,
            message=message,
            data=data,
            request_id=request_id
        )

    @staticmethod
    def updated(
        data: Any,
        message: str = "更新成功",
        request_id: Optional[str] = None
    ) -> SuccessResponse:
        """更新资源成功响应"""
        return SuccessResponse(
            code=0,
            message=message,
            data=data,
            request_id=request_id
        )

    @staticmethod
    def deleted(
        deleted_id: str,
        message: str = "删除成功",
        request_id: Optional[str] = None
    ) -> SuccessResponse:
        """删除资源成功响应"""
        return SuccessResponse(
            code=0,
            message=message,
            data={"deleted_id": deleted_id},
            request_id=request_id
        )

    @staticmethod
    def batch(
        result: BatchOperationResult,
        message: str = "批量操作完成",
        request_id: Optional[str] = None
    ) -> BatchResponse:
        """批量操作响应"""
        return BatchResponse(
            code=0,
            message=message,
            data=result,
            request_id=request_id
        )


# 导出
__all__ = [
    "BaseResponse",
    "SuccessResponse",
    "ErrorResponse",
    "ErrorDetail",
    "PaginationMeta",
    "PaginationRequest",
    "PaginatedMeta",
    "PaginatedResponse",
    "EmptyResponse",
    "BatchOperationItem",
    "BatchOperationResult",
    "BatchResponse",
    "UserInfo",
    "ContentInfo",
    "CommentInfo",
    "RelationInfo",
    "TopicInfo",
    "CreateResult",
    "UpdateResult",
    "DeleteResult",
    "ValidationErrorResponse",
    "ResponseFactory",
]

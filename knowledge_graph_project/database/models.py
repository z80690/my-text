# -*- coding: utf-8 -*-
"""
数据库模型模块
Database Models Module

定义知识图谱数据库的Pydantic模型
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


# ==================== 枚举定义 ====================

class PlatformType(str, Enum):
    """平台类型"""
    BILIBILI = "bilibili"
    TOUTIAO = "toutiao"
    OTHER = "other"


class UserStatus(str, Enum):
    """用户状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"
    VERIFIED = "verified"


class ContentType(str, Enum):
    """内容类型"""
    VIDEO = "video"
    ARTICLE = "article"
    DYNAMIC = "dynamic"
    COMMENT = "comment"
    LIVE = "live"
    SHORT_VIDEO = "short_video"
    QA = "问答"  # 问答
    COLUMN = "专栏"  # 专栏
    GALLERY = "图集"  # 图集


class RelationType(str, Enum):
    """关系类型"""
    FOLLOWS = "follows"  # 关注
    FANS = "fans"  # 粉丝
    LIKES = "likes"  # 点赞
    COLLECTS = "collects"  # 收藏
    SHARES = "shares"  # 分享
    COMMENTS = "comments"  # 评论
    REPLIES = "replies"  # 回复
    MENTIONS = "mentions"  # 提及
    COLLABORATES = "collaborates"  # 合作
    PARTICIPATES = "participates"  # 参与
    CREATES = "creates"  # 创建
    TAGS = "tags"  # 标签
    CATEGORIZES = "categorizes"  # 分类
    FEATURES = "features"  # 特性
    SIMILAR_TO = "similar_to"  # 相似
    DERIVED_FROM = "derived_from"  # 衍生
    TOPIC_OF = "topic_of"  # 话题
    LOCATION_OF = "location_of"  # 位置
    LANGUAGE_OF = "language_of"  # 语言
    AWARDS = "awards"  # 获奖
    PROMOTES = "promotes"  # 推荐
    DISPUTES = "disputes"  # 争议
    RELATED = "related"  # 相关


# ==================== 基础模型 ====================

class BaseEntity(BaseModel):
    """基础实体模型"""
    id: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Platform(BaseEntity):
    """平台模型"""
    platform_key: str
    platform_name: str
    platform_url: Optional[str] = None
    api_base_url: Optional[str] = None
    is_active: bool = True
    config: Dict[str, Any] = {}


# ==================== 用户模型 ====================

class UserBase(BaseEntity):
    """用户基础模型"""
    platform_id: Optional[UUID] = None
    external_user_id: str
    username: Optional[str] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    gender: Optional[str] = None
    birthday: Optional[datetime] = None
    location: Optional[str] = None
    is_verified: bool = False
    verification_type: Optional[str] = None
    profile_url: Optional[str] = None
    level: int = 0
    experience: int = 0
    coins: int = 0
    tags: List[str] = []
    interests: List[str] = []


class User(UserBase):
    """完整用户模型"""
    follower_count: int = 0
    following_count: int = 0
    video_count: int = 0
    article_count: int = 0
    like_count: int = 0
    play_count: int = 0
    read_count: int = 0
    status: UserStatus = UserStatus.ACTIVE
    last_active_at: Optional[datetime] = None


class UserCreate(BaseModel):
    """用户创建模型"""
    platform_key: str
    external_user_id: str
    username: Optional[str] = None
    display_name: Optional[str] = None


class UserUpdate(BaseModel):
    """用户更新模型"""
    username: Optional[str] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    tags: Optional[List[str]] = None
    interests: Optional[List[str]] = None


class UserStats(BaseModel):
    """用户统计模型"""
    user_id: UUID
    follower_count: int = 0
    following_count: int = 0
    video_count: int = 0
    article_count: int = 0
    like_count: int = 0
    play_count: int = 0
    read_count: int = 0


# ==================== 内容模型 ====================

class ContentBase(BaseEntity):
    """内容基础模型"""
    platform_id: Optional[UUID] = None
    external_content_id: str
    content_type: ContentType
    author_id: Optional[UUID] = None
    title: Optional[str] = None
    description: Optional[str] = None
    content_text: Optional[str] = None
    content_html: Optional[str] = None


class Content(ContentBase):
    """完整内容模型"""
    cover_url: Optional[str] = None
    thumbnail_urls: List[str] = []
    video_url: Optional[str] = None
    duration: Optional[int] = None  # 视频时长(秒)
    view_count: int = 0
    like_count: int = 0
    dislike_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    collect_count: int = 0
    coin_count: int = 0
    danmaku_count: int = 0
    score: float = 0.0
    category_id: Optional[str] = None
    category_name: Optional[str] = None
    tags: List[str] = []
    topics: List[str] = []
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_name: Optional[str] = None
    published_at: Optional[datetime] = None
    is_deleted: bool = False
    is_top: bool = False
    is_featured: bool = False
    raw_data: Dict[str, Any] = {}


class ContentCreate(BaseModel):
    """内容创建模型"""
    platform_key: str
    external_content_id: str
    content_type: ContentType
    title: Optional[str] = None
    description: Optional[str] = None
    author_external_id: Optional[str] = None


class ContentFilter(BaseModel):
    """内容筛选模型"""
    platform_key: Optional[str] = None
    content_type: Optional[ContentType] = None
    author_id: Optional[UUID] = None
    tags: Optional[List[str]] = None
    topics: Optional[List[str]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_view_count: Optional[int] = None
    max_view_count: Optional[int] = None
    limit: int = 100
    offset: int = 0


# ==================== 评论模型 ====================

class Comment(BaseEntity):
    """评论模型"""
    platform_id: Optional[UUID] = None
    external_comment_id: str
    content_id: Optional[UUID] = None
    parent_id: Optional[UUID] = None
    root_id: Optional[UUID] = None
    author_id: Optional[UUID] = None
    content: str
    like_count: int = 0
    reply_count: int = 0
    is_top: bool = False
    is_selected: bool = False
    raw_data: Dict[str, Any] = {}


class CommentCreate(BaseModel):
    """评论创建模型"""
    platform_key: str
    external_comment_id: str
    content_external_id: Optional[str] = None
    parent_external_id: Optional[str] = None
    author_external_id: Optional[str] = None
    content: str


# ==================== 关系模型 ====================

class Relation(BaseEntity):
    """关系模型"""
    platform_id: Optional[UUID] = None
    relation_type: RelationType
    source_entity_type: str
    source_entity_id: UUID
    target_entity_type: str
    target_entity_id: UUID
    weight: float = 1.0
    metadata: Dict[str, Any] = {}
    expires_at: Optional[datetime] = None


class RelationCreate(BaseModel):
    """关系创建模型"""
    platform_key: str
    relation_type: RelationType
    source_entity_type: str
    source_entity_id: UUID
    target_entity_type: str
    target_entity_id: UUID
    weight: float = 1.0
    metadata: Optional[Dict[str, Any]] = None


class RelationFilter(BaseModel):
    """关系筛选模型"""
    platform_key: Optional[str] = None
    relation_type: Optional[RelationType] = None
    source_entity_type: Optional[str] = None
    source_entity_id: Optional[UUID] = None
    target_entity_type: Optional[str] = None
    target_entity_id: Optional[UUID] = None
    limit: int = 100


# ==================== 话题模型 ====================

class Topic(BaseEntity):
    """话题模型"""
    platform_id: Optional[UUID] = None
    external_topic_id: str
    name: str
    description: Optional[str] = None
    cover_url: Optional[str] = None
    profile_url: Optional[str] = None
    content_count: int = 0
    view_count: int = 0
    follower_count: int = 0
    hot_score: float = 0.0


# ==================== 分类模型 ====================

class Category(BaseEntity):
    """分类模型"""
    platform_id: Optional[UUID] = None
    external_category_id: str
    name: str
    parent_id: Optional[UUID] = None
    icon_url: Optional[str] = None
    description: Optional[str] = None
    level: int = 1
    path: List[str] = []
    content_count: int = 0
    sort_order: int = 0


# ==================== 会话模型 ====================

class Session(BaseEntity):
    """会话模型"""
    platform_id: Optional[UUID] = None
    session_name: str
    cookies: Dict[str, Any]
    user_agent: Optional[str] = None
    local_storage: Dict[str, Any] = {}
    session_storage: Dict[str, Any] = {}
    is_valid: bool = True
    last_validated_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    bound_user_id: Optional[UUID] = None
    expires_at: Optional[datetime] = None


class SessionCreate(BaseModel):
    """会话创建模型"""
    platform_key: str
    session_name: str
    cookies: Dict[str, Any]
    user_agent: Optional[str] = None
    local_storage: Optional[Dict[str, Any]] = None
    session_storage: Optional[Dict[str, Any]] = None


# ==================== 任务模型 ====================

class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class CrawlTask(BaseEntity):
    """采集任务模型"""
    platform_id: Optional[UUID] = None
    task_type: str
    target_type: str
    target_id: str
    target_name: Optional[str] = None
    config: Dict[str, Any] = {}
    status: TaskStatus = TaskStatus.PENDING
    progress: float = 0.0
    total_count: int = 0
    success_count: int = 0
    fail_count: int = 0
    error_message: Optional[str] = None
    retry_count: int = 0
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


# ==================== 响应模型 ====================

class APIResponse(BaseModel):
    """API响应模型"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class PaginatedResponse(BaseModel):
    """分页响应模型"""
    success: bool
    total: int
    limit: int
    offset: int
    data: List[Dict[str, Any]]


# ==================== 图谱查询模型 ====================

class GraphNode(BaseModel):
    """图谱节点"""
    id: UUID
    entity_type: str  # user, content, comment, topic
    name: str
    properties: Dict[str, Any] = {}


class GraphEdge(BaseModel):
    """图谱边"""
    id: UUID
    source_id: UUID
    target_id: UUID
    relation_type: str
    weight: float = 1.0


class GraphQuery(BaseModel):
    """图谱查询模型"""
    start_node_type: str
    start_node_id: UUID
    relation_types: Optional[List[str]] = None
    max_depth: int = 2
    limit_per_node: int = 10


class GraphResult(BaseModel):
    """图谱查询结果"""
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    path_count: int = 0

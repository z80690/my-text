# REST API 响应格式规范

## REST API Response Format Standard

**版本**: 1.0.0  
**创建日期**: 2026-01-20  
**适用项目**: 知识图谱数据库系统  
**技术栈**: Python FastAPI + PostgreSQL/Supabase

---

## 1. 概述

### 1.1 规范目的

本规范定义项目所有REST API接口的响应格式标准，确保：
- 前端与后端接口一致，减少对接成本
- 错误处理标准化，便于问题排查
- 响应数据结构统一，提升代码可维护性
- 支持多种编程语言和框架

### 1.2 设计原则

| 原则 | 说明 |
|------|------|
| **一致性** | 所有API遵循相同的响应结构 |
| **自描述** | 响应包含足够的元数据供客户端理解 |
| **可扩展** | 支持在不破坏现有客户端的情况下添加字段 |
| **安全性** | 敏感信息不暴露在错误响应中 |

---

## 2. 响应结构

### 2.1 通用响应模板

所有API响应必须包含以下基础结构：

```json
{
    "code": 0,
    "message": "success",
    "data": { ... },
    "meta": { ... },
    "timestamp": "2026-01-20T12:00:00Z",
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 2.2 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `code` | integer | ✅ | 状态码（0表示成功） |
| `message` | string | ✅ | 状态描述信息 |
| `data` | object/array | ❌ | 响应数据（成功时必有） |
| `meta` | object | ❌ | 元数据（分页、统计等） |
| `timestamp` | string | ✅ | 响应时间（ISO 8601格式） |
| `request_id` | string | ✅ | 请求追踪ID |

### 2.3 响应类型分类

```
API响应
├── 成功响应 (Success)
│   ├── 单资源 (Single Resource)
│   ├── 资源列表 (List)
│   └── 分页列表 (Paginated List)
│
├── 错误响应 (Error)
│   ├── 客户端错误 (Client Error - 4xx)
│   ├── 服务端错误 (Server Error - 5xx)
│   └── 业务错误 (Business Error)
│
└── 空响应 (Empty)
    └── 204 No Content
```

---

## 3. 成功响应

### 3.1 单资源响应

**场景**: GET /api/users/{id}

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "username": "zhangsan",
        "display_name": "张三",
        "email": "zhangsan@example.com",
        "created_at": "2026-01-15T10:30:00Z"
    },
    "timestamp": "2026-01-20T12:00:00Z",
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 3.2 资源列表响应

**场景**: GET /api/contents

```json
{
    "code": 0,
    "message": "success",
    "data": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "title": "Python入门教程",
            "content_type": "video",
            "view_count": 1000
        },
        {
            "id": "660e8400-e29b-41d4-a716-446655440001",
            "title": "FastAPI高级教程",
            "content_type": "article",
            "view_count": 2500
        }
    ],
    "timestamp": "2026-01-20T12:00:00Z",
    "request_id": "770e8400-e29b-41d4-a716-446655440000"
}
```

### 3.3 分页响应

**场景**: GET /api/contents?page=1&limit=20

```json
{
    "code": 0,
    "message": "success",
    "data": [...],
    "meta": {
        "pagination": {
            "page": 1,
            "limit": 20,
            "total": 150,
            "total_pages": 8,
            "has_next": true,
            "has_prev": false
        },
        "filters_applied": {
            "content_type": "video",
            "published_after": "2026-01-01T00:00:00Z"
        }
    },
    "timestamp": "2026-01-20T12:00:00Z",
    "request_id": "880e8400-e29b-41d4-a716-446655440000"
}
```

### 3.4 创建操作响应

**场景**: POST /api/users

```json
{
    "code": 0,
    "message": "用户创建成功",
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "username": "newuser",
        "created_at": "2026-01-20T12:00:00Z"
    },
    "timestamp": "2026-01-20T12:00:00Z",
    "request_id": "990e8400-e29b-41d4-a716-446655440000"
}
```

### 3.5 更新操作响应

**场景**: PUT /api/users/{id}

```json
{
    "code": 0,
    "message": "用户信息更新成功",
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "display_name": "李四",
        "updated_at": "2026-01-20T12:00:00Z"
    },
    "timestamp": "2026-01-20T12:00:00Z",
    "request_id": "aa0e8400-e29b-41d4-a716-446655440000"
}
```

### 3.6 删除操作响应

**场景**: DELETE /api/users/{id}

```json
{
    "code": 0,
    "message": "用户删除成功",
    "data": {
        "deleted_id": "550e8400-e29b-41d4-a716-446655440000"
    },
    "timestamp": "2026-01-20T12:00:00Z",
    "request_id": "bb0e8400-e29b-41d4-a716-446655440000"
}
```

### 3.7 空数据响应

**场景**: 资源不存在但请求有效

```json
{
    "code": 0,
    "message": "success",
    "data": null,
    "timestamp": "2026-01-20T12:00:00Z",
    "request_id": "cc0e8400-e29b-41d4-a716-446655440000"
}
```

### 3.8 批量操作响应

**场景**: POST /api/contents/batch-delete

```json
{
    "code": 0,
    "message": "批量删除完成",
    "data": {
        "total_requested": 10,
        "total_deleted": 8,
        "failed": [
            {
                "id": "550e8400-e29b-41d4-a716-446655440001",
                "reason": "资源不存在"
            }
        ],
        "succeeded_ids": [
            "550e8400-e29b-41d4-a716-446655440000"
        ]
    },
    "timestamp": "2026-01-20T12:00:00Z",
    "request_id": "dd0e8400-e29b-41d4-a716-446655440000"
}
```

---

## 4. 错误响应

### 4.1 错误响应结构

```json
{
    "code": 40001,
    "message": "请求参数验证失败",
    "error": {
        "type": "validation_error",
        "details": [
            {
                "field": "email",
                "message": "邮箱格式不正确",
                "value": "invalid-email"
            }
        ]
    },
    "timestamp": "2026-01-20T12:00:00Z",
    "request_id": "ee0e8400-e29b-41d4-a716-446655440000"
}
```

### 4.2 HTTP状态码对照表

| HTTP状态码 | 说明 | 场景 |
|-----------|------|------|
| 200 | OK | 请求成功 |
| 201 | Created | 资源创建成功 |
| 204 | No Content | 删除成功，无返回内容 |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未认证 |
| 403 | Forbidden | 无权限 |
| 404 | Not Found | 资源不存在 |
| 409 | Conflict | 资源冲突 |
| 422 | Unprocessable Entity | 参数验证失败 |
| 429 | Too Many Requests | 请求过于频繁 |
| 500 | Internal Server Error | 服务器内部错误 |
| 503 | Service Unavailable | 服务不可用 |

### 4.3 业务错误码定义

| 错误码 | HTTP状态码 | 说明 |
|--------|-----------|------|
| 0 | - | 成功 |
| 40001 | 400 | 请求参数验证失败 |
| 40002 | 400 | 请求参数格式错误 |
| 40003 | 400 | 缺少必需参数 |
| 40101 | 401 | 未认证 |
| 40102 | 401 | Token已过期 |
| 40301 | 403 | 无权限访问 |
| 40302 | 403 | 禁止操作 |
| 40401 | 404 | 资源不存在 |
| 40402 | 404 | 页面不存在 |
| 40901 | 409 | 资源已存在 |
| 40902 | 409 | 资源冲突 |
| 42201 | 422 | 参数验证失败 |
| 42901 | 429 | 请求过于频繁 |
| 50001 | 500 | 服务器内部错误 |
| 50002 | 500 | 数据库错误 |
| 50003 | 500 | 外部服务调用失败 |
| 50301 | 503 | 服务维护中 |

### 4.4 客户端错误示例

**400 - 请求参数错误**

```json
{
    "code": 40001,
    "message": "请求参数验证失败",
    "error": {
        "type": "validation_error",
        "details": [
            {
                "field": "email",
                "message": "邮箱格式不正确",
                "value": "not-an-email"
            },
            {
                "field": "age",
                "message": "年龄必须在0-150之间",
                "value": 200
            }
        ]
    },
    "timestamp": "2026-01-20T12:00:00Z",
    "request_id": "ff0e8400-e29b-41d4-a716-446655440000"
}
```

**401 - 未认证**

```json
{
    "code": 40101,
    "message": "请先登录",
    "error": {
        "type": "authentication_error",
        "details": "缺少认证Token"
    },
    "timestamp": "2026-01-20T12:00:00Z",
    "request_id": "001e8400-e29b-41d4-a716-446655440000"
}
```

**403 - 无权限**

```json
{
    "code": 40301,
    "message": "无权访问此资源",
    "error": {
        "type": "authorization_error",
        "details": "需要管理员权限"
    },
    "timestamp": "2026-01-20T12:00:00Z",
    "request_id": "002e8400-e29b-41d4-a716-446655440000"
}
```

**404 - 资源不存在**

```json
{
    "code": 40401,
    "message": "用户不存在",
    "error": {
        "type": "not_found",
        "details": {
            "resource_type": "user",
            "resource_id": "non-existent-id"
        }
    },
    "timestamp": "2026-01-20T12:00:00Z",
    "request_id": "003e8400-e29b-41d4-a716-446655440000"
}
```

**409 - 资源冲突**

```json
{
    "code": 40901,
    "message": "用户名已存在",
    "error": {
        "type": "conflict",
        "details": {
            "field": "username",
            "value": "existing_user"
        }
    },
    "timestamp": "2026-01-20T12:00:00Z",
    "request_id": "004e8400-e29b-41d4-a716-446655440000"
}
```

### 4.5 服务器错误示例

**500 - 服务器内部错误**

```json
{
    "code": 50001,
    "message": "服务器内部错误，请稍后重试",
    "error": {
        "type": "internal_error",
        "reference": "log_id_12345"
    },
    "timestamp": "2026-01-20T12:00:00Z",
    "request_id": "005e8400-e29b-41d4-a716-446655440000"
}
```

**503 - 服务不可用**

```json
{
    "code": 50301,
    "message": "服务维护中，请稍后访问",
    "error": {
        "type": "service_unavailable",
        "details": {
            "maintenance_window": "2026-01-21 02:00 - 04:00",
            "estimated_completion": "2026-01-21T04:00:00Z"
        }
    },
    "timestamp": "2026-01-20T12:00:00Z",
    "request_id": "006e8400-e29b-41d4-a716-446655440000"
}
```

---

## 5. 分页规范

### 5.1 分页参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `page` | integer | ❌ | 1 | 当前页码 |
| `limit` | integer | ❌ | 20 | 每页数量 |
| `sort_by` | string | ❌ | created_at | 排序字段 |
| `order` | string | ❌ | desc | 排序方向 (asc/desc) |

### 5.2 分页响应结构

```json
{
    "code": 0,
    "message": "success",
    "data": [...],
    "meta": {
        "pagination": {
            "page": 1,
            "limit": 20,
            "total": 150,
            "total_pages": 8,
            "has_next": true,
            "has_prev": false,
            "next_page": 2,
            "prev_page": null
        },
        "cursor": null,
        "filters_applied": {},
        "sort_applied": {
            "field": "created_at",
            "direction": "desc"
        }
    },
    "timestamp": "2026-01-20T12:00:00Z",
    "request_id": "007e8400-e29b-41d4-a716-446655440000"
}
```

### 5.3 游标分页响应

```json
{
    "code": 0,
    "message": "success",
    "data": [...],
    "meta": {
        "pagination": {
            "page": null,
            "limit": 20,
            "total": null,
            "total_pages": null,
            "has_next": true,
            "has_prev": false,
            "next_cursor": "cursor_token_abc123",
            "prev_cursor": null
        },
        "cursor": "initial_cursor",
        "filters_applied": {},
        "sort_applied": {
            "field": "created_at",
            "direction": "desc"
        }
    },
    "timestamp": "2026-01-20T12:00:00Z",
    "request_id": "008e8400-e29b-41d4-a716-446655440000"
}
```

---

## 6. HTTP方法语义

### 6.1 方法与响应对照

| HTTP方法 | 用途 | 成功状态码 | 响应示例 |
|---------|------|-----------|---------|
| GET | 获取资源 | 200 | 返回资源/列表 |
| POST | 创建资源 | 201 | 返回创建的资源 |
| PUT | 全量更新 | 200 | 返回更新后的资源 |
| PATCH | 部分更新 | 200 | 返回更新后的资源 |
| DELETE | 删除资源 | 204 | 空响应 |

### 6.2 幂等性

| HTTP方法 | 幂等 | 缓存 |
|---------|------|------|
| GET | ✅ | ✅ |
| PUT | ✅ | ❌ |
| DELETE | ✅ | ❌ |
| POST | ❌ | ❌ |
| PATCH | ❌ | ❌ |

---

## 7. 实现指南

### 7.1 FastAPI实现

请参考以下文件：
- `src/api/responses/` - 响应模型定义
- `src/api/middleware/response_wrapper.py` - 响应包装中间件
- `src/api/exceptions/` - 自定义异常

### 7.2 响应包装器使用

```python
from src.api.responses import success_response, error_response, paginated_response

# 成功响应
return success_response(data=user)

# 分页响应
return paginated_response(
    data=contents,
    page=page,
    limit=limit,
    total=total
)

# 错误响应
return error_response(code=40401, message="用户不存在")
```

### 7.3 异常处理

```python
from src.api.exceptions import APIException, ErrorCode

# 抛出业务异常
raise APIException(
    code=ErrorCode.RESOURCE_NOT_FOUND,
    message="用户不存在",
    details={"user_id": user_id}
```

---

## 8. 最佳实践

### 8.1 消息指南

| 场景 | 示例 |
|------|------|
| 成功 | "success"、"操作成功"、"删除成功" |
| 参数错误 | "请求参数验证失败"、"邮箱格式不正确" |
| 权限错误 | "无权访问"、"请先登录" |
| 资源错误 | "用户不存在"、"内容已删除" |

### 8.2 字段命名

| 场景 | 规范 |
|------|------|
| API请求 | snake_case (email, user_id) |
| API响应 | snake_case (email, user_id) |
| 数据库 | snake_case (email, user_id) |
| JavaScript | camelCase (email, userId) |

### 8.3 敏感数据

❌ **禁止**在错误响应中暴露：
- 数据库错误详情
- 文件路径
- 内部IP地址
- 认证凭据
- 个人信息

✅ **应该**返回：
- 通用错误消息
- 错误类型
- 内部追踪ID（供运维排查）

---

## 9. 版本管理

### 9.1 响应格式版本

```json
{
    "code": 0,
    "message": "success",
    "data": {...},
    "meta": {
        "api_version": "v1",
        "response_format": "2.0"
    },
    "timestamp": "2026-01-20T12:00:00Z",
    "request_id": "009e8400-e29b-41d4-a716-446655440000"
}
```

### 9.2 破坏性变更

当需要破坏现有响应格式时：
1. 增加 `meta.api_version` 字段
2. 新版本使用新的响应结构
3. 保留旧版本支持（可通过请求头切换）
4. 文档明确标注版本差异

---

## 10. 快速参考

### 10.1 成功响应模板

```json
{
    "code": 0,
    "message": "success",
    "data": { ... },
    "timestamp": "ISO8601",
    "request_id": "UUID"
}
```

### 10.2 错误响应模板

```json
{
    "code": 错误码,
    "message": "错误描述",
    "error": {
        "type": "错误类型",
        "details": { ... }
    },
    "timestamp": "ISO8601",
    "request_id": "UUID"
}
```

### 10.3 分页响应模板

```json
{
    "code": 0,
    "message": "success",
    "data": [...],
    "meta": {
        "pagination": {
            "page": 1,
            "limit": 20,
            "total": 100,
            "total_pages": 5,
            "has_next": true,
            "has_prev": false
        }
    },
    "timestamp": "ISO8601",
    "request_id": "UUID"
}
```

---

**文档版本**: 1.0.0  
**最后更新**: 2026-01-20  
**维护者**: 知识图谱项目组

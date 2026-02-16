# 用户资料管理 API 文档

## 目录

1. [概述](#概述)
2. [获取用户资料](#获取用户资料)
3. [更新用户资料](#更新用户资料)
4. [错误处理](#错误处理)
5. [字段验证规则](#字段验证规则)

---

## 概述

用户资料管理 API 提供以下功能：
- 获取用户完整资料信息
- 更新用户资料字段（display_name, avatar_url, bio, phone, website, preferences）

所有端点通过云函数主入口调用，使用 `action` 参数区分不同操作。

**基础 URL**: `https://your-function-url.amazonaws.com/`

**认证**: 通过 Supabase API Key (anon) 进行认证

---

## 获取用户资料

获取指定用户的完整资料信息。

### 请求

```http
POST / HTTP/1.1
Content-Type: application/json

{
  "action": "get_profile",
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### cURL 示例

```bash
curl -X POST https://your-function-url.amazonaws.com/ \
  -H "Content-Type: application/json" \
  -d '{
    "action": "get_profile",
    "user_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

### Python 示例

```python
import requests

response = requests.post(
    "https://your-function-url.amazonaws.com/",
    json={
        "action": "get_profile",
        "user_id": "550e8400-e29b-41d4-a716-446655440000"
    }
)
print(response.json())
```

### 成功响应

```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "display_name": "张三",
    "avatar_url": "https://example.com/avatar.jpg",
    "bio": "软件工程师",
    "phone": "13800138000",
    "website": "https://example.com",
    "preferences": {
      "theme": "dark",
      "language": "zh-CN",
      "notifications": true
    },
    "stats": {
      "login_count": 15,
      "posts_count": 3
    },
    "is_active": true,
    "last_login_at": "2026-01-17T10:00:00Z",
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": "2026-01-17T10:00:00Z"
  }
}
```

### 错误响应 (404)

```json
{
  "success": false,
  "error": "Profile not found"
}
```

---

## 更新用户资料

更新用户的资料信息。支持部分更新，只提交需要更改的字段。

### 请求

```http
POST / HTTP/1.1
Content-Type: application/json

{
  "action": "update_profile",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "data": {
    "display_name": "新名称",
    "bio": "更新后的个人简介",
    "preferences": {
      "theme": "light"
    }
  }
}
```

### cURL 示例

```bash
curl -X POST https://your-function-url.amazonaws.com/ \
  -H "Content-Type: application/json" \
  -d '{
    "action": "update_profile",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "data": {
      "display_name": "新名称",
      "bio": "更新后的个人简介"
    }
  }'
```

### Python 示例

```python
import requests

response = requests.post(
    "https://your-function-url.amazonaws.com/",
    json={
        "action": "update_profile",
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "data": {
            "display_name": "新名称",
            "bio": "软件开发者",
            "preferences": {
                "theme": "dark",
                "language": "en-US"
            }
        }
    }
)
print(response.json())
```

### 成功响应

```json
{
  "success": true,
  "message": "Profile updated successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "display_name": "新名称",
    "bio": "更新后的个人简介",
    "preferences": {
      "theme": "light"
    },
    "updated_at": "2026-01-17T11:00:00Z"
  }
}
```

### 错误响应 (400 - 验证失败)

```json
{
  "success": false,
  "error": "display_name must be 100 characters or less"
}
```

---

## 错误处理

### 错误响应格式

```json
{
  "success": false,
  "error": "Error message description"
}
```

### HTTP 状态码

| 状态码 | 描述 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误或验证失败 |
| 404 | 用户资料不存在 |
| 500 | 服务器内部错误 |

### 常见错误码

| 错误码 | HTTP 状态码 | 错误信息 | 说明 |
|--------|-------------|----------|------|
| 4004 | 400 | `user_id is required` | 缺少 user_id 参数 |
| 4005 | 400 | `display_name must be a string` | display_name 类型错误 |
| 4006 | 400 | `display_name must be 100 characters or less` | 显示名称过长 |
| 4007 | 400 | `avatar_url must be a valid URL` | 头像 URL 格式无效 |
| 4008 | 400 | `website must be a valid URL` | 网站 URL 格式无效 |
| 4009 | 400 | `bio must be 500 characters or less` | 个人简介过长 |
| 4010 | 400 | `preferences must be a JSON object` | preferences 格式错误 |
| 4040 | 404 | `Profile not found` | 用户资料不存在 |

---

## 字段验证规则

### display_name

| 规则 | 值 |
|------|-----|
| 类型 | string |
| 必填 | 否 |
| 最大长度 | 100 字符 |
| 默认值 | 空字符串 |

### avatar_url

| 规则 | 值 |
|------|-----|
| 类型 | string (URL) |
| 必填 | 否 |
| 格式 | http:// 或 https:// 开头 |
| 默认值 | null |

### bio

| 规则 | 值 |
|------|-----|
| 类型 | string |
| 必填 | 否 |
| 最大长度 | 500 字符 |
| 默认值 | null |

### phone

| 规则 | 值 |
|------|-----|
| 类型 | string |
| 必填 | 否 |
| 最大长度 | 20 字符 |
| 默认值 | null |

### website

| 规则 | 值 |
|------|-----|
| 类型 | string (URL) |
| 必填 | 否 |
| 格式 | http:// 或 https:// 开头 |
| 默认值 | null |

### preferences

| 规则 | 值 |
|------|-----|
| 类型 | object (JSON) |
| 必填 | 否 |
| 默认值 | {} |

**preferences 示例**:

```json
{
  "theme": "dark",
  "language": "zh-CN",
  "notifications": true,
  "email_subscriptions": false,
  "timezone": "Asia/Shanghai"
}
```

---

## 完整请求示例

### 获取用户资料

```bash
curl -X POST https://your-function-url.amazonaws.com/ \
  -H "Content-Type: application/json" \
  -d '{
    "action": "get_profile",
    "user_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

### 更新头像和显示名称

```bash
curl -X POST https://your-function-url.amazonaws.com/ \
  -H "Content-Type: application/json" \
  -d '{
    "action": "update_profile",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "data": {
      "display_name": "李四",
      "avatar_url": "https://example.com/photos/user.jpg"
    }
  }'
```

### 更新偏好设置

```bash
curl -X POST https://your-function-url.amazonaws.com/ \
  -H "Content-Type: application/json" \
  -d '{
    "action": "update_profile",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "data": {
      "preferences": {
        "theme": "light",
        "language": "en-US",
        "notifications": false
      }
    }
  }'
```

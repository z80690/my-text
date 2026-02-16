# Project Overview

A full-stack application that provides data access to a knowledge base through Supabase integration. The project is designed to run as a serverless cloud function on Tencent Cloud, with a Python backend handling database queries and a frontend interface.

## Tech Stack

### Backend
- **Language**: Python 3.10
- **Framework**: Serverless Cloud Functions (Tencent Cloud SCF)
- **Database**: Supabase (PostgreSQL)
- **Key Libraries**:
  - `supabase==2.27.0` - Supabase Python client
  - `httpx==0.28.1` - Async HTTP client
  - `postgrest==2.27.0` - PostgREST client
  - `realtime==2.27.0` - Realtime subscriptions
  - `storage3==2.27.0` - Storage client
  - `supabase-auth==2.27.0` - Authentication
  - `supabase-functions==2.27.0` - Edge functions
  - `yarl==1.22.0` - URL parsing and handling
  - `httpcore==1.0.9` - HTTP core functionality
  - `h11==0.16.0` - HTTP/1.1 protocol implementation

### Frontend
- **Runtime**: Node.js
- **Current State**: Initial setup, awaiting implementation

### DevOps
- **Containerization**: Docker (Python 3.10-slim base image)
- **Deployment**: Tencent Cloud Serverless Cloud Functions
- **Port**: 9000 (Tencent Cloud SCF requirement)
- **Package Source**: Alibaba Cloud mirror for faster dependency installation in China

### Development Tools
- **LSP Server**: pylsp (Python Language Server Protocol)
- **Virtual Environment**: `my_clean_venv` (located at project root)
- **OpenCode Configuration**: `opencode.json` for AI-assisted development
- **IDE Support**: VSCode with debug configuration in `.vscode/launch.json`

## Project Structure

```
my-text/
├── backend/              # Backend Node.js setup (currently minimal)
│   ├── package.json
│   └── package-lock.json
├── frontend/             # Frontend setup
│   ├── package.json
│   └── package-lock.json
├── src/                  # Main Python application code
│   ├── index.py          # Main SCF handler for data queries
│   ├── requirements.txt  # Python dependencies
│   └── test_connectivity.py  # Connectivity testing suite
├── openspec/             # Project specification
│   └── project.md        # This file
├── Dockerfile            # Docker configuration
└── .vscode/              # IDE configuration
    └── launch.json
```

## Conventions

### Code Style
- **Encoding**: UTF-8 for all Python files
- **Type Hints**: Uses Python `typing` module for function signatures
- **Error Handling**: Try-except blocks with descriptive error messages
- **Comments**: Chinese language comments for code documentation
- **Indentation**: Standard 4-space indentation (PEP 8)

### Configuration Management
- **Environment Variables**: All sensitive data stored in environment variables
  - `SUPABASE_URL`: Supabase project URL
  - `SUPABASE_KEY`: Supabase API key (anon or service role)
  - `SUPABASE_JWT_SECRET`: JWT secret for token verification (auth specific)
  - `ACCESS_TOKEN_EXPIRY`: Access token expiration time in seconds (default: 3600)
  - `REFRESH_TOKEN_EXPIRY`: Refresh token expiration time in seconds (default: 604800)
  - `MIN_PASSWORD_LENGTH`: Minimum password length (default: 8)
- **No Hardcoded Secrets**: Never commit credentials to repository
- **Environment Template**: See `.env.example` for all required variables

### API Design
- **Handler Pattern**: Cloud function uses `main_handler(event, context)` entry point
- **Response Format**: HTTP response with statusCode, headers, and body
  ```python
  {
    'statusCode': 200,
    'headers': {'Content-Type': 'application/json'},
    'body': json.dumps(response_data, ensure_ascii=False)
  }
  ```
- **Database Operations**: Uses Supabase client for type-safe queries
  - Table: `knowledge_base`
  - Operations: `select()`, `limit()`, `execute()`

## API 接口文档

### 概述

本项目提供基于 Supabase 的知识库数据查询 API 和用户资料管理 API，通过腾讯云 SCF 部署为无服务器云函数。所有接口返回 JSON 格式数据，支持 CORS。

### 接口端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/` | GET/POST | 知识库数据查询主入口 |
| `/` | POST | 用户资料管理 (action=get_profile, action=update_profile) |

### 用户资料管理接口

#### 获取用户资料

请求参数：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `action` | string | 是 | 固定值: `get_profile` |
| `user_id` | string | 是 | 用户 UUID |

请求示例：

```json
{
  "action": "get_profile",
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

响应示例：

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
      "language": "zh-CN"
    },
    "stats": {
      "login_count": 10
    },
    "is_active": true,
    "last_login_at": "2026-01-17T10:00:00Z",
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": "2026-01-17T10:00:00Z"
  }
}
```

#### 更新用户资料

请求参数：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `action` | string | 是 | 固定值: `update_profile` |
| `user_id` | string | 是 | 用户 UUID |
| `data` | object | 是 | 要更新的资料字段 |

可选更新字段：

| 字段 | 类型 | 限制 |
|------|------|------|
| `display_name` | string | 最大 100 字符 |
| `avatar_url` | string | 有效 URL 格式 |
| `bio` | string | 最大 500 字符 |
| `phone` | string | 最大 20 字符 |
| `website` | string | 有效 URL 格式 |
| `preferences` | object | JSON 对象 |

请求示例：

```json
{
  "action": "update_profile",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "data": {
    "display_name": "新名称",
    "bio": "更新后的个人简介",
    "preferences": {
      "theme": "light",
      "notifications": true
    }
  }
}
```

响应示例：

```json
{
  "success": true,
  "message": "Profile updated successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "display_name": "新名称",
    "bio": "更新后的个人简介",
    "preferences": {
      "theme": "light",
      "notifications": true
    },
    "updated_at": "2026-01-17T10:00:00Z"
  }
}
```

### 请求格式

#### 请求参数（环境变量）

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `SUPABASE_URL` | string | 是 | Supabase 项目 URL |
| `SUPABASE_KEY` | string | 是 | Supabase API Key (anon 或 service_role) |

#### 请求体（可选）

当前主接口支持通过 `event` 参数传递查询配置：

```json
{
  "query": {
    "table": "knowledge_base",
    "limit": 5,
    "columns": "*"
  }
}
```

### 响应格式

#### 成功响应

```json
{
  "success": true,
  "message": "Query successful",
  "data": [...],
  "count": 5
}
```

| 字段 | 类型 | 描述 |
|------|------|------|
| `success` | boolean | 请求是否成功 |
| `message` | string | 结果描述信息 |
| `data` | array | 查询返回的数据记录 |
| `count` | integer | 返回记录数量 |

#### 错误响应

```json
{
  "error": "Error description"
}
```

### 状态码说明

| 状态码 | 描述 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误（缺少环境变量等） |
| 500 | 服务器内部错误 |

### 示例请求

#### cURL

```bash
curl -X GET https://your-function-url.amazonaws.com/ \
  -H "Content-Type: application/json"
```

#### Python

```python
import requests

response = requests.get(
    "https://your-function-url.amazonaws.com/",
    headers={"Content-Type": "application/json"}
)
print(response.json())
```

### 错误码详细说明

| 错误信息 | 原因 | 解决方案 |
|----------|------|----------|
| `SUPABASE_URL or SUPABASE_KEY is not set` | 环境变量未配置 | 检查部署平台的环境变量配置 |
| `relation "knowledge_base" does not exist` | 数据库表不存在 | 在 Supabase 中创建 knowledge_base 表 |
| `could not connect to server` | Supabase 连接失败 | 检查 SUPABASE_URL 是否正确 |

### Rate Limiting

当前版本未实现速率限制，生产环境建议：
- 腾讯云 SCF 已内置一定程度的并发控制
- 可通过 Supabase 配置行级安全策略 (RLS)
- 建议在 API Gateway 层添加 WAF 防护

## 错误处理

### 错误分类

| 错误类型 | HTTP 状态码 | 说明 |
|----------|-------------|------|
| 参数错误 | 400 | 请求参数缺失或格式错误 |
| 认证错误 | 401 | API Key 无效或过期 |
| 权限错误 | 403 | 无权限访问指定资源 |
| 资源不存在 | 404 | 查询的资源不存在 |
| 业务验证错误 | 400 | 用户资料字段验证失败 |
| 服务器错误 | 500 | 内部错误或数据库异常 |

### 详细错误码

| 错误码 | 错误信息 | 原因 | 解决方案 |
|--------|----------|------|----------|
| 4001 | `SUPABASE_URL or SUPABASE_KEY is not set` | 环境变量未配置 | 检查部署平台的环境变量配置 |
| 4002 | `Invalid SUPABASE_URL format` | URL 格式不正确 | 检查 URL 是否以 https:// 开头 |
| 4003 | `Invalid request format` | 请求体 JSON 解析失败 | 验证请求体为有效 JSON |
| 4004 | `user_id is required` | 缺少用户 ID | 确保请求包含 user_id 参数 |
| 4005 | `display_name must be a string` | 显示名称类型错误 | 检查 display_name 是否为字符串 |
| 4006 | `display_name must be 100 characters or less` | 显示名称过长 | 缩短 display_name 至 100 字符以内 |
| 4007 | `avatar_url must be a valid URL` | 头像 URL 格式错误 | 提供有效的 HTTP/HTTPS URL |
| 4008 | `website must be a valid URL` | 网站 URL 格式错误 | 提供有效的 HTTP/HTTPS URL |
| 4009 | `bio must be 500 characters or less` | 个人简介过长 | 缩短 bio 至 500 字符以内 |
| 4010 | `preferences must be a JSON object` | 偏好设置格式错误 | 确保 preferences 为 JSON 对象 |
| 4040 | `Profile not found` | 用户资料不存在 | 检查 user_id 是否正确 |
| 5001 | `Failed to create Supabase client` | 客户端初始化失败 | 检查 URL 和 Key 是否匹配 |
| 5002 | `relation "knowledge_base" does not exist` | 数据库表不存在 | 在 Supabase 中创建 knowledge_base 表 |
| 5003 | `could not connect to server` | Supabase 连接失败 | 检查 SUPABASE_URL 是否正确且服务可用 |
| 5004 | `Query execution failed` | 数据库查询错误 | 检查查询语法和表结构 |
| 5005 | `Timeout waiting for response` | 请求超时 | 检查 Supabase 服务状态 |

### 错误响应格式

```json
{
  "success": false,
  "error": {
    "code": 5001,
    "message": "Failed to create Supabase client",
    "details": "Connection timeout after 30 seconds"
  }
}
```

### 错误处理模式

#### 1. 环境变量验证

```python
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    return {
        'statusCode': 400,
        'body': json.dumps({
            'success': False,
            'error': {'code': 4001, 'message': 'SUPABASE_URL or SUPABASE_KEY is not set'}
        })
    }
```

#### 2. 数据库操作错误处理

```python
try:
    response = supabase.table("knowledge_base").select("*").limit(5).execute()
    return {
        'statusCode': 200,
        'body': json.dumps({
            'success': True,
            'data': response.data,
            'count': len(response.data)
        })
    }
except Exception as e:
    error_code = 5004
    if "relation" in str(e) and "does not exist" in str(e):
        error_code = 5002
    elif "connection" in str(e).lower():
        error_code = 5003
    
    return {
        'statusCode': 500,
        'body': json.dumps({
            'success': False,
            'error': {'code': error_code, 'message': str(e)}
        })
    }
```

### 最佳实践

1. **错误日志记录**: 所有错误应记录到日志系统，使用 `[ERROR]` 前缀
2. **错误信息脱敏**: 不在错误响应中暴露敏感信息（如数据库结构、内部路径）
3. **用户友好消息**: 对外返回通用错误信息，详细错误记录在服务端
4. **错误重试机制**: 对临时性错误（如网络超时）实现重试逻辑
5. **监控告警**: 关键错误应触发监控告警

### 调试模式

在开发环境可启用详细错误日志：

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

try:
    # ... database operations
except Exception as e:
    logger.debug(f"Full error details: {e}", exc_info=True)
```

### Testing
- **Integration Tests**: Comprehensive test suite in `test_connectivity.py`
- **Test Categories**:
  1. Environment variable validation (`test_env_vars`)
  2. Supabase client connection (`test_supabase_connection`)
  3. Database query execution (`test_db_query`)
- **Test Functions**: Return dict with `test`, `status`, `message` keys
- **Flexible Execution**: Supports command-line arguments and environment variables
- **Exit Codes**: Returns 0 for success, 1 for failure
- **Test Result Format**:
  ```python
  {
    "test": "test_name",
    "status": "PASSED" | "FAILED",
    "message": "description"
  }
  ```

### Deployment
- **Docker Build**: Multi-stage build process using slim Python image
- **Package Mirrors**: Uses Alibaba Cloud PyPI mirror for China region
- **Port Exposure**: Container exposes port 9000 for SCF compatibility

### LSP and AI Integration
- **LSP Server**: pylsp with comprehensive plugins enabled
  - pycodestyle: Code style checking (max 120 characters)
  - pyflakes: Linting and error detection
  - mccabe: Complexity analysis (threshold: 15)
  - pydocstyle: Docstring convention (PEP 257)
  - jedi: Code completion, definition lookup, hover help, symbols
- **OpenCode AI Features**:
  - Context awareness with symbol resolution
  - Codebase navigation with import following
  - Intelligent query handling with definitions and examples
  - Real-time error checking and diagnostics

## 数据库详细 Schema

### 数据库概述

本项目使用 Supabase（PostgreSQL）作为主数据库，采用以下设计原则：
- **认证相关表**: 使用 `auth` schema（Supabase 内置）
- **业务数据表**: 使用 `public` schema
- **安全策略**: 所有表启用行级安全（RLS）
- **审计追踪**: 认证事件记录在 `auth.audit_log` 表中

### ER 图

```
┌─────────────────────────────────────────────────────────────────┐
│                         auth.users                               │
│  (Supabase 内置认证表)                                           │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ 1:1 关联
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     public.user_profiles                         │
│  (用户资料扩展)                                                  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ 1:N 关联
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   public.user_role_assignments                   │
│  (用户角色关联)                                                  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ N:1 关联
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      public.user_roles                           │
│  (角色定义)                                                      │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ 1:N 关联
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      auth.audit_log                              │
│  (审计日志 - 可选)                                               │
└─────────────────────────────────────────────────────────────────┘
```

### 表结构详解

#### 1. public.user_profiles（用户资料表）

| 字段名 | 类型 | 约束 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `id` | UUID | PRIMARY KEY, REFERENCES auth.users(id) ON DELETE CASCADE | - | 用户 ID，主键 |
| `display_name` | TEXT | NOT NULL | '' | 显示名称 |
| `avatar_url` | TEXT | - | NULL | 头像 URL |
| `bio` | TEXT | - | NULL | 个人简介 |
| `phone` | TEXT | - | NULL | 电话号码 |
| `website` | TEXT | - | NULL | 个人网站 URL |
| `preferences` | JSONB | NOT NULL | '{}' | 用户偏好设置 |
| `stats` | JSONB | NOT NULL | '{}' | 统计数据 |
| `is_active` | BOOLEAN | NOT NULL | true | 是否激活 |
| `last_login_at` | TIMESTAMPTZ | - | NULL | 最后登录时间 |
| `metadata` | JSONB | NOT NULL | '{}' | 其他元数据 |
| `created_at` | TIMESTAMPTZ | NOT NULL | NOW() | 创建时间 |
| `updated_at` | TIMESTAMPTZ | NOT NULL | NOW() | 更新时间 |

**preferences 字段示例**:
```json
{
  "theme": "dark",
  "language": "zh-CN",
  "notifications": true,
  "email_subscriptions": false
}
```

**stats 字段示例**:
```json
{
  "login_count": 42,
  "posts_count": 15,
  "views_count": 1250
}
```

#### 2. public.user_roles（角色定义表）

| 字段名 | 类型 | 约束 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `id` | UUID | PRIMARY KEY | gen_random_uuid() | 角色 ID |
| `name` | TEXT | NOT NULL, UNIQUE | - | 角色名称 |
| `description` | TEXT | - | NULL | 角色描述 |
| `permissions` | JSONB | NOT NULL | '[]' | 权限列表 |
| `is_active` | BOOLEAN | NOT NULL | true | 是否启用 |
| `created_at` | TIMESTAMPTZ | NOT NULL | NOW() | 创建时间 |
| `updated_at` | TIMESTAMPTZ | NOT NULL | NOW() | 更新时间 |

**默认角色**:
| 角色名 | 权限 |
|--------|------|
| `user` | profile:read, profile:update |
| `admin` | 所有权限，包括用户管理、角色管理等 |
| `moderator` | profile:read, profile:update, users:read, users:update |

#### 3. public.user_role_assignments（用户角色关联表）

| 字段名 | 类型 | 约束 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `id` | UUID | PRIMARY KEY | gen_random_uuid() | 记录 ID |
| `user_id` | UUID | NOT NULL, REFERENCES auth.users(id) ON DELETE CASCADE | - | 用户 ID |
| `role_id` | UUID | NOT NULL, REFERENCES public.user_roles(id) ON DELETE CASCADE | - | 角色 ID |
| `assigned_at` | TIMESTAMPTZ | NOT NULL | NOW() | 分配时间 |
| `assigned_by` | UUID | REFERENCES auth.users(id) ON DELETE SET NULL | - | 分配者 ID |
| `expires_at` | TIMESTAMPTZ | - | NULL | 过期时间（可选） |

#### 4. auth.audit_log（审计日志表）

| 字段名 | 类型 | 约束 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `id` | BIGSERIAL | PRIMARY KEY | - | 日志 ID |
| `user_id` | UUID | REFERENCES auth.users(id) ON DELETE CASCADE | - | 用户 ID |
| `event_type` | TEXT | NOT NULL | - | 事件类型 |
| `metadata` | JSONB | - | NULL | 事件元数据 |
| `created_at` | TIMESTAMPTZ | - | NOW() | 创建时间 |

### 索引设计

| 表名 | 索引名 | 索引类型 | 字段 | 描述 |
|------|--------|----------|------|------|
| user_profiles | idx_user_profiles_display_name | B-tree | display_name | 搜索优化 |
| user_profiles | idx_user_profiles_is_active | B-tree | is_active | 条件过滤 |
| user_profiles | idx_user_profiles_created_at | B-tree | created_at DESC | 排序优化 |
| user_profiles | idx_user_profiles_updated_at | B-tree | updated_at DESC | 排序优化 |
| user_roles | idx_user_roles_name | B-tree | name | 唯一查找 |
| user_roles | idx_user_roles_is_active | B-tree | is_active | 条件过滤 |
| user_role_assignments | idx_user_role_assignments_user_id | B-tree | user_id | 用户查询 |
| user_role_assignments | idx_user_role_assignments_role_id | B-tree | role_id | 角色查询 |
| user_role_assignments | idx_user_role_assignments_expires_at | B-tree | expires_at | 过期检查 |
| audit_log | idx_audit_log_user_id | B-tree | user_id | 用户日志查询 |
| audit_log | idx_audit_log_created_at | B-tree | created_at | 时间范围查询 |

### 触发器

| 触发器名 | 表 | 时机 | 函数 | 描述 |
|----------|-----|------|------|------|
| `on_auth_user_created` | auth.users | AFTER INSERT | handle_new_user() | 新用户自动创建资料 |
| `update_user_profiles_updated_at` | public.user_profiles | BEFORE UPDATE | handle_updated_at() | 自动更新 updated_at |
| `update_user_roles_updated_at` | public.user_roles | BEFORE UPDATE | handle_roles_updated_at() | 自动更新 updated_at |

### 行级安全策略（RLS）

#### user_profiles 表策略

| 策略名 | 操作 | 条件 |
|--------|------|------|
| Users can view own profile | SELECT | auth.uid() = id |
| Users can update own profile | UPDATE | auth.uid() = id WITH CHECK |
| Users can delete own profile | DELETE | auth.uid() = id |
| Users can insert own profile | INSERT | auth.uid() = id |

#### user_roles 表策略

| 策略名 | 操作 | 条件 |
|--------|------|------|
| Authenticated users can view active roles | SELECT | auth.role() = 'authenticated' AND is_active = true |
| Admins can manage roles | ALL | 管理员角色检查 |

#### user_role_assignments 表策略

| 策略名 | 操作 | 条件 |
|--------|------|------|
| Users can view own role assignments | SELECT | auth.uid() = user_id |
| Admins can manage role assignments | ALL | 管理员角色检查 |

### 辅助函数

#### 用户资料相关

| 函数名 | 返回类型 | 描述 |
|--------|----------|------|
| `get_user_profile(user_id UUID)` | TABLE | 获取用户完整资料（包括 email） |
| `update_last_login(user_id UUID)` | VOID | 更新用户最后登录时间和登录次数 |

#### 角色权限相关

| 函数名 | 返回类型 | 描述 |
|--------|----------|------|
| `user_has_permission(p_user_id UUID, p_permission TEXT)` | BOOLEAN | 检查用户是否有特定权限 |
| `get_user_roles(p_user_id UUID)` | TABLE | 获取用户的所有角色 |
| `assign_role(p_user_id UUID, p_role_name TEXT, p_assigned_by UUID, p_expires_at TIMESTAMPTZ)` | BOOLEAN | 为用户分配角色 |
| `remove_role(p_user_id UUID, p_role_name TEXT)` | BOOLEAN | 移除用户角色 |

### 视图

| 视图名 | 描述 |
|--------|------|
| `user_overview` | 用户概览（包含活跃状态） |
| `user_roles_overview` | 用户角色概览（包含所有角色和权限） |

**user_overview 视图字段**:
| 字段 | 类型 | 描述 |
|------|------|------|
| id | UUID | 用户 ID |
| email | TEXT | 邮箱 |
| display_name | TEXT | 显示名称 |
| is_active | BOOLEAN | 是否激活 |
| email_confirmed_at | TIMESTAMPTZ | 邮箱确认时间 |
| last_login_at | TIMESTAMPTZ | 最后登录时间 |
| created_at | TIMESTAMPTZ | 创建时间 |
| updated_at | TIMESTAMPTZ | 更新时间 |
| activity_status | TEXT | 活跃状态（活跃/近期活跃/不活跃/从未登录） |

### 初始化脚本顺序

```bash
# 1. 先运行认证配置（如果需要自定义认证设置）
001_supabase_auth_config.sql

# 2. 创建用户资料表
002_user_profiles_schema.sql

# 3. 创建角色和权限系统
003_user_roles_and_permissions.sql
```

### 数据库最佳实践

1. **连接池**: 使用 Supabase 内置连接池，无需额外配置
2. **查询优化**: 合理使用索引，避免全表扫描
3. **批量操作**: 使用 `execute()` 批量执行查询
4. **事务**: 复杂操作使用事务保证数据一致性
5. **备份**: Supabase 自动每日备份，恢复点目标（RPO）为 1 天

## Development Workflow

### Local Development
1. **Virtual Environment Setup**:
   ```bash
   # Create virtual environment (if not exists)
   python -m venv my_clean_venv
   
   # Activate virtual environment
   # On Windows:
   my_clean_venv\Scripts\activate
   # On Unix/macOS:
   source my_clean_venv/bin/activate
   ```
2. Install dependencies: `pip install -r src/requirements.txt`
3. Set environment variables: `SUPABASE_URL` and `SUPABASE_KEY`
4. Run connectivity tests: `python src/test_connectivity.py --url <URL> --key <KEY>`
5. LSP Setup: The `opencode.json` configuration automatically detects the `my_clean_venv` virtual environment

### Docker Deployment
1. Build image: `docker build -t my-text .`
2. Run container with environment variables
3. Access service on port 9000

### Cloud Function Deployment
- Target platform: Tencent Cloud Serverless Cloud Functions (SCF)
- Entry point: `src/index.py::main_handler`
- Runtime: Python 3.10

## Security Considerations

- API keys should be stored securely (environment variables or secrets manager)
- Use read-only or appropriately scoped keys when possible
- Implement rate limiting in production
- Validate all input parameters
- Use HTTPS for all external communications

## Documentation

### Key Documentation Files
- **`AGENTS.md`**: Instructions for AI agents working in this codebase
  - Quick start commands for local development and Docker
  - Code conventions and style guidelines
  - Common tasks and debugging procedures
  - Deployment notes and architecture overview

- **`opencode.json`**: OpenCode AI integration configuration
  - LSP server configuration (pylsp)
  - Feature settings (completion, hover, diagnostics)
  - Workspace folder mappings (root, backend, frontend, src)
  - Virtual environment detection
  - AI agent context awareness settings

### Documentation Conventions
- Project specs: `openspec/` directory
- Agent instructions: `AGENTS.md` in root
- Chinese comments for Python code documentation
- README files should use English for broader accessibility

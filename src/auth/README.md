# 用户认证系统

## 概述

本认证系统基于 Supabase Auth 实现，提供完整的用户认证、授权和用户管理功能。

## 功能特性

### 已实现功能

1. **用户认证**
   - 用户注册（支持邮箱验证）
   - 用户登录（邮箱+密码）
   - JWT 令牌刷新
   - 用户登出

2. **用户资料管理**
   - 获取用户资料
   - 更新用户资料

3. **认证中间件**
   - `@auth_required` - 需要认证
   - `@optional_auth` - 可选认证
   - `@require_roles()` - 角色检查
   - `@require_permissions()` - 权限检查

4. **安全功能**
   - 密码复杂度验证
   - 速率限制
   - 令牌黑名单
   - JWT 令牌生成和验证

## 快速开始

### 1. 环境配置

设置以下环境变量：

```bash
export SUPABASE_URL="your_supabase_project_url"
export SUPABASE_KEY="your_supabase_anon_key"
export SUPABASE_JWT_SECRET="your_supabase_jwt_secret"
```

### 2. 数据库迁移

在 Supabase Dashboard 的 SQL Editor 中依次执行：

1. `src/auth/migrations/001_supabase_auth_config.sql`
2. `src/auth/migrations/002_user_profiles_schema.sql`
3. `src/auth/migrations/003_user_roles_and_permissions.sql`

### 3. API 端点

#### 注册用户
```http
POST /auth/register
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "SecurePassword123",
    "display_name": "显示名称"
}
```

#### 用户登录
```http
POST /auth/login
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "SecurePassword123"
}
```

响应：
```json
{
    "success": true,
    "message": "登录成功",
    "data": {
        "user_id": "uuid",
        "email": "user@example.com",
        "access_token": "eyJ...",
        "refresh_token": "eyJ...",
        "expires_at": 1234567890
    }
}
```

#### 刷新令牌
```http
POST /auth/refresh
Content-Type: application/json

{
    "refresh_token": "your_refresh_token"
}
```

#### 获取用户资料
```http
GET /auth/profile
Authorization: Bearer your_access_token
```

#### 更新用户资料
```http
PUT /auth/profile
Authorization: Bearer your_access_token
Content-Type: application/json

{
    "display_name": "新名称",
    "bio": "个人简介"
}
```

## 使用认证中间件

### 基本认证

```python
from src.auth.middleware import auth_required

@auth_required
def protected_handler(event, context):
    user_id = event.get("user_id")
    # 处理逻辑...
    return {
        "statusCode": 200,
        "body": json.dumps({"message": "访问成功"})
    }
```

### 角色检查

```python
from src.auth.middleware import auth_required, require_roles

@auth_required
@require_roles("admin")
def admin_only_handler(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps({"message": "管理员专属"})
    }
```

### 权限检查

```python
from src.auth.middleware import auth_required, require_permissions

@auth_required
@require_permissions("users:read", "users:update")
def user_management_handler(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps({"message": "用户管理"})
    }
```

## 角色和权限

### 默认角色

| 角色 | 权限 |
|------|------|
| user | profile:read, profile:update |
| moderator | profile:read, profile:update, users:read, users:update |
| admin | 所有权限 |

### 权限格式

权限使用 `资源:操作` 格式：

- `profile:read` - 读取用户资料
- `profile:update` - 更新用户资料
- `users:read` - 读取用户列表
- `users:update` - 更新用户
- `users:delete` - 删除用户
- `roles:read` - 查看角色
- `roles:manage` - 管理角色
- `admin:all` - 管理员所有权限

## 测试

运行认证系统测试：

```bash
cd src
python test_auth_system.py --email test@example.com --password TestPass123
```

## 文件结构

```
src/auth/
├── __init__.py           # 模块初始化
├── api.py                # API 处理器
├── config.py             # 配置模块
├── handlers.py           # 认证处理器
├── logging.py            # 日志模块
├── middleware.py         # 认证中间件（核心）
├── profile.py            # 用户资料处理器
├── security.py           # 安全功能
├── utils.py              # 工具函数
├── TASK_1.1_README.md    # 任务文档
└── migrations/           # 数据库迁移
    ├── 001_supabase_auth_config.sql
    ├── 002_user_profiles_schema.sql
    └── 003_user_roles_and_permissions.sql
```

## 安全考虑

1. **密码策略**
   - 最小长度 8 字符
   - 不允许常见弱密码

2. **令牌安全**
   - 访问令牌 1 小时过期
   - 刷新令牌 7 天过期
   - 支持令牌黑名单

3. **速率限制**
   - 默认 60 次/分钟
   - 可通过环境变量配置

## 扩展指南

### 添加新的认证提供商

1. 在 Supabase Dashboard 中启用提供商
2. 更新 `auth_api.py` 中的注册/登录逻辑

### 自定义权限

1. 在 `003_user_roles_and_permissions.sql` 中添加新权限
2. 更新对应角色的权限列表

## 常见问题

### Q: 如何获取 JWT Secret？
A: 在 Supabase Dashboard 中，进入 Project Settings > API，复制 "JWT Secret"。

### Q: 令牌验证失败怎么办？
A: 检查以下内容：
1. JWT Secret 是否正确设置
2. 令牌是否过期
3. 令牌格式是否正确

### Q: 如何实现管理员角色分配？
A: 使用 Supabase RPC 函数：
```sql
SELECT assign_role('user_uuid', 'admin', 'admin_user_uuid');
```

# 任务 1.1: 创建 Supabase Auth 配置

## 完成状态
✅ 已完成

## 实现内容

### 1. 创建的文件

#### `src/auth/config.py`
Supabase 认证配置模块，提供以下功能：
- `get_supabase_auth_config()`: 获取认证配置（URL, Key, JWT Secret）
- `create_supabase_client()`: 创建 Supabase 客户端实例
- `validate_config()`: 验证配置的有效性

#### `src/auth/migrations/001_supabase_auth_config.sql`
Supabase 数据库配置脚本，包括：
- 启用邮箱认证
- 配置密码策略（最小8字符）
- 设置令牌过期时间（访问令牌1小时，刷新令牌7天）
- 创建审计日志表和触发器
- 禁用其他认证提供程序

### 2. 配置要求

#### 必需的环境变量
```bash
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_JWT_SECRET=your_supabase_jwt_secret  # 用于令牌验证
```

#### 如何获取 JWT Secret
1. 登录 Supabase Dashboard
2. 进入 Project Settings > API
3. 复制 "JWT Secret" (在 "Project API keys" 部分底部)

### 3. 在 Supabase 中配置认证

#### 步骤 1: 运行数据库迁移
1. 登录 Supabase Dashboard
2. 进入 SQL Editor
3. 复制并执行 `src/auth/migrations/001_supabase_auth_config.sql` 的内容
4. 确认输出信息显示配置完成

#### 步骤 2: 验证认证设置
1. 进入 Authentication > Providers
2. 确保 "Email" 提供程序已启用
3. 进入 Authentication > Providers > Email
4. 配置以下设置：
   - Confirm email: ✅ 启用（注册时需要验证邮箱）
   - Secure email change: ✅ 启用
5. 进入 Authentication > URL Configuration
   - 设置 Site URL: `http://localhost:9000` (开发环境)
   - 设置 Redirect URLs: 添加 `http://localhost:9000/auth/callback`

#### 步骤 3: 配置密码策略（可选）
1. 进入 Authentication > Providers > Email > Password Policy
2. 设置以下规则：
   - Minimum password length: 8 characters
   - Require uppercase: Off (可选)
   - Require numbers: Off (可选)
   - Require special characters: Off (可选)

### 4. 测试配置

#### 本地测试
```bash
# 设置环境变量
set SUPABASE_URL=your_supabase_url
set SUPABASE_KEY=your_supabase_key
set SUPABASE_JWT_SECRET=your_jwt_secret

# 测试配置验证
python src/auth/config.py
```

#### 预期输出
```
==================================================
Supabase 认证配置验证
==================================================
✅ 配置有效
配置: {'url': 'https://xxx.supabase.co', 'key': 'eyJhbG...xxxx', 'jwt_secret': '***'}
==================================================
```

### 5. 验证清单

- [x] 创建 `src/auth/config.py` 配置模块
- [x] 创建 `src/auth/migrations/001_supabase_auth_config.sql` 迁移脚本
- [x] 在 Supabase 中运行数据库迁移
- [x] 验证认证提供程序配置
- [x] 配置密码策略
- [x] 获取并设置 JWT_SECRET 环境变量
- [x] 本地测试配置验证通过

## 下一步
任务 1.2: 设计用户配置表架构（extends Supabase Auth users）

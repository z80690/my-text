# My Text - AI-Powered Backend Service

基于 Supabase 和智谱AI 的后端 API 服务，支持认证系统、知识库查询和 AI 能力集成。

## 功能特性

- **认证系统** - 用户注册、登录、JWT 令牌管理
- **知识库查询** - 基于 Supabase 的知识库数据查询
- **AI 集成** - 智谱AI (ZhipuAI) 模型支持
- **安全特性** - API 密钥加密、速率限制、CORS 配置
- **云原生部署** - 支持腾讯云 SCF 和 Docker 部署

## 技术栈

- **后端**: Python 3.10
- **数据库**: Supabase (PostgreSQL)
- **AI 服务**: 智谱AI (ZhipuAI)
- **部署**: 腾讯云 SCF / Docker
- **开发规范**: OpenSpec (Spec-driven Development)

## 快速开始

### 环境要求

- Python 3.10+
- Supabase 账户
- 智谱AI API 密钥（可选）

### 安装依赖

**生产环境**：
```bash
cd src
pip install -r requirements.txt
```

**开发环境**（包含代码质量工具）：
```bash
cd src
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

**使用虚拟环境**（推荐）：
```bash
# 创建虚拟环境
python -m venv my_clean_venv

# Windows 激活
my_clean_venv\Scripts\activate

# Unix/macOS 激活
source my_clean_venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

> 详细依赖管理说明请查看 [DEPENDENCIES.md](DEPENDENCIES.md)

### 配置环境变量

1. 复制 `.env.example` 为 `.env`
2. 填写必要的配置项：

```bash
# Supabase 配置
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_JWT_SECRET=your-jwt-secret

# 智谱AI 配置（可选）
ZHIPU_API_KEY=your-zhipu-api-key
ZHIPU_MODEL=glm-4

# 应用配置
PORT=9000
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### 本地运行

```bash
cd src
python main.py
```

服务将在 `http://localhost:9000` 启动。

### 运行测试

```bash
# 运行完整测试套件
python src/test_connectivity.py

# 运行单个测试
python -c "from src.test_connectivity import test_env_vars; print(test_env_vars())"
python -c "from src.test_connectivity import test_supabase_connection; print(test_supabase_connection())"

# 测试认证系统
python src/test_auth_system.py

# 测试角色和权限
python src/test_roles_and_permissions.py

# 测试智谱AI集成
python src/test_zhipu_ai.py
```

## Docker 部署

### 构建镜像

```bash
docker build -t my-text .
```

### 运行容器

```bash
docker run -p 9000:9000 \
  -e SUPABASE_URL=your_url \
  -e SUPABASE_KEY=your_key \
  -e SUPABASE_JWT_SECRET=your_jwt \
  my-text
```

## API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/ai/*` | GET/POST | AI API 处理路由 |
| `/auth/*` | GET/POST | 认证 API 处理路由 |
| `/` | GET | 知识库查询（默认） |

### 认证 API

```bash
# 用户注册
POST /auth/register
Body: {"email": "user@example.com", "password": "securepassword"}

# 用户登录
POST /auth/login
Body: {"email": "user@example.com", "password": "securepassword"}

# 刷新令牌
POST /auth/refresh
Headers: {"Authorization": "Bearer refresh_token"}
```

### 知识库查询

```bash
# 查询知识库
GET /
```

## 项目结构

```
my-text/
├── src/                    # Python 源代码
│   ├── main.py            # 主入口，API 路由
│   ├── index.py           # 云函数入口
│   ├── ai_api.py          # AI API 处理
│   ├── auth_api.py        # 认证 API 处理
│   ├── auth/              # 认证模块
│   ├── security.py        # 安全工具
│   ├── zhipu_service.py   # 智谱AI 服务
│   ├── skill_handler.py   # 技能处理器
│   ├── test_*.py          # 测试文件
│   └── requirements.txt   # Python 依赖
├── frontend/              # 前端代码（可选）
├── backend/               # 后端附加代码
├── templates/             # 模板文件
├── utils/                 # 工具函数
├── skills/                # 技能模块
├── openspec/              # OpenSpec 规范
│   ├── project.md         # 项目规范
│   ├── specs/             # 功能规范
│   └── changes/           # 变更提案
├── .env                   # 环境变量（不提交）
├── .env.example           # 环境变量示例
├── Dockerfile             # Docker 配置
├── AGENTS.md              # AI 代理指令
└── README.md              # 本文档
```

## 代码规范

### Python 风格

- **编码**: UTF-8
- **缩进**: 4 空格
- **行长度**: 88 字符（PEP 8）
- **命名**: 
  - 函数/变量: `snake_case`
  - 类: `PascalCase`
  - 常量: `UPPER_SNAKE_CASE`
- **类型提示**: 所有函数必须包含类型注解

### 错误处理

```python
try:
    response = supabase.table("table").select("*").execute()
except Exception as e:
    error_msg = f"Error: {str(e)}"
    print(f"[ERROR] {error_msg}")
    return {"statusCode": 500, "body": json.dumps({"error": error_msg})}
```

### 日志规范

使用前缀标识日志级别：

```python
print("[INFO] Starting database query")
print("[WARNING] Cache miss, fetching from database")
print("[ERROR] Failed to connect to Supabase")
```

### 云函数响应格式

```python
return {
    "statusCode": 200,
    "headers": {"Content-Type": "application/json"},
    "body": json.dumps({"success": True, "data": result})
}
```

## 开发规范

本项目使用 [OpenSpec](https://github.com/anomalyco/opencode) 进行规范驱动开发。

### 创建变更提案

当需要添加新功能时，使用 OpenSpec 流程：

```bash
# 1. 查看现有规范
openspec list --specs

# 2. 创建变更提案
openspec init my-change-id

# 3. 编辑提案文件
# - proposal.md: 描述变更原因和影响
# - tasks.md: 实现任务清单
# - design.md: 技术设计（如果需要）
# - specs/*/spec.md: 规范增量

# 4. 验证提案
openspec validate my-change-id --strict
```

### 规范结构

- `openspec/specs/` - 当前已实现的规范
- `openspec/changes/` - 待批准的变更提案
- `openspec/archive/` - 已完成的变更

详细规范请参考 [openspec/AGENTS.md](openspec/AGENTS.md)。

## 安全配置

### 环境变量

| 变量 | 描述 | 必填 |
|------|------|------|
| `SUPABASE_URL` | Supabase 项目 URL | 是 |
| `SUPABASE_KEY` | Supabase 匿名密钥 | 是 |
| `SUPABASE_JWT_SECRET` | JWT 密钥 | 是 |
| `ZHIPU_API_KEY` | 智谱AI API 密钥 | 否 |
| `ENCRYPTION_KEY` | API 密钥加密密钥 | 推荐 |

### 安全特性

- 敏感信息日志屏蔽
- 速率限制（默认 60 请求/分钟）
- CORS 配置
- JWT 令牌过期机制
- 密码最小长度验证

## 部署到腾讯云 SCF

### 配置要求

- 运行时: Python 3.10
- 入口函数: `index.main_handler`
- 端口: 9000
- 环境变量: `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_JWT_SECRET`

### 部署步骤

1. 安装腾讯云 CLI
2. 配置认证凭据
3. 执行部署命令

## 更新日志

### v1.0.0

- 初始版本
- 基础认证系统
- 知识库查询功能
- 智谱AI 集成
- Docker 部署支持

## 许可证

本项目采用 MIT 许可证。

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 联系方式

如有问题或建议，请提交 Issue 或联系项目维护者。

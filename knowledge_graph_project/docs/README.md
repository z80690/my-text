# 知识图谱数据库项目

## 项目概述

本项目是一个完整的知识图谱数据库系统，具备登录哔哩哔哩(bilibili.com)和今日头条(toutiao.com)两个平台的能力，包括模拟登录、Cookie管理、以及从这两个平台获取和解析信息的基础能力。

## 功能特性

### 🎯 核心功能
- **平台登录**: 支持扫码登录、密码登录多种方式
- **Cookie管理**: 加密存储、自动刷新、有效性检测
- **数据提取**: 用户信息、内容数据、评论数据批量提取
- **知识图谱**: 用户关系网络、内容关联关系构建
- **REST API**: FastAPI提供完整的Web接口

### 📦 技术栈
- **后端框架**: Python 3.10 + FastAPI
- **浏览器自动化**: Playwright
- **数据库**: PostgreSQL (Supabase) + 可选Neo4j
- **加密**: Fernet对称加密
- **API文档**: 自动生成Swagger/OpenAPI

## 项目结构

```
knowledge_graph_project/
├── config/                  # 配置模块
│   ├── __init__.py
│   └── settings.py          # 配置加载和管理
├── platforms/               # 平台模块
│   ├── bilibili/            # 哔哩哔哩
│   │   ├── __init__.py
│   │   ├── bilibili_client.py   # API客户端
│   │   ├── bilibili_login.py    # 登录管理
│   │   └── bilibili_data.py     # 数据提取
│   └── toutiao/             # 今日头条
│       ├── __init__.py
│       ├── toutiao_client.py    # API客户端
│       ├── toutiao_login.py     # 登录管理
│       └── toutiao_data.py      # 数据提取
├── auth/                    # 认证模块
│   ├── __init__.py
│   └── cookie_manager.py    # Cookie和会话管理
├── database/                # 数据库模块
│   ├── __init__.py
│   ├── schema.sql           # PostgreSQL Schema
│   └── models.py            # Pydantic数据模型
├── tests/                   # 测试模块
│   └── test_knowledge_graph.py
├── main.py                  # 主入口
├── requirements.txt         # 依赖列表
├── .env.example             # 环境变量示例
└── README.md               # 本文档
```

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <your-repo-url>
cd knowledge_graph_project

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 安装Playwright浏览器
playwright install chromium
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置文件
# 填写Supabase数据库连接信息
# 填写其他配置项
```

### 3. 初始化数据库

```bash
# 连接Supabase并执行Schema
psql -h your-host.supabase.co -U postgres -d postgres -f database/schema.sql
```

### 4. 运行服务

```bash
# 开发模式运行
python main.py

# 服务将在 http://localhost:8080 启动
# API文档: http://localhost:8080/docs
```

## API接口

### 认证管理

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/auth/login | 登录平台 |
| POST | /api/auth/logout | 退出登录 |
| GET | /api/auth/status | 查看认证状态 |

### 哔哩哔哩数据

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/bilibili/user/{user_id} | 获取用户信息 |
| GET | /api/bilibili/user/{user_id}/videos | 获取用户视频 |
| GET | /api/bilibili/video/{bvid} | 获取视频详情 |
| GET | /api/bilibili/video/{bvid}/comments | 获取视频评论 |
| GET | /api/bilibili/popular | 获取热门视频 |
| GET | /api/bilibili/search | 搜索视频 |

### 今日头条数据

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/toutiao/user/{user_id} | 获取用户信息 |
| GET | /api/toutiao/user/{user_id}/articles | 获取用户文章 |
| GET | /api/toutiao/article/{group_id} | 获取文章详情 |
| GET | /api/toutiao/feed | 获取推荐内容 |
| GET | /api/toutiao/hot | 获取热搜榜 |

### 知识图谱

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/graph/crawl/user | 爬取用户关系网络 |

## 使用示例

### Python调用示例

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from platforms.bilibili import BilibiliLogin, BilibiliDataExtractor
from platforms.toutiao import ToutiaoLogin, ToutiaoDataExtractor
from auth.cookie_manager import CookieManager

# 登录B站
with BilibiliLogin(headless=False) as login:
    success, cookies = login.login_with_qrcode()
    if success:
        print("B站登录成功!")
        login.save_cookies(cookies)

# 提取数据
from platforms.bilibili import BilibiliClient
client = BilibiliClient(cookies=cookies)
extractor = BilibiliDataExtractor(client)

# 获取用户信息
user = extractor.extract_user("2")
print(f"用户名: {user['display_name']}")

# 获取用户视频
videos = extractor.extract_user_with_contents("2")
print(f"视频数: {len(videos.get('videos', []))}")
```

### API调用示例

```bash
# 登录B站
curl -X POST "http://localhost:8080/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"platform": "bilibili", "method": "qrcode"}'

# 获取用户信息
curl "http://localhost:8080/api/bilibili/user/2"

# 搜索视频
curl "http://localhost:8080/api/bilibili/search?keyword=Python"
```

## 数据库Schema

项目使用PostgreSQL数据库，主要表包括：

- `platforms` - 平台配置表
- `users` - 用户实体表
- `contents` - 内容实体表
- `comments` - 评论实体表
- `relations` - 关系表（知识图谱核心）
- `topics` - 话题/标签表
- `categories` - 分类表
- `sessions` - Cookie/会话管理表
- `crawl_tasks` - 采集任务表

详细Schema请参考 `database/schema.sql`

## Cookie管理

Cookie管理器提供以下功能：

- **加密存储**: 使用Fernet对称加密保护Cookie
- **自动刷新**: 支持Cookie过期自动刷新
- **有效性检测**: 定期验证Cookie有效性
- **多平台支持**: 同时管理多个平台的Cookie

## 注意事项

1. **法律合规**: 请遵守平台的使用条款和robots.txt
2. **频率限制**: 请合理控制请求频率，避免对平台造成压力
3. **Cookie安全**: 不要将Cookie泄露给他人
4. **测试环境**: 建议先在测试环境中验证功能

## 许可证

MIT License

## 贡献指南

1. Fork 本仓库
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

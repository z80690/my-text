# OpenCode 帮助文档

## 目录

1. [简介](#1-简介)
2. [安装](#2-安装)
3. [快速开始](#3-快速开始)
4. [CLI 命令](#4-cli-命令)
5. [TUI 命令](#5-tui-命令)
6. [内置工具](#6-内置工具)
7. [代理系统](#7-代理系统)
8. [模型配置](#8-模型配置)
9. [自定义命令](#9-自定义命令)
10. [配置文件](#10-配置文件)
11. [权限管理](#11-权限管理)
12. [环境变量](#12-环境变量)
13. [常见问题](#13-常见问题)

---

## 1. 简介

OpenCode 是一个开源的 AI 编程代理工具，可作为终端界面、桌面应用或 IDE 扩展使用。

### 主要特性

- **LSP 支持**: 自动加载适合的 LSP 服务器
- **多会话**: 可在同一个项目中启动多个代理并行工作
- **分享链接**: 可分享会话链接用于参考或调试
- **多模型支持**: 支持 75+ LLM 提供商，包括 Claude、GPT、Gemini 等
- **多平台**: 终端、桌面、IDE 三种形态

### GitHub 数据

- ⭐ 60K+ GitHub Stars
- 👥 500+ Contributors
- 👤 650K+ 月活开发者

---

## 2. 安装

### Linux/macOS

```bash
# 官方安装脚本
curl -fsSL https://opencode.ai/install | bash

# 使用 npm
npm install -g opencode-ai

# 使用 bun
bun install -g opencode-ai

# 使用 Homebrew
brew install anomalyco/tap/opencode

# 使用 Paru (Arch Linux)
paru -S opencode-bin
```

### Windows

```powershell
# 使用 Chocolatey
choco install opencode

# 使用 Scoop
scoop bucket add extra
scoop install extras/opencode

# 使用 npm
npm install -g opencode-ai

# 使用 Mise
mise use -g github:anomalyco/opencode

# 使用 Docker
docker run -it --rm ghcr.io/anomalyco/opencode
```

### 先决条件

- 现代终端模拟器: WezTerm、Alacritty、Ghostty、Kitty
- LLM 提供商的 API 密钥

---

## 3. 快速开始

### 3.1 配置提供者

```bash
# 启动 OpenCode
opencode

# 连接提供者
/connect
```

选择提供者后，访问 https://opencode.ai/auth 获取 API 密钥。

### 3.2 初始化项目

```bash
cd /path/to/project
opencode
/init
```

这将分析项目并创建 `AGENTS.md` 文件。

### 3.3 基本使用

```bash
# 询问问题
How is authentication handled?

# 添加功能
Add a login feature with JWT authentication

# 撤销更改
/undo

# 分享会话
/share
```

---

## 4. CLI 命令

### 4.1 基础命令

```bash
# 启动 TUI
opencode
opencode /path/to/project

# 版本信息
opencode --version
opencode -v

# 帮助信息
opencode --help
opencode -h
```

### 4.2 tui 命令

启动终端用户界面。

```bash
opencode [project]
```

**参数:**

| 参数 | 短格式 | 描述 |
|------|--------|------|
| `--continue` | `-c` | 继续上一个会话 |
| `--session` | `-s` | 指定会话 ID |
| `--prompt` | - | 使用的提示词 |
| `--model` | `-m` | 模型名称 (格式: provider/model) |
| `--agent` | - | 使用的代理 |
| `--port` | - | 监听端口 |
| `--hostname` | - | 监听主机名 |

### 4.3 run 命令

非交互模式运行。

```bash
opencode run "Explain closures in JavaScript"
```

**参数:**

| 参数 | 短格式 | 描述 |
|------|--------|------|
| `--command` | - | 要运行的命令 |
| `--continue` | `-c` | 继续上一个会话 |
| `--session` | `-s` | 指定会话 ID |
| `--share` | - | 分享会话 |
| `--model` | `-m` | 模型名称 |
| `--agent` | - | 使用的代理 |
| `--file` | `-f` | 附加到消息的文件 |
| `--format` | - | 输出格式 (default/json) |
| `--title` | - | 会话标题 |
| `--attach` | - | 附加到运行的服务器 |
| `--port` | - | 本地服务器端口 |

**示例:**

```bash
# 附加到运行中的服务器
opencode serve
opencode run --attach http://localhost:4096 "Explain async/await"

# 带文件运行
opencode run -f src/index.ts "Explain this file"
```

### 4.4 serve 命令

启动无头 OpenCode 服务器。

```bash
opencode serve
```

**参数:**

| 参数 | 描述 |
|------|------|
| `--port` | 监听端口 |
| `--hostname` | 监听主机名 |
| `--mdns` | 启用 mDNS 发现 |
| `--cors` | 允许额外的浏览器来源 |

**环境变量:**

```bash
OPENCODE_SERVER_PASSWORD=your_password
```

### 4.5 web 命令

启动带 Web 界面的服务器。

```bash
opencode web
```

参数与 `serve` 相同。

### 4.6 agent 命令

管理代理。

```bash
# 创建新代理
opencode agent create

# 列出所有代理
opencode agent list
```

### 4.7 auth 命令

管理认证凭据。

```bash
# 登录
opencode auth login

# 列出已认证的提供者
opencode auth list
opencode auth ls

# 登出
opencode auth logout
```

### 4.8 models 命令

列出可用模型。

```bash
# 列出所有模型
opencode models

# 列出特定提供者的模型
opencode models anthropic

# 刷新模型缓存
opencode models --refresh
```

**参数:**

| 参数 | 描述 |
|------|------|
| `--refresh` | 刷新模型缓存 |
| `--verbose` | 显示详细模型信息（包括成本等元数据） |

### 4.9 session 命令

管理会话。

```bash
# 列出所有会话
opencode session list

# 参数:
--max-count, -n  # 限制显示数量
--format         # 输出格式 (table/json)
```

### 4.10 stats 命令

显示令牌使用和成本统计。

```bash
opencode stats
```

**参数:**

| 参数 | 描述 |
|------|------|
| `--days` | 显示最近 N 天的统计 |
| `--tools` | 显示的工具数量 |
| `--models` | 显示模型使用分解 |
| `--project` | 按项目过滤 |

**示例:**

```bash
# 显示最近 7 天的统计
opencode stats --days 7

# 显示前 5 个模型的使用情况
opencode stats --models 5

# 过滤特定项目
opencode stats --project my-project
```

### 4.11 export/import 命令

导出/导入会话数据。

```bash
# 导出会话
opencode export [sessionID]

# 导入会话
opencode import session.json
opencode import https://opencode.ai/s/abc123
```

### 4.12 share 命令

分享当前会话。

```bash
/share
```

### 4.13 mcp 命令

管理 MCP 服务器。

```bash
# 添加 MCP 服务器
opencode mcp add

# 列出所有 MCP 服务器
opencode mcp list
opencode mcp ls

# OAuth 认证
opencode mcp auth [name]
opencode mcp auth list
opencode mcp auth ls

# 登出
opencode mcp logout [name]

# 调试 OAuth 连接
opencode mcp debug <name>
```

### 4.14 github 命令

管理 GitHub 代理。

```bash
# 安装 GitHub 代理
opencode github install

# 运行 GitHub 代理
opencode github run
```

**参数:**

| 参数 | 描述 |
|------|------|
| `--event` | GitHub mock 事件 |
| `--token` | GitHub 个人访问令牌 |

### 4.15 upgrade 命令

升级 OpenCode。

```bash
# 升级到最新版本
opencode upgrade

# 升级到特定版本
opencode upgrade v0.1.48
```

**参数:**

| 参数 | 短格式 | 描述 |
|------|--------|------|
| `--method` | `-m` | 安装方法 (curl/npm/pnpm/bun/brew) |

### 4.16 uninstall 命令

卸载 OpenCode。

```bash
opencode uninstall
```

**参数:**

| 参数 | 短格式 | 描述 |
|------|--------|------|
| `--keep-config` | `-c` | 保留配置文件 |
| `--keep-data` | `-d` | 保留会话数据 |
| `--dry-run` | - | 显示将要删除的内容而不删除 |
| `--force` | `-f` | 跳过确认提示 |

### 4.17 attach 命令

附加到运行的 OpenCode 后端服务器。

```bash
opencode attach [url]
```

**参数:**

| 参数 | 短格式 | 描述 |
|------|--------|------|
| `--dir` | - | 工作目录 |
| `--session` | `-s` | 会话 ID |

**示例:**

```bash
# 启动后端服务器
opencode web --port 4096 --hostname 0.0.0.0

# 在另一个终端附加 TUI
opencode attach http://10.20.30.40:4096
```

### 4.18 acp 命令

启动 ACP (Agent Client Protocol) 服务器。

```bash
opencode acp
```

**参数:**

| 参数 | 描述 |
|------|------|
| `--cwd` | 工作目录 |
| `--port` | 监听端口 |
| `--hostname` | 监听主机名 |

---

## 5. TUI 命令

在 TUI 中使用 `/` 前缀输入命令。

### 5.1 内置命令

| 命令 | 别名 | 描述 | 快捷键 |
|------|------|------|--------|
| `/help` | - | 显示帮助对话框 | `Ctrl+X H` |
| `/init` | - | 创建或更新 AGENTS.md | `Ctrl+X I` |
| `/new` | `/clear` | 开始新会话 | `Ctrl+X N` |
| `/undo` | - | 撤销上一次更改 | `Ctrl+X U` |
| `/redo` | - | 重做已撤销的更改 | `Ctrl+X R` |
| `/share` | - | 分享当前会话 | `Ctrl+X S` |
| `/unshare` | - | 取消分享会话 | - |
| `/sessions` | `/resume` `/continue` | 列出并切换会话 | `Ctrl+X L` |
| `/models` | - | 列出可用模型 | `Ctrl+X M` |
| `/connect` | - | 添加提供者 | - |
| `/compact` | `/summarize` | 压缩当前会话 | `Ctrl+X C` |
| `/details` | - | 切换工具执行详情 | `Ctrl+X D` |
| `/editor` | - | 打开外部编辑器 | `Ctrl+X E` |
| `/export` | - | 导出对话到 Markdown | `Ctrl+X X` |
| `/theme` | `/themes` | 列出可用主题 | `Ctrl+X T` |
| `/exit` | `/quit` `/q` | 退出 OpenCode | `Ctrl+X Q` |

### 5.2 使用示例

```bash
# 显示帮助
/help

# 初始化项目
/init

# 开始新会话
/new

# 撤销更改
/undo

# 重做更改
/redo

# 分享会话
/share

# 切换会话
/sessions

# 查看模型列表
/models

# 压缩对话
/compact

# 打开编辑器
/editor

# 导出对话
/export

# 切换主题
/theme

# 退出
/exit
```

### 5.3 文件引用

在消息中使用 `@` 引用文件。

```bash
How is auth handled in @packages/functions/src/api/index.ts?
```

### 5.4 Bash 命令

以 `!` 开头运行 Shell 命令。

```bash
!ls -la
!npm install
!git status
```

---

## 6. 内置工具

### 6.1 工具列表

| 工具 | 描述 | 权限控制 |
|------|------|----------|
| `read` | 读取文件内容 | `read` |
| `write` | 创建/覆盖文件 | `edit` |
| `edit` | 修改现有文件 | `edit` |
| `patch` | 应用补丁 | `edit` |
| `glob` | 按模式查找文件 | `glob` |
| `grep` | 搜索文件内容 | `grep` |
| `list` | 列出目录内容 | `list` |
| `bash` | 执行 Shell 命令 | `bash` |
| `webfetch` | 获取网页内容 | `webfetch` |
| `skill` | 加载技能文件 | `skill` |
| `todowrite` | 管理待办列表 | `todowrite` |
| `todoread` | 读取待办列表 | `todoread` |
| `question` | 向用户提问 | `question` |
| `lsp` | LSP 交互 (实验性) | `lsp` |

### 6.2 工具使用示例

```bash
# 读取文件
read filePath: /path/to/file.txt

# 写入文件
write filePath: /path/to/new.txt, content: "Hello World"

# 编辑文件
edit filePath: /path/to/file.txt, oldString: "old text", newString: "new text"

# 查找文件
glob pattern: "**/*.py"

# 搜索内容
grep pattern: "def.*main", include: "*.py"

# 列出目录
list path: /path/to/directory

# 执行命令
bash command: "npm install", description: "Install dependencies"

# 获取网页
webfetch url: "https://example.com", format: "markdown"

# 加载技能
skill name: "code-review"

# 管理待办
todowrite todos: [{"id": "1", "content": "Task 1", "status": "in_progress"}]

# 读取待办
todoread

# 提问用户
question questions: [{"header": "Confirm", "question": "Continue?", "options": [{"label": "Yes"}, {"label": "No"}]}]
```

### 6.3 忽略模式

默认情况下，工具会遵守 `.gitignore` 规则。创建 `.ignore` 文件来覆盖：

```gitignore
!node_modules/
!dist/
!build/
```

---

## 7. 代理系统

### 7.1 代理类型

#### 主代理 (Primary Agents)

直接交互的主要助手。使用 **Tab** 键切换。

- **Build**: 默认主代理，启用所有工具
- **Plan**: 规划和分析代理，限制写操作

#### 子代理 (Subagents)

可被主代理调用的专业助手。使用 **@** 提及调用。

- **General**: 通用任务代理
- **Explore**: 快速代码库探索代理

### 7.2 配置代理

#### JSON 格式 (opencode.json)

```json
{
  "$schema": "https://opencode.ai/config.json",
  "agent": {
    "build": {
      "mode": "primary",
      "model": "anthropic/claude-sonnet-4-20250514",
      "tools": {
        "write": true,
        "edit": true,
        "bash": true
      }
    },
    "plan": {
      "mode": "primary",
      "model": "anthropic/claude-haiku-4-20250514",
      "tools": {
        "write": false,
        "edit": false,
        "bash": false
      }
    },
    "review": {
      "description": "Code review agent",
      "mode": "subagent",
      "model": "anthropic/claude-sonnet-4-20250514",
      "tools": {
        "write": false,
        "edit": false
      }
    }
  }
}
```

#### Markdown 格式

文件位置:
- 全局: `~/.config/opencode/agent/`
- 项目: `.opencode/agent/`

```markdown
---
description: Reviews code for quality and best practices
mode: subagent
model: anthropic/claude-sonnet-4-20250514
temperature: 0.1
tools:
  write: false
  edit: false
  bash: false
---

You are in code review mode. Focus on:
- Code quality and best practices
- Potential bugs and edge cases
- Performance implications
- Security considerations

Provide constructive feedback without making direct changes.
```

### 7.3 代理选项

| 选项 | 描述 | 必填 |
|------|------|------|
| `description` | 代理描述 | 是 |
| `mode` | 代理模式 (primary/subagent/all) | 否 |
| `model` | 使用的模型 | 否 |
| `prompt` | 系统提示文件路径 | 否 |
| `temperature` | 模型温度 (0.0-1.0) | 否 |
| `maxSteps` | 最大步骤数 | 否 |
| `disable` | 禁用代理 | 否 |
| `hidden` | 隐藏子代理 | 否 |
| `tools` | 可用工具配置 | 否 |
| `permission` | 权限配置 | 否 |

### 7.4 使用代理

```bash
# 切换主代理 (Tab 键)
<Tab>

# 调用子代理
@general help me search for this function

# 创建新代理
opencode agent create
```

---

## 8. 模型配置

### 8.1 推荐模型

- GPT 5.2
- GPT 5.1 Codex
- Claude Opus 4.5
- Claude Sonnet 4.5
- Minimax M2.1
- Gemini 3 Pro

### 8.2 设置默认模型

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4-20250514"
}
```

### 8.3 模型变体

#### 内置变体

**Anthropic:**
- `high` - 高思考预算 (默认)
- `max` - 最大思考预算

**OpenAI:**
- `none` - 无思考
- `minimal` - 最小思考努力
- `low` - 低思考努力
- `medium` - 中等思考努力
- `high` - 高思考努力
- `xhigh` - 极高思考努力

**Google:**
- `low` - 低努力/令牌预算
- `high` - 高努力/令牌预算

#### 自定义变体

```json
{
  "provider": {
    "anthropic": {
      "models": {
        "claude-sonnet-4-20250514": {
          "variants": {
            "fast": {
              "thinking": {
                "type": "enabled",
                "budgetTokens": 4000
              }
            }
          }
        }
      }
    }
  }
}
```

### 8.4 模型加载优先级

1. CLI 参数 `--model`
2. 配置文件中的 `model` 设置
3. 上次使用的模型
4. 内部优先级第一个模型

---

## 9. 自定义命令

### 9.1 创建命令

#### Markdown 格式

文件位置:
- 全局: `~/.config/opencode/command/`
- 项目: `.opencode/command/`

```markdown
---
description: Run tests with coverage
agent: build
model: anthropic/claude-3-5-sonnet-20241022
---

Run the full test suite with coverage report and show any failures.
Focus on the failing tests and suggest fixes.
```

命令文件名为 `test.md`，使用 `/test` 调用。

#### JSON 格式

```json
{
  "$schema": "https://opencode.ai/config.json",
  "command": {
    "test": {
      "template": "Run the full test suite with coverage report...",
      "description": "Run tests with coverage",
      "agent": "build",
      "model": "anthropic/claude-3-5-sonnet-20241022"
    }
  }
}
```

### 9.2 命令参数

#### 位置参数

| 占位符 | 描述 |
|--------|------|
| `$ARGUMENTS` | 所有参数 |
| `$1` | 第一个参数 |
| `$2` | 第二个参数 |
| `$3` | 第三个参数 |

```markdown
---
description: Create a new file
---

Create a file named $1 in the directory $2 with the content: $3
```

使用: `/create-file config.json src "{ \"key\": \"value\" }"`

#### Shell 输出

```markdown
---
description: Analyze test coverage
---

Test results:
!`npm test`

Based on these results, suggest improvements.
```

#### 文件引用

```markdown
---
description: Review component
---

Review the component in @src/components/Button.tsx
```

### 9.3 命令选项

| 选项 | 描述 |
|------|------|
| `template` | 发送给 LLM 的提示词 (必填) |
| `description` | 命令描述 |
| `agent` | 使用的代理 |
| `model` | 使用的模型 |
| `subtask` | 强制子代理调用 |

---

## 10. 配置文件

### 10.1 配置文件位置

- 全局: `~/.config/opencode/opencode.json`
- 项目: `.opencode/opencode.json`
- CLI 参数: `OPENCODE_CONFIG`

### 10.2 完整配置示例

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4-20250514",
  "agent": {
    "build": {
      "mode": "primary",
      "model": "anthropic/claude-sonnet-4-20250514",
      "prompt": "{file:./prompts/build.txt}",
      "tools": {
        "write": true,
        "edit": true,
        "bash": true
      }
    },
    "plan": {
      "mode": "primary",
      "model": "anthropic/claude-haiku-4-20250514",
      "tools": {
        "write": false,
        "edit": false,
        "bash": false
      }
    }
  },
  "permission": {
    "edit": "ask",
    "bash": "ask",
    "webfetch": "allow"
  },
  "tui": {
    "scroll_speed": 3,
    "scroll_acceleration": {
      "enabled": true
    }
  },
  "command": {
    "test": {
      "template": "Run tests...",
      "description": "Run tests with coverage",
      "agent": "build"
    }
  }
}
```

---

## 11. 权限管理

### 11.1 权限级别

| 级别 | 描述 |
|------|------|
| `allow` | 允许所有操作，无需批准 |
| `ask` | 运行前请求批准 |
| `deny` | 禁用工具 |

### 11.2 配置权限

#### 全局权限

```json
{
  "permission": {
    "edit": "deny",
    "bash": "ask",
    "webfetch": "allow"
  }
}
```

#### 特定命令权限

```json
{
  "agent": {
    "build": {
      "permission": {
        "bash": {
          "*": "ask",
          "git status": "allow",
          "git push": "deny"
        }
      }
    }
  }
}
```

#### Bash 命令权限示例

```json
{
  "permission": {
    "bash": {
      "git *": "ask",
      "npm install": "allow"
    }
  }
}
```

### 11.3 MCP 服务器权限

```json
{
  "permission": {
    "mymcp_*": "ask"
  }
}
```

---

## 12. 环境变量

### 12.1 常规配置

| 变量 | 类型 | 描述 |
|------|------|------|
| `OPENCODE_AUTO_SHARE` | boolean | 自动分享会话 |
| `OPENCODE_CONFIG` | string | 配置文件路径 |
| `OPENCODE_CONFIG_DIR` | string | 配置目录路径 |
| `OPENCODE_CONFIG_CONTENT` | string | 内联 JSON 配置 |
| `OPENCODE_DISABLE_AUTOUPDATE` | boolean | 禁用自动更新检查 |
| `OPENCODE_DISABLE_PRUNE` | boolean | 禁用旧数据清理 |
| `OPENCODE_DISABLE_TERMINAL_TITLE` | boolean | 禁用终端标题自动更新 |
| `OPENCODE_DISABLE_DEFAULT_PLUGINS` | boolean | 禁用默认插件 |
| `OPENCODE_DISABLE_LSP_DOWNLOAD` | boolean | 禁用自动 LSP 下载 |
| `OPENCODE_CLIENT` | string | 客户端标识符 |

### 12.2 功能开关

| 变量 | 类型 | 描述 |
|------|------|------|
| `OPENCODE_ENABLE_EXPERIMENTAL_MODELS` | boolean | 启用实验模型 |
| `OPENCODE_DISABLE_AUTOCOMPACT` | boolean | 禁用自动上下文压缩 |
| `OPENCODE_DISABLE_CLAUDE_CODE` | boolean | 禁用读取 `.claude` |
| `OPENCODE_DISABLE_CLAUDE_CODE_PROMPT` | boolean | 禁用读取 `~/.claude/CLAUDE.md` |
| `OPENCODE_DISABLE_CLAUDE_CODE_SKILLS` | boolean | 禁用加载 `.claude/skills` |
| `OPENCODE_ENABLE_EXA` | boolean | 启用 Exa 网络搜索工具 |

### 12.3 服务器配置

| 变量 | 类型 | 描述 |
|------|------|------|
| `OPENCODE_SERVER_PASSWORD` | string | serve/web 的 HTTP 基本认证密码 |
| `OPENCODE_SERVER_USERNAME` | string | 基本认证用户名 (默认: opencode) |

### 12.4 Windows 专用

| 变量 | 类型 | 描述 |
|------|------|------|
| `OPENCODE_GIT_BASH_PATH` | string | Windows 上 Git Bash 可执行文件路径 |

### 12.5 权限配置

| 变量 | 类型 | 描述 |
|------|------|------|
| `OPENCODE_PERMISSION` | string | 内联 JSON 权限配置 |

### 12.6 实验性功能

| 变量 | 类型 | 描述 |
|------|------|------|
| `OPENCODE_EXPERIMENTAL` | boolean | 启用所有实验性功能 |
| `OPENCODE_EXPERIMENTAL_ICON_DISCOVERY` | boolean | 启用图标发现 |
| `OPENCODE_EXPERIMENTAL_DISABLE_COPY_ON_SELECT` | boolean | 禁用 TUI 中选择时复制 |
| `OPENCODE_EXPERIMENTAL_BASH_MAX_OUTPUT_LENGTH` | number | Bash 命令最大输出长度 |
| `OPENCODE_EXPERIMENTAL_BASH_DEFAULT_TIMEOUT_MS` | number | Bash 命令默认超时 (毫秒) |
| `OPENCODE_EXPERIMENTAL_OUTPUT_TOKEN_MAX` | number | LLM 响应最大输出令牌数 |
| `OPENCODE_EXPERIMENTAL_FILEWATCHER` | boolean | 启用整个目录的文件监视器 |
| `OPENCODE_EXPERIMENTAL_OXFMT` | boolean | 启用 oxfmt 格式化器 |
| `OPENCODE_EXPERIMENTAL_LSP_TOOL` | boolean | 启用实验性 LSP 工具 |

---

## 13. 常见问题

### 13.1 安装问题

**Q: 安装失败怎么办?**
A: 确保已安装依赖 (Node.js/Python)，尝试使用不同的安装方法。

**Q: Windows 上找不到命令?**
A: 检查 PATH 环境变量，或使用完整路径运行。

### 13.2 使用问题

**Q: 如何切换代理?**
A: 使用 **Tab** 键切换主代理，使用 **@** 提及调用子代理。

**Q: 如何撤销更改?**
A: 使用 `/undo` 命令，它会使用 Git 恢复文件更改。

**Q: 如何分享会话?**
A: 使用 `/share` 命令创建可分享链接。

**Q: 如何配置不同的模型?**
A: 使用 `/models` 查看可用模型，使用 `--model` 参数或配置文件设置默认模型。

### 13.3 配置问题

**Q: 如何禁用某些工具?**
A: 在 `permission` 配置中设置相应工具为 `deny` 或 `ask`。

**Q: 如何为不同项目设置不同配置?**
A: 在项目根目录创建 `.opencode/opencode.json` 文件。

**Q: 如何使用自定义提示词?**
A: 在代理配置中使用 `prompt` 选项指定提示词文件路径。

### 13.4 权限问题

**Q: 为什么工具不执行?**
A: 检查权限配置，确保工具设置为 `allow` 或 `ask` 时批准执行。

**Q: 如何只允许特定的 bash 命令?**
A: 使用细粒度的 bash 权限配置。

---

## 附录 A: 键盘快捷键

| 快捷键 | 功能 |
|--------|------|
| `Tab` | 切换代理 |
| `Ctrl+X H` | 显示帮助 |
| `Ctrl+X I` | 初始化项目 |
| `Ctrl+X N` | 新会话 |
| `Ctrl+X U` | 撤销 |
| `Ctrl+X R` | 重做 |
| `Ctrl+X S` | 分享 |
| `Ctrl+X L` | 会话列表 |
| `Ctrl+X M` | 模型列表 |
| `Ctrl+X C` | 压缩会话 |
| `Ctrl+X D` | 工具详情 |
| `Ctrl+X E` | 外部编辑器 |
| `Ctrl+X X` | 导出 |
| `Ctrl+X T` | 主题 |
| `Ctrl+X Q` | 退出 |
| `<Leader>+Right` | 切换到子会话 |
| `<Leader>+Left` | 切换回父会话 |

---

## 附录 B: 快捷键配置

在 `opencode.json` 中自定义快捷键:

```json
{
  "keybind": {
    "switch_agent": "tab",
    "variant_cycle": "ctrl+shift+j",
    "session_child_cycle": "ctrl+right",
    "session_child_cycle_reverse": "ctrl+left"
  }
}
```

---

## 附录 C: 相关资源

- **官网**: https://opencode.ai
- **文档**: https://opencode.ai/docs
- **GitHub**: https://github.com/anomalyco/opencode
- **Discord**: https://opencode.ai/discord
- **Models.dev**: https://models.dev
- **Zen**: https://opencode.ai/zen

---

*文档更新时间: 2026-01-14*

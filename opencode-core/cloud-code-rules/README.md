# Claude Code Leaked Prompts for OpenCode

> 本文件夹包含从 Claude Code 源码泄露中提取的系统提示词和工具定义，可嫁接到 OpenCode 或 TRAE 中使用。

---

## 📁 文件结构

```
cloud-code-rules/
├── README.md                          # 本文件
├── claude-code-system-prompt.md       # Claude Code 主系统提示词
├── claude-code-tools.md              # Claude Code 工具定义和使用说明
└── AGENTS.md                         # Cloud Code 项目规则（之前创建）
```

---

## 📋 文件说明

### 1. claude-code-system-prompt.md
**来源**: Claude Code v1.0.50 泄露源码 (Line 262475-262629)  
**内容**: Claude Code 的核心系统提示词，包含：
- 角色定义（交互式 CLI 工具）
- 安全准则（防御性安全、不猜测 URL）
- 语气和风格（简洁直接、最小化 token、无前后缀）
- 示例演示

### 2. claude-code-tools.md
**来源**: Claude Code 泄露源码  
**内容**: Claude Code 使用的工具定义，包含：
- Task（任务代理）
- Bash（命令执行）
- Glob（文件匹配）
- Grep（代码搜索）
- LS（目录列表）
- Read（文件读取）
- Edit（文件编辑）
- MultiEdit（批量编辑）
- Write（文件写入）
- WebFetch/WebSearch（网络操作）
- TodoRead/TodoWrite（待办事项）
- NotebookRead/NotebookEdit（笔记本操作）

### 3. AGENTS.md
**来源**: Cloud Code 开源项目  
**内容**: Cloud Code 项目的 AI Agent 开发规则

---

## 🚀 如何嫁接到 OpenCode

### 方法 1：作为系统提示词配置

修改 `.opencode/oh-my-openagent.json`：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "instructions": [
    ".opencode/cloud-code-rules/claude-code-system-prompt.md",
    ".opencode/cloud-code-rules/claude-code-tools.md"
  ]
}
```

### 方法 2：作为命令规则

在 `.opencode/command/` 下创建新的命令文件：

```markdown
# claude-code-mode.md
---
name: Claude Code Mode
description: 使用 Claude Code 风格的提示词和工具
---

@import "../cloud-code-rules/claude-code-system-prompt.md"
@import "../cloud-code-rules/claude-code-tools.md"
```

### 方法 3：作为工作流配置

在 `.opencode/workflows/` 下创建工作流：

```yaml
# claude-code-workflow.yml
name: Claude Code Workflow
description: 使用 Claude Code 的提示词和工具集
instructions:
  - ../cloud-code-rules/claude-code-system-prompt.md
  - ../cloud-code-rules/claude-code-tools.md
```

---

## 🔧 如何嫁接到 TRAE

### 方法 1：作为智能体规则

在 `.trae/rules/` 下创建新的规则文件：

```markdown
# claude-code-agent.md
---
id: claude-code-agent
name: Claude Code Agent
version: 1.0
---

## 系统提示词
@import "../../.opencode/cloud-code-rules/claude-code-system-prompt.md"

## 工具定义
@import "../../.opencode/cloud-code-rules/claude-code-tools.md"

## TRAE 特定扩展
- 使用 TRAE 的工具链（Read、Write、RunCommand 等）
- 遵循 TRAE 的三层架构（L1/L2/L3）
- 集成到智能体团队调度系统
```

### 方法 2：作为技能规则

在 `.trae/skills/` 下创建技能：

```markdown
# claude-code-skill.md
## 技能名称：Claude Code 风格助手

## 规则导入
@import "../../.opencode/cloud-code-rules/claude-code-system-prompt.md"

## 能力
- 简洁直接的回答风格
- 最小化 token 使用
- 无前后缀的响应格式
- 防御性安全原则
```

---

## 💡 核心特点

### Claude Code 提示词的核心原则

| 原则 | 说明 |
|------|------|
| **简洁直接** | 回答不超过4行（不包括工具使用或代码生成） |
| **最小化token** | 在保持有用性、质量和准确性的前提下，最小化输出token |
| **无前后缀** | 避免不必要的前言或结语，除非用户要求 |
| **无表情符号** | 除非用户明确要求，否则不使用表情符号 |
| **防御性安全** | 仅协助防御性安全任务，拒绝恶意代码 |
| **不猜测URL** | 绝不生成或猜测URL，除非确信是用于编程帮助 |
| **解释命令** | 运行非平凡bash命令时，解释命令作用和原因 |
| **工具优先** | 仅使用工具完成任务，不使用bash或代码注释与用户通信 |

---

## 📚 参考资源

- [Claude Code 泄露源码分析](https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools)
- [Claude Code 工具定义](https://gist.github.com/wong2/e0f34aac66caf890a332f7b6f9e2ba8f)
- [Claude Code 架构分析](https://claudecoding.dev/posts/prompt-list/)

---

## ⚠️ 免责声明

这些提示词是从 Claude Code 的泄露源码中提取的，仅供学习和研究使用。请遵守相关法律法规，不要将提取的内容用于商业目的或侵犯他人权益。

---

**版本**: v1.0  
**来源**: Claude Code 泄露源码 (v1.0.50)  
**适配**: OpenCode / TRAE  
**日期**: 2026-05-08

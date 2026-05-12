# Auto Memory MCP Server

自动记忆MCP服务器 - 自动识别暗知识并保存到记忆库

**作者**: z80690 (z80690@qq.com)

## 功能

- 自动识别用户消息中的**暗知识**（需要记忆的信息）
- 自动分类存储到不同的记忆类型：
  - `user/` - 用户偏好、习惯
  - `feedback/` - 用户反馈、建议
  - `project/` - 项目规则、设计决策
  - `reference/` - 外部引用、文档链接
- 支持中文内容

## 安装

```bash
npm install -g auto-memory-mcp
```

## 使用

### 在Trae IDE中配置

1. 打开Trae IDE设置
2. 进入MCP配置
3. 添加以下配置：

```json
{
  "mcpServers": {
    "auto-memory": {
      "command": "npx",
      "args": ["-y", "auto-memory-mcp"],
      "cwd": "."
    }
  }
}
```

### 作为库使用

```typescript
import { AutoMemorySystem } from 'auto-memory-mcp';

const memory = new AutoMemorySystem();
const result = memory.process('我习惯用4空格缩进');
console.log(result);
// { auto_saved: true, type: 'user', path: '.trae/memories/user/...', reason: '用户偏好' }
```

## 暗知识识别规则

| 类型 | 关键词 | 示例 |
|------|--------|------|
| 用户偏好 | 习惯、喜欢、偏好 | "我习惯用4空格缩进" |
| 用户反馈 | 很好、认可、建议 | "很好，以后都这样" |
| 团队规则 | 禁止、必须、团队 | "禁止用for循环" |
| 设计决策 | 因为要、为了兼容 | "因为要兼容旧版本" |
| 项目背景 | 系统、项目启动 | "这是电商后台系统" |
| 外部引用 | Jira、票号、文档 | "Jira票号ABC-123" |

## 记忆文件格式

```markdown
---
type: user
created: 2026-05-09 14:40:41
---

# 我习惯用4空格缩进...

我习惯用4空格缩进

**Why:** 用户偏好
**How to apply:** 根据记忆类型自动触发
```

## License

MIT

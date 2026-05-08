---
description: 全量代码质量检查 - 执行 OpenSpec 规范检查和 npm 脚本
agent: build
model: anthropic/claude-sonnet-4-20250514
---

执行完整的代码质量检查，包括以下两个步骤：

**步骤 1: OpenSpec 规范检查**
运行以下命令验证接口规范：
```bash
cd backend && npx openspec validate --all --json
```

**步骤 2: 代码质量检查**
运行以下命令执行 ESLint + Prettier 检查：
```bash
cd backend && npm run quality:check
```

请依次执行上述两个命令，将结果整理后返回给我。如果发现任何问题或错误，请列出具体的文件和修复建议。

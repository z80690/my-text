# oh-my-opencode Workflows

工作流注册目录 - 存放 oh-my-opencode 可调用的自定义工作流

## 已注册工作流

### 1. code-quality-check（代码质量检查）

**触发指令：**
- "全量检查"
- "代码质量检查"
- "质量检查"
- "检查代码质量"

**执行内容：**
1. `openspec validate --all` - 验证 OpenSpec 接口规范
2. `npm run quality:check` - 执行 ESLint + Prettier 检查

**配置文件：**
- `.opencode/workflows/code-quality-check.yml`

## 添加新工作流

在 `.opencode/workflows/` 目录下创建 `.yml` 文件，格式如下：

```yaml
name: workflow-name
description: 工作流描述

triggers:
  - pattern: "触发指令1"
    description: 描述
  - pattern: "触发指令2"
    description: 描述

workflow:
  type: sequential | parallel
  steps:
    - name: step-name
      description: 步骤描述
      command: cd backend && npm run your-script
      timeout: 60000
      onFailure: continue | stop
```

## 验证方法

在工作流文件中包含 `workflow.type` 字段后，oh-my-opencode 会自动加载该工作流。

### 本地验证命令

```bash
# 进入后端目录
cd backend

# 1. 单独测试 OpenSpec 规范检查
npx openspec validate --all --json

# 2. 单独测试 ESLint 检查
npm run lint

# 3. 单独测试 Prettier 检查
npm run format:check

# 4. 执行完整质量检查
npm run quality:check
```

### 通过自然语言触发

在 oh-my-opencode 中输入：
```
"全量检查"
```

系统将自动执行：
1. OpenSpec 规范验证
2. 代码质量检查（ESLint + Prettier）

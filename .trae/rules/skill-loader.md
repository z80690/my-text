---
name: "skill-loader"
description: "技能加载器 - 自动解析技能文件夹，展示信息并询问用户意图"
version: "1.0"
---

# Skill Loader 技能加载器

## 功能说明

自动检测并解析技能文件夹，展示技能信息，然后询问用户要执行什么操作。

## 触发条件

当用户提供以下任一内容时触发：
- 技能文件夹路径
- SKILL.md 文件路径
- "加载技能"、"启动技能"等指令

## 工作流程

### Step 1: 检测技能路径
- 识别用户提供的路径是否为技能文件夹
- 查找是否包含 `SKILL.md` 文件

### Step 2: 解析技能信息
- 读取 `SKILL.md` 的 frontmatter（name、description）
- 列出技能文件夹中的文件结构
- 读取关键文件（如 `examples/`、`config/` 等）

### Step 3: 展示技能卡片
```
📦 技能名称: [name]
📝 技能描述: [description]
📁 文件结构:
  - [file1]
  - [file2]
  ...
```

### Step 4: 询问用户意图
提供以下选项供用户选择：
1. 调用技能执行任务
2. 查看技能详细文档
3. 查看技能示例代码
4. 查看技能配置文件
5. 其他（用户自定义）

## 技能检测逻辑

### 识别技能文件夹
- 检查路径是否包含 `SKILL.md`
- 检查是否为 `.trae/skills/` 下的子文件夹
- 检查是否有标准的技能结构（SKILL.md、config/、examples/ 等）

### 解析 SKILL.md
- 提取 frontmatter 中的 name、description
- 提取文档内容中的关键信息
- 识别触发词和使用场景

## 使用示例

### 场景 1: 用户提供路径
**用户输入**:
`c:\Users\Administrator\Desktop\my-text\.trae\skills\api-token-optimizer`

**加载器响应**:
```
✅ 检测到技能: api-token-optimizer

📦 技能信息:
名称: api-token-optimizer
描述: API Token优化技能，涵盖缓存、限流、轮询、优雅降级、Prompt缓存、Few-shot精选等全面策略。

📁 文件结构:
  - SKILL.md
  - advanced_strategies.py
  - config/github.yaml
  - config/openai.yaml
  - examples/token_optimizer.py

你想用这个技能做什么？
1. 调用技能执行任务
2. 查看技能详细文档
3. 查看技能示例代码
4. 查看技能配置文件
5. 其他（告诉我你想做什么）
```

### 场景 2: 用户拖拽 SKILL.md
**用户输入**:
`c:\Users\Administrator\Desktop\my-text\.trae\skills\api-token-optimizer\SKILL.md`

**加载器响应**:
```
✅ 检测到技能文件: SKILL.md
所属技能: api-token-optimizer

📦 技能信息:
名称: api-token-optimizer
描述: API Token优化技能，涵盖缓存、限流、轮询、优雅降级、Prompt缓存、Few-shot精选等全面策略。

你想用这个技能做什么？
1. 调用技能执行任务
2. 查看技能详细文档
3. 查看技能示例代码
4. 查看技能配置文件
5. 其他（告诉我你想做什么）
```

## 执行模式

### 模式 1: 调用技能
- 使用 `Skill` 工具调用指定技能
- 引导用户提供技能执行所需的参数
- 展示执行结果

### 模式 2: 查看文档
- 读取并展示 `SKILL.md` 完整内容
- 提取关键使用说明和示例

### 模式 3: 查看示例
- 读取 `examples/` 文件夹下的文件
- 展示代码示例并说明

### 模式 4: 查看配置
- 读取 `config/` 文件夹下的配置文件
- 展示配置项并说明用途

## 安全原则

- 不会自动执行任何技能，必须用户明确确认
- 不会修改任何文件，除非用户明确要求
- 所有操作都有明确的用户确认步骤

## 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| 1.0 | 2026-06-01 | 初始版本，实现半自动技能加载功能 |

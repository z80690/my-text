# Skill Loader 使用说明

## 简介

Skill Loader 是一个半自动的技能加载器，帮助你快速加载和使用技能。

## 如何使用

### 方式 1: 提供技能文件夹路径

直接在对话中粘贴技能文件夹的路径，例如：

```
c:\Users\Administrator\Desktop\my-text\.trae\skills\api-token-optimizer
```

### 方式 2: 提供 SKILL.md 文件路径

直接提供 SKILL.md 文件的路径：

```
c:\Users\Administrator\Desktop\my-text\.trae\skills\api-token-optimizer\SKILL.md
```

### 方式 3: 使用指令

使用自然语言指令：

```
加载技能
启动技能
使用 api-token-optimizer 技能
```

## 工作流程

1. **检测技能** - 自动识别你提供的路径是否为技能
2. **解析信息** - 读取技能名称、描述、文件结构
3. **展示卡片** - 以友好的格式展示技能信息
4. **询问意图** - 提供5个选项供你选择

## 可选操作

### 1. 调用技能执行任务

使用 `Skill` 工具调用技能，完成你的任务。

### 2. 查看技能详细文档

读取并展示完整的 `SKILL.md` 内容。

### 3. 查看技能示例代码

查看 `examples/` 文件夹下的示例代码。

### 4. 查看技能配置文件

查看 `config/` 文件夹下的配置文件。

### 5. 其他（用户自定义）

告诉我你想做什么，我会尽力帮你完成。

## 技能要求

一个有效的技能文件夹应该包含：

```
my-skill/
  ├── SKILL.md          # 必需，技能描述文件
  ├── config/           # 可选，配置文件
  ├── examples/         # 可选，示例代码
  └── ...
```

### SKILL.md 格式

```markdown
---
name: "skill-name"
description: "技能描述"
version: "1.0"
---

# 技能名称

技能的详细内容...
```

## 示例

### 示例 1: 加载 API Token 优化器

**你输入**:
```
c:\Users\Administrator\Desktop\my-text\.trae\skills\api-token-optimizer
```

**我的响应**:
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

### 示例 2: 选择查看文档

**你输入**:
```
2
```

**我的响应**:
（展示完整的技能文档）

### 示例 3: 选择调用技能

**你输入**:
```
1. 帮我优化一下当前对话的token消耗
```

**我的响应**:
（调用技能并执行任务）

## 安全原则

- ✅ 不会自动执行任何技能，必须你明确确认
- ✅ 不会修改任何文件，除非你明确要求
- ✅ 所有操作都有明确的确认步骤

## 注意事项

- 确保路径是正确的技能文件夹
- 如果技能文件夹很大，文件列表可能会截断
- 可以随时告诉我你想做什么，不限于提供的选项

## 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| 1.0 | 2026-06-01 | 初始版本 |

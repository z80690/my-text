---
name: file-cleaner
description: 文件清理技能，用于扫描和清理项目中的垃圾文件（如日志、缓存、临时文件等），支持预览模式和安全删除。
version: 1.0.0
author: Meta-Cognition Team
tags: ["cleanup", "file-management", "maintenance", "utilities"]
---

# File Cleaner Skill

## 功能描述

文件清理技能，用于扫描和清理项目中的垃圾文件，支持：

### 核心功能
- 🔍 扫描项目目录中的垃圾文件
- 📋 预览模式：先查看将要删除的文件
- 🗑️ 安全删除：支持回收站备份
- 📊 统计报告：显示清理结果

### 支持清理的文件类型

| 类型 | 扩展名/目录 | 说明 |
|------|-------------|------|
| 日志文件 | `.log`, `.log.*`, `.txt` | 日志和临时文本文件 |
| 缓存文件 | `.pyc`, `__pycache__`, `.pytest_cache` | Python缓存 |
| 依赖目录 | `node_modules`, `.venv`, `venv` | Node.js/Python依赖 |
| 构建产物 | `dist`, `build`, `out` | 编译输出目录 |
| 临时文件 | `.tmp`, `.temp`, `.bak` | 临时文件 |
| IDE配置 | `.idea`, `.vscode`, `.DS_Store` | 编辑器配置 |
| 版本控制 | `.git`, `.svn` | 版本控制目录（谨慎使用） |

## 使用说明

### 方法调用

```python
# 扫描垃圾文件（预览模式）
scan_results = file_cleaner.scan(directory, patterns=None)

# 清理垃圾文件
cleanup_result = file_cleaner.clean(directory, patterns=None, dry_run=True)
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `directory` | str | 当前目录 | 要扫描的目录 |
| `patterns` | list | None | 自定义清理模式列表 |
| `dry_run` | bool | True | 预览模式（不实际删除） |
| `exclude_patterns` | list | [] | 排除的模式列表 |

### 安全特性

1. **预览模式默认开启**：默认不删除文件，先显示将要删除的内容
2. **确认机制**：删除前需要确认
3. **重要目录保护**：自动跳过 `.git`, `node_modules` 等重要目录
4. **大小限制**：可以设置最大删除文件大小
5. **日志记录**：记录所有删除操作

## 触发关键词

- 清理、clean、cleanup、垃圾文件、删除临时文件
- 删除缓存、清除日志、清理项目

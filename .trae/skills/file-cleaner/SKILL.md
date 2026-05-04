---
name: file-cleaner
description: 智能文件清理技能，用于扫描和清理项目中的垃圾文件，支持多层智能保护机制，确保关键文件和目录不会被误删。
version: 2.0.0
author: Meta-Cognition Team
tags: ["cleanup", "file-management", "maintenance", "utilities", "security"]
---

# File Cleaner Skill (智能增强版)

## 功能描述

智能文件清理技能，用于扫描和清理项目中的垃圾文件，支持**多层智能保护机制**。

### 核心功能
- 🔍 **智能扫描**：自动识别垃圾文件和保护文件
- 🛡️ **多层保护**：支持4级保护级别，确保关键文件不被误删
- 📋 **预览模式**：默认不删除，先查看将要删除的内容
- 🗑️ **安全删除**：支持回收站备份
- 📊 **详细报告**：显示清理结果和保护状态

### 支持清理的文件类型

| 类型 | 扩展名/目录 | 说明 |
|------|-------------|------|
| 日志文件 | `.log`, `.log.*`, `.txt`, `logs/` | 日志和临时文本文件 |
| Python缓存 | `.pyc`, `__pycache__`, `.pytest_cache` | Python缓存 |
| 构建产物 | `dist`, `build`, `out` | 编译输出目录 |
| 临时文件 | `.tmp`, `.temp`, `.bak`, `.DS_Store` | 临时文件 |
| IDE配置 | `.idea/`, `.vscode/` | 编辑器配置（谨慎使用） |

---

## 🛡️ 智能保护机制

### 保护级别

| 级别 | 名称 | 说明 |
|------|------|------|
| `none` | 无保护 | 不进行任何保护检查 |
| `low` | 低保护 | 基本路径检查 |
| `medium` | 中等保护 | 路径+危险模式检查 |
| `high` | 高保护 | 路径+危险模式+文件扩展名检查 |
| `critical` | 最高保护 | 多层验证+核心文件保护 |

### 默认保护的文件类型

| 类别 | 扩展名 | 说明 |
|------|--------|------|
| 配置文件 | `.env`, `.config`, `.json`, `.yaml`, `.yml`, `.ini` | 永远不删除 |
| 源代码 | `.py`, `.js`, `.ts`, `.jsx`, `.tsx`, `.html`, `.css`, `.md` | 永远不删除 |
| 数据文件 | `.csv`, `.json`, `.xml`, `.sqlite`, `.db` | 谨慎处理 |

### 默认保护的目录

| 目录 | 保护级别 | 说明 |
|------|---------|------|
| `.trae/` | CRITICAL | 智能体核心配置目录 |
| `.env` | CRITICAL | 环境变量配置文件 |
| `.git/` | HIGH | 版本控制目录 |
| `node_modules/` | HIGH | Node.js依赖 |
| `.venv/`, `venv/` | HIGH | Python虚拟环境 |

---

## 使用说明

### 方法调用

```python
from file_cleaner import scan, clean, get_report, create_cleaner_with_protection

# 1. 创建带保护的清理器
protected_paths = [
    ".trae",
    ".env", 
    "新建文件夹",
    "agent.md"
]
cleaner = create_cleaner_with_protection(protected_paths)

# 2. 扫描（预览模式）
result = cleaner.scan(".")

# 3. 获取详细报告
report = cleaner.get_cleanup_report(".")

# 4. 清理（先预览）
clean_result = cleaner.clean(".", dry_run=True)

# 5. 真正删除
clean_result = cleaner.clean(".", dry_run=False)
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `directory` | str | 当前目录 | 要扫描的目录 |
| `patterns` | list | None | 自定义清理模式列表 |
| `dry_run` | bool | True | 预览模式（不实际删除） |
| `protected_paths` | list | [] | 用户自定义保护路径 |
| `protection_level` | ProtectionLevel | HIGH | 保护级别 |

### 快捷函数

```python
# 扫描（带保护）
result = scan(".", protected_paths=[".trae", ".env"])

# 清理（带保护）
clean_result = clean(".", dry_run=True, protected_paths=[".trae", ".env"])

# 获取报告
report = get_report(".", protected_paths=[".trae", ".env"])
```

---

## 🔒 安全特性

1. **预览模式默认开启**：默认不删除文件，先显示将要删除的内容
2. **多级保护机制**：4级保护级别，满足不同安全需求
3. **双重验证**：删除前再次检查保护状态
4. **自动跳过**：自动跳过受保护的目录和文件
5. **用户确认机制**：删除数量超过阈值时需要确认
6. **备份功能**：支持备份到回收站（可选）
7. **详细日志**：记录所有操作和跳过的文件

---

## API 接口

### FileCleaner 类

| 方法 | 说明 |
|------|------|
| `scan(directory, patterns)` | 扫描目录中的垃圾文件 |
| `clean(directory, patterns, dry_run)` | 清理垃圾文件 |
| `get_cleanup_report(directory, patterns)` | 获取详细报告 |
| `add_protected_path(path, reason)` | 添加自定义保护路径 |
| `remove_protected_path(path)` | 移除保护路径 |
| `get_protected_paths()` | 获取所有保护路径 |
| `is_path_protected(filepath)` | 检查路径是否受保护 |

### 数据结构

```python
# 扫描结果
ScanResult(
    files_found=[...],       # 可删除文件列表
    protected_files=[...],   # 受保护文件列表
    directories_found=[...], # 可删除目录列表
    protected_dirs=[...],    # 受保护目录列表
    total_size=123456,       # 总大小（字节）
    total_count=42           # 可删除文件数量
)

# 清理结果
CleanupResult(
    status="success",           # 清理状态
    files_deleted=10,           # 删除文件数
    dirs_deleted=2,             # 删除目录数
    bytes_freed=1024000,        # 释放空间（字节）
    protected_items=[...],      # 跳过的保护项目
    dry_run=False               # 是否预览模式
)
```

---

## 触发关键词

- 清理、clean、cleanup、垃圾文件、删除临时文件
- 删除缓存、清除日志、清理项目、整理文件

---

## 版本历史

| 版本 | 更新内容 |
|------|---------|
| v2.0.0 | 新增智能保护机制、多级保护级别、自定义保护路径 |
| v1.0.0 | 基础文件清理功能 |

---

**安全提醒**：首次使用建议先用预览模式（`dry_run=True`）查看将要删除的内容，确认无误后再执行真正删除！

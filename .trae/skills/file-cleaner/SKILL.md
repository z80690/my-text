---
name: file-cleaner
description: 智能文件清理技能（Knip 增强版 + API Token 优化），集成未使用文件检测、未使用依赖检测、未使用导出检测和 API Token 优化功能
version: 3.1.0
author: Meta-Cognition Team
tags: ["cleanup", "file-management", "maintenance", "utilities", "security", "auto-clean", "knip", "analysis", "api-token-optimizer"]
---

# File Cleaner Skill (Knip增强版 v3.0)

## 功能描述

智能文件清理技能，集成**Knip核心功能**，用于扫描和清理项目中的垃圾文件，支持**多层智能保护机制**。

### 核心功能
- 🔮 **一键全自动**：一句话就能完成清理，无需手动操作
- 🔍 **智能扫描**：自动识别垃圾文件和保护文件
- 🛡️ **多层保护**：支持5级保护级别，确保关键文件不被误删
- 📋 **预览模式**：默认不删除，先查看将要删除的内容
- 🗑️ **安全删除**：支持回收站备份
- 📊 **详细报告**：显示清理结果和保护状态

### Knip 增强功能
- 📁 **未使用文件检测**：分析模块导入关系，找出未被引用的文件
- 📦 **未使用依赖检测**：分析 package.json，找出未被使用的依赖包
- 📤 **未使用导出检测**：分析代码导出，找出未被引用的导出项
- 🔗 **模块图分析**：构建完整的模块依赖关系图

### API Token 优化功能（v3.1.0 新增）
- 🚀 **API 缓存清理**：自动检测和清理 API 缓存文件
- 💰 **Token 使用报告**：分析 API 调用日志，生成优化建议
- 📊 **缓存命中率分析**：检测缓存策略效果
- 🔍 **浪费检测**：识别不必要的 API 调用

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

### 🔮 一键全自动清理（推荐）

```python
from file_cleaner import auto_clean

# 方式1：直接清理当前目录（自动保护关键文件）
result = auto_clean()

# 方式2：指定目录
result = auto_clean("/path/to/project")

# 方式3：自定义保护路径
result = auto_clean(".", protected_paths=[".trae", ".env", "my_folder"])
```

### 手动模式（高级用户）

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

# 3. 获取详细报告（包含Knip分析）
report = cleaner.get_cleanup_report(".")

# 4. 清理（先预览）
clean_result = cleaner.clean(".", dry_run=True)

# 5. 真正删除
clean_result = cleaner.clean(".", dry_run=False)
```

### Knip分析功能

```python
from file_cleaner import FileCleaner, CleanupConfig

# 创建配置，启用Knip分析
config = CleanupConfig(
    analyze_unused_files=True,
    analyze_unused_dependencies=True,
    analyze_unused_exports=True
)
cleaner = FileCleaner(config)

# 扫描并获取分析结果
result = cleaner.scan(".")

# 访问Knip分析结果
print("未使用文件:", result.unused_files)
print("未使用依赖:", result.unused_dependencies)
print("未使用导出:", result.unused_exports)
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `directory` | str | 当前目录 | 要扫描的目录 |
| `patterns` | list | None | 自定义清理模式列表 |
| `dry_run` | bool | True | 预览模式（不实际删除） |
| `protected_paths` | list | [] | 用户自定义保护路径 |
| `protection_level` | ProtectionLevel | HIGH | 保护级别 |
| `analyze_unused_files` | bool | True | 是否分析未使用文件 |
| `analyze_unused_dependencies` | bool | True | 是否分析未使用依赖 |
| `analyze_unused_exports` | bool | True | 是否分析未使用导出 |

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
| `get_cleanup_report(directory, patterns)` | 获取详细报告（含Knip分析） |
| `add_protected_path(path, reason)` | 添加自定义保护路径 |
| `remove_protected_path(path)` | 移除保护路径 |
| `get_protected_paths()` | 获取所有保护路径 |
| `is_path_protected(filepath)` | 检查路径是否受保护 |

### 数据结构

```python
# 扫描结果（含Knip分析）
ScanResult(
    files_found=[...],           # 可删除文件列表
    protected_files=[...],       # 受保护文件列表
    directories_found=[...],     # 可删除目录列表
    protected_dirs=[...],        # 受保护目录列表
    total_size=123456,          # 总大小（字节）
    total_count=42,              # 可删除文件数量
    
    # Knip分析结果
    unused_files=[...],          # 未使用文件列表
    unused_dependencies=[...],   # 未使用依赖列表
    unused_exports=[...],        # 未使用导出列表
    circular_dependencies=[...]  # 循环依赖列表
)

# 清理结果
CleanupResult(
    status="success",           # 清理状态
    files_deleted=10,           # 删除文件数
    dirs_deleted=2,             # 删除目录数
    bytes_freed=1024000,        # 释放空间（字节）
    protected_items=[...],      # 跳过的保护项目
    dry_run=False,              # 是否预览模式
    
    # Knip分析统计
    unused_files_found=5,       # 发现的未使用文件数
    unused_dependencies_found=3, # 发现的未使用依赖数
    unused_exports_found=8      # 发现的未使用导出数
)
```

---

## 触发关键词

- 清理、clean、cleanup、垃圾文件、删除临时文件
- 删除缓存、清除日志、清理项目、整理文件
- 分析未使用、检测死代码、检查依赖

---

## 版本历史

| 版本 | 更新内容 |
|------|---------|
| v3.0.0 | 集成Knip核心功能：未使用文件检测、未使用依赖检测、未使用导出检测 |
| v2.0.0 | 新增智能保护机制、多级保护级别、自定义保护路径 |
| v1.0.0 | 基础文件清理功能 |

---

## 📊 Knip vs 原生功能对比

| 功能 | 原生file-cleaner | Knip插件 | 本增强版 |
|------|------------------|----------|----------|
| 垃圾文件清理 | ✅ | ❌ | ✅ |
| 构建产物清理 | ✅ | ❌ | ✅ |
| 未使用文件检测 | ❌ | ✅ | ✅ |
| 未使用依赖检测 | ❌ | ✅ | ✅ |
| 未使用导出检测 | ❌ | ✅ | ✅ |
| 循环依赖检测 | ❌ | ✅ | ⚙️（开发中） |
| 支持语言 | 通用 | JS/TS | Python + JS/TS |

---

**安全提醒**：首次使用建议先用预览模式（`dry_run=True`）查看将要删除的内容，确认无误后再执行真正删除！
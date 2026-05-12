# Auto-Refactor Skill v4.0

## 功能
全局代码重构 + 项目级重构：批量安全重构整个项目，支持项目结构重组和文件清理

## 经验教训集成

基于之前的重构失败经验，本技能已增强以下能力：

| 问题类型 | 解决方案 | 实现方式 |
|---------|---------|---------|
| **权限不足** | 使用 PowerShell 突破 Windows 权限限制 | `_apply_change_with_powershell()` |
| **文件丢失** | 增强保护机制和备份恢复 | `restore_from_backup()`, 核心文件保护 |
| **用户确认** | 强制确认流程，模拟模式默认开启 | `execute_plan(confirm=True)` |
| **智能分析** | 改进文件使用评分算法 | 综合考虑引用、年龄、类型 |

## 核心能力矩阵

| 能力类别 | 功能 | 说明 |
|---------|------|------|
| **项目级重构** | `scan_project()` | 扫描项目结构，分析文件使用情况 |
| **项目级重构** | `get_unused_files_report()` | 生成无用文件检测报告 |
| **项目级重构** | `delete_unused_files()` | 安全删除未使用文件（支持风险过滤） |
| **项目级重构** | `separate_subprojects()` | 分离子项目到不同目录 |
| **项目级重构** | `batch_rename()` | 批量重命名文件 |
| **项目级重构** | `cleanup_backups()` | 清理旧备份 |
| **代码级重构** | `extract_method()` | 提取代码块为方法 |
| **代码级重构** | `extract_variable()` | 提取表达式为变量 |
| **代码级重构** | `rename_symbol()` | 智能重命名符号 |
| **代码级重构** | `change_signature()` | 修改方法签名 |
| **代码级重构** | `safe_delete()` | 安全删除符号（检查引用） |
| **安全机制** | `dry_run` | 模拟执行模式（默认开启） |
| **安全机制** | `rollback()` | 回滚操作（支持备份恢复） |
| **安全机制** | `restore_from_backup()` | 从备份恢复项目 |
| **安全机制** | `check_permissions()` | 权限检查 |
| **权限突破** | PowerShell 执行 | 自动使用 PowerShell 处理权限问题 |

## 使用方式

```
# 项目级重构
你: 扫描项目，生成文件使用分析报告
你: 删除所有未使用的文件
你: 将 TRAE 和 OpenCode 项目分离到不同目录
你: 批量重命名文件，将 _old 替换为 _backup
你: 清理7天前的旧备份

# 代码级重构
你: 提取这段代码为方法
你: 重命名变量 oldName 为 newName
你: 修改方法签名，添加新参数
你: 安全删除未使用的函数

# 安全操作
你: 模拟执行删除计划
你: 回滚上次操作
你: 从备份恢复项目
```

## 项目级重构场景

| 场景 | 说明 | 示例 |
|------|------|------|
| **项目扫描** | 分析文件结构和使用情况 | `scan_project()` |
| **无用文件检测** | 识别未被引用的文件 | `get_unused_files_report()` |
| **文件清理** | 安全删除无用文件（支持风险过滤） | `delete_unused_files(risk_filter="low")` |
| **子项目分离** | 将项目拆分为多个子项目 | `separate_subprojects()` |
| **目录重组** | 重新组织目录结构 | 创建新目录并移动文件 |
| **批量重命名** | 按模式批量重命名文件 | `batch_rename("_v1", "_v2")` |
| **备份清理** | 清理过期备份文件 | `cleanup_backups(7)` |

## 代码级重构场景

| 场景 | 说明 | 示例 | 快捷键 |
|------|------|------|--------|
| **Extract Method** | 代码块提取为方法 | 选中代码→提取为独立方法 | Ctrl+Alt+M |
| **Extract Variable** | 复杂表达式提取 | 计算式→变量 | Ctrl+Alt+V |
| **Rename** | 智能重命名 | 自动更新所有引用 | Shift+F6 |
| **Change Signature** | 修改方法签名 | 添加/删除参数 | Ctrl+F6 |
| **Safe Delete** | 安全删除 | 检查引用后删除 | Alt+Delete |

## 执行流程（增强版）

### 1. 智能分析
- 全局搜索目标代码
- 分析影响范围（跨文件引用）
- 检测潜在冲突
- 检查操作权限（支持 PowerShell）
- 制定修改计划

### 2. 预览确认
- 显示变更预览
- 列出受影响文件
- 风险等级评估
- 支持选择性应用
- **模拟执行模式（默认开启）**

### 3. 安全重构
- **创建备份点（自动快照）**
- **用户确认后执行（强制）**
- 逐文件修改
- **PowerShell 权限突破**
- 保持引用一致
- 实时错误检测

### 4. 验证保证
- 运行测试确保功能不变
- 检查语法错误
- 验证边界情况
- 生成重构报告

## 安全保障

| 机制 | 说明 |
|------|------|
| **引用追踪** | 跨文件引用分析 |
| **备份机制** | 重构前自动创建快照 |
| **回滚支持** | 一键撤销重构，支持备份恢复 |
| **冲突检测** | 检测潜在问题并提示 |
| **权限检查** | 保护系统目录，自动切换 PowerShell |
| **风险评估** | 根据文件类型和修改范围评估风险 |
| **模拟执行** | 默认模拟模式，不实际修改文件 |
| **用户确认** | 执行前需要用户确认 |
| **核心文件保护** | 高风险文件（.py, .json）自动保护 |

## 权限保护

**保护目录列表**（禁止操作）：
- `.trae` - TRAE 核心配置
- `.git` - Git 版本控制
- `.vscode` - VSCode 配置
- `node_modules` - 依赖目录
- `__pycache__` - Python 缓存
- `backup_*` - 备份目录

**保护文件类型**（高风险，需确认）：
- `.py`, `.json`, `.yaml`, `.yml` - 核心代码和配置

## 风险等级

| 等级 | 标识 | 触发条件 |
|------|------|---------|
| **low** | 🟢 | 单个文件修改，低风险操作 |
| **medium** | 🟡 | 10-50个文件修改，中等风险 |
| **high** | 🔴 | 50+个文件修改，高风险操作 |
| **critical** | ⚫ | 系统文件或核心配置修改 |

## 输出格式

```
📋============================================================
【重构计划预览】
============================================================
范围: 23个文件
修改: 156处
风险等级: 🟡 medium
模拟模式: ✅
备份创建: ✅ 是

【变更详情】

--- 删除文件 (5处) ---
  • 删除未使用文件 (风险: low, 年龄: 35天): docs/temp.md
  • 删除未使用文件 (风险: medium, 年龄: 120天): src/old_utils.py
  • ...

--- 移动文件 (10处) ---
  • 移动 agent/ → projects/trae/agent/
  • 移动 .trae/ → projects/trae/.trae/
  • ...

【警告】
 ⚠️ 跳过 .trae/config.yaml - 在保护列表中
 ⚠️ 跳过 .git/config - 在保护列表中

============================================================
```

## 配置选项

```yaml
# .auto-refactor.yaml
rules:
  naming_convention: camelCase  # camelCase, snake_case, PascalCase
  max_method_length: 50
  max_nesting_level: 4
  remove_unused_imports: true
  sort_imports: true
  
preview:
  enabled: true
  show_diffs: true
  
safety:
  create_backup: true
  require_confirmation: true
  dry_run_by_default: true
  
project:
  unused_file_threshold: 0.15  # 使用分数低于此值视为未使用
  risk_filter: low  # low, medium, high - 删除时的风险过滤
  
powershell:
  enabled: true  # 启用 PowerShell 权限突破
  timeout: 60  # 超时时间（秒）
```

## API 接口

### 项目级重构

```python
# 扫描项目
structure = refactor.scan_project()

# 生成报告
report = refactor.get_unused_files_report()

# 删除无用文件（模拟模式，仅删除低风险文件）
plan = refactor.delete_unused_files(dry_run=True, risk_filter="low")
result = refactor.execute_plan(plan)

# 分离子项目
config = {
    'trae': ['.trae/**', 'agent/**', 'skills/**', 'mcps/**'],
    'opencode': ['.opencode/**', 'backend/**', 'openapi/**']
}
plan = refactor.separate_subprojects(config, dry_run=False)
result = refactor.execute_plan(plan)

# 批量重命名
plan = refactor.batch_rename("_old", "_backup")
result = refactor.execute_plan(plan)

# 清理备份
plan = refactor.cleanup_backups(days_to_keep=7)
result = refactor.execute_plan(plan)
```

### 代码级重构

```python
# 提取方法
plan = refactor.extract_method(
    file_path='src/utils/helpers.py',
    start_line=10,
    end_line=15,
    method_name='calculate_score'
)

# 重命名
plan = refactor.rename_symbol(
    file_path='src/main.py',
    symbol_name='old_function',
    new_name='process_data',
    scope='project'
)
```

### 安全操作

```python
# 从备份恢复
success = refactor.restore_from_backup()

# 回滚操作
success = refactor.rollback(steps=1)

# 检查权限
permissions = refactor.check_permissions(['src/', 'docs/'])
```

## 文件分析算法

文件使用评分算法综合考虑以下因素：

| 因素 | 权重 | 说明 |
|------|------|------|
| 基础分 | 0.1 | 所有文件默认得分 |
| 被引用数 | 0.15/引用 | 最多 +0.5 |
| 依赖数 | 0.05/依赖 | 最多 +0.2 |
| 文件年龄（≤7天） | +0.15 | 近期修改加分 |
| 文件年龄（≤30天） | +0.1 | 较新文件加分 |
| 文件年龄（≤90天） | +0.05 | 中等年龄加分 |
| 代码文件 | +0.05 | Python/JS/TS/Go 文件 |

**判定标准**：使用分数 > 0.15 视为已使用，否则视为未使用

## 支持语言
- JavaScript/TypeScript
- Python
- Java
- Go
- Rust
- Vue/React（框架特定）

## 版本历史

| 版本 | 新增功能 |
|------|---------|
| **v4.0** | PowerShell 权限突破、增强备份恢复、改进文件评分算法、批量操作、核心文件保护 |
| **v3.0** | 项目级重构、模拟执行、权限检查、回滚功能 |
| **v2.0** | 增强版执行流程、安全保障机制 |
| **v1.0** | 基础代码重构功能 |
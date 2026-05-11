# Skills 自动化系统使用指南

## 🎯 系统概述

本系统为所有 Skills 提供三大自动化功能：
1. **自动追踪** - 记录每次 Skill 执行的详细信息
2. **自动日志** - 生成可读的 Markdown 日志
3. **智能建议** - 根据使用情况推荐下一步操作

---

## 📁 文件结构

```
.trae/
├── skill_auto_integration.py    # 核心自动化模块
├── skill_runner.py              # 统一运行入口
├── auto_hook_system.py          # 钩子系统
├── tool_usage_tracker.py        # 工具追踪器
├── logs/
│   ├── skill_executions_*.json  # 执行记录
│   ├── auto_events_*.md         # 事件日志
│   └── tool_calls_*.json        # 工具调用日志
└── hooks/
    └── hook_config.json         # 钩子配置
```

---

## 🚀 快速使用

### 方式1：使用快捷函数

```python
from skill_runner import quick_debug, quick_hook, quick_doc, quick_refactor, quick_privacy, quick_tracker

# 智能排错
result = quick_debug("TypeError: 'NoneType' object is not callable")

# 设置钩子
result = quick_hook("post_save", "auto_format")

# 生成文档
result = quick_doc("my-project", "README")

# 代码重构
result = quick_refactor("old_pattern", "new_pattern")

# 本地隐私读取
result = quick_privacy("/path/to/local/file")

# 查看统计
summary = quick_tracker()
```

### 方式2：使用装饰器

```python
from skill_auto_integration import with_auto_tracking

@with_auto_tracking("my-skill", "custom_action")
def my_function(x, y):
    return x + y

result = my_function(10, 20)  # 自动追踪、记录、建议
```

### 方式3：使用执行器

```python
from skill_runner import get_runner

runner = get_runner()
result = runner.run_debug("错误信息")
```

---

## 📊 自动追踪功能

每次 Skill 执行都会自动记录：

| 字段 | 说明 |
|------|------|
| `skill_id` | Skill 标识符 |
| `action` | 执行动作 |
| `start_time` | 开始时间 |
| `end_time` | 结束时间 |
| `duration_ms` | 耗时（毫秒） |
| `status` | 状态（success/failed） |
| `input_data` | 输入数据 |
| `output_data` | 输出数据 |
| `error` | 错误信息（如有） |

---

## 📝 自动日志功能

自动生成 Markdown 格式的日志：

```markdown
### 08:24:47 [ℹ️ INFO] SKILL_START

**Skill**: `auto-debug`

```json
{
  "action": "analyze",
  "input": {...}
}
```
---

### 08:24:47 [✅ SUCCESS] SKILL_END

**Skill**: `auto-debug`

```json
{
  "action": "analyze",
  "status": "success",
  "duration_ms": 2.01
}
```
```

---

## 💡 智能建议功能

### Skill 关系映射

| 当前 Skill | 推荐下一步 | 原因 |
|-----------|-----------|------|
| auto-debug | auto-refactor, auto-doc | 调试完成后建议重构或生成文档 |
| auto-doc | auto-hook, auto-refactor | 生成文档后建议设置提醒或重构 |
| auto-refactor | auto-debug, auto-doc | 重构完成后建议测试或更新文档 |
| auto-hook | local-privacy, auto-doc | 设置钩子后建议配置隐私或生成文档 |
| local-privacy | auto-hook, auto-debug | 隐私配置后建议设置钩子或测试 |
| tool-usage-tracker | auto-hook, auto-doc | 查看统计后建议设置钩子或生成报告 |

### 工作流建议

| 工作流 | 步骤 |
|--------|------|
| debug_flow | auto-debug → auto-refactor → auto-doc |
| doc_flow | auto-doc → auto-hook → local-privacy |
| refactor_flow | auto-refactor → auto-debug → auto-doc |
| setup_flow | auto-hook → tool-usage-tracker → local-privacy |

---

## 🔗 钩子系统

### 已注册的钩子

| 触发器 | 动作 | 说明 |
|--------|------|------|
| `post_tool_call` | `track_usage` | 工具调用后自动追踪 |
| `post_tool_call` | `log_event` | 工具调用后自动记录 |
| `post_skill_load` | `track_usage` | Skill 加载后自动追踪 |
| `post_skill_load` | `log_event` | Skill 加载后自动记录 |
| `post_skill_load` | `auto_suggest` | Skill 加载后自动建议 |

---

## 📈 今日统计示例

```
# 📊 今日 Skills 使用摘要

**总执行**: 3 次
**成功**: 3 次
**失败**: 0 次
**平均耗时**: 3.34 ms

## 💡 智能建议

💡 建议使用 auto-hook 设置自动化钩子，提升开发效率

**推荐工作流**: debug_flow
**建议**: 建议继续完成 debug_flow
```

---

## 🧪 测试验证

运行测试脚本：

```bash
python .trae/skill_runner.py
```

输出示例：

```
🚀 执行 Skill: 智能排错 (auto-debug)
   动作: analyze
   分类: debugging

💡 智能建议:
  1. 🔥 使用 auto-refactor
     └─ 调试完成后，建议重构代码或生成文档
  2. 📌 使用 auto-doc
     └─ 调试完成后，建议重构代码或生成文档

调试结果: {'analysis': '...', 'steps': [...], 'status': 'analyzing'}
```

---

## ✅ 功能清单

- [x] 自动追踪所有 Skill 执行
- [x] 自动生成 Markdown 日志
- [x] 智能推荐下一步操作
- [x] Skill 关系映射
- [x] 工作流建议
- [x] 钩子系统集成
- [x] 统计报告生成
- [x] 装饰器支持
- [x] 快捷函数支持

---

## 版本信息

| 项目 | 版本 |
|------|------|
| 自动化系统 | v1.0 |
| 创建日期 | 2026-05-11 |
| 包含 Skills | 6 |
| 钩子数量 | 8 |

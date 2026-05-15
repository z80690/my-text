---
name: tool-usage-tracker
description: 工具调用追踪技能 - 自动记录和读取真实工具调用日志，支持实时监控
version: 2.0.0
author: TRAE System
tags: ["tracking", "monitoring", "reporting", "MCP", "skills", "analytics", "v2"]
---

# 工具调用追踪技能 v2.0

## 🆕 v2.0 更新内容

### 修复问题
- ✅ **真实数据读取**：现在能够正确读取系统日志文件，不再依赖模拟数据
- ✅ **诚信原则**：严格遵守诚信原则，如实报告系统状态
- ✅ **数据可追溯**：所有数据都有明确来源和记录时间

### 新增功能
- 🔍 **日志状态检查**：新增 `check_logs()` 函数检查日志状态
- 📊 **最近调用查询**：新增 `get_recent_calls_summary()` 获取最近N次调用
- 📝 **诚实报告**：如果没有数据，明确告知"暂无工具调用记录"

---

## 功能描述

追踪系统中所有 MCP 和 Skills 的调用情况，自动记录调用时间、状态、耗时等信息，并生成每日报告。

### 核心功能

- 🔍 **自动追踪**：自动记录所有 MCP 和 Skills 的调用
- 📊 **统计分析**：实时统计调用次数、成功率、平均耗时
- 📝 **每日报告**：自动生成 Markdown 格式的日报
- ⏰ **时段分布**：分析不同时段的调用频率
- ❌ **错误追踪**：记录失败调用的详细信息
- ✅ **诚实透明**：如实报告，不伪造数据

---

## 🎯 触发条件

### 自动触发
- MCP 工具调用时自动记录
- Skills 工具调用时自动记录

### 手动触发
- 关键词：报告、日报、追踪、统计、监控、日志、检查

---

## 📁 文件结构

```
.trae/
├── tool_usage_tracker_v2.py    # 核心追踪模块 v2.0
├── logs/                        # 日志存储
│   └── tool_calls_YYYY-MM-DD.json
└── reports/                     # 报告存储
    └── 工具调用日报_YYYY-MM-DD.md
```

---

## 使用说明

### 快速开始

```python
from tool_usage_tracker_v2 import (
    track_mcp_call, 
    track_skill_call, 
    generate_daily_report,
    get_recent_calls,
    check_logs
)

# 检查日志状态
status = check_logs()
print(f"记录数: {status['record_count']}")
print(f"状态: {status['message']}")

# 记录 MCP 调用
track_mcp_call(
    tool_name="Read",
    action="read_file",
    status="success",
    duration_ms=125.5
)

# 记录 Skill 调用
track_skill_call(
    tool_name="file-cleaner",
    action="clean_files",
    status="success",
    duration_ms=2340.0
)

# 获取最近10次调用
recent = get_recent_calls(10)
for call in recent:
    print(f"{call['tool_name']}: {call['action']}")

# 生成今日报告
report = generate_daily_report()
```

### 命令行工具

```bash
python -m tool_usage_tracker_v2        # 测试追踪器
python generate_report.py --today      # 生成今日报告
python generate_report.py --stats      # 显示今日统计
```

---

## 🔌 API 接口

### 追踪函数

| 函数 | 参数 | 说明 |
|------|------|------|
| `track_mcp_call(tool_name, action, status, duration_ms, error=None, metadata=None)` | 工具名、操作、状态、耗时(ms) | 记录 MCP 调用 |
| `track_skill_call(tool_name, action, status, duration_ms, error=None, metadata=None)` | 工具名、操作、状态、耗时(ms) | 记录 Skill 调用 |

### 查询函数

| 函数 | 说明 |
|------|------|
| `check_logs()` | 检查日志状态，返回记录数和状态信息 |
| `get_recent_calls(count=10)` | 获取最近N次调用 |
| `get_daily_stats()` | 获取今日统计数据 |
| `get_summary()` | 获取今日摘要 |

### 报告函数

| 函数 | 说明 |
|------|------|
| `generate_daily_report(date=None)` | 生成指定日期的报告 |
| `list_all_reports()` | 列出所有可用报告 |

---

## 📊 报告内容

### 总体统计
- 总调用次数
- MCP 调用次数
- Skill 调用次数
- 成功率
- 平均耗时

### 工具详情
- 各工具调用次数
- 成功率
- 平均耗时
- 操作分布

### 时段分布
- 各时段调用统计

### 错误记录
- 失败调用详情

---

## 📝 日志格式

```json
{
  "tool_type": "mcp",
  "tool_name": "Read",
  "action": "read_file",
  "timestamp": "2026-05-15T10:30:00",
  "status": "success",
  "duration_ms": 125.5,
  "error": null,
  "metadata": {}
}
```

---

## ⚠️ 诚信原则

根据 L3-R018 诚信原则，本技能严格遵守：

- ✅ **诚实透明**：如实报告系统状态，不伪造任何数据
- ✅ **如实告知**：如果没有数据，直接说明"暂无工具调用记录"
- ✅ **数据来源可追溯**：所有数据都有明确来源

❌ **禁止行为**：
- 禁止伪造日志数据
- 禁止编造工具调用记录
- 禁止虚构任务执行结果

---

## 触发关键词

- 报告、日报、追踪、统计、监控
- 工具调用、MCP、Skills
- 查看日志、分析调用、检查日志

---

## 版本历史

| 版本 | 更新内容 |
|------|---------|
| v2.0.0 | 修复数据读取问题，新增日志检查功能，遵循诚信原则 |
| v1.0.0 | 初始版本：基础追踪和报告功能 |

---

## ⚠️ 注意事项

- 日志文件保留 30 天
- 报告文件保留 90 天
- 建议定期清理旧日志文件
- **重要**：系统如实报告，绝不伪造数据

---

**版本**：v2.0.0 | **更新日期**：2026-05-15
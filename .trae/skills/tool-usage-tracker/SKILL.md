---
name: tool-usage-tracker
description: 工具调用追踪技能 - 追踪MCP和Skills的调用情况，自动生成每日报告
version: 1.0.0
author: TRAE System
tags: ["tracking", "monitoring", "reporting", "MCP", "skills", "analytics"]
---

# 工具调用追踪技能 v1.0

## 功能描述

追踪系统中所有 MCP 和 Skills 的调用情况，自动记录调用时间、状态、耗时等信息，并生成每日报告。

### 核心功能

- 🔍 **自动追踪**：自动记录所有 MCP 和 Skills 的调用
- 📊 **统计分析**：实时统计调用次数、成功率、平均耗时
- 📝 **每日报告**：自动生成 Markdown 格式的日报
- ⏰ **时段分布**：分析不同时段的调用频率
- ❌ **错误追踪**：记录失败调用的详细信息

---

## 🎯 触发条件

### 自动触发
- MCP 工具调用时自动记录
- Skills 工具调用时自动记录

### 手动触发
- 关键词：报告、日报、追踪、统计、监控

---

## 📁 文件结构

```
.trae/
├── tool_usage_tracker.py    # 核心追踪模块
├── logs/                     # 日志存储
│   └── tool_calls_YYYY-MM-DD.json
└── reports/                  # 报告存储
    └── 工具调用日报_YYYY-MM-DD.md
```

---

## 使用说明

### 快速开始

```python
from tool_usage_tracker import track_mcp_call, track_skill_call, generate_report

# 记录 MCP 调用
track_mcp_call(
    tool_name="auto-memory",
    action="write_memory",
    status="success",
    duration_ms=125.5
)

# 记录 Skill 调用
track_skill_call(
    tool_name="nuwa-skill",
    action="distill",
    status="success",
    duration_ms=3500.0
)

# 生成今日报告
report = generate_report()
```

### 命令行工具

```bash
python generate_report.py --today      # 生成今日报告
python generate_report.py --yesterday  # 生成昨日报告
python generate_report.py --stats      # 显示今日统计
python generate_report.py --list       # 列出所有报告
```

---

## 🔌 API 接口

### 追踪函数

| 函数 | 参数 | 说明 |
|------|------|------|
| `track_mcp_call(tool_name, action, status, duration_ms, error=None, metadata=None)` | 工具名、操作、状态、耗时(ms) | 记录 MCP 调用 |
| `track_skill_call(tool_name, action, status, duration_ms, error=None, metadata=None)` | 工具名、操作、状态、耗时(ms) | 记录 Skill 调用 |

### 报告函数

| 函数 | 说明 |
|------|------|
| `generate_report(date=None)` | 生成指定日期的报告 |
| `get_today_stats()` | 获取今日统计数据 |
| `list_reports()` | 列出所有可用报告 |

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

## 📋 支持的工具

### MCP 工具
| 名称 | 描述 |
|------|------|
| auto-memory | 自动记忆MCP |
| auto-workflow | 自动工作流MCP |
| knowledge-graph | 知识图谱MCP |
| trae-auto-memory | TRAE自动记忆MCP |

### Skills 工具
| 名称 | 描述 |
|------|------|
| auto-memory | 自动记忆技能 |
| file-cleaner | 智能文件清理技能 |
| my-code-review | 代码审查技能 |
| nuwa-skill | 女娲造人技能 |
| tool-usage-tracker | 工具调用追踪技能 |

---

## 📝 日志格式

```json
{
  "tool_type": "mcp",
  "tool_name": "auto-memory",
  "action": "write_memory",
  "timestamp": "2026-05-11T10:30:00",
  "status": "success",
  "duration_ms": 125.5,
  "error": null,
  "metadata": {}
}
```

---

## 触发关键词

- 报告、日报、追踪、统计、监控
- 工具调用、MCP、Skills
- 查看日志、分析调用

---

## 版本历史

| 版本 | 更新内容 |
|------|---------|
| v1.0.0 | 初始版本：基础追踪和报告功能 |

---

## ⚠️ 注意事项

- 日志文件保留 30 天
- 报告文件保留 90 天
- 建议定期清理旧日志文件

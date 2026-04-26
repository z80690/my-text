# Meta-Cognition Skill

## 概述

元认知技能，用于在每次任务执行前后自动记录和分析调度策略的有效性。

## 触发条件

- **前置钩子 (Pre-Task)**：执行任何任务前自动触发
- **后置钩子 (Post-Task)**：执行任何任务后自动触发

## 文件结构

```
meta-cognition/
├── SKILL.md           # 本文件
├── hooks/
│   ├── __init__.py
│   ├── pre_task_hook.py    # 前置钩子：读取调度状态
│   └── post_task_hook.py   # 后置钩子：写入调度结果
└── logs/
    └── meta_cognition.json  # 调度日志存储
```

## 功能说明

### 前置钩子 (Pre-Task)

在任务执行前记录：
- 当前时间戳
- 任务类型识别
- 调度决策（使用博弈模式还是常规模式）
- 预期的智能体分配

### 后置钩子 (Post-Task)

在任务执行后记录：
- 任务执行结果（成功/失败）
- 实际使用的智能体
- 执行耗时
- 异常信息（如果有）

## 使用方式

TRAE 会自动在以下时机调用：

1. **用户发送任何任务消息时** → 自动调用 `pre_task_hook.py`
2. **智能体返回任何响应时** → 自动调用 `post_task_hook.py`

## 数据格式

### 调度日志结构

```json
{
  "sessions": [
    {
      "session_id": "uuid",
      "timestamp": "ISO8601",
      "task": "任务描述",
      "mode": "game_theory | normal",
      "agents_used": ["agent1", "agent2"],
      "result": "success | failure",
      "duration_ms": 1234,
      "error": null
    }
  ]
}
```

## 分析能力

基于记录的日志数据，可以分析：
- 调度成功率
- 平均响应时间
- 智能体利用率
- 博弈模式使用频率
- 常见失败模式
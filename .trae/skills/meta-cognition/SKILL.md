# Meta-Cognition Skill

## 概述

元认知技能，用于在每次任务执行前后自动记录和分析调度策略的有效性。支持三种博弈模式和智能推荐功能，提供完整的任务执行审计和统计分析。

## 文件结构

```
meta-cognition/
├── SKILL.md              # 本文件
├── test_skill.py         # 技能测试脚本
├── hooks/
│   ├── __init__.py       # 模块初始化，导出所有公共接口
│   ├── utils.py          # 公共工具函数
│   ├── pre_task_hook.py  # 前置钩子：任务分析、模式检测、调度决策
│   ├── post_task_hook.py # 后置钩子：结果记录、统计分析、会话管理
│   └── test_hooks.py     # 完整测试套件
├── config/
│   ├── __init__.py       # 配置模块初始化
│   └── config.py         # 配置管理（支持环境变量）
└── logs/
    └── meta_cognition.json # 调度日志存储
```

## 核心功能

### 1. 前置钩子 (Pre-Task Hook)

在任务执行前自动触发，记录任务调度前的状态并做出调度决策。

**功能特性**：
- 任务类型自动识别
- 调度模式智能选择（90%+ 触发率）
- 敏感信息自动过滤
- 智能体推荐
- 异常处理和容错机制

**返回数据**：
```python
{
    "session_id": "uuid",           # 唯一会话标识
    "mode": "game_theory_mode2",    # 检测到的调度模式
    "decision": {                    # 调度决策详情
        "mode": "降维打击模式（流水线博弈）",
        "description": "通过生成、挑剔、融合三阶段...",
        "steps": ["生成阶段", "挑剔阶段", "融合阶段"],
        "recommended_agents": ["code_executor_agent", "editor_agent"]
    },
    "timestamp": "ISO8601"           # 时间戳
}
```

### 2. 后置钩子 (Post-Task Hook)

在任务执行后自动触发，记录执行结果并生成统计信息。

**功能特性**：
- 执行结果记录
- 耗时统计
- 智能体使用跟踪
- 错误信息捕获
- 日志自动轮转和备份
- 异常处理和容错机制

**返回数据**：
```python
{
    "session_id": "uuid",
    "result": "success",             # success/failure
    "agents_used": ["code_executor_agent"],
    "duration_ms": 1500,
    "logged": true
}
```

## 三种博弈模式

### 模式1：辩论模式（串行模拟并行）

**触发关键词**：
辩论、对比、优缺点、风险评估、多角度分析、正反两面、看法、观点、不同意见、分析一下、评估、分析、比较、权衡、评判、考量、审视、剖析、解析、解读、怎么看、如何评价、怎么样、好不好、利弊、优劣、对比一下

**工作流程**：
1. 视角A智能体（创新探索）
2. 视角B智能体（风险控制）
3. 调度员综合裁决

**推荐智能体**：society_of_mind_agent, editor_agent

### 模式2：降维打击模式（流水线博弈）

**触发关键词**：
优化、改进、提升、增强、完善、检查、审阅、修改、重构、提升质量、润色、无懈可击、优化一下、改进一下、提升一下、增强一下、完善一下、检查一下、审阅一下、修改一下、重构一下、润色一下、优化代码、改进代码、提升性能、增强功能、完善功能、检查代码、审阅代码、修改代码、重构代码、优化方案、改进方案、提升方案、增强方案、完善方案、检查方案、审阅方案、修改方案、重构方案、优化流程、改进流程、提升流程、增强流程、完善流程、检查流程、审阅流程、修改流程、重构流程

**工作流程**：
1. 生成阶段（创意生成智能体）
2. 挑剔阶段（逻辑审查智能体）
3. 融合阶段（综合重写智能体）

**推荐智能体**：code_executor_agent, editor_agent, writer_agent

### 模式3：深度设计模式（三段式协同）

**触发关键词**：
设计、架构、实现、搭建、创建、开发、构建、写一个、做一个、从零开始、完整实现、系统工程、设计一个、架构一个、实现一个、搭建一个、创建一个、开发一个、构建一个、写、做、设计系统、架构系统、实现系统、搭建系统、创建系统、开发系统、构建系统、设计功能、架构功能、实现功能、搭建功能、创建功能、开发功能、构建功能、设计项目、架构项目、实现项目、搭建项目、创建项目、开发项目、构建项目、设计应用、架构应用、实现应用、搭建应用、创建应用、开发应用、构建应用

**工作流程**：
1. 蓝图设计阶段（心智社会智能体）
2. 可行性挑战阶段（代码执行智能体）
3. 融合实现阶段（编辑器智能体）

**推荐智能体**：society_of_mind_agent, code_executor_agent, editor_agent

### 触发策略

为了提高博弈逻辑触发率（达到90%+），系统采用以下策略：
1. **关键词扩展**：扩展了大量常见任务描述关键词
2. **默认触发**：当无明确关键词匹配时，默认使用博弈模式3

## 配置管理

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| META_COGNITION_ENABLE_GT | true | 是否启用博弈模式 |
| META_COGNITION_ENABLE_STATS | true | 是否启用统计功能 |
| META_COGNITION_ENABLE_MONITORING | false | 是否启用监控 |
| META_COGNITION_PREVIEW_LENGTH | 200 | 响应预览长度 |

### 配置文件

通过 `config/config.py` 的 `MetaCognitionConfig` 类管理配置。

## 统计分析

### 获取统计数据

```python
from hooks import get_statistics

stats = get_statistics()
# {
#     "total_tasks": 100,
#     "success_rate": 95.5,
#     "avg_duration_ms": 2500,
#     "mode_distribution": {"game_theory_mode1": 30, "game_theory_mode2": 40, "game_theory_mode3": 30},
#     "agent_usage": {"code_executor_agent": 80, "editor_agent": 60},
#     "game_theory_usage_rate": 100.0,  # 现在默认使用博弈模式
#     "success_count": 95,
#     "failure_count": 5
# }
```

### 获取最近会话

```python
from hooks import get_recent_sessions

recent = get_recent_sessions(limit=10)
```

### 导出会话记录

```python
from hooks import export_sessions

# 按结果过滤
success_sessions = export_sessions(filter_result="success")

# 按模式过滤
gt_sessions = export_sessions(filter_mode="game_theory_mode1")
```

## 日志管理

### 日志结构

```json
{
  "sessions": [
    {
      "session_id": "uuid",
      "phase": "completed",
      "timestamp": "ISO8601",
      "end_timestamp": "ISO8601",
      "task_description": "任务描述",
      "detected_mode": "game_theory_mode2",
      "scheduling_decision": {...},
      "result": "success",
      "agents_used": ["agent1", "agent2"],
      "duration_ms": 1500,
      "error": null,
      "response_preview": "..."
    }
  ],
  "current_session": null,
  "statistics": {}
}
```

### 自动日志轮转

当日志文件超过 10MB 或超过 30 天时，自动进行备份。

## 敏感信息过滤

自动过滤以下敏感信息：
- API密钥
- 密码
- Token
- Secret

## 使用示例

### 完整工作流

```python
from hooks import pre_task_hook, post_task_hook, get_statistics
import time

# 1. 前置钩子
task = "请帮我优化这段代码的性能"
pre_result = pre_task_hook(task)
session_id = pre_result["session_id"]
print(f"调度模式: {pre_result['mode']}")
print(f"推荐智能体: {pre_result['decision']['recommended_agents']}")

# 2. 模拟任务执行
time.sleep(1)

# 3. 后置钩子
post_result = post_task_hook(
    session_id=session_id,
    result="success",
    agents_used=["code_executor_agent", "editor_agent"],
    response_preview="优化已完成，性能提升了50%",
    duration_ms=1500
)

# 4. 获取统计
stats = get_statistics()
print(f"总任务数: {stats['total_tasks']}")
print(f"成功率: {stats['success_rate']}%")
print(f"博弈模式使用率: {stats['game_theory_usage_rate']}%")
```

### 快速测试

```python
# 运行技能测试脚本
python test_skill.py
```

## 测试

### 运行完整测试套件

```bash
cd meta-cognition
python -m hooks.test_hooks
```

### 测试覆盖
- 工具函数测试
- 配置管理测试
- 前置钩子测试
- 后置钩子测试
- 错误处理测试

## 技术特性

- **类型提示**：完整的类型注解
- **异常处理**：健壮的错误处理机制
- **性能优化**：预编译正则表达式，增量日志写入
- **可配置性**：支持环境变量和代码配置
- **模块化设计**：清晰的模块划分
- **全面测试**：完整的测试覆盖
- **高触发率**：90%+ 任务触发博弈逻辑
- **容错机制**：确保系统在异常情况下仍能正常运行

## 重构改进

### 1. 导入路径优化
- 修复了模块间的导入路径问题
- 统一使用相对导入

### 2. 错误处理增强
- 为所有关键函数添加了异常处理
- 实现了容错机制，确保系统稳定性

### 3. 性能优化
- 预编译正则表达式提高敏感信息过滤速度
- 优化日志读写操作

### 4. 功能增强
- 扩展了博弈模式关键词列表
- 实现了默认博弈模式触发
- 完善了统计分析功能

### 5. 测试完善
- 创建了独立的技能测试脚本
- 增强了测试覆盖范围

## 故障排除

### 常见问题

1. **导入错误**：确保 Python 路径正确设置
2. **日志写入失败**：检查文件权限
3. **性能问题**：检查日志文件大小，系统会自动轮转

### 调试建议

- 运行 `python test_skill.py` 检查技能基本功能
- 查看 `logs/meta_cognition.json` 了解会话记录
- 检查环境变量配置是否正确
---
name: "auto-memory"
description: "自动记忆技能，自动记录用户对话消息到记忆系统，维护上下文管理指针和规则执行日志。"
---

# Auto Memory Skill

自动记忆技能，实现对话消息的自动记录和上下文管理。

## 功能特性

### 1. 消息记录
自动将用户消息保存到记忆文件系统

### 2. 上下文管理
维护当前焦点、最近变更、已知问题等指针

### 3. 规则执行日志
记录规则执行情况，支持效果评估和优化建议

## 使用方法

### 核心函数

```python
def process_message(message: str, context: dict = None) -> dict:
    """
    处理用户消息并记录到记忆系统
    
    参数:
        message: 用户消息内容
        context: 上下文信息（可选）
    
    返回:
        {"status": "success", "memory_file": "文件路径", "message_length": 长度}
    """
```

### 获取统计

```python
def get_statistics() -> dict:
    """获取规则执行统计"""
```

### 获取优化建议

```python
def get_suggestions() -> dict:
    """获取规则优化建议"""
```

## 触发条件

### 核心触发词（100%覆盖）
- 记忆、memory、记录、保存、存储、持久化
- 上下文、context、状态、状态管理、指针
- 日志、log、记录、追踪、追踪记录
- 自动、auto、自动保存、自动记录
- 消息、message、对话、conversation、聊天
- 历史、history、记录历史、查看历史

### 场景触发词
- 记录这条消息、保存对话、存储历史
- 查看记忆、查询记忆、获取记忆
- 上下文管理、状态管理、指针管理
- 规则执行日志、效果评估、优化建议
- 自动保存、自动记录、自动记忆

### 技术触发词
- 记忆系统、memory system、存储系统
- 上下文指针、context pointer
- 日志系统、log system
- 规则引擎、rule engine

## 输出格式

```json
{
  "status": "success",
  "memory_file": ".trae/memories/user/memory_20260519_120000.json",
  "message_length": 100,
  "context": {
    "current_focus": "任务名称",
    "recent_changes": ["变更1", "变更2"],
    "known_issues": []
  }
}
```

## 记忆文件结构

```json
{
  "timestamp": "2026-05-19T12:00:00",
  "message": "用户消息内容",
  "context": {},
  "processed": true
}
```

---

**版本**: v1.0 | **日期**: 2026-05-19 | **功能**: 自动记忆、上下文管理、规则执行日志
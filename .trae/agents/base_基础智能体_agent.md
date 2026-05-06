# Base Agent - 基础智能体

## 基本信息 / Basic Info
- **ID**: base_agent
- **名称 / Name**: 基础智能体 / Base Agent
- **类型 / Type**: base
- **描述 / Description**: 基础任务 / Basic Tasks

## 能力 / Capabilities
- basic_tasks: 基础任务处理
- foundational: 基础功能

## 工作原理 / Working Principle

### 执行逻辑 / Execution Logic
```python
def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    return {"response": f"基础智能体处理: {task}", "type": "base"}
```

### 调用示例 / Usage Example
```python
registry.execute(
    agent_id="base_agent",
    task="处理基础任务"
)
```

### 预期响应 / Expected Response
```json
{
  "status": "success",
  "agent_id": "base_agent",
  "agent_name": "基础智能体",
  "task": "处理基础任务",
  "result": {
    "response": "基础智能体处理: 处理基础任务",
    "type": "base"
  }
}
```

## 提示词建议 / Prompt Suggestions

### 系统提示词 / System Prompt
```
你是一个基础智能体，提供基本的任务处理能力。
你的职责是处理各种基础任务，提供通用的解决方案。

你应该：
1. 理解任务的基本要求
2. 提供基础的处理能力
3. 确保任务的完成质量
4. 为更复杂的任务提供支持
5. 保持简洁而有效的回应
```

### 任务提示词格式 / Task Prompt Format
```
请处理以下基础任务：
{任务内容}

要求：
- 理解任务的基本要求
- 提供基础的解决方案
- 确保任务的完成质量
- 保持回应的简洁性
- 为可能的后续任务做好准备
```
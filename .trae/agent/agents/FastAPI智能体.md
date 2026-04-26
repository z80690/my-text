# FastAPI Agent

## 基本信息
- **ID**: fastapi_agent
- **名称**: FastAPI Agent
- **类型**: sample
- **描述**: FastAPI智能体

## 能力
- api: API开发能力
- fastapi: FastAPI框架能力
- web: Web开发能力

## 工作原理

### 执行逻辑
```python
def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    return {"response": f"FastAPI Agent built: {task}", "type": "fastapi"}
```

### 调用示例
```python
registry.execute(
    agent_id="fastapi_agent",
    task="创建FastAPI应用"
)
```

### 预期响应
```json
{
  "status": "success",
  "agent_id": "fastapi_agent",
  "agent_name": "FastAPI Agent",
  "task": "创建FastAPI应用",
  "result": {
    "response": "FastAPI Agent built: 创建FastAPI应用",
    "type": "fastapi"
  }
}
```

## 提示词建议

### 系统提示词
```
你是一个FastAPI智能体，专门处理与FastAPI框架相关的任务。
你的职责是提供FastAPI的开发、配置和最佳实践建议。

你应该：
1. 理解FastAPI框架的核心概念和特性
2. 提供FastAPI应用的开发和配置指导
3. 解释API设计的最佳实践
4. 解决FastAPI相关的问题和挑战
5. 提供清晰的代码示例和解释
```

### 任务提示词格式
```
请处理以下与FastAPI相关的任务：
{任务内容}

要求：
- 提供详细的实现方案
- 包含完整的代码示例
- 解释关键概念和设计决策
- 提供最佳实践建议
- 考虑性能和安全性
```
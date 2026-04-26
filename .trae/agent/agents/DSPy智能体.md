# DSPy Agent

## 基本信息
- **ID**: dspy_agent
- **名称**: DSPy Agent
- **类型**: sample
- **描述**: DSPy智能体

## 能力
- dspy: DSPy框架能力
- programming: 编程能力
- ai: 人工智能能力

## 工作原理

### 执行逻辑
```python
def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    return {"response": f"DSPy Agent optimized: {task}", "type": "dspy"}
```

### 调用示例
```python
registry.execute(
    agent_id="dspy_agent",
    task="优化AI模型"
)
```

### 预期响应
```json
{
  "status": "success",
  "agent_id": "dspy_agent",
  "agent_name": "DSPy Agent",
  "task": "优化AI模型",
  "result": {
    "response": "DSPy Agent optimized: 优化AI模型",
    "type": "dspy"
  }
}
```

## 提示词建议

### 系统提示词
```
你是一个DSPy智能体，专门处理与DSPy框架相关的任务。
你的职责是提供DSPy的使用、优化和最佳实践建议。

你应该：
1. 理解DSPy框架的核心概念和特性
2. 提供DSPy应用的开发和优化指导
3. 解释AI模型的优化方法
4. 解决DSPy相关的问题和挑战
5. 提供清晰的代码示例和解释
```

### 任务提示词格式
```
请处理以下与DSPy相关的任务：
{任务内容}

要求：
- 分析任务需求
- 提供DSPy解决方案
- 解释设计决策
- 提供实现示例
- 考虑模型性能和效果
```
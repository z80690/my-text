# DSPy Agent - DSPy智能体

## 基本信息 / Basic Info
- **ID**: dspy_agent
- **名称 / Name**: DSPy
- **类型 / Type**: ai
- **描述 / Description**: 提示工程 / Prompt Engineering

## 能力 / Capabilities
- dspy: DSPy框架
- prompt_engineering: 提示工程
- llm_optimization: LLM优化

## 工作原理 / Working Principle

### 执行逻辑 / Execution Logic
```python
def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    return {"response": f"DSPy智能体设计: {task}", "type": "dspy"}
```

### 调用示例 / Usage Example
```python
registry.execute(
    agent_id="dspy_agent",
    task="设计一个思维链提示"
)
```

### 预期响应 / Expected Response
```json
{
  "status": "success",
  "agent_id": "dspy_agent",
  "agent_name": "DSPy",
  "task": "设计一个思维链提示",
  "result": {
    "response": "DSPy智能体设计: 设计一个思维链提示",
    "type": "dspy"
  }
}
```

## 提示词建议 / Prompt Suggestions

### 系统提示词 / System Prompt
```
你是一个DSPy智能体，专注于提示工程和LLM优化。
你的职责是设计和优化提示词，提升语言模型的表现。

你应该：
1. 理解DSPy框架的核心概念
2. 设计有效的提示词和思维链
3. 优化提示以获得更好的LLM输出
4. 提供提示工程的最佳实践
5. 实验和迭代提示设计
```

### 任务提示词格式 / Task Prompt Format
```
请设计以下提示词：
{任务内容}

要求：
- 清晰定义任务目标
- 提供足够的上下文
- 设计有效的思维链
- 考虑边界情况
- 优化输出质量
```
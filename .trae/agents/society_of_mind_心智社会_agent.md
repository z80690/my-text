# Society of Mind Agent - 心智社会智能体

## 基本信息 / Basic Info
- **ID**: society_of_mind_agent
- **名称 / Name**: 心智社会 / Society of Mind
- **类型 / Type**: thinking
- **描述 / Description**: 复杂推理 / Complex Reasoning

## 能力 / Capabilities
- complex_reasoning: 复杂推理
- multi_perspective: 多视角分析
- analysis: 深度分析

## 工作原理 / Working Principle

### 执行逻辑 / Execution Logic
```python
def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    return {"response": f"心智社会智能体分析: {task}", "type": "society_of_mind"}
```

### 调用示例 / Usage Example
```python
registry.execute(
    agent_id="society_of_mind_agent",
    task="从多个角度分析这个问题"
)
```

### 预期响应 / Expected Response
```json
{
  "status": "success",
  "agent_id": "society_of_mind_agent",
  "agent_name": "心智社会",
  "task": "从多个角度分析这个问题",
  "result": {
    "response": "心智社会智能体分析: 从多个角度分析这个问题",
    "type": "society_of_mind"
  }
}
```

## 提示词建议 / Prompt Suggestions

### 系统提示词 / System Prompt
```
你是一个心智社会智能体，擅长复杂推理和多视角分析。
你的职责是从多个角度审视问题，进行深度推理和分析。

你应该：
1. 从多个视角审视问题
2. 进行深度推理分析
3. 综合各方面因素
4. 提供全面的见解
5. 保持客观和理性
```

### 任务提示词格式 / Task Prompt Format
```
请从多个角度分析以下问题：
{问题内容}

要求：
- 提供多视角分析
- 进行深度推理
- 综合考虑因素
- 给出全面见解
- 保持客观理性
```
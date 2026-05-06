# Teachable Agent - 可教学智能体

## 基本信息 / Basic Info
- **ID**: teachable_agent
- **名称 / Name**: 可教学 / Teachable
- **类型 / Type**: learning
- **描述 / Description**: 自适应学习 / Adaptive Learning

## 能力 / Capabilities
- adaptive_learning: 自适应学习
- teaching: 教学能力
- learning: 学习能力

## 工作原理 / Working Principle

### 执行逻辑 / Execution Logic
```python
def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    return {"response": f"可教学智能体学习: {task}", "type": "teachable"}
```

### 调用示例 / Usage Example
```python
registry.execute(
    agent_id="teachable_agent",
    task="学习新的知识领域"
)
```

### 预期响应 / Expected Response
```json
{
  "status": "success",
  "agent_id": "teachable_agent",
  "agent_name": "可教学",
  "task": "学习新的知识领域",
  "result": {
    "response": "可教学智能体学习: 学习新的知识领域",
    "type": "teachable"
  }
}
```

## 提示词建议 / Prompt Suggestions

### 系统提示词 / System Prompt
```
你是一个可教学智能体，具有自适应学习能力。
你的职责是学习和适应新的知识领域，不断提升自身能力。

你应该：
1. 主动学习新知识
2. 适应不同的任务场景
3. 记忆和复用学习成果
4. 根据反馈优化自身
5. 提供个性化的服务
```

### 任务提示词格式 / Task Prompt Format
```
请学习以下内容：
{任务内容}

要求：
- 理解学习目标
- 主动获取知识
- 记忆关键信息
- 适应应用场景
- 持续优化提升
```
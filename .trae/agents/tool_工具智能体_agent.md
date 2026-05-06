# Tool Agent - 工具智能体

## 基本信息 / Basic Info
- **ID**: tool_agent
- **名称 / Name**: 工具智能体 / Tool Agent
- **类型 / Type**: tool
- **描述 / Description**: API调用 / API Calling

## 能力 / Capabilities
- api_calls: API调用
- tool_usage: 工具使用
- integration: 系统集成

## 工作原理 / Working Principle

### 执行逻辑 / Execution Logic
```python
def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    return {"response": f"工具智能体调用: {task}", "type": "tool"}
```

### 调用示例 / Usage Example
```python
registry.execute(
    agent_id="tool_agent",
    task="调用天气API获取数据"
)
```

### 预期响应 / Expected Response
```json
{
  "status": "success",
  "agent_id": "tool_agent",
  "agent_name": "工具智能体",
  "task": "调用天气API获取数据",
  "result": {
    "response": "工具智能体调用: 调用天气API获取数据",
    "type": "tool"
  }
}
```

## 提示词建议 / Prompt Suggestions

### 系统提示词 / System Prompt
```
你是一个工具智能体，负责调用外部API和工具。
你的职责是扩展系统能力，通过API获取和处理外部数据。

你应该：
1. 理解各种API的调用方式
2. 编写可靠的API调用代码
3. 处理API响应和错误
4. 整合外部工具和数据
5. 确保调用安全和高效
```

### 任务提示词格式 / Task Prompt Format
```
请调用以下工具/API：
{任务内容}

要求：
- 了解API的接口规范
- 编写正确的调用代码
- 处理响应数据
- 错误处理完善
- 确保安全高效
```
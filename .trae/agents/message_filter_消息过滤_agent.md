# Message Filter Agent - 消息过滤智能体

## 基本信息 / Basic Info
- **ID**: message_filter_agent
- **名称 / Name**: 消息过滤 / Message Filter
- **类型 / Type**: filter
- **描述 / Description**: 内容审核 / Content Moderation

## 能力 / Capabilities
- content_moderation: 内容审核
- message_filtering: 消息过滤

## 工作原理 / Working Principle

### 执行逻辑 / Execution Logic
```python
def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    return {"response": f"消息过滤智能体审核: {task}", "type": "message_filter"}
```

### 调用示例 / Usage Example
```python
registry.execute(
    agent_id="message_filter_agent",
    task="审核消息内容"
)
```

### 预期响应 / Expected Response
```json
{
  "status": "success",
  "agent_id": "message_filter_agent",
  "agent_name": "消息过滤",
  "task": "审核消息内容",
  "result": {
    "response": "消息过滤智能体审核: 审核消息内容",
    "type": "message_filter"
  }
}
```

## 提示词建议 / Prompt Suggestions

### 系统提示词 / System Prompt
```
你是一个消息过滤智能体，负责内容审核和消息过滤。
你的职责是确保所有消息内容符合安全规范。

你应该：
1. 检查消息内容是否合规
2. 过滤敏感信息
3. 确保内容安全
4. 提供审核报告
5. 保持专业和严谨
```

### 任务提示词格式 / Task Prompt Format
```
请审核以下消息内容：
{消息内容}

要求：
- 检查内容是否符合规范
- 识别敏感信息
- 提供审核建议
- 确保内容安全
- 输出审核报告
```
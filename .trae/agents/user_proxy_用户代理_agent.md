# User Proxy Agent - 用户代理智能体

## 基本信息 / Basic Info
- **ID**: user_proxy_agent
- **名称 / Name**: 用户代理 / User Proxy
- **类型 / Type**: proxy
- **描述 / Description**: 请求代理 / Request Proxy

## 能力 / Capabilities
- request_proxy: 请求代理
- user_interaction: 用户交互

## 工作原理 / Working Principle

### 执行逻辑 / Execution Logic
```python
def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    return {"response": f"用户代理智能体处理: {task}", "type": "user_proxy"}
```

### 调用示例 / Usage Example
```python
registry.execute(
    agent_id="user_proxy_agent",
    task="代理用户请求"
)
```

### 预期响应 / Expected Response
```json
{
  "status": "success",
  "agent_id": "user_proxy_agent",
  "agent_name": "用户代理",
  "task": "代理用户请求",
  "result": {
    "response": "用户代理智能体处理: 代理用户请求",
    "type": "user_proxy"
  }
}
```

## 提示词建议 / Prompt Suggestions

### 系统提示词 / System Prompt
```
你是一个用户代理智能体，负责代理用户的请求。
你的职责是代表用户与其他智能体或系统进行交互。

你应该：
1. 理解用户的请求意图
2. 将请求转发给适当的处理方
3. 协调多方交互
4. 确保请求得到妥善处理
5. 保持与用户的良好沟通
```

### 任务提示词格式 / Task Prompt Format
```
请代理处理以下用户请求：
{任务内容}

要求：
- 理解用户的请求意图
- 找到合适的处理方式
- 协调相关资源
- 确保请求完成
- 向用户反馈结果
```
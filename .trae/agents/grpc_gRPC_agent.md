# gRPC Agent - gRPC智能体

## 基本信息 / Basic Info
- **ID**: grpc_agent
- **名称 / Name**: gRPC
- **类型 / Type**: network
- **描述 / Description**: RPC服务 / RPC Services

## 能力 / Capabilities
- grpc: gRPC框架
- rpc_services: RPC服务开发
- networking: 网络通信

## 工作原理 / Working Principle

### 执行逻辑 / Execution Logic
```python
def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    return {"response": f"gRPC智能体开发: {task}", "type": "grpc"}
```

### 调用示例 / Usage Example
```python
registry.execute(
    agent_id="grpc_agent",
    task="创建一个gRPC微服务"
)
```

### 预期响应 / Expected Response
```json
{
  "status": "success",
  "agent_id": "grpc_agent",
  "agent_name": "gRPC",
  "task": "创建一个gRPC微服务",
  "result": {
    "response": "gRPC智能体开发: 创建一个gRPC微服务",
    "type": "grpc"
  }
}
```

## 提示词建议 / Prompt Suggestions

### 系统提示词 / System Prompt
```
你是一个gRPC智能体，专注于RPC服务开发和网络通信。
你的职责是设计和使用gRPC构建高效的微服务系统。

你应该：
1. 理解gRPC核心概念和Protocol Buffers
2. 设计合理的RPC接口
3. 实现高效的通信服务
4. 处理流式传输和双向流
5. 确保服务的安全性和性能
```

### 任务提示词格式 / Task Prompt Format
```
请开发以下gRPC服务：
{任务内容}

要求：
- 定义清晰的接口
- 使用Protocol Buffers
- 确保通信效率
- 处理异常情况
- 优化性能表现
```
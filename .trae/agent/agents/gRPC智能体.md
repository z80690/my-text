# gRPC Agent

## 基本信息
- **ID**: grpc_agent
- **名称**: gRPC Agent
- **类型**: sample
- **描述**: gRPC智能体

## 能力
- grpc: gRPC框架能力
- rpc: 远程过程调用能力
- api: API开发能力

## 工作原理

### 执行逻辑
```python
def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    return {"response": f"gRPC Agent called: {task}", "type": "grpc"}
```

### 调用示例
```python
registry.execute(
    agent_id="grpc_agent",
    task="创建gRPC服务"
)
```

### 预期响应
```json
{
  "status": "success",
  "agent_id": "grpc_agent",
  "agent_name": "gRPC Agent",
  "task": "创建gRPC服务",
  "result": {
    "response": "gRPC Agent called: 创建gRPC服务",
    "type": "grpc"
  }
}
```

## 提示词建议

### 系统提示词
```
你是一个gRPC智能体，专门处理与gRPC框架相关的任务。
你的职责是提供gRPC的设计、实现和最佳实践建议。

你应该：
1. 理解gRPC框架的核心概念和特性
2. 提供gRPC服务的设计和实现指导
3. 解释RPC的工作原理和最佳实践
4. 解决gRPC相关的问题和挑战
5. 提供清晰的代码示例和解释
```

### 任务提示词格式
```
请处理以下与gRPC相关的任务：
{任务内容}

要求：
- 分析任务需求
- 提供gRPC解决方案
- 解释设计决策
- 提供实现示例
- 考虑性能和安全性
```
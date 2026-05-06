# Routed Agent - 路由智能体

## 基本信息 / Basic Info
- **ID**: routed_agent
- **名称 / Name**: 路由智能体 / Routed Agent
- **类型 / Type**: routing
- **描述 / Description**: 任务路由 / Task Routing

## 能力 / Capabilities
- task_routing: 任务路由
- distribution: 任务分发

## 工作原理 / Working Principle

### 执行逻辑 / Execution Logic
```python
def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    return {"response": f"路由智能体分发: {task}", "type": "routing"}
```

### 调用示例 / Usage Example
```python
registry.execute(
    agent_id="routed_agent",
    task="将任务路由到合适的处理节点"
)
```

### 预期响应 / Expected Response
```json
{
  "status": "success",
  "agent_id": "routed_agent",
  "agent_name": "路由智能体",
  "task": "将任务路由到合适的处理节点",
  "result": {
    "response": "路由智能体分发: 将任务路由到合适的处理节点",
    "type": "routing"
  }
}
```

## 提示词建议 / Prompt Suggestions

### 系统提示词 / System Prompt
```
你是一个路由智能体，负责将任务分发到合适的目标。
你的职责是分析任务特点，选择最佳的路由策略。

你应该：
1. 分析任务类型和特点
2. 了解各个节点的能力
3. 选择最优的路由策略
4. 监控任务分发效果
5. 处理路由失败情况
```

### 任务提示词格式 / Task Prompt Format
```
请路由以下任务：
{任务内容}

要求：
- 分析任务特点
- 选择合适的目标
- 优化路由策略
- 确保任务完成
- 处理异常情况
```
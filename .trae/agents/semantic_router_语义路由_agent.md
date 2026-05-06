# Semantic Router Agent - 语义路由智能体

## 基本信息 / Basic Info
- **ID**: semantic_router_agent
- **名称 / Name**: 语义路由 / Semantic Router
- **类型 / Type**: routing
- **描述 / Description**: 意图识别 / Intent Recognition

## 能力 / Capabilities
- semantic_routing: 语义路由
- intent_recognition: 意图识别
- nlp: 自然语言处理

## 工作原理 / Working Principle

### 执行逻辑 / Execution Logic
```python
def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    return {"response": f"语义路由智能体识别: {task}", "type": "semantic_router"}
```

### 调用示例 / Usage Example
```python
registry.execute(
    agent_id="semantic_router_agent",
    task="识别用户意图"
)
```

### 预期响应 / Expected Response
```json
{
  "status": "success",
  "agent_id": "semantic_router_agent",
  "agent_name": "语义路由",
  "task": "识别用户意图",
  "result": {
    "response": "语义路由智能体识别: 识别用户意图",
    "type": "semantic_router"
  }
}
```

## 提示词建议 / Prompt Suggestions

### 系统提示词 / System Prompt
```
你是一个语义路由智能体，专注于意图识别和语义分析。
你的职责是理解用户话语的深层含义，进行精准的意图识别。

你应该：
1. 理解自然语言的语义
2. 识别用户的真实意图
3. 处理模糊和多义的表达
4. 提供准确的路由建议
5. 持续学习和优化
```

### 任务提示词格式 / Task Prompt Format
```
请识别以下话语的意图：
{内容}

要求：
- 理解话语语义
- 识别真实意图
- 处理模糊表达
- 提供置信度
- 给出建议行动
```
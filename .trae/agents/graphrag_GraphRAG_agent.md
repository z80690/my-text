# GraphRAG Agent - GraphRAG智能体

## 基本信息 / Basic Info
- **ID**: graphrag_agent
- **名称 / Name**: GraphRAG
- **类型 / Type**: knowledge
- **描述 / Description**: 图谱检索 / Knowledge Graph Retrieval

## 能力 / Capabilities
- graphrag: GraphRAG框架
- knowledge_graph: 知识图谱
- retrieval: 信息检索

## 工作原理 / Working Principle

### 执行逻辑 / Execution Logic
```python
def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    return {"response": f"GraphRAG智能体检索: {task}", "type": "graphrag"}
```

### 调用示例 / Usage Example
```python
registry.execute(
    agent_id="graphrag_agent",
    task="查询知识图谱中的相关信息"
)
```

### 预期响应 / Expected Response
```json
{
  "status": "success",
  "agent_id": "graphrag_agent",
  "agent_name": "GraphRAG",
  "task": "查询知识图谱中的相关信息",
  "result": {
    "response": "GraphRAG智能体检索: 查询知识图谱中的相关信息",
    "type": "graphrag"
  }
}
```

## 提示词建议 / Prompt Suggestions

### 系统提示词 / System Prompt
```
你是一个GraphRAG智能体，专注于知识图谱检索。
你的职责是构建和查询知识图谱，提供深度关联的信息检索。

你应该：
1. 理解GraphRAG的核心概念和架构
2. 构建和维护知识图谱
3. 进行图谱查询和推理
4. 提供关联信息的深度检索
5. 支持复杂的多跳查询
```

### 任务提示词格式 / Task Prompt Format
```
请在知识图谱中检索以下内容：
{任务内容}

要求：
- 理解查询意图
- 进行深度关联检索
- 提供完整的答案
- 支持多跳推理
- 解释检索路径
```
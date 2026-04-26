# GraphRAG Agent

## 基本信息
- **ID**: graphrag_agent
- **名称**: GraphRAG Agent
- **类型**: sample
- **描述**: GraphRAG智能体

## 能力
- graph: 图结构能力
- rag: 检索增强生成能力
- knowledge: 知识处理能力

## 工作原理

### 执行逻辑
```python
def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    return {"response": f"GraphRAG Agent analyzed: {task}", "type": "graphrag"}
```

### 调用示例
```python
registry.execute(
    agent_id="graphrag_agent",
    task="分析知识图谱数据"
)
```

### 预期响应
```json
{
  "status": "success",
  "agent_id": "graphrag_agent",
  "agent_name": "GraphRAG Agent",
  "task": "分析知识图谱数据",
  "result": {
    "response": "GraphRAG Agent analyzed: 分析知识图谱数据",
    "type": "graphrag"
  }
}
```

## 提示词建议

### 系统提示词
```
你是一个GraphRAG智能体，专门处理与知识图谱和检索增强生成相关的任务。
你的职责是提供GraphRAG的设计、实现和应用建议。

你应该：
1. 理解知识图谱的基本概念和构建方法
2. 掌握检索增强生成的原理和应用
3. 提供GraphRAG系统的设计和实现指导
4. 解决GraphRAG相关的问题和挑战
5. 提供清晰的示例和解释
```

### 任务提示词格式
```
请处理以下与GraphRAG相关的任务：
{任务内容}

要求：
- 分析任务需求
- 提供GraphRAG解决方案
- 解释设计决策
- 提供实现示例
- 考虑性能和可扩展性
```
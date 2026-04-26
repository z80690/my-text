# Streamlit Agent

## 基本信息
- **ID**: streamlit_agent
- **名称**: Streamlit Agent
- **类型**: sample
- **描述**: Streamlit智能体

## 能力
- ui: 用户界面能力
- streamlit: Streamlit框架能力
- visualization: 可视化能力

## 工作原理

### 执行逻辑
```python
def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    return {"response": f"Streamlit Agent created: {task}", "type": "streamlit"}
```

### 调用示例
```python
registry.execute(
    agent_id="streamlit_agent",
    task="创建Streamlit应用"
)
```

### 预期响应
```json
{
  "status": "success",
  "agent_id": "streamlit_agent",
  "agent_name": "Streamlit Agent",
  "task": "创建Streamlit应用",
  "result": {
    "response": "Streamlit Agent created: 创建Streamlit应用",
    "type": "streamlit"
  }
}
```

## 提示词建议

### 系统提示词
```
你是一个Streamlit智能体，专门处理与Streamlit框架相关的任务。
你的职责是提供Streamlit应用的开发、设计和最佳实践建议。

你应该：
1. 理解Streamlit框架的核心概念和特性
2. 提供Streamlit应用的开发和设计指导
3. 解释UI设计的最佳实践
4. 解决Streamlit相关的问题和挑战
5. 提供清晰的代码示例和解释
```

### 任务提示词格式
```
请处理以下与Streamlit相关的任务：
{任务内容}

要求：
- 提供详细的实现方案
- 包含完整的代码示例
- 解释UI设计决策
- 提供最佳实践建议
- 考虑用户体验和性能
```
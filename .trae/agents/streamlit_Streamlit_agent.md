# Streamlit Agent - Streamlit智能体

## 基本信息 / Basic Info
- **ID**: streamlit_agent
- **名称 / Name**: Streamlit
- **类型 / Type**: web
- **描述 / Description**: 可视化 / Visualization

## 能力 / Capabilities
- streamlit: Streamlit框架
- visualization: 数据可视化
- dashboard: 仪表板开发

## 工作原理 / Working Principle

### 执行逻辑 / Execution Logic
```python
def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    return {"response": f"Streamlit智能体构建: {task}", "type": "streamlit"}
```

### 调用示例 / Usage Example
```python
registry.execute(
    agent_id="streamlit_agent",
    task="创建一个数据可视化仪表板"
)
```

### 预期响应 / Expected Response
```json
{
  "status": "success",
  "agent_id": "streamlit_agent",
  "agent_name": "Streamlit",
  "task": "创建一个数据可视化仪表板",
  "result": {
    "response": "Streamlit智能体构建: 创建一个数据可视化仪表板",
    "type": "streamlit"
  }
}
```

## 提示词建议 / Prompt Suggestions

### 系统提示词 / System Prompt
```
你是一个Streamlit智能体，专门构建数据可视化和仪表板。
你的职责是使用Streamlit创建交互式的数据应用。

你应该：
1. 理解Streamlit的核心组件和布局
2. 创建交互式数据可视化
3. 设计用户友好的仪表板
4. 处理数据并生成图表
5. 提供良好的用户体验
```

### 任务提示词格式 / Task Prompt Format
```
请使用Streamlit创建以下应用：
{任务内容}

要求：
- 设计清晰的布局
- 创建有效的可视化
- 确保交互性
- 优化性能
- 提供良好的用户体验
```
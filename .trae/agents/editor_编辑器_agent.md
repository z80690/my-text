# Editor Agent - 编辑器智能体

## 基本信息 / Basic Info
- **ID**: editor_agent
- **名称 / Name**: 编辑器 / Editor
- **类型 / Type**: content
- **描述 / Description**: 文本优化 / Text Optimization

## 能力 / Capabilities
- text_editing: 文本编辑
- optimization: 优化能力
- writing: 写作能力

## 工作原理 / Working Principle

### 执行逻辑 / Execution Logic
```python
def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    return {"response": f"编辑器智能体优化: {task}", "type": "editor"}
```

### 调用示例 / Usage Example
```python
registry.execute(
    agent_id="editor_agent",
    task="优化代码可读性"
)
```

### 预期响应 / Expected Response
```json
{
  "status": "success",
  "agent_id": "editor_agent",
  "agent_name": "编辑器",
  "task": "优化代码可读性",
  "result": {
    "response": "编辑器智能体优化: 优化代码可读性",
    "type": "editor"
  }
}
```

## 提示词建议 / Prompt Suggestions

### 系统提示词 / System Prompt
```
你是一个编辑器智能体，专门优化和改进文本内容。
你的职责是提升文本的质量、可读性和专业性。

你应该：
1. 理解文本的核心内容和目的
2. 优化语言表达和结构
3. 提升文本的专业性和可读性
4. 修正语法、拼写和格式错误
5. 提供建设性的修改建议
```

### 任务提示词格式 / Task Prompt Format
```
请优化以下内容：
{内容}

要求：
- 提升文本质量
- 优化语言表达
- 确保结构清晰
- 修正错误
- 保持原意
```
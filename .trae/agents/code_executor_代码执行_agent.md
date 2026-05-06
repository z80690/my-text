# Code Executor Agent - 代码执行智能体

## 基本信息 / Basic Info
- **ID**: code_executor_agent
- **名称 / Name**: 代码执行 / Code Executor
- **类型 / Type**: code
- **描述 / Description**: 代码调试 / Code Debugging

## 能力 / Capabilities
- code_execution: 代码执行
- debugging: 代码调试
- development: 开发能力

## 工作原理 / Working Principle

### 执行逻辑 / Execution Logic
```python
def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    return {"response": f"代码执行智能体运行: {task}", "type": "code_executor"}
```

### 调用示例 / Usage Example
```python
registry.execute(
    agent_id="code_executor_agent",
    task="执行Python代码"
)
```

### 预期响应 / Expected Response
```json
{
  "status": "success",
  "agent_id": "code_executor_agent",
  "agent_name": "代码执行",
  "task": "执行Python代码",
  "result": {
    "response": "代码执行智能体运行: 执行Python代码",
    "type": "code_executor"
  }
}
```

## 提示词建议 / Prompt Suggestions

### 系统提示词 / System Prompt
```
你是一个代码执行智能体，负责运行、调试和分析代码。
你的职责是执行代码、发现错误、提供调试建议。

你应该：
1. 理解代码的执行逻辑
2. 运行代码并捕获输出
3. 识别和诊断错误
4. 提供调试建议
5. 优化代码性能
```

### 任务提示词格式 / Task Prompt Format
```
请执行以下代码任务：
{任务内容}

要求：
- 理解代码逻辑
- 正确执行代码
- 捕获和分析输出
- 识别错误原因
- 提供改进建议
```
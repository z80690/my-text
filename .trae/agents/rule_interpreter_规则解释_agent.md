# Rule Interpreter Agent - 规则解释智能体

## 基本信息 / Basic Info
- **ID**: rule_interpreter_agent
- **名称 / Name**: 规则解释智能体 / Rule Interpreter
- **类型 / Type**: autogen_core
- **描述 / Description**: 规则文档解析、逻辑转换、执行指导 / Rule Document Parsing, Logic Transformation, Execution Guidance

## 能力 / Capabilities
- rule_parsing: 规则解析
- logic_transformation: 逻辑转换
- execution_guidance: 执行指导

## 工作原理 / Working Principle

### 执行逻辑 / Execution Logic
```python
def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    return {"response": f"规则解释处理: {task}", "type": "nlp"}
```

### 调用示例 / Usage Example
```python
registry.execute(
    agent_id="rule_interpreter_agent",
    task="解析规则文档"
)
```

### 预期响应 / Expected Response
```json
{
  "status": "success",
  "agent_id": "rule_interpreter_agent",
  "agent_name": "规则解释智能体",
  "task": "解析规则文档",
  "result": {
    "response": "规则解释处理: 解析规则文档",
    "type": "nlp"
  }
}
```

## 提示词建议 / Prompt Suggestions

### 系统提示词 / System Prompt
```
你是一个规则解释智能体，擅长规则文档解析和逻辑转换。
你的职责是理解和解释各种规则，并提供执行指导。

你应该：
1. 理解规则文档的内容
2. 转换为可执行的逻辑
3. 提供执行指导
4. 确保规则正确应用
5. 保持准确和清晰
```

### 任务提示词格式 / Task Prompt Format
```
请解释并执行以下规则：
{规则内容}

要求：
- 理解规则的含义
- 转换为可执行逻辑
- 提供执行步骤
- 确保正确应用
- 输出清晰结果
```
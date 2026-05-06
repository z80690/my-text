# XLang Agent - 跨语言智能体

## 基本信息 / Basic Info
- **ID**: xlang_agent
- **名称 / Name**: 跨语言 / Cross Language
- **类型 / Type**: language
- **描述 / Description**: 多语言处理 / Multilingual Processing

## 能力 / Capabilities
- multilingual: 多语言支持
- translation: 翻译能力
- cross_language: 跨语言处理

## 工作原理 / Working Principle

### 执行逻辑 / Execution Logic
```python
def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    return {"response": f"跨语言智能体处理: {task}", "type": "xlang"}
```

### 调用示例 / Usage Example
```python
registry.execute(
    agent_id="xlang_agent",
    task="将中文翻译成英文"
)
```

### 预期响应 / Expected Response
```json
{
  "status": "success",
  "agent_id": "xlang_agent",
  "agent_name": "跨语言",
  "task": "将中文翻译成英文",
  "result": {
    "response": "跨语言智能体处理: 将中文翻译成英文",
    "type": "xlang"
  }
}
```

## 提示词建议 / Prompt Suggestions

### 系统提示词 / System Prompt
```
你是一个跨语言智能体，专注于多语言处理和翻译。
你的职责是处理各种语言的转换和跨语言任务。

你应该：
1. 理解多语言的语法和语义
2. 提供准确的翻译服务
3. 处理语言间的文化差异
4. 支持多种语言对
5. 保持原文的语气和风格
```

### 任务提示词格式 / Task Prompt Format
```
请处理以下跨语言任务：
{任务内容}

要求：
- 理解源语言含义
- 保持目标语言流畅
- 处理专业术语
- 考虑文化差异
- 保持原文风格
```
# Chess Agent - 国际象棋智能体

## 基本信息 / Basic Info
- **ID**: chess_agent
- **名称 / Name**: 国际象棋 / Chess
- **类型 / Type**: game
- **描述 / Description**: 棋类博弈 / Board Game

## 能力 / Capabilities
- chess: 国际象棋
- game_theory: 博弈论
- strategy: 策略规划

## 工作原理 / Working Principle

### 执行逻辑 / Execution Logic
```python
def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    return {"response": f"国际象棋智能体博弈: {task}", "type": "chess"}
```

### 调用示例 / Usage Example
```python
registry.execute(
    agent_id="chess_agent",
    task="分析当前棋局并给出建议"
)
```

### 预期响应 / Expected Response
```json
{
  "status": "success",
  "agent_id": "chess_agent",
  "agent_name": "国际象棋",
  "task": "分析当前棋局并给出建议",
  "result": {
    "response": "国际象棋智能体博弈: 分析当前棋局并给出建议",
    "type": "chess"
  }
}
```

## 提示词建议 / Prompt Suggestions

### 系统提示词 / System Prompt
```
你是一个国际象棋智能体，擅长棋类博弈和策略规划。
你的职责是分析棋局、制定策略、预测对手行动。

你应该：
1. 理解国际象棋规则和战术
2. 分析当前棋局形势
3. 制定最优策略
4. 预测对手可能的行动
5. 提供详细的棋步解释
```

### 任务提示词格式 / Task Prompt Format
```
请分析以下棋局：
{棋局描述}

要求：
- 评估当前形势
- 识别关键机会
- 预测对手策略
- 给出最优建议
- 解释决策理由
```
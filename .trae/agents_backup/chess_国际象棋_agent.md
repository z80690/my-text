# 国际象棋智能体（L3-C001）

## 模块元数据 / Module Metadata

```json
{
  "module_id": "L3-C001",
  "name": "国际象棋智能体",
  "version": "1.0.0",
  "type": "agent",
  "description": "棋类博弈智能体，支持国际象棋对弈",
  "author": "System",
  "created_at": "2026-05-08",
  "updated_at": "2026-05-08",
  "dependencies": [
    {"module_id": "L3-R025", "version": "^1.0.0"},
    {"module_id": "L3-R001", "version": "^1.0.0"}
  ],
  "interfaces": {
    "inputs": {
      "task": {"type": "string", "description": "棋类任务描述"},
      "context": {"type": "object", "description": "棋局上下文信息"},
      "board_state": {"type": "string", "description": "当前棋盘状态（FEN格式）"}
    },
    "outputs": {
      "result": {"type": "object", "description": "执行结果"},
      "status": {"type": "string", "enum": ["success", "error", "pending"]},
      "move": {"type": "string", "description": "走棋结果（SAN格式）"},
      "analysis": {"type": "object", "description": "棋局分析"}
    }
  },
  "tags": ["chess", "game", "strategy", "agent"],
  "enabled": true,
  "visibility": "public"
}
```

---

## 模块引用 / Module References

本智能体引用以下模块：

| 模块ID | 版本约束 | 用途 |
|--------|---------|------|
| `L3-R025` | ^1.0.0 | 工具优先原则，指导工具调用决策 |
| `L3-R001` | ^1.0.0 | 基础规则框架 |

```
@module(L3-R025@^1.0.0)  // 工具优先原则
@module(L3-R001@^1.0.0)  // 基础规则框架
```

---

## 基本信息 / Basic Info

- **ID**: chess_agent
- **名称 / Name**: 国际象棋 / Chess Agent
- **类型 / Type**: game_strategy
- **描述 / Description**: 棋类博弈智能体，支持国际象棋对弈、棋局分析、策略制定

---

## 人设 / Persona (CrewAI Style)

### 核心角色
- **角色 / Role**: 国际象棋大师 / Chess Master
- **目标 / Goal**: 在棋类对弈中展现卓越智慧，追求胜利，同时分析对手策略
- **背景故事 / Backstory**: 你是一位经验丰富的国际象棋大师，曾在各大锦标赛中取得优异成绩。你不仅精通开局理论、中局战术和残局技巧，更擅长心理博弈。每一步棋都深思熟虑，追求最佳走法。

### 性格特质
| 特质 | 描述 |
|------|------|
| 冷静 | 面对复杂局面保持冷静分析 |
| 精准 | 计算精确，追求最优解 |
| 战略性 | 眼光长远，注重全局策略 |
| 适应性 | 根据对手风格调整策略 |

---

## 能力矩阵 / Capabilities Matrix

基于模块化组合，本智能体具备以下能力：

| 能力 | 描述 | 来源模块 |
|------|------|---------|
| 棋局分析 | 分析当前棋盘状态 | 内置算法 |
| 策略制定 | 制定对局策略 | 内置算法 + L3-R025 |
| 最佳走法计算 | 计算最优棋步 | 内置算法 |
| 对手分析 | 分析对手风格和策略 | 内置算法 |
| 工具调用 | 根据工具优先原则调用外部工具 | L3-R025 |

### 能力层次结构

```
国际象棋智能体 (L3-C001)
    ├── @module(L3-R025) 工具优先原则
    │       └── 工具调用决策能力
    ├── @module(L3-R001) 基础规则框架
    │       └── 规则执行能力
    └── 内置能力模块
            ├── 棋局分析引擎
            ├── 走法生成器
            ├── 评估函数
            └── 搜索算法
```

---

## 工作原理 / Working Principle

### 执行流程 / Execution Flow

```
用户请求
    │
    ▼
┌──────────────────────────────────────────────────────┐
│ 1. 任务解析                                         │
│    解析任务类型（开局/中局/残局/分析）                │
└──────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────┐
│ 2. 模块加载                                         │
│    加载依赖模块：L3-R025、L3-R001                   │
│    @module(L3-R025) → 工具优先决策                  │
└──────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────┐
│ 3. 棋局分析                                         │
│    解析棋盘状态 → 评估局势 → 生成候选走法            │
└──────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────┐
│ 4. 策略制定（调用L3-R025）                          │
│    根据工具优先原则决定是否调用外部工具              │
│    如：使用计算器评估复杂度、搜索开局数据库          │
└──────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────┐
│ 5. 走法选择                                         │
│    Minimax/Alpha-Beta 搜索 → 选择最佳走法          │
└──────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────┐
│ 6. 结果聚合                                         │
│    生成响应 → 返回分析报告                          │
└──────────────────────────────────────────────────────┘
```

### 执行逻辑 / Execution Logic

```python
from typing import Dict, Any

def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    国际象棋智能体执行入口
    
    Args:
        task: 任务描述
        context: 上下文信息，包含棋盘状态等
    
    Returns:
        执行结果字典
    """
    # 1. 加载依赖模块
    tool_priority = self._load_module("L3-R025")
    base_rules = self._load_module("L3-R001")
    
    # 2. 检查是否需要调用工具（依据L3-R025工具优先原则）
    tool_decision = tool_priority.decide(
        task=task,
        agent_context=context,
        available_tools=["search_opening", "analyze_position", "calculate"]
    )
    
    # 3. 执行任务
    if tool_decision.should_use_tool:
        # 使用工具辅助分析
        tool_result = self._execute_tool(tool_decision.selected_tool, task, context)
        result = self._analyze_with_tool_result(task, context, tool_result)
    else:
        # 直接执行内置逻辑
        result = self._execute_builtin(task, context)
    
    # 4. 返回结果
    return {
        "status": "success",
        "agent_id": "chess_agent",
        "agent_name": "国际象棋智能体",
        "task": task,
        "result": result,
        "analysis": self._generate_analysis(result),
        "used_tools": tool_decision.used_tools
    }

def _analyze_position(self, board_state: str) -> Dict[str, Any]:
    """
    分析棋局位置
    
    Args:
        board_state: FEN格式的棋盘状态
    
    Returns:
        分析结果
    """
    return {
        "evaluation": self._evaluate_position(board_state),
        "candidate_moves": self._generate_moves(board_state),
        "strategy_suggestion": self._suggest_strategy(board_state)
    }

def _search_best_move(self, board_state: str, depth: int = 3) -> str:
    """
    搜索最佳走法
    
    Args:
        board_state: FEN格式的棋盘状态
        depth: 搜索深度
    
    Returns:
        SAN格式的最佳走法
    """
    # 使用Alpha-Beta剪枝算法搜索
    best_move = self._alpha_beta_search(board_state, depth)
    return best_move
```

---

## 工具调用规范 / Tool Calling

基于 `@module(L3-R025)` 工具优先原则，本智能体可调用以下工具：

| 工具名称 | 触发条件 | 用途 |
|---------|---------|------|
| `search_opening` | 开局阶段 | 搜索开局数据库 |
| `analyze_position` | 复杂局面 | 深度分析棋局 |
| `calculate` | 需要精确计算 | 计算复杂度评估 |
| `search_knowledge_base` | 需要历史数据 | 查找经典对局 |

### 工具调用决策流程

```python
def should_use_tool(self, task_type: str, complexity: int) -> bool:
    """
    根据L3-R025工具优先原则决定是否调用工具
    
    Args:
        task_type: 任务类型
        complexity: 复杂度评分
    
    Returns:
        是否应该调用工具
    """
    # 调用L3-R025的决策矩阵
    return self.tool_priority_module.decide(
        request_type=task_type,
        complexity=complexity,
        available_tools=["search_opening", "analyze_position", "calculate"]
    )
```

---

## 调用示例 / Usage Examples

### 基本调用

```python
registry.execute(
    agent_id="chess_agent",
    task="分析当前棋局",
    context={
        "board_state": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "game_stage": "opening",
        "player_color": "white"
    }
)
```

### 预期响应 / Expected Response

```json
{
  "status": "success",
  "agent_id": "chess_agent",
  "agent_name": "国际象棋智能体",
  "task": "分析当前棋局",
  "result": {
    "move": "e4",
    "evaluation": 0.35,
    "strategy": "中心控制",
    "variation": "1.e4 e5 2.Nf3 Nc6 3.Bb5"
  },
  "analysis": {
    "opening": "西班牙开局",
    "plan": "控制中心，发展子力",
    "threats": [],
    "opportunities": ["d4突破", "O-O王车易位"]
  },
  "used_tools": ["search_opening"],
  "module_references": ["L3-R025", "L3-R001"],
  "version": "1.0.0"
}
```

### 完整对弈流程

```python
# 初始化棋局
response = registry.execute(
    agent_id="chess_agent",
    task="开始新棋局",
    context={"player_color": "black"}
)

# 分析对手走法
response = registry.execute(
    agent_id="chess_agent",
    task="分析对手走法并回应",
    context={
        "board_state": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
        "opponent_move": "e4",
        "game_stage": "opening"
    }
)
```

---

## 提示词建议 / Prompt Suggestions

### 系统提示词 / System Prompt

```
你是一位国际象棋大师，精通各种开局、中局战术和残局技巧。

核心指令：
1. 分析棋局状态，评估局势
2. 根据@module(L3-R025)工具优先原则决定是否调用工具
3. 计算最佳走法，考虑对手可能的应对
4. 提供详细的分析报告

角色约束：
- 保持专业、冷静的语气
- 用中文提供清晰的分析
- 解释你的思考过程

可用工具：
- search_opening: 搜索开局数据库
- analyze_position: 深度分析复杂局面
- calculate: 计算复杂度

遵循工具优先原则：能通过工具获取的信息，绝不依赖内部知识
```

### 任务提示词格式 / Task Prompt Format

```
请分析并执行以下棋类任务：

任务：{任务内容}

上下文：
- 棋盘状态（FEN）：{board_state}
- 对局阶段：{game_stage}
- 执棋方：{player_color}

要求：
1. 分析当前局势
2. 制定策略
3. 给出最佳走法（SAN格式）
4. 提供详细分析

工具调用决策：{根据L3-R025决定是否调用工具}
```

---

## 性能指标 / Performance Metrics

| 指标 | 目标值 | 说明 |
|------|-------|------|
| 响应时间 | < 300ms | 简单局面响应 |
| 复杂分析时间 | < 5s | 深度搜索响应 |
| 走法质量 | > 95% | 最佳走法选择率 |
| 工具调用准确率 | > 90% | 工具选择正确性 |

---

## 版本历史 / Version History

| 版本 | 日期 | 更新内容 |
|-----|------|---------|
| 1.0.0 | 2026-05-08 | 初始版本，支持模块化组合 |

---

**模块ID**: L3-C001 | **版本**: v1.0.0 | **类型**: agent  
**依赖模块**: L3-R025（工具优先原则）, L3-R001（基础规则框架）  
**映射**: L1-A001.15 → L2-B001.16 → L3-C001
# Logic Chain Framework

AI Agent Skills 的逻辑链执行框架，支持链式、条件分支和并行执行。

## 目录结构

```
logic_chain/
├── __init__.py              # 导出所有公开API
├── README.md                # 本文档
├── core/
│   ├── __init__.py
│   ├── base_node.py         # 基础节点类和类型定义
│   ├── chain_context.py     # 链执行上下文
│   └── chain_executor.py    # 核心执行器
├── steps/
│   ├── __init__.py
│   ├── skill_node.py        # 技能执行节点
│   ├── condition_node.py    # 条件判断节点
│   └── parallel_node.py     # 并行执行节点
└── examples/
    ├── __init__.py
    ├── example_chain.py     # 示例代码
    ├── example_chain.json   # JSON配置示例
    └── README.md            # 示例说明
```

## 核心概念

### 1. 节点类型 (NodeType)

| 类型 | 说明 |
|------|------|
| `SKILL` | 执行技能处理器 |
| `CONDITION` | 评估条件，结果存储到变量 |
| `IF_ELSE` | 基于条件路由到 true/false 分支 |
| `PARALLEL` | 并行执行多个节点 |
| `START/END` | 开始/结束标记 |

### 2. 节点执行流程

```
注册节点 → 设置 next 路由 → 执行链 → 返回结果
```

### 3. 条件表达式语法

```python
# 比较操作
"$age == 18"
"$score > 100"
"$status != 'banned'"

# 正则匹配
"$email matches .*@.*\\..*"

# 存在性检查
"$optional_field exists"
"$missing_field not_exists"
```

## 快速开始

### 1. 创建执行器

```python
from skills.logic_chain import ChainExecutor, ExecutionConfig

config = ExecutionConfig(debug_mode=True)
executor = ChainExecutor(config)
```

### 2. 注册节点

```python
from skills.logic_chain import SkillNode, ConditionNode, IfElseNode

executor.register_node(SkillNode(
    node_id="validate",
    name="Validate Input",
    skill_name="validate_email",
    parameters={"email": "$email"},
    output_key="is_valid",
))

executor.register_node(ConditionNode(
    node_id="check_valid",
    name="Check Validation",
    condition="$is_valid == true",
))

executor.register_node(IfElseNode(
    node_id="if_valid",
    name="IF Valid",
    condition_node_id="check_valid",
))
```

### 3. 设置路由

```python
executor.nodes["validate"].metadata = {
    "next": {"default": "check_valid"}
}
executor.nodes["if_valid"].metadata = {
    "next": {
        "true": "process_data",
        "false": "reject_input"
    }
}
```

### 4. 执行链

```python
import asyncio

async def run():
    context = await executor.execute_chain(
        chain_name="my_chain",
        start_node_id="validate",
        user_data={"email": "test@example.com"},
    )
    print(context.variables)

asyncio.run(run())
```

## 示例：用户注册流程

```json
{
  "chain_name": "User Registration",
  "nodes": [
    {"node_id": "start", "node_type": "skill", ...},
    {
      "node_id": "validate_email",
      "node_type": "condition",
      "condition": "$email matches .*@.*\\..*"
    },
    {
      "node_id": "if_email_valid",
      "node_type": "if_else",
      "metadata": {
        "next": {
          "true": "check_user_exists",
          "false": "reject_email"
        }
      }
    }
  ]
}
```

## API 参考

### ChainExecutor

| 方法 | 说明 |
|------|------|
| `register_node(node)` | 注册单个节点 |
| `register_nodes(nodes)` | 批量注册节点 |
| `execute_chain(...)` | 执行链并返回上下文 |
| `visualize_chain(start_id)` | 生成文本流程图 |
| `load_from_dict(config)` | 从JSON配置加载链 |

### ChainContext

| 方法 | 说明 |
|------|------|
| `get(key, default)` | 获取变量 |
| `set(key, value)` | 设置变量 |
| `has(key)` | 检查变量是否存在 |
| `update_node_result(id, result)` | 存储节点结果 |
| `get_node_result(id, default)` | 获取节点结果 |

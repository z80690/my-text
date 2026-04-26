# 🤖 Agent Framework - 智能体使用指南

## 📋 目录

- [快速开始](#快速开始)
- [20个智能体列表](#20个智能体列表)
- [使用方式](#使用方式)
- [API 服务器](#api-服务器)
- [示例代码](#示例代码)

---

## 🚀 快速开始

### 1️⃣ 方式一：直接在 Python 中调用（推荐）

```python
from agent.agents import get_registry, register_all_agents

# 1. 初始化并注册所有智能体
registry = get_registry()
register_all_agents(registry)
print(f"已加载 {len(registry.list_agents())} 个智能体")

# 2. 执行智能体任务
result = registry.execute(
    agent_id="assistant_agent",
    task="你好，请帮助我",
    context={}
)
print(result)
```

### 2️⃣ 方式二：通过 HTTP API 调用

```bash
# 启动服务器
cd my-text
python agent_server.py

# 然后用 curl 或 requests 调用
```

---

## 📦 20个智能体列表

| ID | 名称 | 描述 | 类型 | 能力 |
|----|------|------|------|------|
| 1 | assistant_agent | Assistant Agent | 通用助手智能体 | autogen_agentchat | chat, general, assistant |
| 2 | user_proxy_agent | User Proxy Agent | 用户代理智能体 | autogen_agentchat | user, proxy, interaction |
| 3 | code_executor_agent | Code Executor Agent | 代码执行智能体 | autogen_agentchat | code, execution, programming |
| 4 | message_filter_agent | Message Filter Agent | 消息过滤智能体 | autogen_agentchat | filter, message, processing |
| 5 | society_of_mind_agent | Society of Mind Agent | 心智社会智能体 | autogen_agentchat | reasoning, cognitive, multi_agent |
| 6 | base_agent | Base Agent | 基础智能体 | autogen_core | base, foundation |
| 7 | closure_agent | Closure Agent | 闭包智能体 | autogen_core | closure, encapsulation |
| 8 | routed_agent | Routed Agent | 路由智能体 | autogen_core | routing, dispatch |
| 9 | tool_agent | Tool Agent | 工具智能体 | autogen_core | tools, execution |
| 10 | chess_agent | Chess Agent | 国际象棋智能体 | sample | game, chess, strategy |
| 11 | fastapi_agent | FastAPI Agent | FastAPI智能体 | sample | api, fastapi, web |
| 12 | streamlit_agent | Streamlit Agent | Streamlit智能体 | sample | ui, streamlit, visualization |
| 13 | graphrag_agent | GraphRAG Agent | GraphRAG智能体 | sample | graph, rag, knowledge |
| 14 | dspy_agent | DSPy Agent | DSPy智能体 | sample | dspy, programming, ai |
| 15 | xlang_agent | Cross-language Agent | 跨语言智能体 | sample | multilingual, translation, cross_language |
| 16 | semantic_router_agent | Semantic Router Agent | 语义路由智能体 | sample | semantic, routing, nlp |
| 17 | editor_agent | Editor Agent | 编辑器智能体 | sample | edit, writing, text |
| 18 | writer_agent | Writer Agent | 作家智能体 | sample | write, creative, content |
| 19 | teachable_agent | Teachable Agent | 可教学智能体 | sample | teach, learn, adaptive |
| 20 | grpc_agent | gRPC Agent | gRPC智能体 | sample | grpc, rpc, api |

---

## 💡 使用方式

### 方式 1：Python 模块调用

**完整示例：**

```python
# test_agents.py
from agent.agents import get_registry, register_all_agents

def main():
    # 1. 初始化注册表
    registry = get_registry()
    register_all_agents(registry)
    print("✅ 所有智能体已加载")

    # 2. 列出所有智能体
    agents = registry.list_agents()
    print(f"\n📋 可用智能体 ({len(agents)}):")
    for agent in agents:
        print(f"  - {agent['name']} ({agent['id']})")

    # 3. 选择一个智能体
    print(f"\n🤖 执行任务...")
    result = registry.execute(
        agent_id="assistant_agent",
        task="帮我写一个 Python 脚本",
        context={"date": "2026-04-24"}
    )

    # 4. 查看结果
    print(f"\n📊 执行结果:")
    print(f"  状态: {result['status']}")
    print(f"  智能体: {result['agent_name']}")
    print(f"  结果: {result['result']}")

if __name__ == "__main__":
    main()
```

---

### 方式 2：HTTP API 调用

**启动服务器：**
```bash
python agent_server.py
# 输出:
# Starting Agent Framework Server...
# Loaded 20 agents
# * Running on http://0.0.0.0:8000
```

**API 端点：**

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| GET | `/api/agent/list` | 列出所有智能体 |
| POST | `/api/agent/execute` | 执行智能体任务 |
| GET | `/api/agent/info` | 获取服务信息 |

**API 调用示例：**

```python
# api_test.py
import requests

BASE_URL = "http://localhost:8000"

# 1. 健康检查
response = requests.get(f"{BASE_URL}/health")
print("健康检查:", response.json())

# 2. 获取智能体列表
response = requests.get(f"{BASE_URL}/api/agent/list")
print("智能体列表:", response.json())

# 3. 执行智能体
payload = {
    "agent_id": "assistant_agent",
    "task": "你好，请帮我介绍一下",
    "context": {"user": "demo"}
}
response = requests.post(f"{BASE_URL}/api/agent/execute", json=payload)
print("执行结果:", response.json())
```

---

### 方式 3：通过 OpenMAIC 前端界面

1. 启动 Agent Server：`python agent_server.py`
2. 启动 OpenMAIC：`cd OpenMAIC && npm run dev`
3. 访问 http://localhost:3000
4. 点击右上角的 **"Agent Framework"** 按钮
5. 在展开的面板中选择智能体，输入任务，点击 Execute

---

## 📁 目录结构

```
agent/
├── agent_scheduler.py      # 任务调度器
└── agents/                  # ✅ 智能体模块
    ├── __init__.py          # 模块入口
    ├── base.py              # BaseAgent 基类
    ├── registry.py          # AgentRegistry 注册中心
    └── implementations.py   # 20个智能体实现
```

---

## 🔧 组件说明

### AgentRegistry (注册中心)

```python
from agent.agents import get_registry

registry = get_registry()

# 主要方法：
registry.register(agent)          # 注册一个智能体
registry.get(agent_id)            # 获取智能体
registry.list_agents()             # 列出所有
registry.execute(agent_id, task)  # 执行任务
```

### BaseAgent (基类)

```python
from agent.agents import BaseAgent, AgentConfig

# 创建自定义智能体
class MyAgent(BaseAgent):
    def execute(self, task: str, context: dict = None) -> dict:
        # 实现你的逻辑
        return {"response": f"处理任务: {task}"}

# 注册
config = AgentConfig(
    id="my_agent",
    name="My Agent",
    description="我的智能体",
    type="custom",
    capabilities=["custom"]
)
registry.register(MyAgent(config))
```

---

## 📝 完整示例代码

### 示例 1：列出并测试所有智能体

```python
# test_all_agents.py
from agent.agents import get_registry, register_all_agents

def test_all_agents():
    registry = get_registry()
    register_all_agents(registry)
    print(f"✅ 加载了 {len(registry.list_agents())} 个智能体\n")

    for agent_info in registry.list_agents():
        print(f"🤖 测试: {agent_info['name']}")
        result = registry.execute(
            agent_id=agent_info['id'],
            task=f"测试任务: {agent_info['name']}"
        )
        print(f"   结果: {result['result']}\n")

if __name__ == "__main__":
    test_all_agents()
```

### 示例 2：使用 AgentScheduler 调度任务

```python
# use_scheduler.py
from agent.agent_scheduler import AgentScheduler

def main():
    scheduler = AgentScheduler()
    print("✅ AgentScheduler 已初始化")

    # 查看状态
    status = scheduler.get_scheduler_status()
    print(f"当前智能体数: {len(status['agents'])}")

if __name__ == "__main__":
    main()
```

---

## 🎮 快速测试命令

**直接运行测试：**

```bash
# 方式 1: 测试 Python 模块
python -c "
from agent.agents import get_registry, register_all_agents
registry = get_registry()
register_all_agents(registry)
result = registry.execute('assistant_agent', 'Hello from test')
print(result)
"

# 方式 2: 测试 API（需要先启动 agent_server.py）
python -c "
import requests
r = requests.post('http://localhost:8000/api/agent/execute', json={
    'agent_id': 'assistant_agent',
    'task': 'Hello from API'
})
print(r.json())
"
```

---

## ⚙️ 配置

### 环境变量

```bash
# Agent Server 端口（默认 8000）
export AGENT_FRAMEWORK_URL=http://localhost:8000
```

---

## 📚 下一步

- 查看 `implementations.py` 看每个智能体的具体实现
- 在 `base.py` 继承 `BaseAgent` 来添加自己的智能体
- 使用 `AgentScheduler` 来管理多智能体协作

---

## ❓ 常见问题

**Q: 怎么添加自己的智能体？**
A: 在 `agent/agents/implementations.py` 中继承 `BaseAgent` 并实现 `execute` 方法，然后在 `register_all_agents` 里注册。

**Q: 怎么修改智能体的行为？**
A: 修改对应智能体类里的 `execute` 方法即可。

**Q: 需要安装什么依赖？**
A: Flask（HTTP服务器），requests（测试用）：
```bash
pip install flask requests
```

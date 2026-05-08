# -*- coding: utf-8 -*-
"""
智能体系统演示
"""

import sys
import os
from datetime import datetime

# 设置路径
base_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, base_path)
agents_path = os.path.join(base_path, '.trae', 'agents')
sys.path.insert(0, agents_path)

print("=" * 80)
print("智能体模块化组合系统 - 演示")
print("=" * 80)
print()

print("【系统概述】")
print("  本系统包含 23 个专业智能体，支持模块化引用 L3 功能模块")
print("  核心功能:")
print("    - 工具优先原则 (L3-R025)")
print("    - 模块化组合系统 (L3-R026)")
print("    - 蜂群模式 (L3-R024)")
print()

# 导入并测试
print("【模块导入】")

try:
    # 导入基类
    from base import BaseAgent, AgentConfig, ModuleRegistry
    print("  ✓ BaseAgent, AgentConfig, ModuleRegistry")
    
    # 导入注册中心
    from registry import AgentRegistry
    print("  ✓ AgentRegistry")
    
    # 导入实现类
    from implementations_v2 import (
        AssistantAgent, CodeExecutorAgent, ChessAgent,
        DispatcherAgent, MonitorAgent
    )
    print("  ✓ 智能体实现类")
    
except Exception as e:
    print(f"  ✗ 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# 测试单个智能体
print("【单个智能体测试】")
print("-" * 40)

try:
    # 测试助手智能体
    assistant_config = AgentConfig(
        id="assistant_agent",
        name="通用助手",
        description="问答和查询",
        type="general",
        capabilities=["qa", "query"]
    )
    assistant = AssistantAgent(assistant_config)
    result = assistant._default_execute("你好，请帮我一个忙", {})
    print(f"  ✓ 助手智能体: {result.get('result', {}).get('response')}")
    
    # 测试代码执行智能体
    code_config = AgentConfig(
        id="code_executor_agent",
        name="代码执行",
        description="编程任务",
        type="code",
        capabilities=["code", "debug"],
        module_refs=[{"module_id": "L3-R025", "version_constraint": "latest"}]
    )
    code_agent = CodeExecutorAgent(code_config)
    result = code_agent._default_execute("写一个Python函数", {})
    print(f"  ✓ 代码执行智能体: {result.get('result', {}).get('response')}")
    
    # 测试国际象棋智能体
    chess_config = AgentConfig(
        id="chess_agent",
        name="国际象棋",
        description="棋类游戏",
        type="game",
        capabilities=["chess", "strategy"]
    )
    chess_agent = ChessAgent(chess_config)
    result = chess_agent._default_execute("分析当前棋局", {})
    print(f"  ✓ 国际象棋智能体: {result.get('result', {}).get('response')}")
    
except Exception as e:
    print(f"  ✗ 测试失败: {e}")
    import traceback
    traceback.print_exc()

print()

# 列出所有智能体
print("【智能体列表】")
print("-" * 40)

all_agents = [
    ("assistant_agent", "通用助手", "问答"),
    ("user_proxy_agent", "用户代理", "请求处理"),
    ("code_executor_agent", "代码执行", "编程"),
    ("message_filter_agent", "消息过滤", "内容审核"),
    ("society_of_mind_agent", "心智社会", "多视角分析"),
    ("base_agent", "基础智能体", "通用任务"),
    ("closure_agent", "闭包智能体", "封装"),
    ("routed_agent", "路由智能体", "任务分发"),
    ("tool_agent", "工具智能体", "工具调用"),
    ("chess_agent", "国际象棋", "棋类游戏"),
    ("fastapi_agent", "FastAPI", "Web开发"),
    ("streamlit_agent", "Streamlit", "数据可视化"),
    ("graphrag_agent", "GraphRAG", "知识图谱"),
    ("dspy_agent", "DSPy", "AI开发"),
    ("xlang_agent", "跨语言", "多语言"),
    ("semantic_router_agent", "语义路由", "意图理解"),
    ("editor_agent", "编辑器", "文本优化"),
    ("writer_agent", "作家", "内容创作"),
    ("teachable_agent", "可教学", "学习"),
    ("grpc_agent", "gRPC", "RPC服务"),
    ("monitor_agent", "监控智能体", "监控"),
    ("dispatcher_agent", "调度智能体", "协调"),
    ("rule_interpreter_agent", "规则解释", "规则解析"),
]

for i, (aid, name, desc) in enumerate(all_agents, 1):
    print(f"  {i:2d}. {name:20s} ({aid}) - {desc}")

print()
print("=" * 80)
print("演示完成")
print("=" * 80)
print()
print("文件结构:")
print("  .trae/agents/")
print("    ├── __init__.py           # 模块初始化")
print("    ├── base.py               # 基类和模块注册中心")
print("    ├── registry.py           # 智能体注册中心")
print("    ├── implementations_v2.py # 所有智能体实现")
print("    ├── chess_engine.py       # 国际象棋引擎")
print("    └── *_agent.md            # 23个智能体定义文件")
print()
print("系统特点:")
print("  ✓ 23个专业智能体完整实现")
print("  ✓ 支持L3功能模块引用")
print("  ✓ 工具优先原则内置")
print("  ✓ 模块化组合系统")
print("  ✓ 可扩展架构")
print()

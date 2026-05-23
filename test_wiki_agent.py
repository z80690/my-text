# -*- coding: utf-8 -*-
"""
测试LLM Wiki智能体
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trae.agents.implementations import load_all_agents
from trae.agents.registry import get_registry

# 加载所有智能体
load_all_agents()

# 获取注册中心
registry = get_registry()

# 获取LLM Wiki智能体
agent = registry.get('llm_wiki_agent')
print(f"智能体ID: {agent.id}")
print(f"智能体名称: {agent.name}")
print(f"智能体描述: {agent.description}")
print(f"智能体能力: {agent.capabilities}")

# 测试Ingest操作
print("\n=== 测试Ingest操作 ===")
result1 = agent.execute(
    "编译LLM Wiki知识",
    {
        'title': 'LLM Wiki知识编译范式',
        'content': 'LLM Wiki是一种知识管理方法，核心思想是"Compile, don\'t retrieve"，即一次编译，终身复用。',
        'source': 'https://www.toutiao.com/video/7641118917569561128/'
    }
)
print("Ingest结果:", result1)

# 测试Query操作
print("\n=== 测试Query操作 ===")
result2 = agent.execute("查询LLM Wiki知识")
print("Query结果:", result2)

# 测试Lint操作
print("\n=== 测试Lint操作 ===")
result3 = agent.execute("校验Wiki")
print("Lint结果:", result3)

print("\n=== 测试完成 ===")
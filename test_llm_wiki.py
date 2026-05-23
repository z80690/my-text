import sys
import os
sys.path.insert(0, '.')

# 测试导入
try:
    from trae.agents.llm_wiki_agent import LlmWikiAgent
    print("✅ 成功导入 LlmWikiAgent")
except Exception as e:
    print(f"❌ 导入失败: {e}")

# 测试创建智能体
try:
    from trae.agents.base import AgentConfig
    config = AgentConfig(
        id="llm_wiki_agent",
        name="LLM Wiki管理员",
        description="测试智能体",
        type="knowledge",
        capabilities=["knowledge_ingest", "knowledge_query", "knowledge_lint"]
    )
    agent = LlmWikiAgent(config)
    print("✅ 成功创建 LlmWikiAgent")
    print(f"   ID: {agent.id}")
    print(f"   名称: {agent.name}")
    print(f"   类型: {agent.type}")
except Exception as e:
    print(f"❌ 创建失败: {e}")

# 测试Ingest操作
try:
    result = agent.execute(
        "编译知识",
        {
            'title': '测试知识',
            'content': '这是一条测试知识内容，用于验证LLM Wiki智能体功能。',
            'source': '测试来源'
        }
    )
    print("✅ Ingest操作成功")
    print(f"   结果: {result}")
except Exception as e:
    print(f"❌ Ingest失败: {e}")

# 测试Query操作
try:
    result = agent.execute("查询测试知识")
    print("✅ Query操作成功")
    print(f"   结果: {result}")
except Exception as e:
    print(f"❌ Query失败: {e}")

# 测试Lint操作
try:
    result = agent.execute("校验Wiki")
    print("✅ Lint操作成功")
    print(f"   结果: {result}")
except Exception as e:
    print(f"❌ Lint失败: {e}")

print("\n=== 测试完成 ===")
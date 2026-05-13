# -*- coding: utf-8 -*-
"""
Trae MCP 全面测试结果记录
"""

import sys
import os
sys.path.insert(0, r"C:\Users\Administrator\Desktop\my-text\.trae")

from auto_memory_mcp import AutoMemorySystem

# 测试结果
results = []

# 测试 auto-memory MCP
print("="*70, file=sys.stderr)
print("🚀 测试 auto-memory MCP", file=sys.stderr)
print("="*70, file=sys.stderr)

memory_system = AutoMemorySystem()

test_cases = [
    "我习惯用4空格缩进",
    "很好，以后都这样",
    "我们团队禁止使用var声明变量",
    "因为要兼容旧版本",
    "Jira票号ABC-123",
    "这是电商后台系统"
]

for msg in test_cases:
    is_dark, reason = memory_system.is_dark_knowledge(msg)
    mem_type = memory_system.classify(msg)
    
    print(f"\n📝 消息: {msg}", file=sys.stderr)
    print(f"   暗知识: {'✅' if is_dark else '❌'}", file=sys.stderr)
    print(f"   分类: {mem_type}", file=sys.stderr)
    print(f"   原因: {reason}", file=sys.stderr)
    
    if is_dark:
        result = memory_system.write_memory(msg, mem_type)
        print(f"   记忆文件: {result}", file=sys.stderr)
        results.append({"mcp": "auto-memory", "message": msg, "result": "success"})

print("\n✅ auto-memory MCP 测试完成", file=sys.stderr)

# 测试 knowledge-graph MCP
print("\n" + "="*70, file=sys.stderr)
print("🚀 测试 knowledge-graph MCP", file=sys.stderr)
print("="*70, file=sys.stderr)

try:
    from knowledge_graph_mcp import KnowledgeGraphMemory
    
    kg = KnowledgeGraphMemory()
    kg.add_node("test_concept", "concept", {"description": "测试概念"})
    kg.add_edge("test_concept", "auto-memory", "has_capability")
    
    print("✅ 添加节点成功", file=sys.stderr)
    print("✅ 添加边成功", file=sys.stderr)
    print("✅ knowledge-graph MCP 测试完成", file=sys.stderr)
    results.append({"mcp": "knowledge-graph", "result": "success"})
    
except Exception as e:
    print(f"❌ knowledge-graph MCP 测试失败: {e}", file=sys.stderr)
    results.append({"mcp": "knowledge-graph", "result": "failed", "reason": str(e)})

# 测试 auto-workflow MCP
print("\n" + "="*70, file=sys.stderr)
print("🚀 测试 auto-workflow MCP", file=sys.stderr)
print("="*70, file=sys.stderr)

try:
    from auto_workflow_mcp import AutoWorkflowSystem
    
    workflow = AutoWorkflowSystem()
    tasks = workflow.list_tasks()
    
    print(f"📋 可用任务: {tasks}", file=sys.stderr)
    print("✅ auto-workflow MCP 测试完成", file=sys.stderr)
    results.append({"mcp": "auto-workflow", "result": "success"})
    
except Exception as e:
    print(f"❌ auto-workflow MCP 测试失败: {e}", file=sys.stderr)
    results.append({"mcp": "auto-workflow", "result": "failed", "reason": str(e)})

# 输出汇总报告
print("\n" + "="*70, file=sys.stderr)
print("📊 MCP 测试汇总报告", file=sys.stderr)
print("="*70, file=sys.stderr)

success_count = sum(1 for r in results if r["result"] == "success")
total_count = len(results)

print(f"\n测试总数: {total_count}", file=sys.stderr)
print(f"成功: {success_count}", file=sys.stderr)
print(f"失败: {total_count - success_count}", file=sys.stderr)
print(f"成功率: {success_count/total_count*100:.1f}%", file=sys.stderr)

print("\n详细结果:", file=sys.stderr)
print("-" * 50, file=sys.stderr)
for result in results:
    status = "✅" if result["result"] == "success" else "❌"
    print(f"{status} {result['mcp']}: {result['result']}", file=sys.stderr)
    if "reason" in result:
        print(f"   原因: {result['reason']}", file=sys.stderr)

# 写入结果文件
with open("mcp_test_results.json", "w", encoding="utf-8") as f:
    import json
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n📄 结果已保存到: mcp_test_results.json", file=sys.stderr)
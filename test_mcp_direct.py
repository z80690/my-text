# -*- coding: utf-8 -*-
"""
Trae MCP 全面测试 - 直接调用模块测试
"""

import sys
import os
sys.path.insert(0, r"C:\Users\Administrator\Desktop\my-text\.trae")

from auto_memory_mcp import AutoMemorySystem

def test_auto_memory_mcp():
    print("="*70)
    print("🚀 测试 auto-memory MCP")
    print("="*70)
    
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
        
        print(f"\n📝 消息: {msg}")
        print(f"   暗知识: {'✅' if is_dark else '❌'}")
        print(f"   分类: {mem_type}")
        print(f"   原因: {reason}")
        
        if is_dark:
            result = memory_system.write_memory(msg, mem_type)
            print(f"   记忆文件: {result}")
    
    print("\n✅ auto-memory MCP 测试完成")

def test_knowledge_graph_mcp():
    print("\n" + "="*70)
    print("🚀 测试 knowledge-graph MCP")
    print("="*70)
    
    try:
        from knowledge_graph_mcp import KnowledgeGraphMemory
        
        kg = KnowledgeGraphMemory()
        kg.add_node("test_concept", "concept", {"description": "测试概念"})
        kg.add_edge("test_concept", "auto-memory", "has_capability")
        
        print("✅ 添加节点成功")
        print("✅ 添加边成功")
        print("✅ knowledge-graph MCP 测试完成")
        
    except Exception as e:
        print(f"❌ knowledge-graph MCP 测试失败: {e}")

def test_auto_workflow_mcp():
    print("\n" + "="*70)
    print("🚀 测试 auto-workflow MCP")
    print("="*70)
    
    try:
        from auto_workflow_mcp import AutoWorkflowSystem
        
        workflow = AutoWorkflowSystem()
        tasks = workflow.list_tasks()
        
        print(f"📋 可用任务: {tasks}")
        print("✅ auto-workflow MCP 测试完成")
        
    except Exception as e:
        print(f"❌ auto-workflow MCP 测试失败: {e}")

def test_trae_auto_memory_npm():
    print("\n" + "="*70)
    print("🚀 测试 trae-auto-memory (NPM)")
    print("="*70)
    
    import subprocess
    import json
    
    mcp_path = r"C:\Users\Administrator\Desktop\my-text\auto-memory-mcp\dist\index.js"
    
    if not os.path.exists(mcp_path):
        print("❌ MCP 文件不存在")
        return
    
    process = subprocess.Popen(
        ['node', mcp_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "process_message",
                "arguments": {"message": "测试NPM版本的自动记忆"}
            }
        }
        
        stdout, stderr = process.communicate(
            input=json.dumps(request) + '\n',
            timeout=10
        )
        
        if stdout:
            print(f"📥 响应: {stdout.strip()}")
            print("✅ trae-auto-memory (NPM) 测试完成")
        else:
            print("❌ 无响应")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    print("="*70)
    print("🚀 Trae MCP 全面测试")
    print("="*70)
    print(f"测试时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_auto_memory_mcp()
    test_knowledge_graph_mcp()
    test_auto_workflow_mcp()
    test_trae_auto_memory_npm()
    
    print("\n" + "="*70)
    print("🎉 所有 MCP 测试完成")
    print("="*70)
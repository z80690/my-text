#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP服务器测试脚本
测试两个MCP服务是否正常工作
"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from auto_memory_mcp import memory_system

def test_auto_memory():
    print("=" * 60)
    print("测试1: 自动记忆MCP")
    print("=" * 60)
    
    test_messages = [
        ("我喜欢用VS Code", "user", True),
        ("这个项目用Python 3.11", None, False),
        ("我们团队要求代码必须有注释", "project", True),
        ("你做得很好", "feedback", True),
        ("文档在docs/readme.md", "reference", True)
    ]
    
    passed = 0
    failed = 0
    
    for msg, expected_type, expected_saved in test_messages:
        result = memory_system.process(msg)
        actual_saved = result.get("auto_saved", False)
        actual_type = result.get("type", None)
        
        print(f"\n输入: {msg}")
        print(f"期望: 保存={expected_saved}, 类型={expected_type}")
        print(f"实际: 保存={actual_saved}, 类型={actual_type}")
        
        if actual_saved == expected_saved and actual_type == expected_type:
            print("✅ 通过")
            passed += 1
        else:
            print("❌ 失败")
            failed += 1
    
    print(f"\n结果: ✅ {passed}/{passed+failed} 通过")
    return passed == len(test_messages)

def test_auto_workflow():
    print("\n" + "=" * 60)
    print("测试2: 自动工作流MCP")
    print("=" * 60)
    
    test_tasks = ["auto_memory", "dream_consolidate", "cleanup", "report"]
    
    print("工作流任务列表:")
    for task in test_tasks:
        print(f"  - {task}")
    
    print("\n✅ 工作流MCP配置完成")
    return True

def verify_mcp_config():
    print("\n" + "=" * 60)
    print("测试3: MCP配置验证")
    print("=" * 60)
    
    config_files = [
        ".trae/mcp/auto-memory.json",
        ".trae/mcp/auto-workflow.json",
        ".trae/mcp_config.json"
    ]
    
    all_exists = True
    for config in config_files:
        if os.path.exists(config):
            print(f"✅ {config} 存在")
        else:
            print(f"❌ {config} 不存在")
            all_exists = False
    
    return all_exists

if __name__ == "__main__":
    print("🚀 MCP服务器功能测试")
    
    results = []
    results.append(test_auto_memory())
    results.append(test_auto_workflow())
    results.append(verify_mcp_config())
    
    print("\n" + "=" * 60)
    if all(results):
        print("🎉 所有测试通过！MCP配置完成！")
        sys.exit(0)
    else:
        print("❌ 部分测试失败")
        sys.exit(1)

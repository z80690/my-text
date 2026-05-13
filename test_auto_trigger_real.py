# -*- coding: utf-8 -*-
"""
测试自动触发服务是否能真正调用 MCP
"""

import sys
sys.path.insert(0, r'C:\Users\Administrator\Desktop\my-text\.trae')

import asyncio
from auto_trigger_service import auto_trigger_service

async def test_auto_trigger():
    """测试自动触发服务"""
    print("="*70)
    print("🚀 测试自动触发服务")
    print("="*70)
    
    test_messages = [
        "帮我分析一下这个问题",
        "React useState 怎么用",
        "查询 TypeScript 泛型文档",
        "GitHub 上搜索 trae 相关仓库",
        "用 SQL 查询用户数据"
    ]
    
    print("\n📋 测试消息：")
    print("-" * 50)
    
    for msg in test_messages:
        print(f"\n📥 消息: {msg}")
        print("-" * 40)
        
        triggers = await auto_trigger_service.analyze_and_trigger(msg)
        
        if triggers:
            print("✅ 触发成功！")
            for trigger in triggers:
                print(f"   - 服务: {trigger.get('mcp_id') or trigger.get('skill_id')}")
                print(f"     动作: {trigger.get('action')}")
                print(f"     状态: {'成功' if trigger.get('success') else '失败'}")
        else:
            print("❌ 未触发任何服务")

if __name__ == "__main__":
    asyncio.run(test_auto_trigger())
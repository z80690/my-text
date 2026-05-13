# -*- coding: utf-8 -*-
"""
MCP 自动触发测试脚本
测试前端界面显示的所有 MCP 是否能正常自动触发
"""

import json
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from auto_trigger_service import auto_trigger_service, process_user_input

async def test_auto_trigger():
    """测试自动触发功能"""
    print("="*70)
    print("🚀 MCP 自动触发测试")
    print("="*70)
    
    # 测试用例 - 对应图片中的预期效果
    test_cases = [
        ("追踪", "应该自动触发工具调用追踪技能"),
        ("统计", "应该自动显示工具调用统计"),
        ("工具调用", "应该自动生成调用报告"),
        ("调试", "应该自动触发调试技能"),
        ("修复bug", "应该自动触发调试技能"),
        ("生成文档", "应该自动触发文档生成技能"),
        ("代码审查", "应该自动触发代码审查技能"),
        ("重构代码", "应该自动触发重构技能"),
    ]
    
    print("\n📋 测试用例：")
    print("-" * 50)
    
    success_count = 0
    for input_text, expected in test_cases:
        print(f"\n📥 输入: '{input_text}'")
        print(f"   预期: {expected}")
        
        try:
            result = await process_user_input(input_text)
            
            if result:
                print(f"✅ 触发成功: {result}")
                success_count += 1
            else:
                print("❌ 未触发任何工具")
                
        except Exception as e:
            print(f"❌ 触发失败: {e}")
    
    print("\n" + "="*70)
    print("📊 测试结果汇总")
    print("="*70)
    print(f"成功: {success_count}/{len(test_cases)}")
    
    if success_count == len(test_cases):
        print("🎉 所有自动触发测试通过！")
        return 0
    else:
        print("⚠️ 部分测试未通过，请检查触发规则配置")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(test_auto_trigger()))
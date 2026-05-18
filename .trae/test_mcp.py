#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试重构后的 MCP 是否符合规则体系 L3.4.7
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from auto_memory_mcp_stdio import process_message, search_memory, record_feedback, evolve_knowledge

def test_record():
    print("=== 测试阶段1：记录 ===")
    test_messages = [
        "我习惯用4空格缩进",
        "我们团队禁止用for循环",
        "你刚才的解法很好，以后都这样",
        "API文档在docs/api.md"
    ]
    
    recorded_files = []
    for msg in test_messages:
        result = process_message(msg)
        print(f"消息: {msg}")
        print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        if result.get("success"):
            recorded_files.append(result["path"])
        print()
    
    return recorded_files

def test_apply():
    print("=== 测试阶段2：应用 ===")
    query = "缩进"
    result = search_memory(query)
    print(f"查询: {query}")
    print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    print()
    
    return result.get("results", [])

def test_feedback(memory_path):
    print("=== 测试阶段3：反馈 ===")
    effect = "应用成功，提高了代码可读性"
    result = record_feedback(memory_path, effect)
    print(f"记忆文件: {memory_path}")
    print(f"效果: {effect}")
    print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    print()
    
    return result["path"]

def test_evolve(feedback_path):
    print("=== 测试阶段4：进化 ===")
    result = evolve_knowledge(feedback_path)
    print(f"反馈文件: {feedback_path}")
    print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    print()
    
    return result["path"]

def main():
    print("开始测试重构后的 MCP（基于规则体系 L3.4.7）")
    print("=" * 60)
    print()
    
    try:
        recorded_files = test_record()
        
        if recorded_files:
            search_results = test_apply()
            
            if search_results:
                feedback_path = test_feedback(recorded_files[0])
                evolve_path = test_evolve(feedback_path)
                
                print("=" * 60)
                print("测试完成！")
                print(f"生成的文件:")
                for f in recorded_files:
                    print(f"  - 记录: {f}")
                print(f"  - 反馈: {feedback_path}")
                print(f"  - 进化: {evolve_path}")
                print()
                print("知识应用闭环测试通过：记录→应用→反馈→进化")
            else:
                print("警告：搜索结果为空，无法继续测试反馈和进化")
        else:
            print("警告：没有成功记录任何文件，无法继续测试")
            
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
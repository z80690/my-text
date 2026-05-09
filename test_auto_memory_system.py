#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动记忆系统测试用例
测试5个场景，验证自动记忆是否正常工作
"""

import sys
import os

# 添加技能目录到路径
sys.path.insert(0, r'C:\Users\Administrator\.trae-cn\builtin\work\default\skills\auto-memory')

from auto_memory import auto_process_message

def run_tests():
    test_cases = [
        {
            "id": "TC001",
            "name": "暗知识识别 - 用户偏好",
            "input": "我习惯用Tab键缩进",
            "expected_type": "user",
            "expected_saved": True
        },
        {
            "id": "TC002",
            "name": "暗知识识别 - 团队规则",
            "input": "我们团队禁止使用var声明变量",
            "expected_type": "project",
            "expected_saved": True
        },
        {
            "id": "TC003",
            "name": "明知识过滤 - 版本号",
            "input": "这个项目用的是Node.js 20.10.0",
            "expected_type": None,
            "expected_saved": False
        },
        {
            "id": "TC004",
            "name": "自动分类 - 用户反馈",
            "input": "你刚才的解决方案很好，以后都这样",
            "expected_type": "feedback",
            "expected_saved": True
        },
        {
            "id": "TC005",
            "name": "自动分类 - 外部引用",
            "input": "需求文档在Jira票号DEVOPS-456",
            "expected_type": "reference",
            "expected_saved": True
        }
    ]
    
    print("=" * 60)
    print("自动记忆系统测试套件")
    print("=" * 60)
    print()
    
    passed = 0
    failed = 0
    
    for tc in test_cases:
        print(f"📋 测试用例 {tc['id']}: {tc['name']}")
        print(f"   输入: {tc['input']}")
        
        # 执行自动记忆处理
        result = auto_process_message(tc['input'])
        
        # 验证结果
        actual_saved = result.get("auto_saved", False)
        actual_type = result.get("type", None)
        
        print(f"   期望: 保存={tc['expected_saved']}, 类型={tc['expected_type']}")
        print(f"   实际: 保存={actual_saved}, 类型={actual_type}")
        
        if actual_saved == tc['expected_saved'] and actual_type == tc['expected_type']:
            print("   ✅ 通过")
            passed += 1
        else:
            print("   ❌ 失败")
            failed += 1
        
        if actual_saved:
            print(f"   文件路径: {result.get('path', '未知')}")
        
        print()
    
    print("=" * 60)
    print(f"测试结果: ✅ {passed} 通过, ❌ {failed} 失败")
    print("=" * 60)
    
    # 验证记忆文件是否正确创建
    print("\n📂 验证记忆文件:")
    memories_dir = os.path.join(os.getcwd(), ".trae", "memories")
    if os.path.exists(memories_dir):
        for mem_type in ["user", "feedback", "project", "reference"]:
            type_dir = os.path.join(memories_dir, mem_type)
            if os.path.exists(type_dir):
                files = os.listdir(type_dir)
                if files:
                    print(f"  {mem_type}/: {', '.join(files)}")
                else:
                    print(f"  {mem_type}/: (空)")
    else:
        print("  记忆目录不存在")
    
    return failed == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

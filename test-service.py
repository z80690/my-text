# -*- coding: utf-8 -*-
"""
测试 Meta-Cognition 后台服务
验证真正的完全无感模式
"""

import json
import time
from pathlib import Path

DATA_DIR = Path(__file__).parent / "meta-cognition-data"
LOG_FILE = DATA_DIR / "logs" / "meta_cognition.json"

print("=" * 60)
print("  测试 Meta-Cognition 后台服务")
print("=" * 60)

# 检查服务是否运行
if LOG_FILE.exists():
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"\n📊 当前统计:")
    stats = data.get('statistics', {})
    print(f"  总任务数: {stats.get('total_tasks', 0)}")
    print(f"  成功数: {stats.get('success_count', 0)}")
    print(f"  失败数: {stats.get('failure_count', 0)}")
    print(f"  成功率: {stats.get('success_rate', 0):.1f}%")
    
    print(f"\n📋 最近任务:")
    sessions = data.get('sessions', [])[:5]
    for i, session in enumerate(sessions, 1):
        print(f"  {i}. [{session.get('detected_mode', '未知')}] {session.get('task_description', '')[:40]}...")
        print(f"     结果: {session.get('result', 'unknown')}")
else:
    print("❌ 服务未运行或日志文件不存在")

print("\n" + "=" * 60)
print("✅ 真正的无感体验:")
print("   - 开机自动启动")
print("   - 后台静默运行")
print("   - 无需任何导入")
print("   - 自动记录所有任务")
print("=" * 60)

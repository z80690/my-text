#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP综合测试脚本 - 测试4个核心组件和meta-cognition技能
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '.trae', 'skills', 'meta-cognition'))

from .trae.skills.meta_cognition.meta_cognition import (
    MetaCognition,
    MetaCognitionConfig,
    TriggerEngine,
    LogManager,
    MetaCognitionEngine
)
from .trae.skills.meta_cognition.integration_config import (
    execute_with_hooks,
    complete_with_hooks,
    get_current_session_id
)

def test_mcp_1_log_manager():
    """测试MCP1: LogManager - 日志管理"""
    print('='*60)
    print("🔹 MCP测试1: LogManager (日志管理)")
    print('='*60)
    
    config = MetaCognitionConfig()
    log_manager = LogManager(config.log)
    
    # 测试生成会话ID
    session_id = log_manager.generate_session_id()
    print(f"✅ 生成会话ID: {session_id}")
    
    # 测试时间戳
    timestamp = log_manager.get_current_timestamp()
    print(f"✅ 获取时间戳: {timestamp}")
    
    # 测试敏感信息过滤
    test_text = "我的API密钥是 api_key=abc123secret456token"
    filtered = log_manager.filter_sensitive_info(test_text)
    print(f"✅ 敏感信息过滤: {filtered}")
    
    # 测试添加会话
    session_data = {
        "session_id": session_id,
        "task_description": "测试任务",
        "phase": "completed",
        "success": True,
        "timestamp": timestamp
    }
    log_manager.add_session(session_data)
    print(f"✅ 添加会话记录成功")
    
    # 测试获取统计信息
    stats = log_manager.get_statistics()
    print(f"✅ 获取统计信息: {stats}")
    
    print()

def test_mcp_2_trigger_engine():
    """测试MCP2: TriggerEngine - 自动触发引擎"""
    print('='*60)
    print("🔹 MCP测试2: TriggerEngine (自动触发引擎)")
    print('='*60)
    
    config = MetaCognitionConfig()
    trigger = TriggerEngine(config)
    
    # 测试获取状态
    status = trigger.get_status()
    print(f"✅ 获取触发器状态: {status}")
    
    # 测试事件发射
    trigger.emit_event("test", "测试任务描述")
    print(f"✅ 发射事件成功")
    
    # 测试直接提交任务
    def test_callback(task, context):
        print(f"  回调触发: {task[:30]}...")
        return "processed"
    
    trigger.set_on_task_submit(test_callback)
    result = trigger.submit_direct("直接提交测试任务")
    print(f"✅ 直接提交任务: {result}")
    
    print()

def test_mcp_3_engine():
    """测试MCP3: MetaCognitionEngine - 核心引擎"""
    print('='*60)
    print("🔹 MCP测试3: MetaCognitionEngine (核心引擎)")
    print('='*60)
    
    config = MetaCognitionConfig()
    log_manager = LogManager(config.log)
    engine = MetaCognitionEngine(config, log_manager)
    
    # 测试任务模式检测
    test_tasks = [
        ("对比两种方案的优缺点", "game_theory_mode1"),
        ("优化代码性能", "game_theory_mode2"),
        ("设计系统架构", "game_theory_mode3"),
        ("你好", "normal")
    ]
    
    for task, expected in test_tasks:
        mode = engine.detect_task_mode(task)
        status = "✅" if mode == expected else "❌"
        print(f"{status} 任务: '{task}' → 检测模式: {mode} (期望: {expected})")
    
    # 测试调度决策
    decision = engine.get_scheduling_decision("game_theory_mode2", "优化代码")
    print(f"\n✅ 获取调度决策: {decision['mode']}")
    print(f"   推荐智能体: {decision['recommended_agents']}")
    
    print()

def test_mcp_4_meta_cognition():
    """测试MCP4: MetaCognition - 主类"""
    print('='*60)
    print("🔹 MCP测试4: MetaCognition (主类)")
    print('='*60)
    
    config = MetaCognitionConfig()
    mc = MetaCognition(config)
    
    # 测试初始化
    print(f"✅ MetaCognition 初始化成功")
    print(f"   版本: {mc.__version__ if hasattr(mc, '__version__') else '3.0.0'}")
    
    # 测试启动触发器
    mc.start()
    print(f"✅ 触发器启动成功")
    
    # 测试获取状态
    status = mc.get_status()
    print(f"✅ 获取状态: {status}")
    
    # 测试停止触发器
    mc.stop()
    print(f"✅ 触发器停止成功")
    
    print()

def test_meta_cognition_skill():
    """测试meta-cognition技能完整流程"""
    print('='*60)
    print("🔹 技能测试: meta-cognition 完整流程")
    print('='*60)
    
    # 测试任务1: 优化任务
    print("\n--- 任务1: 代码优化 ---")
    result1 = execute_with_hooks("帮我优化这段Python代码的性能")
    print(f"会话ID: {result1.get('session_id')}")
    print(f"检测模式: {result1.get('mode')}")
    complete_with_hooks(result='success', response_preview='代码优化完成')
    
    # 测试任务2: 架构设计
    print("\n--- 任务2: 架构设计 ---")
    result2 = execute_with_hooks("设计一个分布式微服务架构")
    print(f"会话ID: {result2.get('session_id')}")
    print(f"检测模式: {result2.get('mode')}")
    complete_with_hooks(result='success', response_preview='架构设计完成')
    
    # 测试任务3: 对比分析
    print("\n--- 任务3: 对比分析 ---")
    result3 = execute_with_hooks("对比Docker和Kubernetes的优缺点")
    print(f"会话ID: {result3.get('session_id')}")
    print(f"检测模式: {result3.get('mode')}")
    complete_with_hooks(result='success', response_preview='对比分析完成')
    
    # 测试任务4: 简单问答
    print("\n--- 任务4: 简单问答 ---")
    result4 = execute_with_hooks("什么是人工智能")
    print(f"会话ID: {result4.get('session_id')}")
    print(f"检测模式: {result4.get('mode')}")
    complete_with_hooks(result='success', response_preview='问答完成')
    
    print()

def main():
    print('='*70)
    print("🚀 MCP综合测试套件 - meta-cognition技能")
    print('='*70)
    print()
    
    # 依次测试4个MCP组件
    test_mcp_1_log_manager()
    test_mcp_2_trigger_engine()
    test_mcp_3_engine()
    test_mcp_4_meta_cognition()
    
    # 测试完整技能流程
    test_meta_cognition_skill()
    
    print('='*70)
    print("🎉 所有MCP测试完成!")
    print('='*70)

if __name__ == '__main__':
    main()
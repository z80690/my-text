#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记录之前的错误任务到元认知日志
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# 添加元认知技能路径
sys.path.insert(0, str(Path(__file__).parent / '.trae' / 'skills' / 'meta-cognition'))

from hooks.utils import load_log, save_log, get_current_timestamp, generate_session_id

def record_previous_error():
    """记录之前的错误任务"""
    
    print("=" * 60)
    print("🚀 记录之前的错误任务到元认知日志")
    print("=" * 60)
    
    log_data = load_log()
    
    # 错误任务1: 混淆 iFlow 和 TRAE IDE
    error_session_1 = {
        "session_id": generate_session_id(),
        "phase": "completed",
        "timestamp": get_current_timestamp(),
        "end_timestamp": get_current_timestamp(),
        "task_description": "配置 iFlow 目录结构实现智能体同步",
        "original_task": "我已经进入这个账户，I F L O W 这个界面里头的，我看到那个23个智能体了，但是前端没有任何显示。我想问一下那个 if LOW 这个文件夹的标准目录结构是什么样子的？",
        "detected_mode": "game_theory_mode3",
        "task_type": "architecture",
        "scheduling_advice": {},
        "scheduling_decision": {
            "mode": "深度设计模式（三段式协同）",
            "description": "设计并实现 iFlow 目录结构",
            "recommended_agents": ["society_of_mind_agent", "code_executor_agent", "editor_agent"]
        },
        "result": "failure",
        "success": False,
        "agents_used": ["code_executor_agent"],
        "duration_ms": 0,
        "error": "混淆了 TRAE IDE 和 iFlow CLI 两个不同工具，错误创建了 .iflow 目录结构",
        "error_details": "用户明确要求 TRAE 前端智能体同步，但系统错误地去配置 iFlow CLI 的目录结构，创建了不存在的 .iflow 文件夹，导致用户强烈不满",
        "response_preview": "错误配置了 .iflow 目录，已被用户指出错误",
        "root_cause": "误解了用户的需求，混淆了两个不同的产品（TRAE IDE vs iFlow CLI）",
        "impact": "用户体验差，任务执行失败",
        "fix_needed": True
    }
    
    # 错误任务2: 自我净化功能未被调用
    error_session_2 = {
        "session_id": generate_session_id(),
        "phase": "completed",
        "timestamp": get_current_timestamp(),
        "end_timestamp": get_current_timestamp(),
        "task_description": "自我净化功能调用检查",
        "original_task": "分期为什么出错？然后你是否调用了自我净化功能？是否保存了错误的？",
        "detected_mode": "game_theory_mode1",
        "task_type": "analysis",
        "scheduling_decision": {
            "mode": "辩论模式（串行模拟并行）",
            "description": "分析错误原因并检查自我净化功能",
            "recommended_agents": ["society_of_mind_agent", "editor_agent"]
        },
        "result": "failure",
        "success": False,
        "agents_used": [],
        "duration_ms": 0,
        "error": "自我净化功能未被自动调用，错误任务也未被记录",
        "error_details": "任务出错后，系统没有自动记录错误，也没有调用自我净化功能进行分析",
        "response_preview": "正在检查自我净化功能",
        "root_cause": "元认知技能的钩子没有被正确集成到执行流程中",
        "impact": "错误无法被追踪和分析，无法从错误中学习",
        "fix_needed": True
    }
    
    # 添加到日志
    log_data["sessions"].append(error_session_1)
    log_data["sessions"].append(error_session_2)
    
    # 更新统计信息
    if "task_statistics" not in log_data:
        log_data["task_statistics"] = {
            "total": 0,
            "success": 0,
            "failure": 0,
            "last_updated": get_current_timestamp()
        }
    
    log_data["task_statistics"]["total"] += 2
    log_data["task_statistics"]["failure"] += 2
    log_data["task_statistics"]["last_updated"] = get_current_timestamp()
    
    # 保存日志
    save_log(log_data)
    
    print("\n✅ 成功记录 2 个错误任务到元认知日志")
    print(f"\n📊 当前统计:")
    print(f"   - 总任务: {log_data['task_statistics']['total']}")
    print(f"   - 成功: {log_data['task_statistics']['success']}")
    print(f"   - 失败: {log_data['task_statistics']['failure']}")
    print(f"\n📝 日志文件: .trae/skills/meta-cognition/logs/meta_cognition.json")
    
    return [error_session_1, error_session_2]

if __name__ == "__main__":
    record_previous_error()

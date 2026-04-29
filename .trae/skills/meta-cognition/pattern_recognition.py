# -*- coding: utf-8 -*-
"""
Meta-Cognition 模式识别模块

实现自动识别常见任务类型并优化调度的功能
"""

import re
from collections import defaultdict
from typing import Dict, List, Tuple, Set

from .hooks.utils import load_log, save_log, get_current_timestamp
from .config.config import CONFIG


# 任务类型定义
TASK_TYPES = {
    "optimization": {
        "keywords": ["优化", "提升", "改进", "加速", "性能", "效率", "重构", "优化", "改进", "加速", "性能", "效率", "重构"],
        "description": "优化类任务",
        "recommended_mode": "game_theory_mode2"
    },
    "design": {
        "keywords": ["设计", "架构", "创建", "开发", "构建", "规划", "设计", "架构", "创建", "开发", "构建", "规划"],
        "description": "设计类任务",
        "recommended_mode": "game_theory_mode3"
    },
    "debate": {
        "keywords": ["对比", "优缺点", "利弊", "讨论", "分析", "评估", "对比", "优缺点", "利弊", "讨论", "分析", "评估"],
        "description": "辩论类任务",
        "recommended_mode": "game_theory_mode1"
    },
    "debug": {
        "keywords": ["修复", "调试", "错误", "问题", "解决", "bug", "修复", "调试", "错误", "问题", "解决", "bug"],
        "description": "调试类任务",
        "recommended_mode": "game_theory_mode2"
    },
    "research": {
        "keywords": ["研究", "调研", "分析", "了解", "学习", "探索", "研究", "调研", "分析", "了解", "学习", "探索"],
        "description": "研究类任务",
        "recommended_mode": "game_theory_mode3"
    },
    "normal": {
        "keywords": [],
        "description": "常规任务",
        "recommended_mode": "normal"
    }
}


def recognize_task_type(task_description: str) -> Tuple[str, float]:
    """
    识别任务类型
    
    Args:
        task_description: 任务描述
    
    Returns:
        (任务类型, 置信度)
    """
    task_lower = task_description.lower()
    scores = defaultdict(float)
    
    for task_type, config in TASK_TYPES.items():
        if task_type == "normal":
            continue
        
        # 计算关键词匹配得分
        for keyword in config["keywords"]:
            if keyword in task_lower:
                scores[task_type] += 1.0
    
    if not scores:
        return "normal", 1.0
    
    # 找出得分最高的任务类型
    max_score = max(scores.values())
    best_type = max(scores, key=scores.get)
    
    # 计算置信度
    total_score = sum(scores.values())
    confidence = max_score / total_score if total_score > 0 else 0.0
    
    return best_type, confidence


def optimize_scheduling(task_description: str) -> Dict[str, Any]:
    """
    优化调度策略
    
    Args:
        task_description: 任务描述
    
    Returns:
        优化后的调度策略
    """
    # 识别任务类型
    task_type, confidence = recognize_task_type(task_description)
    
    # 获取推荐模式
    recommended_mode = TASK_TYPES[task_type]["recommended_mode"]
    
    # 分析历史数据，调整推荐
    historical_data = analyze_historical_scheduling()
    
    # 根据历史成功率调整推荐
    adjusted_mode = adjust_based_on_history(recommended_mode, task_type)
    
    # 生成调度建议
    scheduling_advice = {
        "task_type": task_type,
        "confidence": confidence,
        "recommended_mode": recommended_mode,
        "adjusted_mode": adjusted_mode,
        "reason": f"任务类型识别为{task_type}，基于历史数据调整为{adjusted_mode}",
        "historical_data": historical_data
    }
    
    return scheduling_advice


def analyze_historical_scheduling() -> Dict[str, Any]:
    """
    分析历史调度数据
    
    Returns:
        历史调度分析结果
    """
    log_data = load_log()
    sessions = log_data.get("sessions", [])
    
    # 按任务类型和模式统计成功率
    stats = defaultdict(lambda: defaultdict(lambda: {
        "total": 0,
        "success": 0,
        "success_rate": 0.0
    }))
    
    for session in sessions:
        if session.get("phase") == "completed":
            task_desc = session.get("task_description", "")
            detected_mode = session.get("detected_mode", "normal")
            success = session.get("success", False)
            
            task_type, _ = recognize_task_type(task_desc)
            
            stats[task_type][detected_mode]["total"] += 1
            if success:
                stats[task_type][detected_mode]["success"] += 1
    
    # 计算成功率
    for task_type, modes in stats.items():
        for mode, data in modes.items():
            if data["total"] > 0:
                data["success_rate"] = data["success"] / data["total"] * 100
    
    return stats


def adjust_based_on_history(recommended_mode: str, task_type: str) -> str:
    """
    根据历史数据调整推荐模式
    
    Args:
        recommended_mode: 推荐模式
        task_type: 任务类型
    
    Returns:
        调整后的模式
    """
    historical_data = analyze_historical_scheduling()
    
    # 检查历史数据
    if task_type in historical_data:
        mode_stats = historical_data[task_type]
        
        # 找出成功率最高的模式
        best_mode = recommended_mode
        best_rate = 0.0
        
        for mode, data in mode_stats.items():
            if data["success_rate"] > best_rate and data["total"] >= 2:  # 至少有2个样本
                best_rate = data["success_rate"]
                best_mode = mode
        
        return best_mode
    
    return recommended_mode


def get_pattern_statistics() -> Dict[str, Any]:
    """
    获取模式统计信息
    
    Returns:
        模式统计信息
    """
    historical_data = analyze_historical_scheduling()
    
    # 计算总体统计
    overall_stats = {
        "total_tasks": 0,
        "success_rate": 0.0,
        "by_task_type": {},
        "by_mode": {}
    }
    
    # 按任务类型统计
    for task_type, modes in historical_data.items():
        task_total = 0
        task_success = 0
        
        for mode, data in modes.items():
            task_total += data["total"]
            task_success += data["success"]
        
        if task_total > 0:
            overall_stats["by_task_type"][task_type] = {
                "total": task_total,
                "success": task_success,
                "success_rate": task_success / task_total * 100
            }
            overall_stats["total_tasks"] += task_total
    
    # 按模式统计
    mode_stats = defaultdict(lambda: {"total": 0, "success": 0})
    for task_type, modes in historical_data.items():
        for mode, data in modes.items():
            mode_stats[mode]["total"] += data["total"]
            mode_stats[mode]["success"] += data["success"]
    
    for mode, data in mode_stats.items():
        if data["total"] > 0:
            overall_stats["by_mode"][mode] = {
                "total": data["total"],
                "success": data["success"],
                "success_rate": data["success"] / data["total"] * 100
            }
    
    # 计算总体成功率
    total_success = sum(data["success"] for data in overall_stats["by_task_type"].values())
    if overall_stats["total_tasks"] > 0:
        overall_stats["success_rate"] = total_success / overall_stats["total_tasks"] * 100
    
    return overall_stats


def generate_scheduling_recommendations() -> Dict[str, Any]:
    """
    生成调度建议
    
    Returns:
        调度建议
    """
    stats = get_pattern_statistics()
    
    # 找出最佳模式
    best_mode = "normal"
    best_rate = 0.0
    
    for mode, data in stats["by_mode"].items():
        if data["success_rate"] > best_rate and data["total"] >= 3:  # 至少有3个样本
            best_rate = data["success_rate"]
            best_mode = mode
    
    # 生成建议
    recommendations = {
        "best_mode": best_mode,
        "best_success_rate": best_rate,
        "task_type_recommendations": {},
        "overall_stats": stats,
        "timestamp": get_current_timestamp()
    }
    
    # 为每种任务类型生成建议
    for task_type, data in stats["by_task_type"].items():
        # 找出该任务类型的最佳模式
        historical_data = analyze_historical_scheduling()
        if task_type in historical_data:
            task_modes = historical_data[task_type]
            task_best_mode = TASK_TYPES[task_type]["recommended_mode"]
            task_best_rate = 0.0
            
            for mode, mode_data in task_modes.items():
                if mode_data["success_rate"] > task_best_rate and mode_data["total"] >= 2:
                    task_best_rate = mode_data["success_rate"]
                    task_best_mode = mode
            
            recommendations["task_type_recommendations"][task_type] = {
                "recommended_mode": TASK_TYPES[task_type]["recommended_mode"],
                "best_mode": task_best_mode,
                "best_success_rate": task_best_rate
            }
    
    # 保存建议
    log_data = load_log()
    log_data["scheduling_recommendations"] = recommendations
    save_log(log_data)
    
    return recommendations


if __name__ == "__main__":
    print("=== 模式识别模块测试 ===")
    
    # 测试任务类型识别
    test_tasks = [
        "请帮我优化这段代码，提升性能",
        "请对比敏捷开发和瀑布模型的优缺点",
        "帮我设计一个用户认证系统",
        "1+1等于几？",
        "这个代码报错了，帮我修复一下",
        "帮我研究一下最新的AI技术"
    ]
    
    for task in test_tasks:
        task_type, confidence = recognize_task_type(task)
        print(f"任务: {task}")
        print(f"类型: {task_type}, 置信度: {confidence:.2f}")
        
        # 测试优化调度
        scheduling = optimize_scheduling(task)
        print(f"调度建议: {scheduling}")
        print()
    
    # 测试统计信息
    stats = get_pattern_statistics()
    print(f"模式统计: {stats}")
    
    # 测试调度建议
    recommendations = generate_scheduling_recommendations()
    print(f"调度建议: {recommendations}")

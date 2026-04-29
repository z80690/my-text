# -*- coding: utf-8 -*-
"""
Meta-Cognition 主动学习模块

实现根据历史数据自动调整知识图谱关系的功能
"""

import re
from collections import defaultdict
from typing import Dict, List, Tuple, Set

from .hooks.utils import load_log, save_log, get_current_timestamp
from .config.config import CONFIG


def extract_keywords(task_description: str) -> List[str]:
    """
    从任务描述中提取关键词
    
    Args:
        task_description: 任务描述
    
    Returns:
        关键词列表
    """
    # 清理标点
    cleaned = re.sub(r'[.,;!?()\[\]{}]', ' ', task_description)
    # 分词
    words = cleaned.split()
    # 过滤短词和常见词
    common_words = set(["请", "帮", "我", "你", "的", "这", "那", "个", "是", "在", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这"])
    
    keywords = []
    for word in words:
        word = word.strip()
        if len(word) > 1 and word not in common_words:
            keywords.append(word)
    
    return keywords


def analyze_task_patterns() -> Dict[str, Dict[str, int]]:
    """
    分析任务模式和关键词的关联
    
    Returns:
        模式到关键词的映射
    """
    log_data = load_log()
    sessions = log_data.get("sessions", [])
    
    # 模式到关键词的映射
    pattern_keywords = defaultdict(lambda: defaultdict(int))
    
    for session in sessions:
        if session.get("phase") == "completed":
            task_desc = session.get("task_description", "")
            detected_mode = session.get("detected_mode", "normal")
            
            if task_desc and detected_mode != "normal":
                keywords = extract_keywords(task_desc)
                for keyword in keywords:
                    pattern_keywords[detected_mode][keyword] += 1
    
    return pattern_keywords


def update_knowledge_graph() -> Dict[str, Any]:
    """
    根据历史数据更新知识图谱
    
    Returns:
        更新结果
    """
    # 分析任务模式
    pattern_keywords = analyze_task_patterns()
    
    # 模式到核心概念的映射
    mode_to_concept = {
        "game_theory_mode1": "辩论",
        "game_theory_mode2": "优化",
        "game_theory_mode3": "设计"
    }
    
    # 收集新的知识图谱关系
    new_relations = {}
    
    for mode, keywords in pattern_keywords.items():
        concept = mode_to_concept.get(mode)
        if not concept:
            continue
        
        # 只保留出现次数大于1的关键词
        for keyword, count in keywords.items():
            if count > 1:
                new_relations[keyword] = [concept]
    
    # 合并到现有知识图谱
    updated_kg = CONFIG.knowledge_graph.kg_relations.copy()
    updated_kg.update(new_relations)
    
    # 保存更新后的知识图谱
    log_data = load_log()
    log_data["knowledge_graph_update"] = {
        "timestamp": get_current_timestamp(),
        "updated_relations": new_relations,
        "total_relations": len(updated_kg)
    }
    save_log(log_data)
    
    return {
        "updated": True,
        "new_relations": new_relations,
        "total_relations": len(updated_kg),
        "message": f"更新了{len(new_relations)}个知识图谱关系"
    }


def get_learning_status() -> Dict[str, Any]:
    """
    获取学习状态
    
    Returns:
        学习状态信息
    """
    log_data = load_log()
    last_update = log_data.get("knowledge_graph_update", {})
    
    # 分析当前知识图谱
    current_kg = CONFIG.knowledge_graph.kg_relations
    
    # 分析任务模式
    pattern_keywords = analyze_task_patterns()
    
    return {
        "last_update": last_update,
        "current_relations": len(current_kg),
        "pattern_keywords": pattern_keywords,
        "message": "主动学习状态"
    }


def identify_weak_patterns() -> Dict[str, List[str]]:
    """
    识别弱模式（出现次数较少的模式）
    
    Returns:
        弱模式到关键词的映射
    """
    pattern_keywords = analyze_task_patterns()
    weak_patterns = {}
    
    for mode, keywords in pattern_keywords.items():
        weak_keywords = [k for k, v in keywords.items() if v == 1]
        if weak_keywords:
            weak_patterns[mode] = weak_keywords
    
    return weak_patterns


def optimize_knowledge_graph() -> Dict[str, Any]:
    """
    优化知识图谱
    
    Returns:
        优化结果
    """
    # 分析任务模式
    pattern_keywords = analyze_task_patterns()
    
    # 模式到核心概念的映射
    mode_to_concept = {
        "game_theory_mode1": "辩论",
        "game_theory_mode2": "优化",
        "game_theory_mode3": "设计"
    }
    
    # 计算关键词权重
    keyword_weights = defaultdict(int)
    for mode, keywords in pattern_keywords.items():
        for keyword, count in keywords.items():
            keyword_weights[keyword] += count
    
    # 只保留权重较高的关键词
    threshold = 2  # 权重阈值
    important_keywords = {k: v for k, v in keyword_weights.items() if v >= threshold}
    
    # 更新知识图谱
    new_relations = {}
    for mode, keywords in pattern_keywords.items():
        concept = mode_to_concept.get(mode)
        if not concept:
            continue
        
        for keyword, count in keywords.items():
            if keyword in important_keywords:
                new_relations[keyword] = [concept]
    
    # 合并到现有知识图谱
    updated_kg = CONFIG.knowledge_graph.kg_relations.copy()
    updated_kg.update(new_relations)
    
    # 保存更新后的知识图谱
    log_data = load_log()
    log_data["knowledge_graph_optimization"] = {
        "timestamp": get_current_timestamp(),
        "important_keywords": important_keywords,
        "total_relations": len(updated_kg)
    }
    save_log(log_data)
    
    return {
        "optimized": True,
        "important_keywords": important_keywords,
        "total_relations": len(updated_kg),
        "message": f"优化了知识图谱，保留了{len(important_keywords)}个重要关键词"
    }


if __name__ == "__main__":
    print("=== 主动学习模块测试 ===")
    
    # 分析任务模式
    patterns = analyze_task_patterns()
    print(f"任务模式分析: {patterns}")
    
    # 识别弱模式
    weak_patterns = identify_weak_patterns()
    print(f"弱模式: {weak_patterns}")
    
    # 更新知识图谱
    update_result = update_knowledge_graph()
    print(f"知识图谱更新: {update_result}")
    
    # 优化知识图谱
    optimize_result = optimize_knowledge_graph()
    print(f"知识图谱优化: {optimize_result}")
    
    # 获取学习状态
    status = get_learning_status()
    print(f"学习状态: {status}")

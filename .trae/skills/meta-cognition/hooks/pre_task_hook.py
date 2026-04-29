# -*- coding: utf-8 -*-
"""
Meta-Cognition Pre-Task Hook (前置钩子)

触发时机：执行任何任务前自动调用
功能：记录任务调度前的状态，分析任务类型，决定调度模式

触发机制：高频词匹配为主，复杂度判断为辅
强制触发：90%以上的任务必须进入博弈工作流

强制触发逻辑与优先级：
1. 第一优先级：关键词匹配。一旦发现关键词，立即触发对应模式，无需任何进一步思考
2. 第二优先级：复杂度兜底。未匹配关键词但满足复杂度条件，默认触发模式三
3. 唯一例外：极简的单一事实查询，可跳过博弈，使用常规单一路由

行为准则：在分析任务时，不是在"判断"是否需要博弈，而是在"寻找"触发博弈的关键词或复杂度证据
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from .utils import (
    load_log, save_log, generate_session_id,
    get_current_timestamp, filter_sensitive_info
)
from ..config.config import CONFIG


def is_complex_task(task_description: str) -> bool:
    """
    判断任务是否为复杂任务

    复杂度判断条件（满足任一即触发模式三）：
    - 任务描述包含超过2个独立分句
    - 包含技术名词、文件名、URL、代码片段
    - 总字符数超过15字
    """
    if not task_description:
        return False

    complexity_config = CONFIG.complexity

    if len(task_description) > complexity_config.max_simple_length:
        return True

    clause_separators = ['。', '？', '！', ';', '；']
    clause_count = sum(1 for sep in clause_separators if sep in task_description)
    if clause_count >= complexity_config.max_simple_clauses:
        return True

    task_lower = task_description.lower()
    for indicator in complexity_config.technical_indicators:
        if indicator.lower() in task_lower:
            return True

    return False


def query_kg(concept: str) -> list:
    """
    知识图谱查询函数
    
    Args:
        concept: 概念或词语
    
    Returns:
        关联的核心博弈概念列表
    """
    kg_relations = CONFIG.knowledge_graph.kg_relations
    # 直接匹配
    if concept in kg_relations:
        return kg_relations[concept]
    # 部分匹配
    for key, concepts in kg_relations.items():
        if key in concept:
            return concepts
    # 核心概念自身
    if concept in CONFIG.knowledge_graph.core_concepts:
        return [concept]
    return []


def detect_task_mode(task_description: str) -> str:
    """
    检测任务类型，决定使用博弈模式还是常规模式

    触发机制：
    - 第一优先级：知识图谱查询
    - 第二优先级：关键词匹配
    - 第三优先级：复杂度兜底
    - 唯一例外：极简单一事实查询

    模式判断：
    - 模式一：辩论、对比、风险、挑战等关键词
    - 模式二：优化、改进、重构、检查等关键词
    - 模式三：设计、架构、开发、创建或复杂度触发
    """
    if not CONFIG.enable_game_theory:
        return "normal"

    # 1. 知识图谱查询
    task_lower = task_description.lower()
    concepts = set()
    
    # 简单分词
    words = task_lower.split()
    for word in words:
        # 清理标点
        word = ''.join(c for c in word if c.isalnum() or c in '中文')
        if word:
            kg_results = query_kg(word)
            concepts.update(kg_results)
    
    # 概念优先级判断
    if concepts:
        priority = CONFIG.knowledge_graph.concept_priority
        for concept in priority:
            if concept in concepts:
                if concept == "辩论":
                    return "game_theory_mode1"
                elif concept == "优化":
                    return "game_theory_mode2"
                elif concept == "设计":
                    return "game_theory_mode3"
    
    # 2. 关键词匹配
    keywords = CONFIG.keywords
    if any(kw in task_lower for kw in keywords.mode1_keywords):
        return "game_theory_mode1"
    elif any(kw in task_lower for kw in keywords.mode2_keywords):
        return "game_theory_mode2"
    elif any(kw in task_lower for kw in keywords.mode3_keywords):
        return "game_theory_mode3"
    
    # 3. 复杂度兜底
    elif is_complex_task(task_description):
        return "game_theory_mode3"
    else:
        return "normal"


def get_trigger_reason(task_description: str, task_mode: str) -> str:
    """获取触发原因"""
    if task_mode == "normal":
        return "极简单一事实查询"

    task_lower = task_description.lower()
    keywords = CONFIG.keywords

    if task_mode == "game_theory_mode1":
        matched = [kw for kw in keywords.mode1_keywords if kw in task_lower]
        return f"检测到辩论/对比类关键词: {matched[0] if matched else '未知'}"
    elif task_mode == "game_theory_mode2":
        matched = [kw for kw in keywords.mode2_keywords if kw in task_lower]
        return f"检测到优化/改进类关键词: {matched[0] if matched else '未知'}"
    elif task_mode == "game_theory_mode3":
        matched = [kw for kw in keywords.mode3_keywords if kw in task_lower]
        if matched:
            return f"检测到设计/架构/实现类关键词: {matched[0]}"
        else:
            return "复杂度兜底触发（无关键词匹配但满足复杂度条件）"
    return "未知"


def get_scheduling_decision(task_mode: str, task_description: str) -> Dict[str, Any]:
    """
    根据任务模式获取调度决策

    Args:
        task_mode: 检测到的任务模式
        task_description: 任务描述

    Returns:
        包含调度决策信息的字典
    """
    decisions = {
        "game_theory_mode1": {
            "mode": "辩论模式（串行模拟并行）",
            "mode_number": "一",
            "description": "通过视角A和视角B的对立碰撞，产出更全面的解决方案",
            "workflow": CONFIG.workflows.mode1_workflow,
            "steps": [
                {"step": 1, "name": "识别对立视角", "description": "根据任务，确定需要哪两种对立视角"},
                {"step": 2, "name": "调用视角A智能体", "description": "调用创新探索视角智能体，给予完整原始任务"},
                {"step": 3, "name": "调用视角B智能体", "description": "请针对视角A结论，从风险控制视角提出反对意见"},
                {"step": 4, "name": "最终裁决", "description": "综合分析，输出包含共识、核心分歧和综合建议的报告"}
            ],
            "recommended_agents": ["society_of_mind_agent", "editor_agent"],
            "trigger_reason": get_trigger_reason(task_description, "game_theory_mode1")
        },
        "game_theory_mode2": {
            "mode": "降维打击模式（流水线博弈）",
            "mode_number": "二",
            "description": "通过生成、挑剔、融合三阶段，不断优化产出物的质量",
            "workflow": CONFIG.workflows.mode2_workflow,
            "steps": [
                {"step": 1, "name": "生成阶段", "description": "调用创意生成智能体，产出初始方案", "output_label": "方案初稿"},
                {"step": 2, "name": "挑剔阶段", "description": "调用逻辑审查智能体，找出所有潜在问题和漏洞", "output_label": "审阅意见"},
                {"step": 3, "name": "融合阶段", "description": "调用综合重写智能体，输出融合优化的最终方案", "output_label": "最终方案"},
                {"step": 4, "name": "最终交付", "description": "将融合阶段智能体的输出作为本次任务的最终结果"}
            ],
            "recommended_agents": ["code_executor_agent", "editor_agent", "writer_agent"],
            "trigger_reason": get_trigger_reason(task_description, "game_theory_mode2")
        },
        "game_theory_mode3": {
            "mode": "深度设计模式（三段式协同）",
            "mode_number": "三",
            "description": "通过蓝图设计、可行性挑战、融合实现，确保设计的可落地性",
            "workflow": CONFIG.workflows.mode3_workflow,
            "steps": [
                {"step": 1, "name": "蓝图设计阶段", "description": "心智社会智能体进行顶层架构与蓝图设计（不超过800字）", "agent": "society_of_mind_agent", "output_label": "design_blueprint"},
                {"step": 2, "name": "可行性挑战阶段", "description": "代码执行智能体评审设计蓝图的实现复杂性、技术风险、性能瓶颈（前3个最关键问题）", "agent": "code_executor_agent", "output_label": "feasibility_report"},
                {"step": 3, "name": "融合实现阶段", "description": "编辑器智能体综合蓝图和风险评估，输出可落地的最终实施方案（约1000字）", "agent": "editor_agent", "output_label": "最终方案"}
            ],
            "recommended_agents": ["society_of_mind_agent", "code_executor_agent", "editor_agent"],
            "trigger_reason": get_trigger_reason(task_description, "game_theory_mode3")
        },
        "normal": {
            "mode": "常规单一路由",
            "mode_number": "常规",
            "description": "直接匹配最合适的专业智能体进行处理",
            "steps": [
                {"step": 1, "name": "任务分析", "description": "解析用户任务，识别核心需求和专业领域"},
                {"step": 2, "name": "智能体匹配", "description": "基于任务需求匹配最合适的智能体"},
                {"step": 3, "name": "任务执行", "description": "分配任务并监控执行进度"}
            ],
            "recommended_agents": ["assistant_agent", "code_executor_agent"],
            "trigger_reason": get_trigger_reason(task_description, "normal")
        }
    }

    return decisions.get(task_mode, decisions["normal"])


def format_workflow_output(decision: Dict[str, Any]) -> str:
    """格式化工作流输出，用于显示给用户"""
    output = []
    output.append(f"\n{'='*60}")
    output.append(f"【{decision['mode']}】")
    output.append(f"{'='*60}")
    output.append(f"\n📋 模式说明: {decision['description']}")
    output.append(f"\n🔍 触发原因: {decision.get('trigger_reason', '未知')}")
    output.append(f"\n👥 推荐智能体: {', '.join(decision.get('recommended_agents', []))}")

    if 'steps' in decision:
        output.append(f"\n📝 执行步骤:")
        for step in decision['steps']:
            if isinstance(step, dict):
                output.append(f"   {step['step']}. {step['name']}: {step['description']}")
                if 'output_label' in step:
                    output.append(f"      → 产出标记: {step['output_label']}")
                if 'agent' in step:
                    output.append(f"      → 调用智能体: {step['agent']}")
            else:
                output.append(f"   • {step}")

    output.append(f"\n{'='*60}\n")
    return "\n".join(output)


def pre_task_hook(task_description: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    前置钩子主函数

    Args:
        task_description: 任务描述
        context: 可选的上下文信息

    Returns:
        包含调度决策信息的字典
    """
    try:
        # 检查自我更新
        try:
            from ..self_update import check_and_update
            check_and_update()
        except ImportError:
            pass

        # 检查并分析日志
        try:
            from ..auto_analyzer import check_and_analyze
            check_and_analyze()
        except ImportError:
            pass

        # 模式识别和调度优化
        task_type = "normal"
        scheduling_advice = {}
        try:
            from ..pattern_recognition import recognize_task_type, optimize_scheduling
            task_type, _ = recognize_task_type(task_description or "")
            scheduling_advice = optimize_scheduling(task_description or "")
        except ImportError:
            pass

        # 基于调度建议调整任务模式
        task_mode = detect_task_mode(task_description or "")
        if scheduling_advice and scheduling_advice.get("adjusted_mode"):
            task_mode = scheduling_advice["adjusted_mode"]

        session_id = generate_session_id()
        timestamp = get_current_timestamp()

        filtered_task = filter_sensitive_info(task_description or "")

        pre_record = {
            "session_id": session_id,
            "phase": "pre_task",
            "timestamp": timestamp,
            "task_description": filtered_task,
            "original_task": task_description if task_description == filtered_task else "[FILTERED]",
            "detected_mode": task_mode,
            "task_type": task_type,
            "scheduling_advice": scheduling_advice,
            "context": context or {}
        }

        decision = get_scheduling_decision(task_mode, task_description or "")
        pre_record["scheduling_decision"] = decision

        log_data = load_log()
        log_data["sessions"].append(pre_record)
        log_data["current_session"] = session_id
        save_log(log_data)

        return {
            "session_id": session_id,
            "mode": task_mode,
            "task_type": task_type,
            "scheduling_advice": scheduling_advice,
            "mode_info": {
                "mode": decision['mode'],
                "mode_number": decision.get('mode_number', ''),
                "description": decision['description']
            },
            "decision": decision,
            "timestamp": timestamp,
            "workflow_output": format_workflow_output(decision)
        }
    except Exception as e:
        print(f"[ERROR] 前置钩子执行失败: {e}")
        session_id = generate_session_id()
        fallback_decision = get_scheduling_decision("game_theory_mode3", "")
        return {
            "session_id": session_id,
            "mode": "game_theory_mode3",
            "task_type": "normal",
            "scheduling_advice": {},
            "mode_info": {
                "mode": fallback_decision['mode'],
                "mode_number": fallback_decision.get('mode_number', ''),
                "description": fallback_decision['description']
            },
            "decision": fallback_decision,
            "timestamp": get_current_timestamp(),
            "workflow_output": format_workflow_output(fallback_decision)
        }


def get_task_recommendations(task_description: str) -> Dict[str, Any]:
    """
    获取任务相关的智能体推荐和建议

    Args:
        task_description: 任务描述

    Returns:
        包含推荐信息的字典
    """
    task_mode = detect_task_mode(task_description)
    decision = get_scheduling_decision(task_mode, task_description)

    return {
        "mode": task_mode,
        "mode_info": {
            "mode": decision['mode'],
            "mode_number": decision.get('mode_number', ''),
            "description": decision['description']
        },
        "recommended_agents": decision.get("recommended_agents", []),
        "scheduling_steps": decision.get("steps", []),
        "mode_description": decision.get("description", ""),
        "workflow_output": format_workflow_output(decision)
    }


if __name__ == "__main__":
    test_cases = [
        ("请帮我优化这段代码，提升性能", "game_theory_mode2"),
        ("请对比敏捷开发和瀑布模型的优缺点", "game_theory_mode1"),
        ("帮我设计一个用户认证系统", "game_theory_mode3"),
        ("帮我写一个用户登录功能", "game_theory_mode3"),
        ("1+1等于几？", "normal"),
        ("现在几点了", "normal"),
        ("这个代码报错了，帮我修复一下", "game_theory_mode2"),
        ("看看这个方案有什么问题", "game_theory_mode2"),
    ]

    print("=" * 60)
    print("Pre-Task Hook 测试 - 完整博弈逻辑验证")
    print("=" * 60)

    for i, (task, expected_mode) in enumerate(test_cases, 1):
        print(f"\n【测试 {i}】任务: {task}")
        result = pre_task_hook(task)
        status = "✓" if result["mode"] == expected_mode else "✗"
        print(f"  状态: {status}")
        print(f"  预期: {expected_mode} -> 实际: {result['mode']}")
        print(f"  触发原因: {result['decision'].get('trigger_reason', 'N/A')}")
        print(result['workflow_output'])

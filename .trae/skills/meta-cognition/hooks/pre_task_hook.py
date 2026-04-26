"""
Meta-Cognition Pre-Task Hook (读取钩子)

触发时机：执行任何任务前自动调用
功能：记录任务调度前的状态，分析任务类型，决定调度模式
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

LOG_FILE = Path(__file__).parent.parent / "logs" / "meta_cognition.json"


def load_log() -> Dict[str, Any]:
    """加载现有日志，若不存在则创建空结构"""
    if LOG_FILE.exists():
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"sessions": [], "current_session": None}


def save_log(data: Dict[str, Any]) -> None:
    """保存日志到文件"""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def detect_task_mode(task_description: str) -> str:
    """
    检测任务类型，决定使用博弈模式还是常规模式

    触发关键词：
    - 博弈模式1：辩论、对比、优缺点、风险评估、多角度分析、正反两面
    - 博弈模式2：优化、改进、重构、提升质量、润色、无懈可击
    """
    task_lower = task_description.lower()

    mode1_keywords = ["辩论", "对比", "优缺点", "风险评估", "多角度分析", "正反两面"]
    mode2_keywords = ["优化", "改进", "重构", "提升质量", "润色", "无懈可击"]

    if any(kw in task_lower for kw in mode1_keywords):
        return "game_theory_mode1"
    elif any(kw in task_lower for kw in mode2_keywords):
        return "game_theory_mode2"
    else:
        return "normal"


def pre_task_hook(task_description: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    前置钩子主函数

    Args:
        task_description: 任务描述
        context: 可选的上下文信息

    Returns:
        包含调度决策信息的字典
    """

    task_mode = detect_task_mode(task_description)

    session_id = str(uuid.uuid4())

    pre_record = {
        "session_id": session_id,
        "phase": "pre_task",
        "timestamp": datetime.now().isoformat(),
        "task_description": task_description,
        "detected_mode": task_mode,
        "context": context or {}
    }

    if task_mode.startswith("game_theory"):
        if task_mode == "game_theory_mode1":
            pre_record["scheduling_decision"] = {
                "mode": "辩论模式（串行模拟并行）",
                "steps": ["视角A智能体", "视角B智能体", "调度员裁决"],
                "trigger_keyword": "检测到辩论/对比类关键词"
            }
        else:
            pre_record["scheduling_decision"] = {
                "mode": "降维打击模式（流水线博弈）",
                "steps": ["生成阶段", "挑剔阶段", "融合阶段"],
                "trigger_keyword": "检测到优化/改进类关键词"
            }
    else:
        pre_record["scheduling_decision"] = {
            "mode": "常规单一路由",
            "steps": ["任务分析", "智能体匹配", "任务执行"],
            "trigger_keyword": "无博弈触发词"
        }

    log_data = load_log()
    log_data["sessions"].append(pre_record)
    log_data["current_session"] = session_id
    save_log(log_data)

    return {
        "session_id": session_id,
        "mode": task_mode,
        "decision": pre_record["scheduling_decision"]
    }


if __name__ == "__main__":
    test_result = pre_task_hook("请帮我优化这段代码，提升其性能")
    print("=== Pre-Task Hook 测试 ===")
    print(json.dumps(test_result, ensure_ascii=False, indent=2))

    test_result2 = pre_task_hook("请对比一下敏捷开发和瀑布模型的优缺点")
    print("\n=== Pre-Task Hook 测试2（辩论模式）===")
    print(json.dumps(test_result2, ensure_ascii=False, indent=2))

    test_result3 = pre_task_hook("帮我写一个用户登录功能")
    print("\n=== Pre-Task Hook 测试3（常规模式）===")
    print(json.dumps(test_result3, ensure_ascii=False, indent=2))
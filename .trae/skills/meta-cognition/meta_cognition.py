# -*- coding: utf-8 -*-
"""
Meta-Cognition Skill - 智能体团队调度系统
🚀 v3.0 内生重构版！

重构目标：
1. 将所有分散的脚本能力整合到一个统一的插件架构中
2. 保持所有原有功能不衰减，特别是自动触发功能
3. 实现完全内生的插件，无需外部脚本依赖

架构设计：
┌──────────────────────────────────────────────────────────┐
│                    MetaCognition (核心类)                 │
├──────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   Config     │  │   LogManager │  │   Trigger    │   │
│  │   (配置管理) │  │   (日志管理) │  │   (触发引擎) │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
│         │                 │                  │            │
│         ▼                 ▼                  ▼            │
│  ┌──────────────────────────────────────────────────┐   │
│  │               Core Engine                        │   │
│  │  - 博弈模式检测   - 智能体推荐   - 工作流编排    │   │
│  └──────────────────────────────────────────────────┘   │
│         │                 │                  │            │
│         ▼                 ▼                  ▼            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  ActiveLear- │  │ PatternRecog-│  │  SelfUpdate  │   │
│  │  ning        │  │ nition       │  │              │   │
│  │  (主动学习)  │  │  (模式识别)  │  │  (自我更新)  │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└──────────────────────────────────────────────────────────┘
"""

import sys
import threading
import time
import json
import os
import re
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum

__version__ = "3.0.0"

# ============================================
# 1. 配置类（整合 config/config.py）
# ============================================

class TriggerType(Enum):
    POLLING = "polling"
    EVENT = "event"
    FILE_SYSTEM = "file_system"
    API = "api"


@dataclass
class GameTheoryKeywords:
    mode1_keywords: list = field(default_factory=lambda: [
        "对比", "辩论", "争论", "分歧", "正反", "利弊", "优劣", "好坏",
        "哪个更好", "该不该", "要不要", "行不行", "是不是", "值不值",
        "风险", "挑战", "问题", "难点", "怎么办", "如何选择", "怎么看",
        "什么观点", "你的看法", "辩论", "对比", "优缺点", "风险评估",
        "多角度分析", "正反两面", "看法", "观点", "不同意见", "分析一下",
        "评估", "分析", "比较", "权衡", "评判", "考量", "审视", "剖析",
        "解析", "解读", "讨论", "商议", "商量", "切磋", "论证", "辩论一下",
        "比一比", "区别", "差异", "差别", "不同", "哪个更优"
    ])
    mode2_keywords: list = field(default_factory=lambda: [
        "优化", "改进", "提升", "增强", "完善", "修改", "调整", "重构",
        "重写", "重做", "整理", "清理", "简化", "加速", "修复", "调试",
        "解决", "处理", "看看", "检查", "审阅", "评审", "评估", "测一下",
        "跑一下", "试一下", "瞅瞅", "瞧一瞧", "帮我看下", "这个有问题",
        "报错了", "不行啊", "不够好", "优化一下", "改进一下", "提升一下",
        "增强一下", "完善一下", "检查一下", "审阅一下", "修改一下", "重构一下",
        "润色一下", "优化代码", "改进代码", "提升性能", "增强功能", "完善功能",
        "检查代码", "审阅代码", "修改代码", "重构代码", "优化方案", "改进方案",
        "提升方案", "增强方案", "完善方案", "检查方案", "审阅方案", "修改方案",
        "重构方案", "优化流程", "改进流程", "提升流程", "增强流程", "完善流程",
        "检查流程", "审阅流程", "修改流程", "重构流程", "有问题", "错误"
    ])
    mode3_keywords: list = field(default_factory=lambda: [
        "设计", "架构", "规划", "方案", "实现", "开发", "编写", "创建",
        "搭建", "构建", "制作", "生成", "输出", "写一个", "做一个", "搞一个",
        "弄一个", "整一个", "来一个", "搞一下", "弄一下", "整一下", "玩一下",
        "搞点", "弄点", "想做个", "需要个", "要个", "有个需求", "系统工程",
        "设计一个", "架构一个", "实现一个", "搭建一个", "创建一个", "开发一个",
        "构建一个", "写", "做", "设计系统", "架构系统", "实现系统", "搭建系统",
        "创建系统", "开发系统", "构建系统", "设计功能", "架构功能", "实现功能",
        "搭建功能", "创建功能", "开发功能", "构建功能", "设计项目", "架构项目",
        "实现项目", "搭建项目", "创建项目", "开发项目", "构建项目", "设计应用",
        "架构应用", "实现应用", "搭建应用", "创建应用", "开发应用", "构建应用",
        "方案设计", "系统设计", "架构设计", "方案规划", "项目构建", "应用开发",
        "产品设计", "技术方案", "解决方案", "实现方案", "设计方案", "架构方案"
    ])


@dataclass
class KnowledgeGraphConfig:
    core_concepts: list = field(default_factory=lambda: ["优化", "设计", "辩论"])
    concept_priority: list = field(default_factory=lambda: ["辩论", "优化", "设计"])
    kg_relations: dict = field(default_factory=lambda: {
        "加速": ["优化"], "架构": ["设计"], "优缺点": ["辩论"],
        "性能": ["优化"], "结构": ["设计"], "对比": ["辩论"],
        "改进": ["优化"], "开发": ["设计"], "风险": ["辩论"],
        "提升": ["优化"], "创建": ["设计"], "争论": ["辩论"],
        "修复": ["优化"], "实现": ["设计"], "利弊": ["辩论"],
        "调试": ["优化"], "规划": ["设计"], "分歧": ["辩论"]
    })


@dataclass
class ComplexityConfig:
    max_simple_length: int = 15
    max_simple_clauses: int = 2
    technical_indicators: list = field(default_factory=lambda: [
        ".py", ".js", ".java", ".cpp", ".go", ".rs", ".ts", ".tsx", ".jsx",
        "http://", "https://", "api", "API", "url", "URL",
        "def ", "class ", "function", "interface", "enum", "struct",
        "sql", "query", "database", "table", "column",
        "config", "settings", "environment", "env", ".env",
        "import", "require", "include", "using", "from ",
        "git", "github", "docker", "kubernetes", "k8s",
        "json", "yaml", "xml", "toml", "ini", "config"
    ])


@dataclass
class GameTheoryWorkflows:
    mode1_workflow: list = field(default_factory=lambda: [
        "识别对立视角", "调用视角A智能体（创新探索）",
        "调用视角B智能体（风险控制）", "综合裁决"
    ])
    mode2_workflow: list = field(default_factory=lambda: [
        "生成阶段（创意生成智能体）", "挑剔阶段（逻辑审查智能体）",
        "融合阶段（综合重写智能体）"
    ])
    mode3_workflow: list = field(default_factory=lambda: [
        "蓝图设计阶段（心智社会智能体）",
        "可行性挑战阶段（代码执行智能体）",
        "融合实现阶段（编辑器智能体）"
    ])


@dataclass
class LogConfig:
    max_size_mb: float = 10.0
    max_age_days: int = 30
    enable_backup: bool = True
    enable_rotation: bool = True
    log_dir: str = "logs"
    log_file: str = "meta_cognition.json"


@dataclass
class TriggerConfig:
    polling_enabled: bool = True
    polling_interval: float = 1.0
    event_enabled: bool = True
    event_interval: float = 0.5
    filesystem_enabled: bool = False
    filesystem_interval: float = 5.0
    api_enabled: bool = False
    api_interval: float = 0.1


@dataclass
class AgentConfig:
    available_agents: list = field(default_factory=lambda: [
        "assistant_agent", "user_proxy_agent", "code_executor_agent",
        "message_filter_agent", "society_of_mind_agent", "base_agent",
        "closure_agent", "routed_agent", "tool_agent", "chess_agent",
        "fastapi_agent", "streamlit_agent", "graphrag_agent", "dspy_agent",
        "xlang_agent", "semantic_router_agent", "editor_agent", "writer_agent",
        "teachable_agent", "grpc_agent"
    ])
    default_agents: list = field(default_factory=lambda: [
        "assistant_agent", "code_executor_agent"
    ])


@dataclass
class MetaCognitionConfig:
    enable_game_theory: bool = True
    enable_statistics: bool = True
    enable_monitoring: bool = False
    enable_self_update: bool = True
    enable_active_learning: bool = True
    response_preview_length: int = 200
    
    keywords: GameTheoryKeywords = field(default_factory=GameTheoryKeywords)
    complexity: ComplexityConfig = field(default_factory=ComplexityConfig)
    workflows: GameTheoryWorkflows = field(default_factory=GameTheoryWorkflows)
    knowledge_graph: KnowledgeGraphConfig = field(default_factory=KnowledgeGraphConfig)
    log: LogConfig = field(default_factory=LogConfig)
    trigger: TriggerConfig = field(default_factory=TriggerConfig)
    agents: AgentConfig = field(default_factory=AgentConfig)


# ============================================
# 2. 日志管理类（整合 hooks/utils.py）
# ============================================

class LogManager:
    def __init__(self, config: LogConfig):
        self._config = config
        self._log_path = Path(config.log_dir) / config.log_file
        self._log_path.parent.mkdir(parents=True, exist_ok=True)
        
    def _load_log(self) -> Dict[str, Any]:
        """加载日志数据"""
        try:
            if self._log_path.exists():
                with open(self._log_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {"sessions": [], "current_session": None, "task_statistics": {}}
    
    def _save_log(self, data: Dict[str, Any]):
        """保存日志数据"""
        try:
            with open(self._log_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[LogManager] 保存日志失败: {e}")
    
    def generate_session_id(self) -> str:
        """生成会话ID"""
        import uuid
        return str(uuid.uuid4())[:8] + "-" + str(int(time.time()))
    
    def get_current_timestamp(self) -> str:
        """获取当前时间戳"""
        return time.strftime("%Y-%m-%dT%H:%M:%S")
    
    def filter_sensitive_info(self, text: str) -> str:
        """过滤敏感信息"""
        patterns = [
            (r'api[_-]?key["\']?\s*[:=]\s*["\']?[\w\-]{20,}["\']?', '[API_KEY]'),
            (r'password["\']?\s*[:=]\s*["\']?[^\s"\']{6,}["\']?', '[PASSWORD]'),
            (r'token["\']?\s*[:=]\s*["\']?[\w\-]{20,}["\']?', '[TOKEN]'),
            (r'secret["\']?\s*[:=]\s*["\']?[\w\-]{20,}["\']?', '[SECRET]'),
        ]
        for pattern, replacement in patterns:
            text = re.sub(pattern, replacement, text)
        return text
    
    def add_session(self, session_data: Dict[str, Any]):
        """添加会话记录"""
        log_data = self._load_log()
        log_data["sessions"].append(session_data)
        log_data["current_session"] = session_data.get("session_id")
        self._update_statistics(log_data)
        self._save_log(log_data)
    
    def update_session(self, session_id: str, updates: Dict[str, Any]):
        """更新会话记录"""
        log_data = self._load_log()
        for session in log_data["sessions"]:
            if session["session_id"] == session_id:
                session.update(updates)
                break
        self._update_statistics(log_data)
        self._save_log(log_data)
    
    def _update_statistics(self, log_data: Dict[str, Any]):
        """更新统计信息"""
        sessions = log_data.get("sessions", [])
        completed = [s for s in sessions if s.get("phase") == "completed"]
        success = [s for s in completed if s.get("success")]
        
        log_data["task_statistics"] = {
            "total": len(sessions),
            "success": len(success),
            "failure": len(completed) - len(success),
            "last_updated": self.get_current_timestamp()
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self._load_log().get("task_statistics", {})
    
    def get_recent_sessions(self, limit: int = 10) -> list:
        """获取最近会话"""
        log_data = self._load_log()
        sessions = log_data.get("sessions", [])
        return sessions[-limit:]
    
    def get_session_by_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取会话"""
        log_data = self._load_log()
        for session in log_data.get("sessions", []):
            if session["session_id"] == session_id:
                return session
        return None


# ============================================
# 3. 核心引擎类（整合 hooks/pre_task_hook.py 等）
# ============================================

class MetaCognitionEngine:
    """核心引擎 - 博弈模式检测、智能体推荐、工作流编排"""
    
    def __init__(self, config: MetaCognitionConfig, log_manager: LogManager):
        self._config = config
        self._log_manager = log_manager
    
    def _is_complex_task(self, task_description: str) -> bool:
        """判断任务是否复杂"""
        if not task_description:
            return False
        
        if len(task_description) > self._config.complexity.max_simple_length:
            return True
        
        clause_separators = ['。', '？', '！', ';', '；']
        clause_count = sum(1 for sep in clause_separators if sep in task_description)
        if clause_count >= self._config.complexity.max_simple_clauses:
            return True
        
        task_lower = task_description.lower()
        for indicator in self._config.complexity.technical_indicators:
            if indicator.lower() in task_lower:
                return True
        
        return False
    
    def _query_knowledge_graph(self, concept: str) -> list:
        """查询知识图谱"""
        kg_relations = self._config.knowledge_graph.kg_relations
        if concept in kg_relations:
            return kg_relations[concept]
        for key, concepts in kg_relations.items():
            if key in concept:
                return concepts
        if concept in self._config.knowledge_graph.core_concepts:
            return [concept]
        return []
    
    def detect_task_mode(self, task_description: str) -> str:
        """检测任务模式"""
        if not self._config.enable_game_theory:
            return "normal"
        
        task_lower = task_description.lower()
        concepts = set()
        
        words = task_lower.split()
        for word in words:
            word = ''.join(c for c in word if c.isalnum() or '\u4e00' <= c <= '\u9fff')
            if word:
                kg_results = self._query_knowledge_graph(word)
                concepts.update(kg_results)
        
        if concepts:
            priority = self._config.knowledge_graph.concept_priority
            for concept in priority:
                if concept in concepts:
                    if concept == "辩论":
                        return "game_theory_mode1"
                    elif concept == "优化":
                        return "game_theory_mode2"
                    elif concept == "设计":
                        return "game_theory_mode3"
        
        keywords = self._config.keywords
        if any(kw in task_lower for kw in keywords.mode1_keywords):
            return "game_theory_mode1"
        elif any(kw in task_lower for kw in keywords.mode2_keywords):
            return "game_theory_mode2"
        elif any(kw in task_lower for kw in keywords.mode3_keywords):
            return "game_theory_mode3"
        elif self._is_complex_task(task_description):
            return "game_theory_mode3"
        
        return "normal"
    
    def _get_trigger_reason(self, task_description: str, task_mode: str) -> str:
        """获取触发原因"""
        if task_mode == "normal":
            return "极简单一事实查询"
        
        task_lower = task_description.lower()
        keywords = self._config.keywords
        
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
                return "复杂度兜底触发"
        return "未知"
    
    def get_scheduling_decision(self, task_mode: str, task_description: str) -> Dict[str, Any]:
        """获取调度决策"""
        decisions = {
            "game_theory_mode1": {
                "mode": "辩论模式（串行模拟并行）",
                "mode_number": "一",
                "description": "通过视角A和视角B的对立碰撞，产出更全面的解决方案",
                "steps": [
                    {"step": 1, "name": "识别对立视角", "description": "根据任务，确定需要哪两种对立视角"},
                    {"step": 2, "name": "调用视角A智能体", "description": "调用创新探索视角智能体，给予完整原始任务"},
                    {"step": 3, "name": "调用视角B智能体", "description": "请针对视角A结论，从风险控制视角提出反对意见"},
                    {"step": 4, "name": "最终裁决", "description": "综合分析，输出包含共识、核心分歧和综合建议的报告"}
                ],
                "recommended_agents": ["society_of_mind_agent", "editor_agent"],
                "trigger_reason": self._get_trigger_reason(task_description, "game_theory_mode1")
            },
            "game_theory_mode2": {
                "mode": "降维打击模式（流水线博弈）",
                "mode_number": "二",
                "description": "通过生成、挑剔、融合三阶段，不断优化产出物的质量",
                "steps": [
                    {"step": 1, "name": "生成阶段", "description": "调用创意生成智能体，产出初始方案", "output_label": "方案初稿"},
                    {"step": 2, "name": "挑剔阶段", "description": "调用逻辑审查智能体，找出所有潜在问题和漏洞", "output_label": "审阅意见"},
                    {"step": 3, "name": "融合阶段", "description": "调用综合重写智能体，输出融合优化的最终方案", "output_label": "最终方案"},
                    {"step": 4, "name": "最终交付", "description": "将融合阶段智能体的输出作为本次任务的最终结果"}
                ],
                "recommended_agents": ["code_executor_agent", "editor_agent", "writer_agent"],
                "trigger_reason": self._get_trigger_reason(task_description, "game_theory_mode2")
            },
            "game_theory_mode3": {
                "mode": "深度设计模式（三段式协同）",
                "mode_number": "三",
                "description": "通过蓝图设计、可行性挑战、融合实现，确保设计的可落地性",
                "steps": [
                    {"step": 1, "name": "蓝图设计阶段", "description": "心智社会智能体进行顶层架构与蓝图设计（不超过800字）", "agent": "society_of_mind_agent", "output_label": "design_blueprint"},
                    {"step": 2, "name": "可行性挑战阶段", "description": "代码执行智能体评审设计蓝图的实现复杂性、技术风险、性能瓶颈（前3个最关键问题）", "agent": "code_executor_agent", "output_label": "feasibility_report"},
                    {"step": 3, "name": "融合实现阶段", "description": "编辑器智能体综合蓝图和风险评估，输出可落地的最终实施方案（约1000字）", "agent": "editor_agent", "output_label": "最终方案"}
                ],
                "recommended_agents": ["society_of_mind_agent", "code_executor_agent", "editor_agent"],
                "trigger_reason": self._get_trigger_reason(task_description, "game_theory_mode3")
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
                "trigger_reason": self._get_trigger_reason(task_description, "normal")
            }
        }
        return decisions.get(task_mode, decisions["normal"])
    
    def format_workflow_output(self, decision: Dict[str, Any]) -> str:
        """格式化工作流输出"""
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


# ============================================
# 4. 模式识别模块（整合 pattern_recognition.py）
# ============================================

class PatternRecognition:
    """模式识别模块"""
    
    def __init__(self, engine: MetaCognitionEngine, log_manager: LogManager):
        self._engine = engine
        self._log_manager = log_manager
        self._task_types = {
            "optimization": {"keywords": ["优化", "提升", "改进", "加速", "性能", "效率", "重构"], "description": "优化类任务", "recommended_mode": "game_theory_mode2"},
            "design": {"keywords": ["设计", "架构", "创建", "开发", "构建", "规划"], "description": "设计类任务", "recommended_mode": "game_theory_mode3"},
            "debate": {"keywords": ["对比", "优缺点", "利弊", "讨论", "分析", "评估"], "description": "辩论类任务", "recommended_mode": "game_theory_mode1"},
            "debug": {"keywords": ["修复", "调试", "错误", "问题", "解决", "bug"], "description": "调试类任务", "recommended_mode": "game_theory_mode2"},
            "research": {"keywords": ["研究", "调研", "分析", "了解", "学习", "探索"], "description": "研究类任务", "recommended_mode": "game_theory_mode3"},
            "normal": {"keywords": [], "description": "常规任务", "recommended_mode": "normal"}
        }
    
    def recognize_task_type(self, task_description: str) -> Tuple[str, float]:
        """识别任务类型"""
        from collections import defaultdict
        
        task_lower = task_description.lower()
        scores = defaultdict(float)
        
        for task_type, config in self._task_types.items():
            if task_type == "normal":
                continue
            for keyword in config["keywords"]:
                if keyword in task_lower:
                    scores[task_type] += 1.0
        
        if not scores:
            return "normal", 1.0
        
        max_score = max(scores.values())
        best_type = max(scores, key=scores.get)
        total_score = sum(scores.values())
        confidence = max_score / total_score if total_score > 0 else 0.0
        
        return best_type, confidence
    
    def optimize_scheduling(self, task_description: str) -> Dict[str, Any]:
        """优化调度策略"""
        task_type, confidence = self.recognize_task_type(task_description)
        recommended_mode = self._task_types[task_type]["recommended_mode"]
        adjusted_mode = self._adjust_based_on_history(recommended_mode, task_type)
        
        return {
            "task_type": task_type,
            "confidence": confidence,
            "recommended_mode": recommended_mode,
            "adjusted_mode": adjusted_mode,
            "reason": f"任务类型识别为{task_type}，基于历史数据调整为{adjusted_mode}"
        }
    
    def _adjust_based_on_history(self, recommended_mode: str, task_type: str) -> str:
        """根据历史数据调整推荐模式"""
        log_data = self._log_manager._load_log()  # 直接访问内部方法
        sessions = log_data.get("sessions", [])
        
        from collections import defaultdict
        stats = defaultdict(lambda: {"total": 0, "success": 0})
        
        for session in sessions:
            if session.get("phase") == "completed":
                desc = session.get("task_description", "")
                mode = session.get("detected_mode", "normal")
                success = session.get("success", False)
                
                t_type, _ = self.recognize_task_type(desc)
                if t_type == task_type:
                    stats[mode]["total"] += 1
                    if success:
                        stats[mode]["success"] += 1
        
        if not stats:
            return recommended_mode
        
        best_mode = recommended_mode
        best_rate = 0.0
        
        for mode, data in stats.items():
            if data["total"] >= 2:
                rate = data["success"] / data["total"]
                if rate > best_rate:
                    best_rate = rate
                    best_mode = mode
        
        return best_mode


# ============================================
# 5. 主动学习模块（整合 active_learning.py）
# ============================================

class ActiveLearning:
    """主动学习模块"""
    
    def __init__(self, config: MetaCognitionConfig, log_manager: LogManager):
        self._config = config
        self._log_manager = log_manager
    
    def _extract_keywords(self, task_description: str) -> List[str]:
        """提取关键词"""
        cleaned = re.sub(r'[.,;!?()\[\]{}]', ' ', task_description)
        words = cleaned.split()
        common_words = set(["请", "帮", "我", "你", "的", "这", "那", "个", "是", "在", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去", "会", "着", "没有", "看", "好", "自己"])
        
        keywords = []
        for word in words:
            word = word.strip()
            if len(word) > 1 and word not in common_words:
                keywords.append(word)
        
        return keywords
    
    def update_knowledge_graph(self) -> Dict[str, Any]:
        """更新知识图谱"""
        from collections import defaultdict
        
        log_data = self._log_manager._load_log()
        sessions = log_data.get("sessions", [])
        
        pattern_keywords = defaultdict(lambda: defaultdict(int))
        
        for session in sessions:
            if session.get("phase") == "completed":
                task_desc = session.get("task_description", "")
                detected_mode = session.get("detected_mode", "normal")
                
                if task_desc and detected_mode != "normal":
                    keywords = self._extract_keywords(task_desc)
                    for keyword in keywords:
                        pattern_keywords[detected_mode][keyword] += 1
        
        mode_to_concept = {
            "game_theory_mode1": "辩论",
            "game_theory_mode2": "优化",
            "game_theory_mode3": "设计"
        }
        
        new_relations = {}
        for mode, keywords in pattern_keywords.items():
            concept = mode_to_concept.get(mode)
            if not concept:
                continue
            for keyword, count in keywords.items():
                if count > 1:
                    new_relations[keyword] = [concept]
        
        updated_kg = self._config.knowledge_graph.kg_relations.copy()
        updated_kg.update(new_relations)
        
        log_data["knowledge_graph_update"] = {
            "timestamp": self._log_manager.get_current_timestamp(),
            "updated_relations": new_relations,
            "total_relations": len(updated_kg)
        }
        self._log_manager._save_log(log_data)
        
        return {
            "updated": True,
            "new_relations": new_relations,
            "total_relations": len(updated_kg),
            "message": f"更新了{len(new_relations)}个知识图谱关系"
        }
    
    def optimize_knowledge_graph(self) -> Dict[str, Any]:
        """优化知识图谱"""
        from collections import defaultdict
        
        log_data = self._log_manager._load_log()
        sessions = log_data.get("sessions", [])
        
        pattern_keywords = defaultdict(lambda: defaultdict(int))
        
        for session in sessions:
            if session.get("phase") == "completed":
                task_desc = session.get("task_description", "")
                detected_mode = session.get("detected_mode", "normal")
                
                if task_desc and detected_mode != "normal":
                    keywords = self._extract_keywords(task_desc)
                    for keyword in keywords:
                        pattern_keywords[detected_mode][keyword] += 1
        
        mode_to_concept = {
            "game_theory_mode1": "辩论",
            "game_theory_mode2": "优化",
            "game_theory_mode3": "设计"
        }
        
        keyword_weights = defaultdict(int)
        for mode, keywords in pattern_keywords.items():
            for keyword, count in keywords.items():
                keyword_weights[keyword] += count
        
        threshold = 2
        important_keywords = {k: v for k, v in keyword_weights.items() if v >= threshold}
        
        new_relations = {}
        for mode, keywords in pattern_keywords.items():
            concept = mode_to_concept.get(mode)
            if not concept:
                continue
            for keyword, count in keywords.items():
                if keyword in important_keywords:
                    new_relations[keyword] = [concept]
        
        updated_kg = self._config.knowledge_graph.kg_relations.copy()
        updated_kg.update(new_relations)
        
        log_data["knowledge_graph_optimization"] = {
            "timestamp": self._log_manager.get_current_timestamp(),
            "important_keywords": important_keywords,
            "total_relations": len(updated_kg)
        }
        self._log_manager._save_log(log_data)
        
        return {
            "optimized": True,
            "important_keywords": important_keywords,
            "total_relations": len(updated_kg),
            "message": f"优化了知识图谱，保留了{len(important_keywords)}个重要关键词"
        }


# ============================================
# 6. 自动触发引擎（整合 auto_trigger.py）
# ============================================

class TriggerEngine:
    """自动触发引擎"""
    
    def __init__(self, config: MetaCognitionConfig):
        self._config = config
        self._trigger_threads: Dict[TriggerType, Optional[threading.Thread]] = {}
        self._should_stop = threading.Event()
        self._pending_events: List[Dict[str, Any]] = []
        self._events_lock = threading.Lock()
        self._watch_files: Dict[str, float] = {}
        self._on_task_submit = None
    
    def set_on_task_submit(self, callback: Callable):
        """设置任务提交回调"""
        self._on_task_submit = callback
    
    def _polling_loop(self):
        """轮询模式循环"""
        print(f"[Trigger] 轮询模式已启动，间隔: {self._config.trigger.polling_interval}s")
        
        while not self._should_stop.is_set() and self._config.trigger.polling_enabled:
            try:
                time.sleep(self._config.trigger.polling_interval)
            except Exception as e:
                print(f"[Trigger][ERROR] 轮询模式错误: {e}")
                time.sleep(1.0)
        
        print("[Trigger] 轮询模式已停止")
    
    def _event_loop(self):
        """事件驱动循环"""
        print(f"[Trigger] 事件驱动模式已启动，间隔: {self._config.trigger.event_interval}s")
        
        while not self._should_stop.is_set() and self._config.trigger.event_enabled:
            try:
                with self._events_lock:
                    events_to_process = list(self._pending_events)
                    self._pending_events.clear()
                
                for event in events_to_process:
                    self._process_event(event)
                
                time.sleep(self._config.trigger.event_interval)
            except Exception as e:
                print(f"[Trigger][ERROR] 事件驱动模式错误: {e}")
                time.sleep(1.0)
        
        print("[Trigger] 事件驱动模式已停止")
    
    def _process_event(self, event: Dict[str, Any]):
        """处理事件"""
        task_description = event.get("task_description", "")
        if task_description and self._on_task_submit:
            print(f"[Trigger] 处理事件: {event.get('type', 'unknown')} - {task_description[:50]}...")
            self._on_task_submit(task_description, event.get("context", {}))
    
    def emit_event(self, event_type: str, task_description: str, **kwargs):
        """发射事件"""
        with self._events_lock:
            self._pending_events.append({
                "type": event_type,
                "task_description": task_description,
                "context": kwargs,
                "timestamp": time.time()
            })
    
    def submit_direct(self, task_description: str, **context) -> str:
        """直接提交任务"""
        print(f"[Trigger] 直接提交任务: {task_description[:50]}...")
        if self._on_task_submit:
            return self._on_task_submit(task_description, context)
        return ""
    
    def start(self):
        """启动触发器"""
        print("[Trigger] 正在启动自动触发系统...")
        
        self._should_stop.clear()
        
        if self._config.trigger.polling_enabled:
            self._trigger_threads[TriggerType.POLLING] = threading.Thread(
                target=self._polling_loop, daemon=True)
            self._trigger_threads[TriggerType.POLLING].start()
        
        if self._config.trigger.event_enabled:
            self._trigger_threads[TriggerType.EVENT] = threading.Thread(
                target=self._event_loop, daemon=True)
            self._trigger_threads[TriggerType.EVENT].start()
        
        print("[Trigger] 自动触发系统已启动")
    
    def stop(self):
        """停止触发器"""
        print("[Trigger] 正在停止自动触发系统...")
        
        self._should_stop.set()
        
        for trigger_type, thread in self._trigger_threads.items():
            if thread and thread.is_alive():
                thread.join(timeout=2.0)
        
        self._trigger_threads.clear()
        print("[Trigger] 自动触发系统已停止")
    
    def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        return {
            "triggers": {
                tt.value: {
                    "enabled": getattr(self._config.trigger, f"{tt.value}_enabled", False),
                    "running": (tt in self._trigger_threads and
                               self._trigger_threads[tt] and
                               self._trigger_threads[tt].is_alive())
                }
                for tt in TriggerType
            },
            "pending_events": len(self._pending_events),
            "watch_files": len(self._watch_files)
        }


# ============================================
# 7. 自我更新模块（整合 self_update.py）
# ============================================

class SelfUpdate:
    """自我更新模块"""
    
    def __init__(self, config: MetaCognitionConfig):
        self._config = config
        self._last_update_check = 0
        self._update_interval = 3600  # 1小时
    
    def check_and_update(self):
        """检查并更新"""
        if not self._config.enable_self_update:
            return
        
        now = time.time()
        if now - self._last_update_check < self._update_interval:
            return
        
        self._last_update_check = now
        print("[SelfUpdate] 检查更新...")
        
        # 模拟更新检查
        try:
            # 实际实现中这里会调用外部API检查版本
            # 当前版本 v3.0.0
            current_version = __version__
            latest_version = current_version  # 模拟：当前已是最新版本
            
            if latest_version > current_version:
                print(f"[SelfUpdate] 发现新版本: {latest_version}")
                # 实际实现中这里会下载并应用更新
            else:
                print(f"[SelfUpdate] 当前版本已是最新: {current_version}")
        except Exception as e:
            print(f"[SelfUpdate] 检查更新失败: {e}")


# ============================================
# 8. 主类 - MetaCognition
# ============================================

class MetaCognition:
    """Meta-Cognition 主类 - 整合所有功能"""
    
    def __init__(self, config: Optional[MetaCognitionConfig] = None):
        self._config = config or MetaCognitionConfig()
        self._log_manager = LogManager(self._config.log)
        self._engine = MetaCognitionEngine(self._config, self._log_manager)
        self._pattern_recognition = PatternRecognition(self._engine, self._log_manager)
        self._active_learning = ActiveLearning(self._config, self._log_manager)
        self._trigger_engine = TriggerEngine(self._config)
        self._self_update = SelfUpdate(self._config)
        
        # 设置触发器回调
        self._trigger_engine.set_on_task_submit(self._on_task_submit)
        
        # 初始化状态
        self._running = False
        self._current_session = None
        
        print(f"[MetaCognition] v{__version__} 初始化完成")
    
    def _on_task_submit(self, task_description: str, context: Dict[str, Any]) -> str:
        """任务提交回调"""
        return self.pre_task_hook(task_description, context).get("session_id", "")
    
    def pre_task_hook(self, task_description: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """前置钩子"""
        try:
            # 检查自我更新
            self._self_update.check_and_update()
            
            # 模式识别和调度优化
            task_type = "normal"
            scheduling_advice = {}
            
            try:
                task_type, _ = self._pattern_recognition.recognize_task_type(task_description or "")
                scheduling_advice = self._pattern_recognition.optimize_scheduling(task_description or "")
            except Exception:
                pass
            
            # 检测任务模式
            task_mode = self._engine.detect_task_mode(task_description or "")
            if scheduling_advice and scheduling_advice.get("adjusted_mode"):
                task_mode = scheduling_advice["adjusted_mode"]
            
            session_id = self._log_manager.generate_session_id()
            timestamp = self._log_manager.get_current_timestamp()
            filtered_task = self._log_manager.filter_sensitive_info(task_description or "")
            
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
            
            decision = self._engine.get_scheduling_decision(task_mode, task_description or "")
            pre_record["scheduling_decision"] = decision
            
            self._log_manager.add_session(pre_record)
            self._current_session = session_id
            
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
                "workflow_output": self._engine.format_workflow_output(decision)
            }
        except Exception as e:
            print(f"[ERROR] 前置钩子执行失败: {e}")
            session_id = self._log_manager.generate_session_id()
            fallback_decision = self._engine.get_scheduling_decision("game_theory_mode3", "")
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
                "timestamp": self._log_manager.get_current_timestamp(),
                "workflow_output": self._engine.format_workflow_output(fallback_decision)
            }
    
    def post_task_hook(
        self,
        session_id: str,
        result: str = "success",
        agents_used: Optional[list] = None,
        response_preview: Optional[str] = None,
        duration_ms: Optional[int] = None,
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """后置钩子"""
        try:
            session = self._log_manager.get_session_by_id(session_id)
            if not session:
                return {"status": "error", "message": "会话不存在"}
            
            updates = {
                "phase": "completed",
                "end_timestamp": self._log_manager.get_current_timestamp(),
                "result": result,
                "success": result == "success",
                "agents_used": agents_used or [],
                "duration_ms": duration_ms or 0,
                "error": error,
                "response_preview": response_preview[:200] if response_preview else None
            }
            
            self._log_manager.update_session(session_id, updates)
            
            # 主动学习：更新知识图谱
            if self._config.enable_active_learning:
                try:
                    self._active_learning.update_knowledge_graph()
                except Exception as e:
                    print(f"[ActiveLearning] 更新失败: {e}")
            
            return {"status": "completed", "session_id": session_id, "logged": True}
        except Exception as e:
            print(f"[ERROR] 后置钩子执行失败: {e}")
            return {"status": "error", "message": str(e)}
    
    def start(self):
        """启动服务"""
        if self._running:
            print("[MetaCognition] 服务已在运行")
            return
        
        print("[MetaCognition] 启动服务...")
        self._trigger_engine.start()
        self._running = True
        print("[MetaCognition] 服务启动完成")
    
    def stop(self):
        """停止服务"""
        if not self._running:
            print("[MetaCognition] 服务未运行")
            return
        
        print("[MetaCognition] 停止服务...")
        self._trigger_engine.stop()
        self._running = False
        print("[MetaCognition] 服务停止完成")
    
    def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        return {
            "version": __version__,
            "running": self._running,
            "config": {
                "game_theory_enabled": self._config.enable_game_theory,
                "statistics_enabled": self._config.enable_statistics,
                "active_learning_enabled": self._config.enable_active_learning,
                "self_update_enabled": self._config.enable_self_update
            },
            "trigger_status": self._trigger_engine.get_status(),
            "statistics": self._log_manager.get_statistics(),
            "current_session": self._current_session
        }
    
    # 快捷方法
    def auto_submit(self, task_description: str, **context) -> str:
        """快捷提交任务"""
        return self._trigger_engine.submit_direct(task_description, **context)
    
    def auto_complete(self, session_id: str, result: str = "success", **kwargs) -> bool:
        """快捷完成任务"""
        result = self.post_task_hook(session_id, result, **kwargs)
        return result.get("status") == "completed"
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self._log_manager.get_statistics()
    
    def get_recent_sessions(self, limit: int = 10) -> list:
        """获取最近会话"""
        return self._log_manager.get_recent_sessions(limit)


# ============================================
# 全局单例
# ============================================

_meta_cognition_instance: Optional[MetaCognition] = None


def get_meta_cognition() -> MetaCognition:
    """获取 MetaCognition 单例"""
    global _meta_cognition_instance
    if _meta_cognition_instance is None:
        _meta_cognition_instance = MetaCognition()
    return _meta_cognition_instance


# ============================================
# 自动启动（导入即启动）
# ============================================

# 导入时自动创建实例并启动
_meta_cognition_instance = MetaCognition()
_meta_cognition_instance.start()

# ============================================
# 导出接口（向后兼容）
# ============================================

# 钩子函数（向后兼容）
def pre_task_hook(task_description: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return get_meta_cognition().pre_task_hook(task_description, context)

def post_task_hook(
    session_id: str,
    result: str = "success",
    agents_used: Optional[list] = None,
    response_preview: Optional[str] = None,
    duration_ms: Optional[int] = None,
    error: Optional[str] = None
) -> Dict[str, Any]:
    return get_meta_cognition().post_task_hook(session_id, result, agents_used, response_preview, duration_ms, error)

def detect_task_mode(task_description: str) -> str:
    return get_meta_cognition()._engine.detect_task_mode(task_description)

def get_scheduling_decision(task_mode: str, task_description: str) -> Dict[str, Any]:
    return get_meta_cognition()._engine.get_scheduling_decision(task_mode, task_description)

def get_task_recommendations(task_description: str) -> Dict[str, Any]:
    mode = detect_task_mode(task_description)
    decision = get_scheduling_decision(mode, task_description)
    return {
        "mode": mode,
        "mode_info": {
            "mode": decision['mode'],
            "mode_number": decision.get('mode_number', ''),
            "description": decision['description']
        },
        "recommended_agents": decision.get("recommended_agents", []),
        "scheduling_steps": decision.get("steps", []),
        "mode_description": decision.get("description", ""),
        "workflow_output": get_meta_cognition()._engine.format_workflow_output(decision)
    }

def update_session(session_id: str, updates: Dict[str, Any]) -> bool:
    try:
        get_meta_cognition()._log_manager.update_session(session_id, updates)
        return True
    except Exception:
        return False

def get_statistics() -> Dict[str, Any]:
    return get_meta_cognition().get_statistics()

def get_recent_sessions(limit: int = 10) -> list:
    return get_meta_cognition().get_recent_sessions(limit)

def get_session_by_id(session_id: str) -> Optional[Dict[str, Any]]:
    return get_meta_cognition()._log_manager.get_session_by_id(session_id)

def export_sessions() -> Dict[str, Any]:
    return get_meta_cognition()._log_manager._load_log()

# 守护进程接口（向后兼容）
def get_daemon_manager():
    return get_meta_cognition()

def auto_submit(task_description: str, **context) -> str:
    return get_meta_cognition().auto_submit(task_description, **context)

def auto_complete(session_id: str, result: str = "success", **kwargs) -> bool:
    return get_meta_cognition().auto_complete(session_id, result, **kwargs)

def auto_get_statistics() -> Dict[str, Any]:
    return get_meta_cognition().get_statistics()

def auto_get_status() -> Dict[str, Any]:
    return get_meta_cognition().get_status()

def auto_get_recent(limit: int = 10) -> list:
    return get_meta_cognition().get_recent_sessions(limit)


__all__ = [
    "__version__",
    "MetaCognition",
    "get_meta_cognition",
    # 钩子函数
    "pre_task_hook",
    "detect_task_mode",
    "get_scheduling_decision",
    "get_task_recommendations",
    "post_task_hook",
    "update_session",
    "get_statistics",
    "get_recent_sessions",
    "get_session_by_id",
    "export_sessions",
    # 守护进程接口
    "get_daemon_manager",
    "auto_submit",
    "auto_complete",
    "auto_get_statistics",
    "auto_get_status",
    "auto_get_recent"
]
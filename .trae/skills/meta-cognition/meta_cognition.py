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
    
    # 空闲模式配置
    idle_mode_enabled: bool = True
    idle_threshold_seconds: float = 60.0
    idle_polling_interval: float = 5.0
    idle_event_interval: float = 2.0
    idle_filesystem_interval: float = 30.0
    idle_api_interval: float = 1.0


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
class CompletionThresholdConfig:
    """完成度阈值配置"""
    success_threshold: float = 0.8    # 80%以上算成功
    partial_threshold: float = 0.5    # 50%-80%算部分完成
    failure_threshold: float = 0.5    # 50%以下算失败
    enable_soft_failure: bool = True  # 启用软失败（部分完成）


@dataclass
class SelfPurificationConfig:
    """自我净化配置"""
    enabled: bool = True
    enable_error_analysis: bool = True
    enable_self_reflect: bool = True
    enable_kg_purification: bool = True
    enable_pattern_validation: bool = True
    enable_completion_analysis: bool = True  # 启用完成度分析
    min_error_count_for_analysis: int = 1
    auto_purify_on_failure: bool = True
    purify_similar_tasks: bool = True
    max_kg_relations: int = 100
    completion_threshold: CompletionThresholdConfig = field(default_factory=CompletionThresholdConfig)


@dataclass
class MetaCognitionConfig:
    enable_game_theory: bool = True
    enable_statistics: bool = True
    enable_monitoring: bool = True  # 默认开启监控
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
    self_purification: SelfPurificationConfig = field(default_factory=SelfPurificationConfig)


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
# 5.5. 自我净化模块（Self-Purification）
# ============================================

class ErrorType(Enum):
    """错误类型枚举（基于 AgentDebug 系统）"""
    MISUNDERSTANDING = "misunderstanding"  # 误解用户需求
    WRONG_MODE = "wrong_mode"  # 模式识别错误
    WRONG_AGENT = "wrong_agent"  # 智能体选择错误
    TECHNICAL_ERROR = "technical_error"  # 技术执行错误
    CONTEXT_MISSING = "context_missing"  # 上下文缺失
    KNOWLEDGE_GAP = "knowledge_gap"  # 知识库缺口
    UNKNOWN = "unknown"  # 未知错误


@dataclass
class ErrorAnalysis:
    """错误分析结果"""
    error_type: ErrorType
    root_cause: str
    impact: str
    fix_suggestions: List[str]
    prevention_tips: List[str]
    related_sessions: List[str]


class CompletionStatus(Enum):
    """完成状态枚举"""
    SUCCESS = "success"           # 成功（>=80%）
    PARTIAL = "partial"           # 部分完成（50%-80%）
    FAILURE = "failure"           # 失败（<50%）


@dataclass
class CompletionAnalysis:
    """完成度分析结果"""
    score: float                   # 完成度分数 (0.0-1.0)
    status: CompletionStatus       # 完成状态
    status_text: str               # 状态文本描述
    breakdown: Dict[str, float]    # 各维度得分明细
    suggestions: List[str]         # 改进建议


class SelfPurification:
    """自我净化模块 - 基于 Self-Reflect 和 AgentDebug 最佳实践"""
    
    def __init__(self, config: MetaCognitionConfig, log_manager: LogManager):
        self._config = config
        self._log_manager = log_manager
        self._purification_config = config.self_purification
        print("[SelfPurification] 自我净化模块已初始化")
    
    def analyze_completion(self, session: Dict[str, Any]) -> CompletionAnalysis:
        """分析任务完成度（多维度评估）"""
        if not self._purification_config.enable_completion_analysis:
            return CompletionAnalysis(
                score=1.0 if session.get("success") else 0.0,
                status=CompletionStatus.SUCCESS if session.get("success") else CompletionStatus.FAILURE,
                status_text="完成度分析未启用",
                breakdown={},
                suggestions=[]
            )
        
        # 1. 计算各维度得分
        breakdown = self._calculate_completion_breakdown(session)
        
        # 2. 综合计算完成度分数（加权平均）
        weights = {
            "result_score": 0.4,     # 结果是否成功（权重最高）
            "completeness_score": 0.3, # 任务完成完整性
            "quality_score": 0.2,    # 输出质量
            "efficiency_score": 0.1   # 执行效率
        }
        
        total_score = sum(breakdown.get(dim, 0) * weights.get(dim, 0) for dim in weights)
        
        # 3. 判断完成状态
        threshold = self._purification_config.completion_threshold
        if total_score >= threshold.success_threshold:
            status = CompletionStatus.SUCCESS
            status_text = f"成功（完成度: {total_score:.1%}）"
        elif threshold.enable_soft_failure and total_score >= threshold.partial_threshold:
            status = CompletionStatus.PARTIAL
            status_text = f"部分完成（完成度: {total_score:.1%}）"
        else:
            status = CompletionStatus.FAILURE
            status_text = f"失败（完成度: {total_score:.1%}）"
        
        # 4. 生成改进建议
        suggestions = self._generate_completion_suggestions(total_score, breakdown, session)
        
        return CompletionAnalysis(
            score=total_score,
            status=status,
            status_text=status_text,
            breakdown=breakdown,
            suggestions=suggestions
        )
    
    def _calculate_completion_breakdown(self, session: Dict[str, Any]) -> Dict[str, float]:
        """计算各维度完成度得分"""
        breakdown = {}
        
        # 1. 结果得分（是否成功）
        is_success = session.get("success", False)
        breakdown["result_score"] = 1.0 if is_success else 0.5  # 即使失败也给50%，因为可能完成了一部分
        
        # 2. 任务完整性得分
        task_desc = session.get("task_description", "")
        response_preview = session.get("response_preview", "")
        
        # 根据任务类型和响应内容评估完整性
        if len(task_desc) < 10:
            breakdown["completeness_score"] = 0.9 if response_preview else 0.3
        elif len(response_preview) > len(task_desc) * 2:
            breakdown["completeness_score"] = 0.9
        elif len(response_preview) > len(task_desc):
            breakdown["completeness_score"] = 0.7
        elif response_preview:
            breakdown["completeness_score"] = 0.5
        else:
            breakdown["completeness_score"] = 0.2
        
        # 3. 质量得分（基于是否有错误）
        error = session.get("error")
        if error:
            breakdown["quality_score"] = 0.3
        elif session.get("success"):
            breakdown["quality_score"] = 0.9
        else:
            breakdown["quality_score"] = 0.5
        
        # 4. 效率得分（基于耗时）
        duration_ms = session.get("duration_ms", 0)
        if duration_ms < 1000:
            breakdown["efficiency_score"] = 0.9
        elif duration_ms < 5000:
            breakdown["efficiency_score"] = 0.7
        elif duration_ms < 10000:
            breakdown["efficiency_score"] = 0.5
        else:
            breakdown["efficiency_score"] = 0.3
        
        return breakdown
    
    def _generate_completion_suggestions(self, total_score: float, breakdown: Dict[str, float], 
                                       session: Dict[str, Any]) -> List[str]:
        """生成完成度改进建议"""
        suggestions = []
        
        if total_score < 0.8:
            # 低于80%时给出具体建议
            if breakdown.get("completeness_score", 0) < 0.7:
                suggestions.append("建议增加输出内容的完整性，确保覆盖任务的所有要求")
            
            if breakdown.get("quality_score", 0) < 0.7:
                suggestions.append("建议检查输出质量，确保没有错误或需要改进的地方")
            
            if breakdown.get("efficiency_score", 0) < 0.7:
                suggestions.append("建议优化执行流程，减少响应时间")
        
        if total_score >= 0.5 and total_score < 0.8:
            suggestions.append("任务部分完成，建议继续完善剩余部分")
        
        if total_score < 0.5:
            suggestions.append("任务未完成，建议重新分析需求并重新执行")
        
        # 通用建议
        suggestions.append("建议收集用户反馈以验证实际完成情况")
        
        return suggestions
    
    def get_completion_status(self, session: Dict[str, Any]) -> CompletionStatus:
        """获取任务完成状态"""
        analysis = self.analyze_completion(session)
        return analysis.status
    
    def is_success_by_threshold(self, session: Dict[str, Any]) -> bool:
        """根据阈值判断是否成功"""
        analysis = self.analyze_completion(session)
        return analysis.status == CompletionStatus.SUCCESS
    
    def analyze_failure(self, session: Dict[str, Any]) -> ErrorAnalysis:
        """分析失败任务（基于 AgentDebug 系统）"""
        task_description = session.get("task_description", "")
        detected_mode = session.get("detected_mode", "normal")
        error = session.get("error", "")
        error_details = session.get("error_details", "")
        root_cause = session.get("root_cause", "")
        
        # 1. 错误分类
        error_type = self._classify_error(session)
        
        # 2. 根因分析
        if not root_cause:
            root_cause = self._analyze_root_cause(task_description, detected_mode, error, error_type)
        
        # 3. 影响评估
        impact = self._assess_impact(session, error_type)
        
        # 4. 修复建议
        fix_suggestions = self._generate_fix_suggestions(error_type, root_cause, session)
        
        # 5. 预防建议
        prevention_tips = self._generate_prevention_tips(error_type, root_cause)
        
        # 6. 查找相关会话
        related_sessions = self._find_related_sessions(task_description, error_type)
        
        return ErrorAnalysis(
            error_type=error_type,
            root_cause=root_cause,
            impact=impact,
            fix_suggestions=fix_suggestions,
            prevention_tips=prevention_tips,
            related_sessions=related_sessions
        )
    
    def _classify_error(self, session: Dict[str, Any]) -> ErrorType:
        """错误分类"""
        task_description = session.get("task_description", "")
        detected_mode = session.get("detected_mode", "normal")
        error = session.get("error", "").lower()
        error_details = session.get("error_details", "").lower()
        root_cause = session.get("root_cause", "").lower()
        
        # 检查是否有明确的根因
        if root_cause:
            if any(keyword in root_cause for keyword in ["误解", "混淆", "理解错"]):
                return ErrorType.MISUNDERSTANDING
            if any(keyword in root_cause for keyword in ["模式", "识别", "分类"]):
                return ErrorType.WRONG_MODE
            if any(keyword in root_cause for keyword in ["智能体", "agent"]):
                return ErrorType.WRONG_AGENT
            if any(keyword in root_cause for keyword in ["知识", "知识库", "kg"]):
                return ErrorType.KNOWLEDGE_GAP
        
        # 基于错误信息分类
        if error:
            if any(keyword in error for keyword in ["理解", "误解", "混淆"]):
                return ErrorType.MISUNDERSTANDING
            if any(keyword in error for keyword in ["模式", "识别", "分类"]):
                return ErrorType.WRONG_MODE
            if any(keyword in error for keyword in ["技术", "执行", "api", "调用"]):
                return ErrorType.TECHNICAL_ERROR
            if any(keyword in error for keyword in ["上下文", "context", "历史"]):
                return ErrorType.CONTEXT_MISSING
        
        return ErrorType.UNKNOWN
    
    def _analyze_root_cause(self, task_description: str, detected_mode: str, 
                          error: str, error_type: ErrorType) -> str:
        """根因分析（基于 Self-Reflect 策略）"""
        # 检查模式识别是否正确
        if error_type == ErrorType.UNKNOWN:
            # 简单的模式识别验证
            has_debate_keywords = any(kw in task_description for kw in self._config.keywords.mode1_keywords[:10])
            has_optimize_keywords = any(kw in task_description for kw in self._config.keywords.mode2_keywords[:10])
            has_design_keywords = any(kw in task_description for kw in self._config.keywords.mode3_keywords[:10])
            
            if detected_mode == "game_theory_mode1" and not has_debate_keywords:
                return "模式识别可能有误，任务中没有明显的辩论/对比关键词"
            if detected_mode == "game_theory_mode2" and not has_optimize_keywords:
                return "模式识别可能有误，任务中没有明显的优化/改进关键词"
            if detected_mode == "game_theory_mode3" and not has_design_keywords:
                return "模式识别可能有误，任务中没有明显的设计/架构关键词"
        
        return "需要进一步分析的错误原因"
    
    def _assess_impact(self, session: Dict[str, Any], error_type: ErrorType) -> str:
        """影响评估"""
        impact_levels = {
            ErrorType.MISUNDERSTANDING: "高 - 用户需求被完全误解",
            ErrorType.WRONG_MODE: "中 - 模式选择不当导致效率降低",
            ErrorType.WRONG_AGENT: "中 - 智能体选择不匹配",
            ErrorType.TECHNICAL_ERROR: "低 - 技术执行问题，可重试",
            ErrorType.CONTEXT_MISSING: "中 - 上下文信息不足",
            ErrorType.KNOWLEDGE_GAP: "中 - 知识库需要补充",
            ErrorType.UNKNOWN: "低 - 未知错误类型"
        }
        return impact_levels.get(error_type, "未知影响级别")
    
    def _generate_fix_suggestions(self, error_type: ErrorType, root_cause: str, 
                                session: Dict[str, Any]) -> List[str]:
        """生成修复建议"""
        suggestions = []
        
        if error_type == ErrorType.MISUNDERSTANDING:
            suggestions.append("在执行前添加确认步骤，确认理解用户需求")
            suggestions.append("对于模糊的任务，主动询问用户以澄清需求")
        elif error_type == ErrorType.WRONG_MODE:
            suggestions.append("重新评估任务的模式匹配")
            suggestions.append("考虑增加模式识别的置信度阈值")
        elif error_type == ErrorType.WRONG_AGENT:
            suggestions.append("重新评估智能体选择策略")
            suggestions.append("考虑增加智能体能力与任务的匹配度检查")
        elif error_type == ErrorType.TECHNICAL_ERROR:
            suggestions.append("添加重试机制")
            suggestions.append("增加错误恢复逻辑")
        elif error_type == ErrorType.KNOWLEDGE_GAP:
            suggestions.append("补充相关知识到知识图谱")
            suggestions.append("考虑使用外部知识源")
        
        suggestions.append("记录此错误案例用于未来学习")
        return suggestions
    
    def _generate_prevention_tips(self, error_type: ErrorType, root_cause: str) -> List[str]:
        """生成预防建议"""
        tips = []
        
        if error_type == ErrorType.MISUNDERSTANDING:
            tips.append("建立需求确认清单")
            tips.append("对于复杂任务，先输出理解再执行")
        elif error_type == ErrorType.WRONG_MODE:
            tips.append("定期验证模式识别准确性")
            tips.append("收集用户反馈用于优化模式识别")
        elif error_type == ErrorType.KNOWLEDGE_GAP:
            tips.append("建立知识缺口追踪机制")
            tips.append("定期补充和更新知识库")
        
        tips.append("建立错误案例库用于持续学习")
        return tips
    
    def _find_related_sessions(self, task_description: str, error_type: ErrorType) -> List[str]:
        """查找相关会话"""
        log_data = self._log_manager._load_log()
        sessions = log_data.get("sessions", [])
        
        related = []
        # 简单的关键词匹配查找相似任务
        task_keywords = set(task_description.split())
        
        for session in sessions:
            if session.get("session_id") and session.get("result") == "failure":
                desc = session.get("task_description", "")
                desc_keywords = set(desc.split())
                if len(task_keywords & desc_keywords) >= 2:  # 至少2个关键词匹配
                    related.append(session.get("session_id"))
        
        return related[:5]  # 最多返回5个相关会话
    
    def self_reflect(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """自我反思（Self-Reflect 策略）"""
        if not self._purification_config.enable_self_reflect:
            return {"status": "disabled", "message": "自我反思功能未启用"}
        
        print(f"[SelfPurification] 开始自我反思: {session.get('session_id')}")
        
        # 1. 输出初版决策
        initial_decision = {
            "detected_mode": session.get("detected_mode"),
            "task_type": session.get("task_type"),
            "scheduling_advice": session.get("scheduling_advice"),
            "timestamp": session.get("timestamp")
        }
        
        # 2. 自我评估
        assessment = self._assess_decision(session)
        
        # 3. 定位潜在问题
        issues = self._identify_issues(session, assessment)
        
        # 4. 生成优化建议
        optimization = self._generate_optimization(issues, session)
        
        return {
            "status": "completed",
            "initial_decision": initial_decision,
            "assessment": assessment,
            "issues": issues,
            "optimization": optimization,
            "timestamp": self._log_manager.get_current_timestamp()
        }
    
    def _assess_decision(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """评估决策质量"""
        assessment = {
            "mode_confidence": "medium",
            "agent_match": "medium",
            "context_usage": "medium",
            "overall_score": 0.5
        }
        
        # 简单的评估逻辑
        detected_mode = session.get("detected_mode", "normal")
        task_type = session.get("task_type", "normal")
        
        if detected_mode == "game_theory_mode1" and task_type == "debate":
            assessment["mode_confidence"] = "high"
        elif detected_mode == "game_theory_mode2" and task_type == "optimization":
            assessment["mode_confidence"] = "high"
        elif detected_mode == "game_theory_mode3" and task_type in ["design", "architecture"]:
            assessment["mode_confidence"] = "high"
        elif detected_mode == "normal" and task_type == "normal":
            assessment["mode_confidence"] = "high"
        else:
            assessment["mode_confidence"] = "low"
        
        # 基于成功/失败调整分数
        if session.get("success"):
            assessment["overall_score"] = min(1.0, assessment["overall_score"] + 0.3)
        else:
            assessment["overall_score"] = max(0.0, assessment["overall_score"] - 0.3)
        
        return assessment
    
    def _identify_issues(self, session: Dict[str, Any], assessment: Dict[str, Any]) -> List[str]:
        """识别潜在问题"""
        issues = []
        
        if assessment["mode_confidence"] == "low":
            issues.append("模式识别置信度较低")
        
        if not session.get("success"):
            issues.append("任务执行失败")
        
        if session.get("error"):
            issues.append(f"存在错误: {session.get('error')}")
        
        if not issues:
            issues.append("未发现明显问题")
        
        return issues
    
    def _generate_optimization(self, issues: List[str], session: Dict[str, Any]) -> List[str]:
        """生成优化建议"""
        optimizations = []
        
        for issue in issues:
            if "模式识别" in issue:
                optimizations.append("建议重新评估任务模式，考虑增加关键词匹配阈值")
            if "执行失败" in issue:
                optimizations.append("建议分析失败原因，建立错误案例库")
            if "错误" in issue:
                optimizations.append("建议添加错误处理和恢复机制")
        
        optimizations.append("建议持续收集用户反馈用于系统优化")
        return optimizations
    
    def purify_knowledge_graph(self) -> Dict[str, Any]:
        """净化知识图谱（基于 ERASER 环境反馈型自修正）"""
        if not self._purification_config.enable_kg_purification:
            return {"status": "disabled", "message": "知识图谱净化功能未启用"}
        
        print("[SelfPurification] 开始净化知识图谱")
        
        log_data = self._log_manager._load_log()
        sessions = log_data.get("sessions", [])
        
        # 1. 分析失败案例中的模式识别问题
        failed_sessions = [s for s in sessions if s.get("result") == "failure"]
        
        kg_issues = []
        removed_relations = {}
        corrected_relations = {}
        
        for session in failed_sessions:
            analysis = self.analyze_failure(session)
            if analysis.error_type in [ErrorType.WRONG_MODE, ErrorType.MISUNDERSTANDING]:
                task_desc = session.get("task_description", "")
                detected_mode = session.get("detected_mode", "")
                
                # 分析关键词映射问题
                keywords = self._extract_keywords(task_desc)
                for keyword in keywords:
                    # 检查这个关键词是否在知识图谱中有错误的映射
                    if keyword in self._config.knowledge_graph.kg_relations:
                        mapped_concepts = self._config.knowledge_graph.kg_relations[keyword]
                        # 如果失败模式与映射概念不匹配，标记为问题
                        mode_to_concept = {
                            "game_theory_mode1": "辩论",
                            "game_theory_mode2": "优化", 
                            "game_theory_mode3": "设计"
                        }
                        if detected_mode in mode_to_concept:
                            mapped_concept = mode_to_concept[detected_mode]
                            if mapped_concept not in mapped_concepts:
                                kg_issues.append({
                                    "keyword": keyword,
                                    "mapped_concepts": mapped_concepts,
                                    "correct_concept": mapped_concept,
                                    "session_id": session.get("session_id")
                                })
        
        # 2. 移除低频关系（防止知识图谱膨胀）
        current_relations = self._config.knowledge_graph.kg_relations.copy()
        if len(current_relations) > self._purification_config.max_kg_relations:
            # 统计每个关系的使用频率
            relation_usage = {}
            for session in sessions:
                if session.get("result") == "success":
                    task_desc = session.get("task_description", "")
                    keywords = self._extract_keywords(task_desc)
                    for keyword in keywords:
                        if keyword in current_relations:
                            relation_usage[keyword] = relation_usage.get(keyword, 0) + 1
            
            # 移除使用频率最低的关系
            sorted_relations = sorted(relation_usage.items(), key=lambda x: x[1])
            to_remove = len(current_relations) - self._purification_config.max_kg_relations
            for keyword, _ in sorted_relations[:to_remove]:
                if keyword in current_relations:
                    removed_relations[keyword] = current_relations.pop(keyword)
        
        # 3. 保存净化结果
        purification_result = {
            "timestamp": self._log_manager.get_current_timestamp(),
            "issues_found": kg_issues,
            "removed_relations": removed_relations,
            "corrected_relations": corrected_relations,
            "remaining_relations": len(current_relations)
        }
        
        log_data["kg_purification"] = purification_result
        self._log_manager._save_log(log_data)
        
        print(f"[SelfPurification] 知识图谱净化完成: 发现 {len(kg_issues)} 个问题，移除 {len(removed_relations)} 个关系")
        
        return purification_result
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        cleaned = re.sub(r'[.,;!?()\[\]{}]', ' ', text)
        words = cleaned.split()
        common_words = set(["请", "帮", "我", "你", "的", "这", "那", "个", "是", "在", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去", "会", "着", "没有", "看", "好", "自己"])
        
        keywords = []
        for word in words:
            word = word.strip()
            if len(word) > 1 and word not in common_words:
                keywords.append(word)
        
        return keywords
    
    def validate_pattern_recognition(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """验证模式识别准确性"""
        if not self._purification_config.enable_pattern_validation:
            return {"status": "disabled", "message": "模式验证功能未启用"}
        
        task_description = session.get("task_description", "")
        detected_mode = session.get("detected_mode", "normal")
        
        # 1. 检查关键词匹配
        has_mode1 = any(kw in task_description for kw in self._config.keywords.mode1_keywords[:20])
        has_mode2 = any(kw in task_description for kw in self._config.keywords.mode2_keywords[:20])
        has_mode3 = any(kw in task_description for kw in self._config.keywords.mode3_keywords[:20])
        
        # 2. 验证模式选择
        validation = {
            "detected_mode": detected_mode,
            "has_mode1_keywords": has_mode1,
            "has_mode2_keywords": has_mode2,
            "has_mode3_keywords": has_mode3,
            "is_valid": True,
            "suggested_mode": detected_mode,
            "confidence": 0.5
        }
        
        # 3. 简单的一致性检查
        if detected_mode == "game_theory_mode1" and not has_mode1:
            validation["is_valid"] = False
            if has_mode2:
                validation["suggested_mode"] = "game_theory_mode2"
            elif has_mode3:
                validation["suggested_mode"] = "game_theory_mode3"
            else:
                validation["suggested_mode"] = "normal"
        
        if detected_mode == "game_theory_mode2" and not has_mode2:
            validation["is_valid"] = False
            if has_mode1:
                validation["suggested_mode"] = "game_theory_mode1"
            elif has_mode3:
                validation["suggested_mode"] = "game_theory_mode3"
            else:
                validation["suggested_mode"] = "normal"
        
        if detected_mode == "game_theory_mode3" and not has_mode3:
            validation["is_valid"] = False
            if has_mode1:
                validation["suggested_mode"] = "game_theory_mode1"
            elif has_mode2:
                validation["suggested_mode"] = "game_theory_mode2"
            else:
                validation["suggested_mode"] = "normal"
        
        # 4. 计算置信度
        match_count = sum([has_mode1, has_mode2, has_mode3])
        if match_count == 1:
            validation["confidence"] = 0.9
        elif match_count > 1:
            validation["confidence"] = 0.6
        else:
            validation["confidence"] = 0.3
        
        # 5. 如果验证失败且任务成功，可能是模式识别有问题但执行正确
        if not validation["is_valid"] and session.get("success"):
            validation["note"] = "模式验证失败但任务成功，可能需要调整关键词"
        
        return validation
    
    def run_full_purification(self) -> Dict[str, Any]:
        """运行完整的自我净化流程"""
        if not self._purification_config.enabled:
            return {"status": "disabled", "message": "自我净化功能未启用"}
        
        print("[SelfPurification] 开始完整自我净化流程")
        
        results = {
            "timestamp": self._log_manager.get_current_timestamp(),
            "error_analysis": [],
            "self_reflections": [],
            "kg_purification": None,
            "pattern_validations": [],
            "summary": {}
        }
        
        log_data = self._log_manager._load_log()
        sessions = log_data.get("sessions", [])
        
        # 1. 分析所有失败任务
        failed_sessions = [s for s in sessions if s.get("result") == "failure"]
        for session in failed_sessions:
            analysis = self.analyze_failure(session)
            results["error_analysis"].append({
                "session_id": session.get("session_id"),
                "error_type": analysis.error_type.value,
                "root_cause": analysis.root_cause,
                "impact": analysis.impact
            })
        
        # 2. 对最近任务进行自我反思
        recent_sessions = sessions[-5:]  # 最近5个任务
        for session in recent_sessions:
            reflection = self.self_reflect(session)
            results["self_reflections"].append({
                "session_id": session.get("session_id"),
                "status": reflection.get("status"),
                "assessment": reflection.get("assessment", {})
            })
        
        # 3. 净化知识图谱
        results["kg_purification"] = self.purify_knowledge_graph()
        
        # 4. 验证模式识别
        for session in recent_sessions:
            validation = self.validate_pattern_recognition(session)
            results["pattern_validations"].append({
                "session_id": session.get("session_id"),
                "is_valid": validation.get("is_valid"),
                "confidence": validation.get("confidence")
            })
        
        # 5. 生成总结
        total_failures = len(failed_sessions)
        total_validations = len(results["pattern_validations"])
        invalid_patterns = sum(1 for v in results["pattern_validations"] if not v.get("is_valid"))
        
        results["summary"] = {
            "total_sessions_analyzed": len(sessions),
            "failed_sessions": total_failures,
            "pattern_validations": total_validations,
            "invalid_patterns": invalid_patterns,
            "success_rate": (len(sessions) - total_failures) / len(sessions) if sessions else 0
        }
        
        # 6. 保存净化结果
        log_data["self_purification"] = results
        self._log_manager._save_log(log_data)
        
        print(f"[SelfPurification] 完整净化流程完成: 分析了 {total_failures} 个失败任务")
        
        return results


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
        self._last_activity_time = time.time()
    
    def _update_activity(self):
        """更新最后活动时间"""
        self._last_activity_time = time.time()
    
    def _is_working(self) -> bool:
        """判断是否正在执行任务（通过外部集成模块）"""
        try:
            from .integration_config import is_working
            return is_working()
        except ImportError:
            # 如果无法导入，使用本地活动时间判断
            elapsed = time.time() - self._last_activity_time
            return elapsed < self._config.trigger.idle_threshold_seconds
    
    def _is_idle(self) -> bool:
        """判断是否处于空闲状态"""
        if not self._config.trigger.idle_mode_enabled:
            return False
        # 如果正在执行任务，不算空闲
        if self._is_working():
            return False
        elapsed = time.time() - self._last_activity_time
        return elapsed >= self._config.trigger.idle_threshold_seconds
    
    def _get_polling_interval(self) -> float:
        """根据状态获取轮询间隔"""
        # 如果正在工作，使用工作间隔
        if self._is_working():
            return self._config.trigger.polling_interval
        # 否则根据空闲状态决定
        if self._is_idle():
            return self._config.trigger.idle_polling_interval
        return self._config.trigger.polling_interval
    
    def _get_event_interval(self) -> float:
        """根据状态获取事件间隔"""
        # 如果正在工作，使用工作间隔
        if self._is_working():
            return self._config.trigger.event_interval
        # 否则根据空闲状态决定
        if self._is_idle():
            return self._config.trigger.idle_event_interval
        return self._config.trigger.event_interval
    
    def set_on_task_submit(self, callback: Callable):
        """设置任务提交回调"""
        self._on_task_submit = callback
    
    def _polling_loop(self):
        """轮询模式循环（支持动态频率）"""
        print(f"[Trigger] 轮询模式已启动，工作间隔: {self._config.trigger.polling_interval}s, 空闲间隔: {self._config.trigger.idle_polling_interval}s")
        
        while not self._should_stop.is_set() and self._config.trigger.polling_enabled:
            try:
                interval = self._get_polling_interval()
                time.sleep(interval)
            except Exception as e:
                print(f"[Trigger][ERROR] 轮询模式错误: {e}")
                time.sleep(1.0)
        
        print("[Trigger] 轮询模式已停止")
    
    def _event_loop(self):
        """事件驱动循环（支持动态频率）"""
        print(f"[Trigger] 事件驱动模式已启动，工作间隔: {self._config.trigger.event_interval}s, 空闲间隔: {self._config.trigger.idle_event_interval}s")
        
        while not self._should_stop.is_set() and self._config.trigger.event_enabled:
            try:
                with self._events_lock:
                    events_to_process = list(self._pending_events)
                    self._pending_events.clear()
                
                # 有事件处理，表示正在工作
                if events_to_process:
                    self._update_activity()
                    for event in events_to_process:
                        self._process_event(event)
                
                interval = self._get_event_interval()
                time.sleep(interval)
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
        self._self_purification = SelfPurification(self._config, self._log_manager)  # 新增：自我净化
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
            
            # 自我净化：失败时自动分析
            if result == "failure" and self._config.self_purification.auto_purify_on_failure:
                try:
                    session = self._log_manager.get_session_by_id(session_id)
                    if session:
                        analysis = self._self_purification.analyze_failure(session)
                        print(f"[SelfPurification] 失败分析完成: {analysis.error_type.value}")
                except Exception as e:
                    print(f"[SelfPurification] 分析失败: {e}")
            
            return {"status": "completed", "session_id": session_id, "logged": True}
        except Exception as e:
            print(f"[ERROR] 后置钩子执行失败: {e}")
            return {"status": "error", "message": str(e)}
    
    def run_self_purification(self) -> Dict[str, Any]:
        """运行完整的自我净化流程"""
        return self._self_purification.run_full_purification()
    
    def analyze_failure(self, session_id: str) -> Dict[str, Any]:
        """分析指定失败会话"""
        session = self._log_manager.get_session_by_id(session_id)
        if not session:
            return {"status": "error", "message": "会话不存在"}
        analysis = self._self_purification.analyze_failure(session)
        return {
            "status": "completed",
            "error_type": analysis.error_type.value,
            "root_cause": analysis.root_cause,
            "impact": analysis.impact,
            "fix_suggestions": analysis.fix_suggestions,
            "prevention_tips": analysis.prevention_tips,
            "related_sessions": analysis.related_sessions
        }
    
    def purify_knowledge_graph(self) -> Dict[str, Any]:
        """净化知识图谱"""
        return self._self_purification.purify_knowledge_graph()
    
    def self_reflect(self, session_id: str) -> Dict[str, Any]:
        """对指定会话进行自我反思"""
        session = self._log_manager.get_session_by_id(session_id)
        if not session:
            return {"status": "error", "message": "会话不存在"}
        return self._self_purification.self_reflect(session)
    
    def analyze_completion(self, session_id: str) -> Dict[str, Any]:
        """分析指定会话的完成度"""
        session = self._log_manager.get_session_by_id(session_id)
        if not session:
            return {"status": "error", "message": "会话不存在"}
        analysis = self._self_purification.analyze_completion(session)
        return {
            "status": "completed",
            "score": analysis.score,
            "status_text": analysis.status_text,
            "completion_status": analysis.status.value,
            "breakdown": analysis.breakdown,
            "suggestions": analysis.suggestions
        }
    
    def is_success_by_threshold(self, session_id: str) -> Dict[str, Any]:
        """根据阈值判断任务是否成功"""
        session = self._log_manager.get_session_by_id(session_id)
        if not session:
            return {"status": "error", "message": "会话不存在"}
        result = self._self_purification.is_success_by_threshold(session)
        analysis = self._self_purification.analyze_completion(session)
        return {
            "status": "completed",
            "is_success": result,
            "completion_score": analysis.score,
            "completion_status": analysis.status.value,
            "threshold_info": {
                "success_threshold": self._config.self_purification.completion_threshold.success_threshold,
                "partial_threshold": self._config.self_purification.completion_threshold.partial_threshold
            }
        }
    
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
                "self_update_enabled": self._config.enable_self_update,
                "self_purification_enabled": self._config.self_purification.enabled,
                "auto_purify_on_failure": self._config.self_purification.auto_purify_on_failure
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
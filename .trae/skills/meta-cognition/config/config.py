# -*- coding: utf-8 -*-
"""
Meta-Cognition 配置管理模块

管理技能的配置参数，支持环境变量和配置文件两种方式
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class GameTheoryKeywords:
    """博弈模式关键词配置

    触发机制：高频词匹配为主，复杂度判断为辅
    强制触发：90%以上的任务必须进入博弈工作流
    """
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
    """知识图谱配置
    
    核心博弈概念：优化、设计、辩论
    分别对应模式二、模式三、模式一
    """
    core_concepts: list = field(default_factory=lambda: ["优化", "设计", "辩论"])
    concept_priority: list = field(default_factory=lambda: ["辩论", "优化", "设计"])
    kg_relations: dict = field(default_factory=lambda: {
        "加速": ["优化"],
        "架构": ["设计"],
        "优缺点": ["辩论"],
        "性能": ["优化"],
        "结构": ["设计"],
        "对比": ["辩论"],
        "改进": ["优化"],
        "开发": ["设计"],
        "风险": ["辩论"],
        "提升": ["优化"],
        "创建": ["设计"],
        "争论": ["辩论"],
        "修复": ["优化"],
        "实现": ["设计"],
        "利弊": ["辩论"],
        "调试": ["优化"],
        "规划": ["设计"],
        "分歧": ["辩论"]
    })


@dataclass
class ComplexityConfig:
    """复杂度判断配置（辅助触发条件）

    满足任一条件即触发模式三（深度设计）：
    - 任务描述包含超过2个独立分句
    - 包含技术名词、文件名、URL、代码片段
    - 总字符数超过15字
    """
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
    """博弈工作流配置"""
    mode1_workflow: list = field(default_factory=lambda: [
        "识别对立视角",
        "调用视角A智能体（创新探索）",
        "调用视角B智能体（风险控制）",
        "综合裁决"
    ])
    mode2_workflow: list = field(default_factory=lambda: [
        "生成阶段（创意生成智能体）",
        "挑剔阶段（逻辑审查智能体）",
        "融合阶段（综合重写智能体）"
    ])
    mode3_workflow: list = field(default_factory=lambda: [
        "蓝图设计阶段（心智社会智能体）",
        "可行性挑战阶段（代码执行智能体）",
        "融合实现阶段（编辑器智能体）"
    ])


@dataclass
class LogConfig:
    """日志配置"""
    max_size_mb: float = 10.0
    max_age_days: int = 30
    enable_backup: bool = True
    enable_rotation: bool = True
    sensitive_patterns: list = field(default_factory=lambda: [
        (r'api[_-]?key["\']?\s*[:=]\s*["\']?[\w\-]{20,}["\']?', '[API_KEY]'),
        (r'password["\']?\s*[:=]\s*["\']?[^\s"\']{6,}["\']?', '[PASSWORD]'),
        (r'token["\']?\s*[:=]\s*["\']?[\w\-]{20,}["\']?', '[TOKEN]'),
        (r'secret["\']?\s*[:=]\s*["\']?[\w\-]{20,}["\']?', '[SECRET]'),
    ])


@dataclass
class AgentConfig:
    """智能体配置"""
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
    """元认知技能全局配置"""
    enable_game_theory: bool = True
    enable_statistics: bool = True
    enable_monitoring: bool = False
    enable_self_update: bool = True
    response_preview_length: int = 200
    keywords: GameTheoryKeywords = field(default_factory=GameTheoryKeywords)
    complexity: ComplexityConfig = field(default_factory=ComplexityConfig)
    workflows: GameTheoryWorkflows = field(default_factory=GameTheoryWorkflows)
    knowledge_graph: KnowledgeGraphConfig = field(default_factory=KnowledgeGraphConfig)
    log: LogConfig = field(default_factory=LogConfig)
    agents: AgentConfig = field(default_factory=AgentConfig)


def get_config() -> MetaCognitionConfig:
    """获取配置实例（支持环境变量覆盖）"""
    config = MetaCognitionConfig()

    if os.getenv("META_COGNITION_ENABLE_GT"):
        config.enable_game_theory = os.getenv("META_COGNITION_ENABLE_GT").lower() == "true"

    if os.getenv("META_COGNITION_ENABLE_STATS"):
        config.enable_statistics = os.getenv("META_COGNITION_ENABLE_STATS").lower() == "true"

    if os.getenv("META_COGNITION_ENABLE_MONITORING"):
        config.enable_monitoring = os.getenv("META_COGNITION_ENABLE_MONITORING").lower() == "true"

    if os.getenv("META_COGNITION_ENABLE_SELF_UPDATE"):
        config.enable_self_update = os.getenv("META_COGNITION_ENABLE_SELF_UPDATE").lower() == "true"

    if os.getenv("META_COGNITION_PREVIEW_LENGTH"):
        try:
            config.response_preview_length = int(os.getenv("META_COGNITION_PREVIEW_LENGTH"))
        except ValueError:
            pass

    return config


CONFIG = get_config()

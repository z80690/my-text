# -*- coding: utf-8 -*-
"""
Meta-Cognition Skill - 智能体团队调度系统

🚀 v3.0 内生重构版！

重构目标：
1. 将所有分散的脚本能力整合到一个统一的插件架构中
2. 保持所有原有功能不衰减，特别是自动触发功能
3. 实现完全内生的插件，无需外部脚本依赖

核心特性：
- 导入即启动 - 模块导入时自动启动守护进程
- 全自动触发 - 无需手动调用
- 完全无感 - 后台自动运行
- 内生架构 - 所有能力内置，无外部脚本依赖
"""

__version__ = "3.0.0"

# ============================================
# 从统一的 meta_cognition 模块导出所有接口
# ============================================

# 核心类
from .meta_cognition import (
    MetaCognition,
    get_meta_cognition,
    __version__
)

# 钩子函数（向后兼容）
from .meta_cognition import (
    pre_task_hook,
    detect_task_mode,
    get_scheduling_decision,
    get_task_recommendations,
    post_task_hook,
    update_session,
    get_statistics,
    get_recent_sessions,
    get_session_by_id,
    export_sessions
)

# 守护进程模块（导入即启动！全自动！）
from .meta_cognition import (
    get_daemon_manager,
    auto_submit,
    auto_complete,
    auto_get_statistics,
    auto_get_status,
    auto_get_recent
)

HAS_DAEMON = True

# ============================================
# 配置类导出（供高级用户自定义配置）
# ============================================

from .meta_cognition import (
    MetaCognitionConfig,
    GameTheoryKeywords,
    KnowledgeGraphConfig,
    ComplexityConfig,
    GameTheoryWorkflows,
    LogConfig,
    TriggerConfig,
    AgentConfig,
    TriggerType
)

__all__ = [
    # 版本
    "__version__",
    # 核心类
    "MetaCognition",
    "get_meta_cognition",
    # 配置类
    "MetaCognitionConfig",
    "GameTheoryKeywords",
    "KnowledgeGraphConfig",
    "ComplexityConfig",
    "GameTheoryWorkflows",
    "LogConfig",
    "TriggerConfig",
    "AgentConfig",
    "TriggerType",
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
    # 守护进程（导入即启动！）
    "get_daemon_manager",
    "auto_submit",
    "auto_complete",
    "auto_get_statistics",
    "auto_get_status",
    "auto_get_recent",
    "HAS_DAEMON"
]

# ============================================
# 自动启动验证
# ============================================

print(f"[Meta-Cognition] v{__version__} 内生重构版已加载")
print("[Meta-Cognition] 所有功能已整合到单一模块中")
print("[Meta-Cognition] 自动触发系统已启动")
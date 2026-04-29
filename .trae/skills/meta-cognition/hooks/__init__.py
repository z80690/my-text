# -*- coding: utf-8 -*-
"""Meta-Cognition Hooks 模块初始化"""

from .pre_task_hook import (
    pre_task_hook,
    detect_task_mode,
    get_scheduling_decision,
    get_task_recommendations
)

from .post_task_hook import (
    post_task_hook,
    update_session,
    get_statistics,
    get_recent_sessions,
    get_session_by_id,
    export_sessions
)

from .utils import (
    load_log,
    save_log,
    generate_session_id,
    get_current_timestamp,
    calculate_duration_ms,
    filter_sensitive_info,
    truncate_text,
    rotate_log_if_needed,
    backup_log
)

__all__ = [
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
    "load_log",
    "save_log",
    "generate_session_id",
    "get_current_timestamp",
    "calculate_duration_ms",
    "filter_sensitive_info",
    "truncate_text",
    "rotate_log_if_needed",
    "backup_log"
]

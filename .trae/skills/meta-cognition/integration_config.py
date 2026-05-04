# -*- coding: utf-8 -*-
"""
meta-cognition 集成配置 - 确保钩子函数正确集成到调度流程

核心功能：
1. 任务开始时自动调用 pre_task_hook
2. 任务结束时自动调用 post_task_hook
3. 读取历史会话信息供当前任务参考
4. 完全无感，后台静默执行
5. 动态频率调整：工作时高频，空闲时低频
6. IDE关闭时自动停止守护进程
"""

import time
import threading
import atexit
import signal
from typing import Dict, Any, Optional, Callable
from .meta_cognition import (
    MetaCognition,
    get_meta_cognition,
    pre_task_hook,
    post_task_hook,
    get_recent_sessions,
    get_session_by_id
)

# 全局会话追踪
_current_session_id = None
_session_lock = threading.Lock()

def execute_with_hooks(task_description: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    带钩子的任务执行入口
    
    在任务执行前自动调用 pre_task_hook：
    - 读取历史会话信息
    - 检测任务模式
    - 记录任务开始
    - 增加任务计数（进入工作模式）
    
    返回：包含 session_id 和调度决策的字典
    """
    global _current_session_id
    
    # 增加任务计数（标记正在工作）
    _increment_task_count()
    
    # 读取历史会话（您要求的"开始时读取"）
    recent_sessions = get_recent_sessions(limit=5)
    context = context or {}
    context["history"] = recent_sessions
    
    # 调用前置钩子
    result = pre_task_hook(task_description, context)
    
    with _session_lock:
        _current_session_id = result.get("session_id")
    
    print(f"[Meta-Cognition] 任务开始 - Session ID: {_current_session_id}")
    print(f"[Meta-Cognition] 检测模式: {result.get('mode')}")
    
    return result

def complete_with_hooks(result: str = "success", agents_used: Optional[list] = None, 
                        response_preview: Optional[str] = None, duration_ms: Optional[int] = None,
                        error: Optional[str] = None) -> Dict[str, Any]:
    """
    带钩子的任务完成入口
    
    在任务完成后自动调用 post_task_hook：
    - 记录任务结果
    - 更新统计信息
    - 触发主动学习
    - 减少任务计数（退出工作模式）
    
    返回：完成状态
    """
    global _current_session_id
    
    with _session_lock:
        session_id = _current_session_id
    
    if not session_id:
        print("[Meta-Cognition][WARN] 没有当前会话，跳过后置钩子")
        return {"status": "skipped", "reason": "no session"}
    
    print(f"[Meta-Cognition] 任务完成 - Session ID: {session_id}, 结果: {result}")
    
    # 调用后置钩子（您要求的"结束时写入"）
    result = post_task_hook(
        session_id=session_id,
        result=result,
        agents_used=agents_used,
        response_preview=response_preview,
        duration_ms=duration_ms,
        error=error
    )
    
    with _session_lock:
        _current_session_id = None
    
    # 减少任务计数（标记任务完成）
    _decrement_task_count()
    
    return result

def get_current_session_id() -> Optional[str]:
    """获取当前会话ID"""
    with _session_lock:
        return _current_session_id

# ============================================
# 守护进程模式 - 自动监控所有任务
# ============================================

# 全局Meta-Cognition实例
_meta_cognition_instance = None
_daemon_thread = None
_daemon_running = False

# 任务状态追踪
_task_count = 0
_task_lock = threading.Lock()

def _start_daemon():
    """启动守护进程"""
    global _meta_cognition_instance, _daemon_thread, _daemon_running
    
    if _daemon_running:
        print("[Meta-Cognition Daemon] 守护进程已在运行")
        return
    
    print("[Meta-Cognition Daemon] 启动守护进程...")
    
    # 创建Meta-Cognition实例并启动
    _meta_cognition_instance = get_meta_cognition()
    _meta_cognition_instance.start()
    
    _daemon_running = True
    print("[Meta-Cognition Daemon] 守护进程启动完成")

def _stop_daemon():
    """停止守护进程"""
    global _meta_cognition_instance, _daemon_running
    
    if not _daemon_running:
        print("[Meta-Cognition Daemon] 守护进程未运行")
        return
    
    print("[Meta-Cognition Daemon] 停止守护进程...")
    
    if _meta_cognition_instance:
        _meta_cognition_instance.stop()
    
    _daemon_running = False
    print("[Meta-Cognition Daemon] 守护进程停止完成")

def is_daemon_running() -> bool:
    """检查守护进程是否运行"""
    return _daemon_running

def get_daemon_status() -> Dict[str, Any]:
    """获取守护进程状态"""
    status = {"running": _daemon_running}
    if _meta_cognition_instance:
        status.update(_meta_cognition_instance.get_status())
    with _task_lock:
        status["active_tasks"] = _task_count
        status["is_working"] = _task_count > 0
    return status

def _increment_task_count():
    """增加任务计数（标记正在工作）"""
    global _task_count
    with _task_lock:
        _task_count += 1
        if _task_count == 1:
            print("[Meta-Cognition Daemon] 进入工作模式 - 高频响应")

def _decrement_task_count():
    """减少任务计数（标记任务完成）"""
    global _task_count
    with _task_lock:
        _task_count = max(0, _task_count - 1)
        if _task_count == 0:
            print("[Meta-Cognition Daemon] 进入空闲模式 - 低频响应")

def is_working() -> bool:
    """判断是否正在执行任务"""
    with _task_lock:
        return _task_count > 0

# 记录最近一次任务开始时间
_last_task_start = 0
_task_interval = 0.1  # 100ms间隔

def _auto_detect_task(task_description: str):
    """自动检测任务并触发钩子"""
    global _last_task_start
    
    now = time.time()
    if now - _last_task_start < _task_interval:
        return  # 防止重复触发
    
    _last_task_start = now
    
    # 自动调用前置钩子
    execute_with_hooks(task_description)

# ============================================
# IDE关闭时自动停止守护进程
# ============================================

def _handle_exit(signum=None, frame=None):
    """处理进程退出信号"""
    print(f"[Meta-Cognition Daemon] 收到退出信号 ({signum})，准备停止...")
    _stop_daemon()

# 注册退出处理
atexit.register(_handle_exit)

# 注册信号处理（Unix/Linux）
try:
    signal.signal(signal.SIGTERM, _handle_exit)
    signal.signal(signal.SIGINT, _handle_exit)
except AttributeError:
    # Windows不支持这些信号，忽略
    pass

# 导出接口
__all__ = [
    "execute_with_hooks",
    "complete_with_hooks",
    "get_current_session_id",
    "_auto_detect_task",
    "_start_daemon",
    "_stop_daemon",
    "is_daemon_running",
    "get_daemon_status",
    "is_working"
]

# 自动启动守护进程
_start_daemon()

print("[Meta-Cognition Integration] 集成配置已加载")
print("[Meta-Cognition Integration] execute_with_hooks / complete_with_hooks 已就绪")
print("[Meta-Cognition Integration] 守护进程模式已启用")
print("[Meta-Cognition Integration] IDE关闭时将自动停止守护进程")

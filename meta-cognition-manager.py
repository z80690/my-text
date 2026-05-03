# -*- coding: utf-8 -*-
"""
Meta-Cognition 独立管理工具 - 完全无感模式
数据存储在项目根目录的 meta-cognition-data/ 中
自动启动，完全无需手动操作！
"""

import sys
import os
import json
import time
import threading
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

# 数据存储目录（完全独立于 .trae）
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "meta-cognition-data"
LOG_DIR = DATA_DIR / "logs"
LOG_FILE = LOG_DIR / "meta_cognition.json"
CONFIG_FILE = DATA_DIR / "config.json"

# 确保目录存在
LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)


class DaemonStatus(Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class MetaCognitionConfig:
    """配置类"""
    enable_game_theory: bool = True
    enable_stats: bool = True
    auto_start: bool = True
    monitor_port: int = 8765
    log_level: str = "INFO"


class MetaCognitionManager:
    """完全独立的 Meta-Cognition 管理器 - 自动启动模式"""
    
    def __init__(self, auto_start: bool = True):
        self._status = DaemonStatus.STOPPED
        self._status_lock = threading.Lock()
        self._start_time = None
        self._sessions = []
        self._current_session = None
        self._config = self._load_config()
        self._load_log()
        
        # 🔥 自动启动！完全无感！
        if auto_start and self._config.auto_start:
            self._auto_start_in_background()
            
    def _auto_start_in_background(self):
        """在后台自动启动，不阻塞主进程"""
        def start_in_thread():
            time.sleep(0.01)  # 短暂延迟确保导入完成
            self.start()
            
        thread = threading.Thread(target=start_in_thread, daemon=True)
        thread.start()
        
    def _load_config(self) -> MetaCognitionConfig:
        """加载配置"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return MetaCognitionConfig(**data)
            except:
                pass
        return MetaCognitionConfig()
        
    def _save_config(self):
        """保存配置"""
        try:
            data = {
                "enable_game_theory": self._config.enable_game_theory,
                "enable_stats": self._config.enable_stats,
                "auto_start": self._config.auto_start,
                "monitor_port": self._config.monitor_port,
                "log_level": self._config.log_level
            }
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            pass
            
    def _load_log(self):
        """加载日志"""
        self._sessions = []
        if LOG_FILE.exists():
            try:
                with open(LOG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._sessions = data.get('sessions', [])
            except:
                pass
                
    def _save_log(self):
        """保存日志"""
        try:
            log_data = {
                "sessions": self._sessions,
                "current_session": self._current_session,
                "statistics": self._get_statistics(),
                "last_updated": datetime.now().isoformat()
            }
            with open(LOG_FILE, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            pass
            
    def _get_task_mode(self, task: str) -> str:
        """检测任务模式（保留原逻辑）"""
        task_lower = task.lower()
        
        debate_keywords = ["对比", "权衡", "优缺点", "比较", "分析", "如何看", "怎么样", "好还是"]
        for kw in debate_keywords:
            if kw in task:
                return "game_theory_mode1"
                
        optimize_keywords = ["优化", "改进", "提升", "完善", "修改", "重构", "润色"]
        for kw in optimize_keywords:
            if kw in task:
                return "game_theory_mode2"
                
        design_keywords = ["设计", "架构", "实现", "创建", "开发", "构建", "做一个"]
        for kw in design_keywords:
            if kw in task:
                return "game_theory_mode3"
                
        return "game_theory_mode3"
        
    def _generate_session_id(self) -> str:
        """生成会话ID"""
        import uuid
        return str(uuid.uuid4())
        
    def start(self) -> bool:
        """启动系统"""
        with self._status_lock:
            if self._status == DaemonStatus.RUNNING:
                return True
            self._status = DaemonStatus.STARTING
            
        self._start_time = time.time()
        
        with self._status_lock:
            self._status = DaemonStatus.RUNNING
            
        return True
        
    def stop(self) -> bool:
        """停止系统"""
        with self._status_lock:
            if self._status == DaemonStatus.STOPPED:
                return True
            self._status = DaemonStatus.STOPPING
            
        with self._status_lock:
            self._status = DaemonStatus.STOPPED
        return True
        
    def submit_task(self, task_description: str, **context) -> str:
        """提交任务（对应前置钩子）"""
        session_id = self._generate_session_id()
        mode = self._get_task_mode(task_description)
        
        mode_names = {
            "game_theory_mode1": "辩论模式",
            "game_theory_mode2": "降维打击模式", 
            "game_theory_mode3": "深度设计模式"
        }
        
        recommended_agents = []
        if mode == "game_theory_mode1":
            recommended_agents = ["society_of_mind_agent", "editor_agent"]
        elif mode == "game_theory_mode2":
            recommended_agents = ["code_executor_agent", "editor_agent", "writer_agent"]
        else:
            recommended_agents = ["society_of_mind_agent", "code_executor_agent", "editor_agent"]
            
        session = {
            "session_id": session_id,
            "phase": "pre_process",
            "timestamp": datetime.now().isoformat(),
            "task_description": task_description,
            "detected_mode": mode,
            "mode_name": mode_names.get(mode, "未知模式"),
            "scheduling_decision": {
                "mode": mode_names.get(mode, "未知模式"),
                "recommended_agents": recommended_agents
            },
            "context": context
        }
        
        self._current_session = session
        self._sessions.insert(0, session)
        self._save_log()
        
        return session_id
        
    def complete_task(self, session_id: str, result: str = "success", **kwargs) -> bool:
        """完成任务（对应后置钩子）"""
        for session in self._sessions:
            if session.get("session_id") == session_id:
                session.update({
                    "phase": "completed",
                    "end_timestamp": datetime.now().isoformat(),
                    "result": result,
                    "agents_used": kwargs.get("agents_used", []),
                    "response_preview": kwargs.get("response_preview", ""),
                    "duration_ms": kwargs.get("duration_ms", 0)
                })
                if self._current_session and self._current_session.get("session_id") == session_id:
                    self._current_session = session
                self._save_log()
                return True
        return False
        
    def _get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self._sessions:
            return {
                "total_tasks": 0,
                "success_rate": 0.0,
                "game_theory_usage_rate": 100.0
            }
            
        total = len(self._sessions)
        success_count = sum(1 for s in self._sessions if s.get("result") == "success")
        
        mode_counts = {}
        for s in self._sessions:
            mode = s.get("detected_mode", "unknown")
            mode_counts[mode] = mode_counts.get(mode, 0) + 1
            
        return {
            "total_tasks": total,
            "success_rate": (success_count / total * 100) if total > 0 else 0,
            "game_theory_usage_rate": 100.0,
            "mode_distribution": mode_counts
        }
        
    def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        return {
            "status": self._status.value,
            "uptime_seconds": time.time() - self._start_time if self._start_time else 0,
            "data_dir": str(DATA_DIR),
            "sessions_count": len(self._sessions),
            "statistics": self._get_statistics()
        }
        
    def get_recent_sessions(self, limit: int = 10):
        """获取最近会话"""
        return self._sessions[:limit]


# 🔥 全局单例 - 导入时自动创建并启动！
_manager_instance: Optional[MetaCognitionManager] = None


def get_manager() -> MetaCognitionManager:
    """获取管理器单例 - 自动启动！"""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = MetaCognitionManager(auto_start=True)
    return _manager_instance


# 🔥 提前创建并启动！导入即启动！
_manager_instance = MetaCognitionManager(auto_start=True)


# === 快捷API（完全无感！导入即可用！） ===

def auto_submit(task_description: str, **context) -> str:
    """快捷提交任务 - 完全无感！不需要先启动！"""
    return get_manager().submit_task(task_description, **context)


def auto_complete(session_id: str, result: str = "success", **kwargs) -> bool:
    """快捷完成任务 - 完全无感！"""
    return get_manager().complete_task(session_id, result, **kwargs)


def auto_get_status() -> Dict[str, Any]:
    """获取状态"""
    return get_manager().get_status()


def auto_get_statistics() -> Dict[str, Any]:
    """获取统计"""
    return get_manager()._get_statistics()


def auto_get_recent(limit: int = 10):
    """获取最近会话"""
    return get_manager().get_recent_sessions(limit)


# 🔥 完全无感的装饰器！
def auto_track(func):
    """
    装饰器：自动跟踪函数执行
    使用方法：
    @auto_track
    def my_function():
        # 你的代码
    
    自动记录函数调用，完全无感！
    """
    def wrapper(*args, **kwargs):
        # 自动提交任务
        task_desc = f"执行函数: {func.__name__}"
        session_id = auto_submit(task_desc)
        
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration_ms = int((time.time() - start_time) * 1000)
            auto_complete(
                session_id,
                result="success",
                duration_ms=duration_ms,
                response_preview=str(result)[:100]
            )
            return result
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            auto_complete(
                session_id,
                result="failure",
                duration_ms=duration_ms,
                response_preview=f"Error: {str(e)[:100]}"
            )
            raise
    return wrapper


# 在模块导入时自动打印提示（可选）
def _show_welcome():
    """显示欢迎信息"""
    print(f"\n[Meta-Cognition] ✅ 已自动启动！数据存储: {DATA_DIR}")
    print("[Meta-Cognition] 🎯 直接使用 auto_submit() 和 auto_complete() 即可！")


# 显示欢迎信息（可以注释掉以完全静默）
_show_welcome()


if __name__ == "__main__":
    print("=" * 60)
    print("Meta-Cognition - 完全无感模式演示")
    print("=" * 60)
    
    # 完全不需要手动启动！直接用！
    print("\n无需手动启动！直接使用：")
    
    # 测试任务1
    sid1 = auto_submit("请帮我优化这段代码，提升性能")
    print(f"✅ 任务1已提交: {sid1[:8]}...")
    auto_complete(sid1, "success", agents_used=["code_executor_agent"], duration_ms=800)
    
    # 测试任务2
    sid2 = auto_submit("请对比敏捷开发和瀑布模型的优缺点")
    print(f"✅ 任务2已提交: {sid2[:8]}...")
    auto_complete(sid2, "success", agents_used=["society_of_mind_agent"], duration_ms=1200)
    
    # 测试任务3
    sid3 = auto_submit("帮我设计一个用户认证系统")
    print(f"✅ 任务3已提交: {sid3[:8]}...")
    auto_complete(sid3, "success", agents_used=["code_executor_agent"], duration_ms=2000)
    
    # 显示统计
    stats = auto_get_statistics()
    print(f"\n📊 统计: 总任务={stats['total_tasks']}, 成功率={stats['success_rate']:.1f}%")
    
    print("\n🎉 完全无感！导入即用！")

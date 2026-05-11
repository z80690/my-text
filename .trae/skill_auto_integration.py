# -*- coding: utf-8 -*-
"""
Skills 自动化集成系统 v1.0
整合追踪、日志、建议三大功能，为所有 Skills 提供自动化支持
自动触发钩子，无需手动调用
"""

import json
import time
import functools
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict


@dataclass
class SkillExecution:
    skill_id: str
    action: str
    start_time: str
    end_time: Optional[str] = None
    duration_ms: float = 0
    status: str = "running"
    input_data: Optional[Dict] = None
    output_data: Optional[Dict] = None
    error: Optional[str] = None


class AutoHookIntegration:
    """自动钩子集成模块 - 关键！连接 Skill 执行和钩子系统"""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if AutoHookIntegration._initialized:
            return
        AutoHookIntegration._initialized = True
        self._hook_system = None
        self._init_hooks()

    def _init_hooks(self):
        """延迟导入并初始化钩子系统"""
        try:
            from auto_hook_system import get_hook_system, initialize_default_hooks
            initialize_default_hooks()
            self._hook_system = get_hook_system()
        except Exception as e:
            print(f"⚠️ 钩子系统初始化失败: {e}")
            self._hook_system = None

    def trigger_pre_hook(self, skill_id: str, action: str, tool_type: str = "skill"):
        """触发前置钩子"""
        if self._hook_system is None:
            return
        try:
            self._hook_system.trigger_hooks('pre_tool_call', {
                'skill_id': skill_id,
                'action': action,
                'tool_type': tool_type,
                'phase': 'pre'
            })
        except Exception as e:
            print(f"⚠️ 前置钩子触发失败: {e}")

    def trigger_post_hook(self, skill_id: str, action: str, status: str, duration_ms: float,
                         tool_type: str = "skill", output_data: Dict = None):
        """触发后置钩子"""
        if self._hook_system is None:
            return
        try:
            self._hook_system.trigger_hooks('post_tool_call', {
                'skill_id': skill_id,
                'action': action,
                'status': status,
                'duration_ms': duration_ms,
                'tool_type': tool_type,
                'phase': 'post',
                'output': output_data
            })
        except Exception as e:
            print(f"⚠️ 后置钩子触发失败: {e}")

    def trigger_skill_load_hook(self, skill_id: str, action: str, tool_type: str = "skill"):
        """触发Skill加载钩子"""
        if self._hook_system is None:
            return
        try:
            self._hook_system.trigger_hooks('post_skill_load', {
                'skill_id': skill_id,
                'action': action,
                'tool_type': tool_type,
                'phase': 'load'
            })
        except Exception as e:
            print(f"⚠️ Skill加载钩子触发失败: {e}")


class AutoTracker:
    """自动追踪模块"""

    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.logs_dir = self.base_dir / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        self._current_session: List[SkillExecution] = []

    def start_tracking(self, skill_id: str, action: str, input_data: Dict = None) -> SkillExecution:
        execution = SkillExecution(
            skill_id=skill_id,
            action=action,
            start_time=datetime.now().isoformat(),
            input_data=input_data
        )
        self._current_session.append(execution)
        return execution

    def end_tracking(self, execution: SkillExecution, status: str, output_data: Dict = None, error: str = None):
        execution.end_time = datetime.now().isoformat()
        start = datetime.fromisoformat(execution.start_time)
        end = datetime.fromisoformat(execution.end_time)
        execution.duration_ms = (end - start).total_seconds() * 1000
        execution.status = status
        execution.output_data = output_data
        execution.error = error

        self._save_to_log(execution)
        self._update_tracker_stats(execution)

    def _save_to_log(self, execution: SkillExecution):
        log_file = self.logs_dir / f"skill_executions_{datetime.now().strftime('%Y-%m-%d')}.json"
        records = []
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    records = json.load(f)
            except:
                records = []

        records.append(asdict(execution))

        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

    def _update_tracker_stats(self, execution: SkillExecution):
        try:
            from tool_usage_tracker import track_skill_call
            track_skill_call(
                tool_name=execution.skill_id,
                action=execution.action,
                status=execution.status,
                duration_ms=execution.duration_ms,
                error=execution.error
            )
        except:
            pass

    def get_session_stats(self) -> Dict:
        if not self._current_session:
            return {"total": 0, "success": 0, "failed": 0, "avg_duration_ms": 0}

        success = sum(1 for e in self._current_session if e.status == "success")
        failed = sum(1 for e in self._current_session if e.status == "failed")
        total_duration = sum(e.duration_ms for e in self._current_session)

        return {
            "total": len(self._current_session),
            "success": success,
            "failed": failed,
            "avg_duration_ms": total_duration / len(self._current_session)
        }


class AutoLogger:
    """自动日志模块"""

    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.logs_dir = self.base_dir / "logs"
        self.logs_dir.mkdir(exist_ok=True)

    def log_event(self, event_type: str, skill_id: str, data: Dict, level: str = "INFO"):
        log_file = self.logs_dir / f"auto_events_{datetime.now().strftime('%Y-%m-%d')}.md"

        timestamp = datetime.now().strftime('%H:%M:%S')
        level_emoji = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}.get(level, "ℹ️")

        entry = f"\n### {timestamp} [{level_emoji} {level}] {event_type}\n\n**Skill**: `{skill_id}`\n\n```json\n{json.dumps(data, ensure_ascii=False, indent=2)}\n```\n---\n"

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(entry)

    def log_skill_start(self, skill_id: str, action: str, input_data: Dict):
        self.log_event("SKILL_START", skill_id, {
            "action": action,
            "input": input_data
        }, "INFO")

    def log_skill_end(self, skill_id: str, action: str, status: str, duration_ms: float, output_data: Dict = None):
        level = "SUCCESS" if status == "success" else "ERROR"
        self.log_event("SKILL_END", skill_id, {
            "action": action,
            "status": status,
            "duration_ms": round(duration_ms, 2),
            "output": output_data
        }, level)

    def log_hook_trigger(self, trigger: str, action: str, skill_id: str, result: Dict):
        self.log_event("HOOK_TRIGGER", skill_id, {
            "trigger": trigger,
            "action": action,
            "result": result
        }, "INFO")


class SmartSuggester:
    """智能建议引擎"""

    SKILL_RELATIONSHIPS = {
        "auto-debug": {
            "next": ["auto-refactor", "auto-doc"],
            "reason": "调试完成后，建议重构代码或生成文档"
        },
        "auto-doc": {
            "next": ["auto-hook", "auto-refactor"],
            "reason": "生成文档后，建议设置更新提醒或重构代码"
        },
        "auto-refactor": {
            "next": ["auto-debug", "auto-doc"],
            "reason": "重构完成后，建议测试或更新文档"
        },
        "auto-hook": {
            "next": ["local-privacy", "auto-doc"],
            "reason": "设置钩子后，建议配置隐私保护或生成文档"
        },
        "local-privacy": {
            "next": ["auto-hook", "auto-debug"],
            "reason": "隐私配置后，建议设置钩子或测试功能"
        },
        "tool-usage-tracker": {
            "next": ["auto-hook", "auto-doc"],
            "reason": "查看统计后，建议设置自动追踪钩子或生成报告"
        }
    }

    WORKFLOW_SUGGESTIONS = {
        "debug_flow": ["auto-debug", "auto-refactor", "auto-doc"],
        "doc_flow": ["auto-doc", "auto-hook", "local-privacy"],
        "refactor_flow": ["auto-refactor", "auto-debug", "auto-doc"],
        "setup_flow": ["auto-hook", "tool-usage-tracker", "local-privacy"]
    }

    def __init__(self):
        self._execution_history: List[str] = []

    def record_execution(self, skill_id: str):
        self._execution_history.append(skill_id)

    def get_next_suggestions(self, current_skill: str) -> List[Dict]:
        suggestions = []

        if current_skill in self.SKILL_RELATIONSHIPS:
            relation = self.SKILL_RELATIONSHIPS[current_skill]
            for next_skill in relation["next"]:
                suggestions.append({
                    "skill_id": next_skill,
                    "reason": relation["reason"],
                    "priority": "high" if next_skill == relation["next"][0] else "medium"
                })

        return suggestions

    def get_workflow_suggestion(self) -> Dict:
        if not self._execution_history:
            return {
                "workflow": "setup_flow",
                "suggestion": "建议从 auto-hook 开始设置自动化",
                "steps": self.WORKFLOW_SUGGESTIONS["setup_flow"]
            }

        recent = self._execution_history[-3:]
        for workflow_name, steps in self.WORKFLOW_SUGGESTIONS.items():
            if any(s in recent for s in steps):
                remaining = [s for s in steps if s not in recent]
                if remaining:
                    return {
                        "workflow": workflow_name,
                        "suggestion": f"建议继续完成 {workflow_name}",
                        "remaining_steps": remaining
                    }

        return {
            "workflow": "custom",
            "suggestion": "根据当前进度，建议继续使用相关 Skills",
            "recent_history": recent
        }

    def get_context_aware_suggestion(self, context: Dict) -> str:
        time_of_day = datetime.now().hour
        recent_skills = self._execution_history[-5:] if self._execution_history else []

        if 9 <= time_of_day < 12:
            return "🌅 上午好！建议使用 auto-debug 或 auto-refactor 进行代码优化"
        elif 14 <= time_of_day < 18:
            return "☀️ 下午好！建议使用 auto-doc 生成文档或 auto-hook 设置自动化"
        elif 18 <= time_of_day < 22:
            return "🌙 晚上好！建议使用 tool-usage-tracker 查看今日统计"

        return "💡 建议使用 auto-hook 设置自动化钩子，提升开发效率"


class SkillExecutor:
    """Skill 执行包装器 - 自动集成追踪、日志、建议、钩子"""

    def __init__(self):
        self.tracker = AutoTracker()
        self.logger = AutoLogger()
        self.suggester = SmartSuggester()
        self.hook_integration = AutoHookIntegration()  # 关键：自动钩子集成

    def execute(self, skill_id: str, action: str, func: Callable, *args, **kwargs) -> Any:
        input_data = {"args": str(args)[:200], "kwargs": str(kwargs)[:200]}

        # 触发前置钩子
        self.hook_integration.trigger_pre_hook(skill_id, action)

        # 开始追踪
        execution = self.tracker.start_tracking(skill_id, action, input_data)
        self.logger.log_skill_start(skill_id, action, input_data)

        try:
            # 执行实际函数
            result = func(*args, **kwargs)

            # 结束追踪
            self.tracker.end_tracking(execution, "success", {"result": str(result)[:500]})
            self.logger.log_skill_end(skill_id, action, "success", execution.duration_ms)

            # 触发后置钩子
            self.hook_integration.trigger_post_hook(
                skill_id, action, "success", execution.duration_ms,
                output_data={"result": str(result)[:200]}
            )

            # 触发Skill加载钩子
            self.hook_integration.trigger_skill_load_hook(skill_id, action)

            # 记录执行历史
            self.suggester.record_execution(skill_id)
            suggestions = self.suggester.get_next_suggestions(skill_id)

            self._show_suggestions(suggestions)

            return result

        except Exception as e:
            # 失败追踪
            self.tracker.end_tracking(execution, "failed", error=str(e))
            self.logger.log_skill_end(skill_id, action, "failed", execution.duration_ms, {"error": str(e)})

            # 触发失败钩子
            self.hook_integration.trigger_post_hook(
                skill_id, action, "failed", execution.duration_ms,
                output_data={"error": str(e)}
            )

            raise

    def _show_suggestions(self, suggestions: List[Dict]):
        if suggestions:
            print("\n💡 智能建议:")
            for i, s in enumerate(suggestions[:3], 1):
                priority_emoji = "🔥" if s["priority"] == "high" else "📌"
                print(f"  {i}. {priority_emoji} 使用 {s['skill_id']}")
                print(f"     └─ {s['reason']}")


def with_auto_tracking(skill_id: str, action: str = "execute"):
    """装饰器：为任何函数添加自动追踪和钩子"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            executor = SkillExecutor()
            return executor.execute(skill_id, action, func, *args, **kwargs)
        return wrapper
    return decorator


_executor: Optional[SkillExecutor] = None


def get_executor() -> SkillExecutor:
    global _executor
    if _executor is None:
        _executor = SkillExecutor()
    return _executor


def execute_skill(skill_id: str, action: str, func: Callable, *args, **kwargs) -> Any:
    """便捷函数：执行 Skill 并自动追踪"""
    return get_executor().execute(skill_id, action, func, *args, **kwargs)


def get_today_summary() -> str:
    """获取今日摘要"""
    executor = get_executor()
    stats = executor.tracker.get_session_stats()
    workflow = executor.suggester.get_workflow_suggestion()
    context = executor.suggester.get_context_aware_suggestion({})

    lines = [
        "# 📊 今日 Skills 使用摘要",
        "",
        f"**总执行**: {stats['total']} 次",
        f"**成功**: {stats['success']} 次",
        f"**失败**: {stats['failed']} 次",
        f"**平均耗时**: {stats['avg_duration_ms']:.2f} ms",
        "",
        "## 💡 智能建议",
        "",
        f"{context}",
        "",
        f"**推荐工作流**: {workflow.get('workflow', 'N/A')}",
        f"**建议**: {workflow.get('suggestion', 'N/A')}",
    ]

    return "\n".join(lines)


if __name__ == '__main__':
    print("🧪 测试自动追踪和钩子功能")
    print("="*60)

    @with_auto_tracking("test-skill", "demo")
    def test_function(x: int, y: int) -> int:
        time.sleep(0.1)
        return x + y

    result = test_function(10, 20)
    print(f"\n✅ 测试结果: {result}")

    print("\n" + get_today_summary())

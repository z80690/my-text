# -*- coding: utf-8 -*-
"""
自动化钩子管理系统 v1.0
为所有 Skills 自动挂载钩子，实现自动触发
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from enum import Enum
import threading


class HookTrigger(Enum):
    PRE_TOOL_CALL = "pre_tool_call"      # 工具调用前
    POST_TOOL_CALL = "post_tool_call"    # 工具调用后
    PRE_SKILL_LOAD = "pre_skill_load"    # Skill加载前
    POST_SKILL_LOAD = "post_skill_load"  # Skill加载后
    PRE_SESSION_END = "pre_session_end"  # 会话结束前
    POST_SESSION_START = "post_session_start"  # 会话开始后


class HookAction(Enum):
    TRACK_USAGE = "track_usage"          # 追踪使用
    LOG_EVENT = "log_event"             # 记录日志
    VALIDATE_PARAMS = "validate_params" # 验证参数
    NOTIFY = "notify"                   # 通知
    AUTO_SUGGEST = "auto_suggest"       # 自动建议


@dataclass
class HookConfig:
    trigger: str
    action: str
    skill_id: Optional[str] = None
    enabled: bool = True
    config: Optional[Dict] = None


@dataclass
class HookEvent:
    timestamp: str
    trigger: str
    action: str
    skill_id: Optional[str]
    data: Dict[str, Any]
    result: Optional[Dict] = None


class AutoHookSystem:
    BASE_DIR = Path(__file__).parent
    HOOKS_DIR = BASE_DIR / "hooks"
    LOGS_DIR = BASE_DIR / "logs"

    def __init__(self):
        self.HOOKS_DIR.mkdir(exist_ok=True)
        self.LOGS_DIR.mkdir(exist_ok=True)
        self._hooks: Dict[str, List[HookConfig]] = {}
        self._handlers: Dict[str, Callable] = {}
        self._lock = threading.Lock()
        self._event_log: List[HookEvent] = []
        self._load_hooks()

    def _load_hooks(self):
        hook_file = self.HOOKS_DIR / "hook_config.json"
        if hook_file.exists():
            with open(hook_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for h in data.get('hooks', []):
                    trigger = h['trigger']
                    if trigger not in self._hooks:
                        self._hooks[trigger] = []
                    self._hooks[trigger].append(HookConfig(**h))

    def _save_hooks(self):
        hook_file = self.HOOKS_DIR / "hook_config.json"
        hooks_list = []
        for trigger, hooks in self._hooks.items():
            for hook in hooks:
                hooks_list.append(asdict(hook))

        with open(hook_file, 'w', encoding='utf-8') as f:
            json.dump({'hooks': hooks_list}, f, ensure_ascii=False, indent=2)

    def register_handler(self, action: str, handler: Callable):
        self._handlers[action] = handler

    def add_hook(self, hook_config: HookConfig) -> bool:
        with self._lock:
            trigger = hook_config.trigger
            if trigger not in self._hooks:
                self._hooks[trigger] = []
            self._hooks[trigger].append(hook_config)
            self._save_hooks()
        return True

    def remove_hook(self, trigger: str, action: str, skill_id: str = None) -> bool:
        with self._lock:
            if trigger in self._hooks:
                before = len(self._hooks[trigger])
                self._hooks[trigger] = [
                    h for h in self._hooks[trigger]
                    if not (h.action == action and (skill_id is None or h.skill_id == skill_id))
                ]
                self._save_hooks()
                return len(self._hooks[trigger]) < before
        return False

    def trigger_hooks(self, trigger: str, data: Dict[str, Any]) -> List[Dict]:
        results = []
        event = HookEvent(
            timestamp=datetime.now().isoformat(),
            trigger=trigger,
            action="",
            skill_id=data.get('skill_id'),
            data=data
        )

        hooks = self._hooks.get(trigger, [])
        for hook in hooks:
            if not hook.enabled:
                continue

            event.action = hook.action
            try:
                handler = self._handlers.get(hook.action)
                if handler:
                    result = handler(data, hook.config or {})
                    event.result = result
                    results.append({
                        'hook': asdict(hook),
                        'result': result,
                        'success': True
                    })
            except Exception as e:
                results.append({
                    'hook': asdict(hook),
                    'error': str(e),
                    'success': False
                })

        self._event_log.append(event)
        self._save_event_log(event)
        return results

    def _save_event_log(self, event: HookEvent):
        log_file = self.LOGS_DIR / f"hook_events_{datetime.now().strftime('%Y-%m-%d')}.json"
        events = []
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                events = json.load(f)
        events.append(asdict(event))
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(events, f, ensure_ascii=False, indent=2)

    def get_active_hooks(self) -> Dict[str, List[Dict]]:
        return {k: [asdict(h) for h in v] for k, v in self._hooks.items()}

    def get_hook_stats(self) -> Dict:
        total = sum(len(hooks) for hooks in self._hooks.values())
        return {
            'total_hooks': total,
            'by_trigger': {k: len(v) for k, v in self._hooks.items()},
            'events_today': len([e for e in self._event_log if e.timestamp.startswith(datetime.now().strftime('%Y-%m-%d'))])
        }


_hook_system: Optional[AutoHookSystem] = None


def get_hook_system() -> AutoHookSystem:
    global _hook_system
    if _hook_system is None:
        _hook_system = AutoHookSystem()
    return _hook_system


def track_usage_handler(data: Dict, config: Dict) -> Dict:
    try:
        from tool_usage_tracker import track_mcp_call, track_skill_call

        tool_type = data.get('tool_type', 'unknown')
        tool_name = data.get('tool_name', 'unknown')
        action = data.get('action', 'call')
        status = data.get('status', 'success')
        duration_ms = data.get('duration_ms', 0)

        if tool_type == 'skill':
            track_skill_call(tool_name, action, status, duration_ms)
        else:
            track_mcp_call(tool_name, action, status, duration_ms)

        return {'tracked': True, 'tool': tool_name}
    except Exception as e:
        return {'tracked': False, 'error': str(e)}


def log_event_handler(data: Dict, config: Dict) -> Dict:
    log_file = Path(__file__).parent / "logs" / f"auto_log_{datetime.now().strftime('%Y-%m-%d')}.md"
    log_entry = f"\n## {datetime.now().strftime('%H:%M:%S')} - {data.get('event', 'unknown')}\n\n```json\n{json.dumps(data, ensure_ascii=False, indent=2)}\n```\n"

    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_entry)

    return {'logged': True, 'file': str(log_file)}


def auto_suggest_handler(data: Dict, config: Dict) -> Dict:
    suggestions = []

    skill_id = data.get('skill_id')
    if skill_id == 'auto-debug':
        suggestions.append("💡 建议：调试完成后可运行 auto-refactor 进行代码优化")
    elif skill_id == 'auto-doc':
        suggestions.append("💡 建议：生成文档后可运行 auto-hook 设置更新提醒")

    return {'suggestions': suggestions}


def initialize_default_hooks():
    system = get_hook_system()

    system.register_handler('track_usage', track_usage_handler)
    system.register_handler('log_event', log_event_handler)
    system.register_handler('auto_suggest', auto_suggest_handler)

    default_hooks = [
        HookConfig(
            trigger=HookTrigger.POST_SKILL_LOAD.value,
            action=HookAction.TRACK_USAGE.value,
            skill_id=None,
            enabled=True,
            config={}
        ),
        HookConfig(
            trigger=HookTrigger.POST_TOOL_CALL.value,
            action=HookAction.LOG_EVENT.value,
            skill_id=None,
            enabled=True,
            config={'log_level': 'info'}
        ),
        HookConfig(
            trigger=HookTrigger.POST_SKILL_LOAD.value,
            action=HookAction.AUTO_SUGGEST.value,
            skill_id=None,
            enabled=True,
            config={}
        ),
    ]

    for hook in default_hooks:
        system.add_hook(hook)

    return system


def get_all_hooks_summary() -> str:
    system = get_hook_system()
    stats = system.get_hook_stats()
    hooks = system.get_active_hooks()

    lines = [
        "# 🔗 自动化钩子系统状态",
        "",
        f"**总钩子数**: {stats['total_hooks']}",
        f"**今日事件**: {stats['events_today']}",
        "",
        "## 按触发器分类",
    ]

    for trigger, trigger_hooks in hooks.items():
        lines.append(f"\n### {trigger}")
        for h in trigger_hooks:
            status = "✅" if h['enabled'] else "❌"
            lines.append(f"  {status} {h['action']} -> {h.get('skill_id') or '全部'}")

    return "\n".join(lines)


if __name__ == '__main__':
    system = initialize_default_hooks()
    print(get_all_hooks_summary())

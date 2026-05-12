# -*- coding: utf-8 -*-
"""
真正的自动触发器 MCP 服务 v1.0
实现 Skills 的真实自动触发 - 当匹配关键词时自动激活对应 Skill
"""

import json
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum


class TriggerType(Enum):
    KEYWORD = "keyword"           # 关键词触发
    PATTERN = "pattern"           # 正则匹配触发
    TIME = "time"                 # 定时触发
    EVENT = "event"               # 事件触发


@dataclass
class TriggerRule:
    rule_id: str
    name: str
    trigger_type: str
    pattern: str                  # 关键词或正则
    skill_id: str                 # 触发的 Skill
    action: str                   # 执行的动作
    enabled: bool = True
    cooldown_seconds: float = 0   # 冷却时间
    last_triggered: Optional[str] = None
    priority: int = 0             # 优先级


@dataclass
class TriggerEvent:
    timestamp: str
    rule_id: str
    skill_id: str
    action: str
    matched_text: str
    result: Optional[Dict] = None
    status: str = "pending"


class TrueAutoTrigger:
    """
    真正的自动触发器 - 监控用户输入并自动触发 Skills

    工作原理：
    1. 持续监听用户消息
    2. 使用关键词匹配判断是否触发
    3. 自动执行对应的 Skill
    4. 记录触发日志
    """

    BASE_DIR = Path(__file__).parent
    TRIGGERS_DIR = BASE_DIR / "triggers"
    LOGS_DIR = BASE_DIR / "logs"

    def __init__(self):
        self.TRIGGERS_DIR.mkdir(exist_ok=True)
        self.LOGS_DIR.mkdir(exist_ok=True)
        self._rules: Dict[str, TriggerRule] = {}
        self._execution_log: List[TriggerEvent] = []
        self._lock = threading.Lock()
        self._callbacks: List[Callable] = []
        self._running = False
        self._load_rules()
        self._load_default_rules()

    def _load_rules(self):
        """加载触发规则"""
        rules_file = self.TRIGGERS_DIR / "trigger_rules.json"
        if rules_file.exists():
            with open(rules_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for rule_data in data.get('rules', []):
                    rule = TriggerRule(**rule_data)
                    self._rules[rule.rule_id] = rule

    def _save_rules(self):
        """保存触发规则"""
        rules_file = self.TRIGGERS_DIR / "trigger_rules.json"
        rules_list = [asdict(r) for r in self._rules.values()]
        with open(rules_file, 'w', encoding='utf-8') as f:
            json.dump({'rules': rules_list}, f, ensure_ascii=False, indent=2)

    def _load_default_rules(self):
        """加载默认触发规则 - 5个 Skills 的关键词"""

        default_rules = [
            # auto-debug 触发规则
            TriggerRule(
                rule_id="debug_keyword_1",
                name="调试关键词触发",
                trigger_type=TriggerType.KEYWORD.value,
                pattern="调试",
                skill_id="auto-debug",
                action="analyze",
                priority=10
            ),
            TriggerRule(
                rule_id="debug_keyword_2",
                name="错误关键词触发",
                trigger_type=TriggerType.KEYWORD.value,
                pattern="报错",
                skill_id="auto-debug",
                action="analyze",
                priority=10
            ),
            TriggerRule(
                rule_id="debug_keyword_3",
                name="Bug关键词触发",
                trigger_type=TriggerType.KEYWORD.value,
                pattern="bug",
                skill_id="auto-debug",
                action="analyze",
                priority=10
            ),
            TriggerRule(
                rule_id="debug_keyword_4",
                name="错误触发",
                trigger_type=TriggerType.KEYWORD.value,
                pattern="错误",
                skill_id="auto-debug",
                action="analyze",
                priority=10
            ),
            TriggerRule(
                rule_id="debug_keyword_5",
                name="修复触发",
                trigger_type=TriggerType.KEYWORD.value,
                pattern="修复",
                skill_id="auto-debug",
                action="analyze",
                priority=10
            ),

            # auto-hook 触发规则
            TriggerRule(
                rule_id="hook_keyword_1",
                name="Hook关键词触发",
                trigger_type=TriggerType.KEYWORD.value,
                pattern="hook",
                skill_id="auto-hook",
                action="register",
                priority=10
            ),
            TriggerRule(
                rule_id="hook_keyword_2",
                name="钩子触发",
                trigger_type=TriggerType.KEYWORD.value,
                pattern="钩子",
                skill_id="auto-hook",
                action="register",
                priority=10
            ),
            TriggerRule(
                rule_id="hook_keyword_3",
                name="自动化触发",
                trigger_type=TriggerType.KEYWORD.value,
                pattern="自动化",
                skill_id="auto-hook",
                action="register",
                priority=10
            ),
            TriggerRule(
                rule_id="hook_keyword_4",
                name="触发触发",
                trigger_type=TriggerType.KEYWORD.value,
                pattern="触发",
                skill_id="auto-hook",
                action="register",
                priority=10
            ),

            # auto-doc 触发规则
            TriggerRule(
                rule_id="doc_keyword_1",
                name="文档触发",
                trigger_type=TriggerType.KEYWORD.value,
                pattern="文档",
                skill_id="auto-doc",
                action="generate",
                priority=10
            ),
            TriggerRule(
                rule_id="doc_keyword_2",
                name="README触发",
                trigger_type=TriggerType.KEYWORD.value,
                pattern="README",
                skill_id="auto-doc",
                action="generate",
                priority=10
            ),
            TriggerRule(
                rule_id="doc_keyword_3",
                name="注释触发",
                trigger_type=TriggerType.KEYWORD.value,
                pattern="注释",
                skill_id="auto-doc",
                action="generate",
                priority=10
            ),
            TriggerRule(
                rule_id="doc_keyword_4",
                name="生成文档触发",
                trigger_type=TriggerType.KEYWORD.value,
                pattern="生成文档",
                skill_id="auto-doc",
                action="generate",
                priority=10
            ),

            # auto-refactor 触发规则
            TriggerRule(
                rule_id="refactor_keyword_1",
                name="重构触发",
                trigger_type=TriggerType.KEYWORD.value,
                pattern="重构",
                skill_id="auto-refactor",
                action="batch",
                priority=10
            ),
            TriggerRule(
                rule_id="refactor_keyword_2",
                name="Refactor触发",
                trigger_type=TriggerType.KEYWORD.value,
                pattern="refactor",
                skill_id="auto-refactor",
                action="batch",
                priority=10
            ),
            TriggerRule(
                rule_id="refactor_keyword_3",
                name="批量修改触发",
                trigger_type=TriggerType.KEYWORD.value,
                pattern="批量修改",
                skill_id="auto-refactor",
                action="batch",
                priority=10
            ),
            TriggerRule(
                rule_id="refactor_keyword_4",
                name="迁移触发",
                trigger_type=TriggerType.KEYWORD.value,
                pattern="迁移",
                skill_id="auto-refactor",
                action="batch",
                priority=10
            ),

            # local-privacy 触发规则
            TriggerRule(
                rule_id="privacy_keyword_1",
                name="本地触发",
                trigger_type=TriggerType.KEYWORD.value,
                pattern="本地",
                skill_id="local-privacy",
                action="read",
                priority=10
            ),
            TriggerRule(
                rule_id="privacy_keyword_2",
                name="隐私触发",
                trigger_type=TriggerType.KEYWORD.value,
                pattern="隐私",
                skill_id="local-privacy",
                action="read",
                priority=10
            ),
            TriggerRule(
                rule_id="privacy_keyword_3",
                name="Local触发",
                trigger_type=TriggerType.KEYWORD.value,
                pattern="local",
                skill_id="local-privacy",
                action="read",
                priority=10
            ),
            TriggerRule(
                rule_id="privacy_keyword_4",
                name="笔记触发",
                trigger_type=TriggerType.KEYWORD.value,
                pattern="笔记",
                skill_id="local-privacy",
                action="read",
                priority=10
            ),
        ]

        for rule in default_rules:
            if rule.rule_id not in self._rules:
                self._rules[rule.rule_id] = rule

        self._save_rules()

    def check_and_trigger(self, user_message: str, context: Dict = None) -> List[TriggerEvent]:
        """
        检查消息并触发匹配的规则

        Args:
            user_message: 用户输入的消息
            context: 上下文信息

        Returns:
            触发的事件列表
        """
        triggered_events = []
        user_message_lower = user_message.lower()

        with self._lock:
            # 按优先级排序
            sorted_rules = sorted(
                self._rules.values(),
                key=lambda r: r.priority,
                reverse=True
            )

            for rule in sorted_rules:
                if not rule.enabled:
                    continue

                # 检查冷却时间
                if rule.last_triggered:
                    last_time = datetime.fromisoformat(rule.last_triggered)
                    elapsed = (datetime.now() - last_time).total_seconds()
                    if elapsed < rule.cooldown_seconds:
                        continue

                # 关键词匹配
                if rule.trigger_type == TriggerType.KEYWORD.value:
                    if rule.pattern.lower() in user_message_lower:
                        event = self._execute_rule(rule, user_message)
                        triggered_events.append(event)

        return triggered_events

    def _execute_rule(self, rule: TriggerRule, matched_text: str) -> TriggerEvent:
        """执行触发规则"""
        event = TriggerEvent(
            timestamp=datetime.now().isoformat(),
            rule_id=rule.rule_id,
            skill_id=rule.skill_id,
            action=rule.action,
            matched_text=matched_text,
            status="triggered"
        )

        # 更新最后触发时间
        rule.last_triggered = datetime.now().isoformat()
        self._save_rules()

        # 执行 Skill
        try:
            from skill_runner import get_runner
            runner = get_runner()

            # 根据 skill_id 选择执行方法
            if rule.skill_id == "auto-debug":
                result = runner.run_debug(matched_text)
            elif rule.skill_id == "auto-hook":
                result = runner.run_hook("manual", rule.action)
            elif rule.skill_id == "auto-doc":
                result = runner.run_doc(matched_text)
            elif rule.skill_id == "auto-refactor":
                result = runner.run_refactor(matched_text, "auto_suggested")
            elif rule.skill_id == "local-privacy":
                result = runner.run_privacy(matched_text)
            else:
                result = {"error": "Unknown skill"}

            event.result = result
            event.status = "success"

        except Exception as e:
            event.result = {"error": str(e)}
            event.status = "failed"

        # 保存事件
        self._execution_log.append(event)
        self._save_event_log(event)

        # 通知回调
        self._notify_callbacks(event)

        return event

    def _save_event_log(self, event: TriggerEvent):
        """保存触发事件日志"""
        log_file = self.LOGS_DIR / f"trigger_events_{datetime.now().strftime('%Y-%m-%d')}.json"
        events = []
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    events = json.load(f)
            except:
                events = []

        events.append(asdict(event))

        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(events, f, ensure_ascii=False, indent=2)

    def register_callback(self, callback: Callable):
        """注册回调函数 - 当触发时调用"""
        self._callbacks.append(callback)

    def _notify_callbacks(self, event: TriggerEvent):
        """通知所有回调"""
        for callback in self._callbacks:
            try:
                callback(event)
            except:
                pass

    def add_rule(self, rule: TriggerRule) -> bool:
        """添加触发规则"""
        with self._lock:
            self._rules[rule.rule_id] = rule
            self._save_rules()
        return True

    def remove_rule(self, rule_id: str) -> bool:
        """删除触发规则"""
        with self._lock:
            if rule_id in self._rules:
                del self._rules[rule_id]
                self._save_rules()
                return True
        return False

    def get_active_rules(self) -> List[Dict]:
        """获取所有激活的规则"""
        return [
            {
                **asdict(rule),
                "cooldown_remaining": self._get_cooldown_remaining(rule)
            }
            for rule in self._rules.values()
            if rule.enabled
        ]

    def _get_cooldown_remaining(self, rule: TriggerRule) -> float:
        """获取冷却剩余时间"""
        if not rule.last_triggered:
            return 0
        last_time = datetime.fromisoformat(rule.last_triggered)
        elapsed = (datetime.now() - last_time).total_seconds()
        return max(0, rule.cooldown_seconds - elapsed)

    def get_trigger_stats(self) -> Dict:
        """获取触发统计"""
        today = datetime.now().strftime('%Y-%m-%d')
        today_events = [e for e in self._execution_log if e.timestamp.startswith(today)]

        skill_counts = {}
        for event in today_events:
            skill_counts[event.skill_id] = skill_counts.get(event.skill_id, 0) + 1

        return {
            "total_rules": len(self._rules),
            "enabled_rules": sum(1 for r in self._rules.values() if r.enabled),
            "today_triggers": len(today_events),
            "by_skill": skill_counts,
            "success_count": sum(1 for e in today_events if e.status == "success"),
            "failed_count": sum(1 for e in today_events if e.status == "failed")
        }


_trigger: Optional[TrueAutoTrigger] = None


def get_auto_trigger() -> TrueAutoTrigger:
    global _trigger
    if _trigger is None:
        _trigger = TrueAutoTrigger()
    return _trigger


def auto_trigger_check(user_message: str, context: Dict = None) -> List[TriggerEvent]:
    """
    自动触发检查函数 - 每次用户消息时调用此函数
    返回触发的事件列表
    """
    trigger = get_auto_trigger()
    return trigger.check_and_trigger(user_message, context)


if __name__ == '__main__':
    print("="*70)
    print("🚀 真正的自动触发器测试")
    print("="*70)

    trigger = get_auto_trigger()

    print(f"\n📋 已加载 {len(trigger._rules)} 个触发规则")

    print("\n规则列表:")
    rules = trigger.get_active_rules()
    for r in rules:
        print(f"  - {r['skill_id']}: '{r['pattern']}' -> {r['action']}")

    print("\n" + "="*70)
    print("🧪 测试自动触发")
    print("="*70)

    test_messages = [
        "帮我调试这个错误",
        "设置一个hook",
        "生成README文档",
        "重构这段代码",
        "读取本地笔记",
    ]

    for msg in test_messages:
        print(f"\n📝 用户消息: {msg}")
        events = auto_trigger_check(msg)
        if events:
            for event in events:
                print(f"  ✅ 触发: {event.skill_id} ({event.action})")
                print(f"     状态: {event.status}")
        else:
            print("  ⚠️ 未匹配任何规则")

    print("\n" + "="*70)
    print("📊 触发统计")
    print("="*70)
    stats = trigger.get_trigger_stats()
    print(f"总规则数: {stats['total_rules']}")
    print(f"激活规则: {stats['enabled_rules']}")
    print(f"今日触发: {stats['today_triggers']}")
    print(f"成功率: {stats['success_count']}/{stats['today_triggers']}")

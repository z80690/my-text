#!/usr/bin/env python3
"""
监控智能体系统 v5.0
完整设计模式重构版 - 包含：
1. 单例模式 (Singleton Pattern)
2. 观察者模式 (Observer Pattern)
3. 规则引擎模式 (Rule Engine Pattern)
4. 责任链模式 (Chain of Responsibility Pattern)
5. 策略模式增强 (Enhanced Strategy Pattern)
6. 插件化架构 (Plugin Architecture)
"""

import os
import re
import json
import time
import asyncio
import datetime
import importlib
import inspect
from typing import Dict, List, Any, Optional, Tuple, Callable
from pathlib import Path
from abc import ABC, abstractmethod


class Rule:
    """规则对象 - 使用策略模式"""
    def __init__(self, id: str, name: str, level: str, severity: str,
                 description: str, condition: Dict = None, validator: 'RuleValidatorBase' = None):
        self.id = id
        self.name = name
        self.level = level
        self.severity = severity
        self.description = description
        self.condition = condition or {}
        self.validator = validator
        self.violations = []
        self.last_check = None

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "level": self.level,
            "severity": self.severity,
            "description": self.description
        }


class Violation:
    """违规对象"""
    def __init__(self, rule: Rule, message: str, match_score: float = 0.0,
                 action_taken: str = "WARN", auto_fixed: bool = False):
        self.rule = rule
        self.message = message
        self.match_score = match_score
        self.action_taken = action_taken
        self.auto_fixed = auto_fixed
        self.timestamp = datetime.datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return {
            "rule_id": self.rule.id,
            "rule_name": self.rule.name,
            "message": self.message,
            "match_score": self.match_score,
            "action_taken": self.action_taken,
            "auto_fixed": self.auto_fixed,
            "timestamp": self.timestamp
        }


class Context:
    """共用上下文对象"""
    def __init__(self, context_id: str):
        self.context_id = context_id
        self.data: Dict[str, Any] = {}
        self.agent_state: Dict[str, Any] = {}
        self.tool_calls: List[Dict] = []
        self.memory_state: Dict[str, Any] = {}
        self.messages: List[Dict] = []
        self.created_at = datetime.datetime.now().isoformat()
        self.last_updated = self.created_at

    def set(self, key: str, value: Any):
        self.data[key] = value
        self.last_updated = datetime.datetime.now().isoformat()

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def add_tool_call(self, tool_name: str, params: Dict, result: Any):
        self.tool_calls.append({
            "name": tool_name,
            "params": params,
            "result": result,
            "timestamp": datetime.datetime.now().isoformat()
        })

    def add_message(self, role: str, content: str):
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.datetime.now().isoformat()
        })

    def get_message_count(self) -> int:
        return len(self.messages)

    def get_tool_calls(self) -> List[Dict]:
        return self.tool_calls


class Observer(ABC):
    """观察者基类 - 观察者模式"""
    @abstractmethod
    def on_violation(self, violation: Violation):
        pass

    @abstractmethod
    def on_rule_loaded(self, rule: Rule):
        pass


class ViolationLogger(Observer):
    """违规日志记录器 - 观察者实现"""
    def __init__(self, log_path: str = ".trae/logs"):
        self.log_path = Path(log_path)
        self.log_path.mkdir(parents=True, exist_ok=True)

    def on_violation(self, violation: Violation):
        log_file = self.log_path / f"violations_{datetime.date.today()}.log"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{violation.timestamp}] {violation.rule.id} - {violation.message}\n")

    def on_rule_loaded(self, rule: Rule):
        pass


class ViolationNotifier(Observer):
    """违规通知器 - 实时通知"""
    def __init__(self):
        self.notifications: List[Dict] = []

    def on_violation(self, violation: Violation):
        self.notifications.append({
            "type": "violation",
            "rule_id": violation.rule.id,
            "rule_name": violation.rule.name,
            "message": violation.message,
            "severity": violation.rule.severity,
            "timestamp": violation.timestamp
        })

    def on_rule_loaded(self, rule: Rule):
        pass

    def get_notifications(self) -> List[Dict]:
        return self.notifications


class Subject:
    """主题对象 - 被观察者"""
    def __init__(self):
        self._observers: List[Observer] = []

    def add_observer(self, observer: Observer):
        self._observers.append(observer)

    def remove_observer(self, observer: Observer):
        self._observers.remove(observer)

    def notify_violation(self, violation: Violation):
        for observer in self._observers:
            observer.on_violation(violation)

    def notify_rule_loaded(self, rule: Rule):
        for observer in self._observers:
            observer.on_rule_loaded(rule)


class RuleValidatorBase(ABC):
    """规则验证器基类 - 策略模式"""
    @abstractmethod
    def validate(self, rule: Rule, context: Context, agent_behavior: Dict[str, Any]) -> Optional[Violation]:
        pass


class ToolPriorityValidator(RuleValidatorBase):
    """工具优先规则验证器"""
    def validate(self, rule: Rule, context: Context, agent_behavior: Dict[str, Any]) -> Optional[Violation]:
        keywords = ["搜索", "查询", "获取", "查找", "下载", "天气", "新闻"]
        needs_tool = any(kw in str(context.messages) for kw in keywords)
        has_tool = len(context.tool_calls) > 0 or len(agent_behavior.get("tool_calls", [])) > 0

        if needs_tool and not has_tool:
            return Violation(
                rule=rule,
                message=f"检测到可能需要工具的请求，但未使用工具。关键词: {context.messages[-1]['content'][:20]}",
                match_score=0.6,
                action_taken="WARN"
            )
        return None


class ParallelExecutionValidator(RuleValidatorBase):
    """并行执行规则验证器"""
    def validate(self, rule: Rule, context: Context, agent_behavior: Dict[str, Any]) -> Optional[Violation]:
        is_parallel = agent_behavior.get("parallel_mode", False)
        has_monitor = "monitor" in str(agent_behavior.get("agent_id", ""))

        if not is_parallel:
            return Violation(
                rule=rule,
                message="检测到可能未启动并行执行模式，监控智能体不在状态中",
                match_score=0.4,
                action_taken="HIGH_WARNING"
            )
        return None


class MemoryRuleValidator(RuleValidatorBase):
    """记忆规则验证器"""
    def validate(self, rule: Rule, context: Context, agent_behavior: Dict[str, Any]) -> Optional[Violation]:
        has_memory_action = any("记忆" in str(m) for m in context.messages)

        if not has_memory_action and rule.level == "L1":
            return Violation(
                rule=rule,
                message="检测到未执行AI自动记忆操作",
                match_score=0.3,
                action_taken="WARN"
            )
        return None


class RuleHandler(ABC):
    """责任链处理基类 - 责任链模式"""
    def __init__(self):
        self._next_handler: Optional['RuleHandler'] = None

    def set_next(self, handler: 'RuleHandler') -> 'RuleHandler':
        self._next_handler = handler
        return handler

    @abstractmethod
    async def handle(self, rule: Rule, context: Context, agent_behavior: Dict[str, Any]) -> Optional[Violation]:
        pass

    async def next(self, rule: Rule, context: Context, agent_behavior: Dict[str, Any]) -> Optional[Violation]:
        if self._next_handler:
            return await self._next_handler.handle(rule, context, agent_behavior)
        return None


class ToolPriorityHandler(RuleHandler):
    """工具优先规则处理器"""
    async def handle(self, rule: Rule, context: Context, agent_behavior: Dict[str, Any]) -> Optional[Violation]:
        if rule.id == "R001":
            validator = ToolPriorityValidator()
            return await asyncio.to_thread(validator.validate, rule, context, agent_behavior)
        return await self.next(rule, context, agent_behavior)


class ParallelExecutionHandler(RuleHandler):
    """并行执行规则处理器"""
    async def handle(self, rule: Rule, context: Context, agent_behavior: Dict[str, Any]) -> Optional[Violation]:
        if rule.id == "R003":
            validator = ParallelExecutionValidator()
            return await asyncio.to_thread(validator.validate, rule, context, agent_behavior)
        return await self.next(rule, context, agent_behavior)


class DefaultHandler(RuleHandler):
    """默认规则处理器"""
    async def handle(self, rule: Rule, context: Context, agent_behavior: Dict[str, Any]) -> Optional[Violation]:
        return None


class RuleEngine:
    """规则引擎 - 规则引擎模式"""

    def __init__(self):
        self.rule_definitions: Dict[str, Any] = {}

    def load_rules_from_json(self, path: str):
        """从 JSON 加载规则定义"""
        json_path = Path(path)
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                self.rule_definitions = json.load(f)

    def load_rules_from_yaml(self, path: str):
        """从 YAML 加载规则定义"""
        yaml_path = Path(path)
        if yaml_path.exists():
            try:
                import yaml
                with open(yaml_path, 'r', encoding='utf-8') as f:
                    self.rule_definitions = yaml.safe_load(f)
            except ImportError:
                print("[RuleEngine] PyYAML 未安装，使用 JSON 格式")

    def evaluate_condition(self, condition: Dict, context: Context, behavior: Dict) -> bool:
        """动态评估规则条件"""
        if not condition:
            return False

        condition_type = condition.get("type", "keyword")

        if condition_type == "keyword":
            keywords = condition.get("keywords", [])
            content = str(context.messages)
            return any(kw in content for kw in keywords)

        elif condition_type == "state":
            key = condition.get("key")
            expected = condition.get("expected")
            actual = behavior.get(key)
            return actual == expected

        elif condition_type == "custom":
            func_name = condition.get("function")
            return self._call_custom_function(func_name, context, behavior)

        return False

    def _call_custom_function(self, func_name: str, context: Context, behavior: Dict) -> bool:
        """调用自定义函数"""
        if hasattr(self, func_name):
            func = getattr(self, func_name)
            return func(context, behavior)
        return False


class PluginLoader:
    """插件加载器 - 插件化架构"""
    def __init__(self, plugin_dir: str = ".trae/plugins"):
        self.plugin_dir = Path(plugin_dir)
        self.plugins: Dict[str, Any] = {}

    def load_plugins(self):
        """加载所有插件"""
        if not self.plugin_dir.exists():
            self.plugin_dir.mkdir(parents=True, exist_ok=True)
            return

        for plugin_file in self.plugin_dir.glob("*.py"):
            if plugin_file.name.startswith("_"):
                continue
            self._load_plugin(plugin_file)

    def _load_plugin(self, plugin_file: Path):
        """加载单个插件"""
        try:
            module_name = plugin_file.stem
            spec = importlib.util.spec_from_file_location(module_name, plugin_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and hasattr(obj, 'validate'):
                        self.plugins[name] = obj()
                        print(f"[PluginLoader] 加载插件: {name}")

        except Exception as e:
            print(f"[PluginLoader] 加载插件 {plugin_file} 失败: {e}")

    def get_plugin(self, name: str) -> Optional[Any]:
        """获取插件"""
        return self.plugins.get(name)


class RuleLoader:
    """规则加载器"""

    def __init__(self, rules_path: str = ".trae/rules"):
        self.rules_path = Path(rules_path)
        self.rules: List[Rule] = []

    def load_all_rules(self) -> List[Rule]:
        """加载所有规则"""
        print(f"[RuleLoader] 从 {self.rules_path} 加载所有规则...")

        validators = {
            "R001": ToolPriorityValidator(),
            "R002": MemoryRuleValidator(),
            "R003": ParallelExecutionValidator(),
        }

        self._load_l1_rules(validators)
        self._load_l2_rules(validators)
        self._load_l3_rules(validators)

        print(f"[RuleLoader] 共加载 {len(self.rules)} 条规则")
        return self.rules

    def _load_l1_rules(self, validators: Dict):
        l1_path = Path(".trae/agent.md")
        if l1_path.exists():
            self._parse_rules_from_file(l1_path, "L1", validators)

    def _load_l2_rules(self, validators: Dict):
        l2_path = Path("agent.md")
        if l2_path.exists():
            self._parse_rules_from_file(l2_path, "L2", validators)
        else:
            project_l2 = Path.cwd() / "agent.md"
            if project_l2.exists():
                self._parse_rules_from_file(project_l2, "L2", validators)

    def _load_l3_rules(self, validators: Dict):
        if not self.rules_path.exists():
            return

        for md_file in self.rules_path.rglob("*.md"):
            if "新建文件夹" in str(md_file) or "旧版" in str(md_file):
                continue
            self._parse_rules_from_file(md_file, "L3", validators)

    def _parse_rules_from_file(self, file_path: Path, level: str, validators: Dict):
        try:
            content = file_path.read_text(encoding="utf-8")
            rules = self._extract_rules(content, file_path, level, validators)
            self.rules.extend(rules)
        except Exception as e:
            print(f"[RuleLoader] 解析文件 {file_path} 失败: {e}")

    def _extract_rules(self, content: str, file_path: Path, level: str, validators: Dict) -> List[Rule]:
        rules = []

        rule_configs = [
            ("R001", "工具优先原则", "MEDIUM", "工具优先" in content, "当存在可用工具时，应使用工具而非直接回答"),
            ("R002", "AI自动记忆规则", "MEDIUM", "AI自动记忆" in content and "记忆" in content, "每次回复必须自动执行暗知识识别并写入记忆"),
            ("R003", "并行执行规则", "HIGH", "并行" in content and "监控" in content, "所有任务默认使用并行执行模式"),
            ("R004", "上下文保持规则", "MEDIUM", "上下文" in content, "多轮对话应保持上下文连续性"),
            ("R005", "规则体系互斥规则", "CRITICAL", "互斥" in content or ".opencode" in content, ".trae/ 和 .opencode/ 规则体系绝对不能混用"),
            ("R006", "日志记录规则", "LOW", "日志" in content, "关键操作应记录日志"),
            ("R007", "工作流执行规则", "MEDIUM", "工作流" in content, "任务应按正确工作流执行"),
            ("R008", "蜂群协作规则", "MEDIUM", "蜂群" in content, "多智能体协作应遵循蜂群模式规则"),
            ("R009", "Cloud Code记忆系统规则", "HIGH", "Cloud Code" in content, "遵循主动整理、智能检索、严谨验证、质量把控四大精髓"),
            ("R010", "智能体调用规则", "MEDIUM", "智能体" in content, "智能体调用应遵循标准协议"),
        ]

        for rule_id, name, severity, condition, description in rule_configs:
            if condition:
                rules.append(Rule(
                    id=rule_id,
                    name=name,
                    level=level,
                    severity=severity,
                    description=description,
                    validator=validators.get(rule_id)
                ))

        return rules


class RuleValidator:
    """规则验证引擎 - 策略模式"""

    def __init__(self, rules: List[Rule]):
        self.rules = rules
        self.violations: List[Violation] = []

    def validate(self, context: Context, agent_behavior: Dict[str, Any]) -> List[Violation]:
        """验证智能体行为"""
        self.violations = []

        for rule in self.rules:
            violation = self._check_rule(rule, context, agent_behavior)
            if violation:
                self.violations.append(violation)
                rule.violations.append(violation)

        return self.violations

    def _check_rule(self, rule: Rule, context: Context, agent_behavior: Dict[str, Any]) -> Optional[Violation]:
        """检查特定规则"""
        if rule.validator:
            return rule.validator.validate(rule, context, agent_behavior)

        validators = {
            "R001": ToolPriorityValidator(),
            "R002": MemoryRuleValidator(),
            "R003": ParallelExecutionValidator(),
        }

        validator = validators.get(rule.id)
        if validator:
            return validator.validate(rule, context, agent_behavior)

        return None


class RuleChainValidator:
    """责任链验证器 - 责任链模式"""

    def __init__(self):
        self.handlers: List[RuleHandler] = []

    def add_handler(self, handler: RuleHandler):
        self.handlers.append(handler)

    def build_chain(self):
        """构建责任链"""
        tool_handler = ToolPriorityHandler()
        parallel_handler = ParallelExecutionHandler()
        default_handler = DefaultHandler()

        tool_handler.set_next(parallel_handler).set_next(default_handler)
        self.handlers.append(tool_handler)

    async def validate_parallel(self, rules: List[Rule], context: Context, agent_behavior: Dict[str, Any]) -> List[Violation]:
        """并行验证所有规则"""
        if not self.handlers:
            self.build_chain()

        tasks = []
        for rule in rules:
            handler = self.handlers[0]
            tasks.append(handler.handle(rule, context, agent_behavior))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        violations = []
        for result in results:
            if isinstance(result, Violation):
                violations.append(result)
            elif isinstance(result, Exception):
                print(f"[RuleChainValidator] 验证异常: {result}")

        return violations


class AutoProcessor:
    """自动处理器"""

    def __init__(self):
        self.action_handlers: Dict[str, Callable] = {
            "WARN": self._handle_warn,
            "HIGH_WARNING": self._handle_high_warning,
            "FIX": self._handle_fix,
            "BLOCK": self._handle_block,
        }

    def process(self, violations: List[Violation], context: Context) -> Dict[str, Any]:
        """处理违规"""
        results = {
            "total": len(violations),
            "warned": 0,
            "fixed": 0,
            "blocked": 0,
            "details": []
        }

        for violation in violations:
            action = violation.action_taken
            handler = self.action_handlers.get(action, self._handle_warn)
            result = handler(violation, context)
            results["details"].append(result)

            if action == "WARN" or action == "HIGH_WARNING":
                results["warned"] += 1
            elif action == "FIX":
                results["fixed"] += 1
            elif action == "BLOCK":
                results["blocked"] += 1

        return results

    def _handle_warn(self, violation: Violation, context: Context) -> Dict:
        return {"action": "WARN", "violation": violation.message, "status": "logged"}

    def _handle_high_warning(self, violation: Violation, context: Context) -> Dict:
        return {"action": "HIGH_WARNING", "violation": violation.message, "status": "alerted"}

    def _handle_fix(self, violation: Violation, context: Context) -> Dict:
        violation.auto_fixed = True
        return {"action": "FIX", "violation": violation.message, "status": "auto_fixed"}

    def _handle_block(self, violation: Violation, context: Context) -> Dict:
        return {"action": "BLOCK", "violation": violation.message, "status": "blocked"}


class MonitorAgentFactory:
    """监控智能体工厂 - 单例模式"""
    _instance = None
    _rules = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls, rules_path: str = ".trae/rules") -> 'MonitorAgentV5':
        """获取单例实例"""
        if cls._instance is None or not cls._initialized:
            cls._instance = MonitorAgentV5(rules_path)
            cls._initialized = True
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """重置单例（用于测试）"""
        cls._instance = None
        cls._rules = None
        cls._initialized = False


class MonitorAgentV5:
    """监控智能体 v5.0 - 完整设计模式实现"""

    def __init__(self, rules_path: str = ".trae/rules"):
        self.rules_path = rules_path
        self.subject = Subject()
        self.rule_engine = RuleEngine()
        self.plugin_loader = PluginLoader()
        self.chain_validator = RuleChainValidator()
        self.chain_validator.build_chain()

        self.logger = ViolationLogger()
        self.notifier = ViolationNotifier()
        self.subject.add_observer(self.logger)
        self.subject.add_observer(self.notifier)

        self.contexts: Dict[str, Context] = {}
        self.rule_loader = RuleLoader(rules_path)

        if MonitorAgentFactory._rules is None:
            MonitorAgentFactory._rules = self.rule_loader.load_all_rules()
            for rule in MonitorAgentFactory._rules:
                self.subject.notify_rule_loaded(rule)

        self.rules = MonitorAgentFactory._rules
        self.validator = RuleValidator(self.rules)
        self.processor = AutoProcessor()
        
        # 自动过期配置（默认24小时过期）
        self.context_expiry_seconds = 86400

    def create_context(self, context_id: str) -> Context:
        """创建共用上下文"""
        # 先清理过期上下文
        self._cleanup_expired_contexts()
        
        context = Context(context_id)
        self.contexts[context_id] = context
        return context

    def get_context(self, context_id: str) -> Optional[Context]:
        """获取共用上下文"""
        context = self.contexts.get(context_id)
        if context:
            context.last_updated = datetime.datetime.now().isoformat()
        return context

    def delete_context(self, context_id: str) -> bool:
        """删除指定上下文 - 公共API"""
        if context_id in self.contexts:
            del self.contexts[context_id]
            return True
        return False

    def cleanup_all_contexts(self) -> int:
        """清空所有上下文 - 公共API"""
        count = len(self.contexts)
        self.contexts.clear()
        return count

    def cleanup_expired_contexts(self, max_age_seconds: int = None) -> int:
        """清理过期上下文 - 公共API"""
        return self._cleanup_expired_contexts(max_age_seconds)

    def _cleanup_expired_contexts(self, max_age_seconds: int = None) -> int:
        """内部方法：清理过期上下文"""
        if max_age_seconds is None:
            max_age_seconds = self.context_expiry_seconds

        now = datetime.datetime.now()
        expired_ids = []
        
        for context_id, context in self.contexts.items():
            try:
                last_updated = datetime.datetime.fromisoformat(context.last_updated)
                age_seconds = (now - last_updated).total_seconds()
                if age_seconds > max_age_seconds:
                    expired_ids.append(context_id)
            except (ValueError, TypeError):
                expired_ids.append(context_id)

        for context_id in expired_ids:
            del self.contexts[context_id]

        return len(expired_ids)

    def get_context_stats(self) -> Dict[str, Any]:
        """获取上下文统计信息 - 公共API"""
        now = datetime.datetime.now()
        
        total_contexts = len(self.contexts)
        total_messages = sum(len(ctx.messages) for ctx in self.contexts.values())
        total_tool_calls = sum(len(ctx.tool_calls) for ctx in self.contexts.values())
        
        try:
            import psutil
            memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
        except (ImportError, Exception):
            memory_mb = None

        return {
            "total_contexts": total_contexts,
            "total_messages": total_messages,
            "total_tool_calls": total_tool_calls,
            "memory_mb": memory_mb,
            "timestamp": now.isoformat()
        }

    async def monitor_async(self, context_id: str, agent_behavior: Dict[str, Any] = None) -> Dict[str, Any]:
        """异步监控"""
        context = self.get_context(context_id)
        if not context:
            return {"error": "Context not found"}

        agent_behavior = agent_behavior or {}

        violations = await self.chain_validator.validate_parallel(
            self.rules, context, agent_behavior
        )

        for violation in violations:
            self.subject.notify_violation(violation)

        process_result = self.processor.process(violations, context)

        return self._generate_report(context, violations, process_result)

    def monitor(self, context_id: str, agent_behavior: Dict[str, Any] = None) -> Dict[str, Any]:
        """同步监控"""
        return asyncio.run(self.monitor_async(context_id, agent_behavior))

    def _generate_report(self, context: Context, violations: List[Violation], process_result: Dict) -> Dict:
        """生成监控报告"""
        return {
            "context_id": context.context_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "rules_count": {
                "total": len(self.rules),
                "L1": len([r for r in self.rules if r.level == "L1"]),
                "L2": len([r for r in self.rules if r.level == "L2"]),
                "L3": len([r for r in self.rules if r.level == "L3"]),
            },
            "violations_count": len(violations),
            "violations": [v.to_dict() for v in violations],
            "process_result": process_result,
            "notifications": self.notifier.get_notifications()
        }


if __name__ == "__main__":
    print("\n" + "="*60)
    print("监控智能体 v5.0 - 完整设计模式测试")
    print("="*60)
    print(f"测试时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    factory = MonitorAgentFactory()
    monitor1 = factory.get_instance()
    monitor2 = factory.get_instance()

    print(f"\n单例模式测试: {monitor1 is monitor2}")

    context = monitor1.create_context("test_context")

    context.add_message("user", "请告诉我今天天气怎么样？")
    context.add_tool_call("weather_api", {"city": "北京"}, result={"temp": 25})

    agent_state = {
        "agent_id": "code_executor_agent",
        "status": "running",
        "tool_calls": ["weather_api"],
        "parallel_mode": False
    }

    report = monitor1.monitor("test_context", agent_behavior=agent_state)

    print(f"\n规则总数: {report['rules_count']['total']}")
    print(f"L1规则: {report['rules_count']['L1']}")
    print(f"L2规则: {report['rules_count']['L2']}")
    print(f"L3规则: {report['rules_count']['L3']}")
    print(f"违规数: {report['violations_count']}")

    print("\n观察者模式 - 通知列表:")
    for notification in report.get('notifications', [])[:3]:
        print(f"  - {notification['type']}: {notification['message']}")

    print("\n✅ 测试完成！")

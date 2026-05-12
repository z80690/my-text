#!/usr/bin/env python3
"""
监控智能体系统 v4.0
完整 L1/L2/L3 规则体系监控 + 上下文同步执行
"""

import os
import re
import json
import time
import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path


class Rule:
    """规则对象"""
    def __init__(self, id: str, name: str, level: str, severity: str, 
                 description: str, condition: Dict = None):
        self.id = id
        self.name = name
        self.level = level  # L1 / L2 / L3
        self.severity = severity  # LOW / MEDIUM / HIGH / CRITICAL
        self.description = description
        self.condition = condition or {}
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
        """获取消息数量"""
        return len(self.messages)

    def get_tool_calls(self) -> List[Dict]:
        """获取工具调用列表"""
        return self.tool_calls


class RuleLoader:
    """规则加载器 - 自动解析 L1/L2/L3 规则体系"""

    def __init__(self, rules_path: str = ".trae/rules"):
        self.rules_path = Path(rules_path)
        self.rules: List[Rule] = []

    def load_all_rules(self) -> List[Rule]:
        """加载所有规则"""
        print(f"[RuleLoader] 从 {self.rules_path} 加载所有规则...")
        
        # L1 规则（顶层规范）
        self._load_l1_rules()
        
        # L2 规则（项目配置）
        self._load_l2_rules()
        
        # L3 规则（具体实现）
        self._load_l3_rules()
        
        print(f"[RuleLoader] 共加载 {len(self.rules)} 条规则")
        return self.rules

    def _load_l1_rules(self):
        """加载 L1 规则"""
        l1_path = Path(".trae/agent.md")
        if l1_path.exists():
            self._parse_rules_from_file(l1_path, "L1")

    def _load_l2_rules(self):
        """加载 L2 规则"""
        l2_path = Path("agent.md")
        if l2_path.exists():
            self._parse_rules_from_file(l2_path, "L2")
        else:
            # 也检查项目根目录的 agent.md
            project_l2 = Path.cwd() / "agent.md"
            if project_l2.exists():
                self._parse_rules_from_file(project_l2, "L2")

    def _load_l3_rules(self):
        """加载 L3 规则"""
        if not self.rules_path.exists():
            return

        # 扫描所有 .md 文件
        for md_file in self.rules_path.rglob("*.md"):
            if "新建文件夹" in str(md_file) or "旧版" in str(md_file):
                continue
            self._parse_rules_from_file(md_file, "L3")

    def _parse_rules_from_file(self, file_path: Path, level: str):
        """从文件解析规则"""
        try:
            content = file_path.read_text(encoding="utf-8")
            
            # 解析规则
            rules = self._extract_rules(content, file_path, level)
            self.rules.extend(rules)
            
        except Exception as e:
            print(f"[RuleLoader] 解析文件 {file_path} 失败: {e}")

    def _extract_rules(self, content: str, file_path: Path, level: str) -> List[Rule]:
        """从内容提取规则"""
        rules = []
        
        # 1. 工具优先原则
        if "工具优先" in content:
            rules.append(Rule(
                id="R001",
                name="工具优先原则",
                level=level,
                severity="MEDIUM",
                description="当存在可用工具时，应使用工具而非直接回答"
            ))
        
        # 2. 记忆规则
        if "记忆" in content and "AI自动记忆" in content:
            rules.append(Rule(
                id="R002",
                name="AI自动记忆规则",
                level=level,
                severity="MEDIUM",
                description="每次回复必须自动执行暗知识识别并写入记忆"
            ))
        
        # 3. 并行执行规则
        if "并行" in content and "监控智能体" in content:
            rules.append(Rule(
                id="R003",
                name="并行执行规则",
                level=level,
                severity="HIGH",
                description="所有任务默认使用并行执行模式，执行智能体和监控智能体同时启动"
            ))
        
        # 4. 上下文保持规则
        if "上下文" in content:
            rules.append(Rule(
                id="R004",
                name="上下文保持规则",
                level=level,
                severity="MEDIUM",
                description="多轮对话应保持上下文连续性"
            ))
        
        # 5. 安全规则 - 路径体系互斥
        if "互斥" in content or ".opencode" in content:
            rules.append(Rule(
                id="R005",
                name="规则体系互斥规则",
                level=level,
                severity="CRITICAL",
                description=".trae/ 和 .opencode/ 规则体系绝对不能混用"
            ))
        
        # 6. 日志规则
        if "日志" in content:
            rules.append(Rule(
                id="R006",
                name="日志记录规则",
                level=level,
                severity="LOW",
                description="关键操作应记录日志"
            ))
        
        # 7. 工作流规则
        if "工作流" in content:
            rules.append(Rule(
                id="R007",
                name="工作流执行规则",
                level=level,
                severity="MEDIUM",
                description="任务应按正确工作流执行"
            ))
        
        # 8. 蜂群模式规则
        if "蜂群" in content:
            rules.append(Rule(
                id="R008",
                name="蜂群协作规则",
                level=level,
                severity="MEDIUM",
                description="多智能体协作应遵循蜂群模式规则"
            ))
        
        # 9. Cloud Code记忆系统规则
        if "Cloud Code" in content:
            rules.append(Rule(
                id="R009",
                name="Cloud Code记忆系统规则",
                level=level,
                severity="HIGH",
                description="遵循主动整理、智能检索、严谨验证、质量把控四大精髓"
            ))
        
        # 10. 智能体规则
        if "智能体" in content:
            rules.append(Rule(
                id="R010",
                name="智能体调用规则",
                level=level,
                severity="MEDIUM",
                description="智能体调用应遵循标准协议"
            ))
        
        return rules


class RuleValidator:
    """规则验证引擎"""

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
        if rule.id == "R001":
            return self._check_tool_priority(rule, context, agent_behavior)
        elif rule.id == "R002":
            return self._check_memory_rule(rule, context, agent_behavior)
        elif rule.id == "R003":
            return self._check_parallel_execution(rule, context, agent_behavior)
        elif rule.id == "R004":
            return self._check_context_preservation(rule, context, agent_behavior)
        elif rule.id == "R005":
            return self._check_rule_system_exclusion(rule, context, agent_behavior)
        elif rule.id == "R009":
            return self._check_cloud_code_memory(rule, context, agent_behavior)
        
        return None

    def _check_tool_priority(self, rule: Rule, context: Context, 
                            agent_behavior: Dict[str, Any]) -> Optional[Violation]:
        """检查工具优先原则"""
        # 简单检查：如果有消息但没有工具调用，可能违反
        last_user_message = None
        for msg in reversed(context.messages):
            if msg["role"] == "user":
                last_user_message = msg
                break
        
        if last_user_message and not context.tool_calls:
            # 检查是否存在关键词表示需要工具
            keywords = ["搜索", "查询", "获取", "查找", "分析", "计算", "统计"]
            content = last_user_message["content"].lower()
            
            if any(kw in content for kw in keywords):
                return Violation(
                    rule=rule,
                    message=f"检测到可能需要工具的请求，但未使用工具。关键词: {last_user_message['content']}",
                    match_score=0.6,
                    action_taken="WARN"
                )
        
        return None

    def _check_memory_rule(self, rule: Rule, context: Context, 
                         agent_behavior: Dict[str, Any]) -> Optional[Violation]:
        """检查记忆规则"""
        # 简化检查：是否有暗知识特征但未记录
        keywords = ["我习惯", "我喜欢", "我们团队", "以后都", "历史遗留", "这是系统", "项目"]
        for msg in context.messages:
            if msg["role"] == "user":
                content = msg["content"]
                if any(kw in content for kw in keywords):
                    # 检查是否有记忆写入
                    memory_path = Path(".trae/memories")
                    if not memory_path.exists():
                        return Violation(
                            rule=rule,
                            message=f"检测到暗知识特征但未找到记忆系统目录。内容: {content}",
                            match_score=0.5,
                            action_taken="WARN"
                        )
        
        return None

    def _check_parallel_execution(self, rule: Rule, context: Context, 
                                agent_behavior: Dict[str, Any]) -> Optional[Violation]:
        """检查并行执行规则"""
        # 简化检查：监控智能体是否被启动
        if "monitor_agent" not in context.agent_state:
            return Violation(
                rule=rule,
                message="检测到可能未启动并行执行模式，监控智能体不在状态中",
                match_score=0.4,
                action_taken="WARN"
            )
        
        return None

    def _check_context_preservation(self, rule: Rule, context: Context, 
                                  agent_behavior: Dict[str, Any]) -> Optional[Violation]:
        """检查上下文保持"""
        # 简化检查：上下文是否有历史消息
        if len(context.messages) < 2:
            return None
        
        # 检查是否有上下文ID
        if not context.context_id or context.context_id == "":
            return Violation(
                rule=rule,
                message="上下文ID为空，可能影响上下文连续性",
                match_score=0.3,
                action_taken="WARN"
            )
        
        return None

    def _check_rule_system_exclusion(self, rule: Rule, context: Context, 
                                   agent_behavior: Dict[str, Any]) -> Optional[Violation]:
        """检查规则体系互斥"""
        # 检查是否同时使用 .trae 和 .opencode
        last_message = ""
        for msg in context.messages:
            last_message = msg["content"]
        
        has_trae = ".trae" in last_message
        has_opencode = ".opencode" in last_message
        
        if has_trae and has_opencode:
            return Violation(
                rule=rule,
                message="🚫 严重违规！检测到同时使用 .trae/ 和 .opencode/ 规则体系！",
                match_score=1.0,
                action_taken="BLOCK"
            )
        
        return None

    def _check_cloud_code_memory(self, rule: Rule, context: Context, 
                               agent_behavior: Dict[str, Any]) -> Optional[Violation]:
        """检查Cloud Code记忆系统"""
        # 简化检查：记忆系统目录是否存在
        memory_path = Path(".trae/memories")
        if not memory_path.exists():
            return Violation(
                rule=rule,
                message="Cloud Code记忆系统目录 .trae/memories 不存在",
                match_score=0.4,
                action_taken="WARN"
            )
        
        return None


class AutoProcessor:
    """自动处理器"""

    def __init__(self):
        self.fixes_applied: List[Dict] = []

    def process(self, violations: List[Violation], context: Context) -> Dict[str, Any]:
        """自动处理违规"""
        results = {
            "processed_count": len(violations),
            "warnings_issued": 0,
            "blocks": 0,
            "auto_fixes": [],
            "needs_human_review": False
        }

        for violation in violations:
            if violation.rule.severity == "CRITICAL":
                results["blocks"] += 1
                self._handle_critical(violation, context, results)
            elif violation.rule.severity == "HIGH":
                results["warnings_issued"] += 1
                self._handle_high(violation, context, results)
            elif violation.rule.severity in ["MEDIUM", "LOW"]:
                results["warnings_issued"] += 1
                self._handle_medium_low(violation, context, results)

        return results

    def _handle_critical(self, violation: Violation, context: Context, results: Dict):
        """处理严重违规"""
        print(f"🚫 [CRITICAL] {violation.rule.name}: {violation.message}")
        violation.action_taken = "BLOCK"

    def _handle_high(self, violation: Violation, context: Context, results: Dict):
        """处理高优先级违规"""
        print(f"⚠️ [HIGH] {violation.rule.name}: {violation.message}")
        violation.action_taken = "HIGH_WARNING"

    def _handle_medium_low(self, violation: Violation, context: Context, results: Dict):
        """处理中低优先级违规"""
        print(f"⚠️ [WARN] {violation.rule.name}: {violation.message}")
        violation.action_taken = "WARN"


class Logger:
    """日志记录器"""

    def __init__(self, log_path: str = ".trae/logs"):
        self.log_path = Path(log_path)
        self.log_path.mkdir(parents=True, exist_ok=True)

    def log_violations(self, violations: List[Violation], context: Context):
        """记录违规"""
        log_file = self.log_path / f"violations_{datetime.date.today()}.json"
        
        log_entries = [v.to_dict() for v in violations]
        
        existing = []
        if log_file.exists():
            try:
                existing = json.loads(log_file.read_text(encoding="utf-8"))
            except:
                pass
        
        existing.extend(log_entries)
        log_file.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")

    def log_summary(self, summary: Dict):
        """记录汇总"""
        summary_file = self.log_path / "monitor_summary.json"
        
        existing = {}
        if summary_file.exists():
            try:
                existing = json.loads(summary_file.read_text(encoding="utf-8"))
            except:
                pass
        
        today = datetime.date.today().isoformat()
        existing[today] = summary
        summary_file.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")


class MonitorAgentV4:
    """
    监控智能体 v4.0
    完整 L1/L2/L3 规则体系监控 + 上下文同步执行
    """

    def __init__(self, rules_path: str = ".trae/rules"):
        self.rule_loader = RuleLoader(rules_path)
        self.rules = self.rule_loader.load_all_rules()
        self.validator = RuleValidator(self.rules)
        self.processor = AutoProcessor()
        self.logger = Logger()
        self.contexts: Dict[str, Context] = {}

    def create_context(self, context_id: str) -> Context:
        """创建共用上下文"""
        context = Context(context_id)
        self.contexts[context_id] = context
        print(f"[MonitorAgent] 创建共用上下文: {context_id}")
        return context

    def get_context(self, context_id: str) -> Context:
        """获取上下文"""
        if context_id not in self.contexts:
            return self.create_context(context_id)
        return self.contexts[context_id]

    def monitor(self, context_id: str, agent_behavior: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        监控执行（与智能体同步）
        """
        context = self.get_context(context_id)
        
        if agent_behavior is None:
            agent_behavior = {"timestamp": datetime.datetime.now().isoformat()}
        
        # 1. 验证规则
        violations = self.validator.validate(context, agent_behavior)
        
        # 2. 自动处理
        process_result = self.processor.process(violations, context)
        
        # 3. 记录日志
        self.logger.log_violations(violations, context)
        
        # 4. 生成报告
        report = self._generate_report(context, violations, process_result)
        
        # 5. 记录汇总
        summary = {
            "total_rules": len(self.rules),
            "violations": len(violations),
            "warnings": process_result.get("warnings_issued", 0),
            "blocks": process_result.get("blocks", 0),
            "auto_fixes": len(process_result.get("auto_fixes", [])),
            "context_id": context_id
        }
        self.logger.log_summary(summary)
        
        return report

    def _generate_report(self, context: Context, violations: List[Violation], 
                       process_result: Dict) -> Dict[str, Any]:
        """生成监控报告"""
        # 统计规则
        l1_count = sum(1 for r in self.rules if r.level == "L1")
        l2_count = sum(1 for r in self.rules if r.level == "L2")
        l3_count = sum(1 for r in self.rules if r.level == "L3")
        
        return {
            "status": "success",
            "timestamp": datetime.datetime.now().isoformat(),
            "context_id": context.context_id,
            "rules_summary": {
                "total": len(self.rules),
                "L1": l1_count,
                "L2": l2_count,
                "L3": l3_count
            },
            "violations": [v.to_dict() for v in violations],
            "process_result": process_result,
            "messages_in_context": len(context.messages),
            "tool_calls_in_context": len(context.tool_calls)
        }

    def quick_test(self):
        """快速测试"""
        print("\n" + "="*60)
        print("监控智能体 v4.0 - 快速测试")
        print("="*60)
        
        # 1. 创建测试上下文
        context = self.create_context("test_context_001")
        
        # 2. 添加测试消息
        context.add_message("user", "搜索一下如何学习Python")
        context.add_message("assistant", "好的，我给你一些建议...")
        
        # 3. 执行监控
        report = self.monitor("test_context_001")
        
        # 4. 打印报告
        print("\n监控报告:")
        print(f"  规则总数: {report['rules_summary']['total']}")
        print(f"  L1规则: {report['rules_summary']['L1']}")
        print(f"  L2规则: {report['rules_summary']['L2']}")
        print(f"  L3规则: {report['rules_summary']['L3']}")
        print(f"  违规数量: {report['violations']}")
        print(f"  警告数: {report['process_result']['warnings_issued']}")
        print(f"  阻断数: {report['process_result']['blocks']}")
        
        print("\n✅ 测试完成！")
        print("="*60)
        
        return report


if __name__ == "__main__":
    # 运行快速测试
    monitor = MonitorAgentV4()
    monitor.quick_test()


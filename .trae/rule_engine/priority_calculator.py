# -*- coding: utf-8 -*-
from typing import Dict, List, Any, Optional
from rule_parser import RuleParser


class PriorityCalculator:
    L1_PRIORITY = 100
    L2_PRIORITY = 50
    L3_PRIORITY = 10

    PRIORITY_MAP = {
        "L1": 100,
        "L2": 50,
        "L3": 10,
        "l1": 100,
        "l2": 50,
        "l3": 10
    }

    def __init__(self, rules_dir: str = None):
        self.parser = RuleParser(rules_dir)
        self.rules = []
        self.priorities: Dict[str, int] = {}

    def load_and_assign_priorities(self) -> Dict[str, int]:
        self.rules = self.parser.load_all_rules()
        self.priorities = {}

        for rule in self.rules:
            priority = self._calculate_priority(rule)
            self.priorities[rule["name"]] = priority

        return self.priorities

    def _calculate_priority(self, rule: Dict) -> int:
        file_name = rule["file_name"].lower()
        rule_name = rule["name"]

        if "l1" in file_name or "硬约束" in rule_name:
            return self.L1_PRIORITY
        elif "l2" in file_name or "软约束" in rule_name:
            return self.L2_PRIORITY
        elif "l3" in file_name:
            return self.L3_PRIORITY

        if any(keyword in rule_name for keyword in ["规则引擎", "规则管理", "安全", "质量"]):
            return self.L1_PRIORITY

        if file_name in ["rule-engine.md", "rule-mgmt-core.md", "security-audit.md"]:
            return self.L1_PRIORITY

        if file_name in ["test-core.md", "git-core.md"]:
            return self.L2_PRIORITY

        if file_name in ["source-core.md", "dialogue-core.md"]:
            return self.L3_PRIORITY

        if "engine" in file_name or "guard" in file_name:
            return self.L1_PRIORITY

        return self.L2_PRIORITY

    def get_priority(self, rule_name: str) -> Optional[int]:
        if rule_name in self.priorities:
            return self.priorities[rule_name]
        return None

    def sort_by_priority(self, descending: bool = True) -> List[tuple]:
        sorted_rules = sorted(
            self.priorities.items(),
            key=lambda x: x[1],
            reverse=descending
        )
        return sorted_rules

    def get_priority_level(self, rule_name: str) -> str:
        priority = self.get_priority(rule_name)
        if priority is None:
            return "Unknown"
        if priority >= 100:
            return "L1"
        elif priority >= 50:
            return "L2"
        else:
            return "L3"

    def validate_priority_order(self) -> Dict[str, Any]:
        sorted_rules = self.sort_by_priority()

        violations = []
        prev_priority = float("inf")

        for rule_name, priority in sorted_rules:
            if priority > prev_priority:
                violations.append({
                    "rule": rule_name,
                    "priority": priority,
                    "issue": "Priority out of order"
                })
            prev_priority = priority

        return {
            "total_rules": len(sorted_rules),
            "l1_count": sum(1 for _, p in sorted_rules if p == 100),
            "l2_count": sum(1 for _, p in sorted_rules if p == 50),
            "l3_count": sum(1 for _, p in sorted_rules if p == 10),
            "violations": violations,
            "is_valid": len(violations) == 0
        }


if __name__ == "__main__":
    calc = PriorityCalculator()
    priorities = calc.load_and_assign_priorities()

    print("=== 优先级计算 ===")
    print(f"总规则数: {len(priorities)}")

    validation = calc.validate_priority_order()
    print(f"L1规则: {validation['l1_count']}")
    print(f"L2规则: {validation['l2_count']}")
    print(f"L3规则: {validation['l3_count']}")
    print(f"验证通过: {validation['is_valid']}")

    print("\n优先级排序 (前10):")
    sorted_rules = calc.sort_by_priority()[:10]
    for name, priority in sorted_rules:
        level = calc.get_priority_level(name)
        print(f"  {priority} ({level}): {name}")

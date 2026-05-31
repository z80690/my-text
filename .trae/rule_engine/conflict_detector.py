# -*- coding: utf-8 -*-
from typing import Dict, List, Any, Optional, Tuple
from priority_calculator import PriorityCalculator


class ConflictDetector:
    def __init__(self, rules_dir: str = None):
        self.calculator = PriorityCalculator(rules_dir)
        self.rules = []
        self.priorities = {}
        self.conflicts: List[Dict[str, Any]] = []

    def load_rules_and_detect(self) -> List[Dict[str, Any]]:
        self.rules = self.calculator.parser.load_all_rules()
        self.priorities = self.calculator.load_and_assign_priorities()
        self.conflicts = []

        self._detect_same_priority_conflicts()
        self._detect_related_module_conflicts()

        return self.conflicts

    def _detect_same_priority_conflicts(self):
        priority_groups = {}
        for rule in self.rules:
            priority = self.priorities.get(rule["name"], 50)
            if priority not in priority_groups:
                priority_groups[priority] = []
            priority_groups[priority].append(rule)

        for priority, rules in priority_groups.items():
            if len(rules) > 1:
                for i, r1 in enumerate(rules):
                    for r2 in rules[i+1:]:
                        if self._has_module_overlap(r1, r2):
                            conflict = {
                                "type": "same_priority",
                                "priority": priority,
                                "rule1": r1["name"],
                                "rule2": r2["name"],
                                "overlap": self._get_overlapping_modules(r1, r2),
                                "resolution": "L1>L2>L3" if priority < 100 else "时间戳排序"
                            }
                            self.conflicts.append(conflict)

    def _detect_related_module_conflicts(self):
        for i, r1 in enumerate(self.rules):
            for r2 in self.rules[i+1:]:
                overlap = self._get_overlapping_modules(r1, r2)
                if len(overlap) >= 3:
                    conflict = {
                        "type": "module_overlap",
                        "priority1": self.priorities.get(r1["name"], 50),
                        "priority2": self.priorities.get(r2["name"], 50),
                        "rule1": r1["name"],
                        "rule2": r2["name"],
                        "overlap": overlap,
                        "resolution": "按优先级裁决"
                    }
                    self.conflicts.append(conflict)

    def _has_module_overlap(self, r1: Dict, r2: Dict) -> bool:
        modules1 = set(r1.get("related_modules", []))
        modules2 = set(r2.get("related_modules", []))
        return len(modules1 & modules2) > 0

    def _get_overlapping_modules(self, r1: Dict, r2: Dict) -> List[str]:
        modules1 = set(r1.get("related_modules", []))
        modules2 = set(r2.get("related_modules", []))
        return list(modules1 & modules2)

    def check_conflict(self, rule1_name: str, rule2_name: str) -> Optional[Dict]:
        for conflict in self.conflicts:
            if (conflict.get("rule1") == rule1_name and conflict.get("rule2") == rule2_name) or \
               (conflict.get("rule1") == rule2_name and conflict.get("rule2") == rule1_name):
                return conflict
        return None

    def get_conflict_report(self) -> Dict[str, Any]:
        return {
            "total_conflicts": len(self.conflicts),
            "same_priority_conflicts": sum(1 for c in self.conflicts if c["type"] == "same_priority"),
            "module_overlap_conflicts": sum(1 for c in self.conflicts if c["type"] == "module_overlap"),
            "conflicts": self.conflicts,
            "has_critical_conflicts": any(c["priority"] == 100 for c in self.conflicts if c["type"] == "same_priority")
        }


if __name__ == "__main__":
    detector = ConflictDetector()
    conflicts = detector.load_rules_and_detect()

    print("=== 冲突检测报告 ===")
    print(f"总冲突数: {len(conflicts)}")

    report = detector.get_conflict_report()
    print(f"同优先级冲突: {report['same_priority_conflicts']}")
    print(f"模块重叠冲突: {report['module_overlap_conflicts']}")

    if conflicts:
        print("\n冲突详情 (前5):")
        for c in conflicts[:5]:
            print(f"  [{c['type']}] {c['rule1']} <-> {c['rule2']}")
    else:
        print("\n未检测到冲突")

# -*- coding: utf-8 -*-
from typing import Dict, List, Any, Optional
from conflict_detector import ConflictDetector
from priority_calculator import PriorityCalculator
import time


class ConflictResolver:
    def __init__(self, rules_dir: str = None):
        self.detector = ConflictDetector(rules_dir)
        self.calculator = PriorityCalculator(rules_dir)
        self.resolutions: List[Dict[str, Any]] = []
        self.rule_timestamps: Dict[str, float] = {}

    def resolve_conflict(self, conflict: Dict) -> Dict[str, Any]:
        rule1 = conflict.get("rule1")
        rule2 = conflict.get("rule2")
        conflict_type = conflict.get("type")

        priority1 = self.calculator.get_priority(rule1) or 50
        priority2 = self.calculator.get_priority(rule2) or 50

        if priority1 != priority2:
            winner = rule1 if priority1 > priority2 else rule2
            loser = rule2 if priority1 > priority2 else rule1
            reason = f"优先级裁决: {priority1} > {priority2}"
        else:
            timestamp1 = self.rule_timestamps.get(rule1, time.time())
            timestamp2 = self.rule_timestamps.get(rule2, time.time())
            if timestamp1 >= timestamp2:
                winner = rule1
                loser = rule2
            else:
                winner = rule2
                loser = rule1
            reason = f"时间戳裁决: {timestamp1} vs {timestamp2}"

        resolution = {
            "conflict": conflict,
            "winner": winner,
            "loser": loser,
            "reason": reason,
            "timestamp": time.time()
        }

        self.resolutions.append(resolution)
        return resolution

    def resolve_all_conflicts(self) -> List[Dict[str, Any]]:
        conflicts = self.detector.load_rules_and_detect()
        self.resolutions = []

        for conflict in conflicts:
            resolution = self.resolve_conflict(conflict)
            self.resolutions.append(resolution)

        return self.resolutions

    def get_resolution_report(self) -> Dict[str, Any]:
        return {
            "total_conflicts": len(self.detector.conflicts),
            "total_resolutions": len(self.resolutions),
            "resolutions": self.resolutions,
            "all_resolved": len(self.resolutions) == len(self.detector.conflicts)
        }

    def validate_resolutions(self) -> Dict[str, Any]:
        validation = {
            "valid": True,
            "issues": []
        }

        for resolution in self.resolutions:
            winner = resolution["winner"]
            loser = resolution["loser"]
            conflict = resolution["conflict"]

            winner_priority = self.calculator.get_priority(winner) or 50
            loser_priority = self.calculator.get_priority(loser) or 50

            if winner_priority < loser_priority:
                validation["valid"] = False
                validation["issues"].append({
                    "resolution": resolution,
                    "issue": f"Winner {winner} has lower priority than loser {loser}"
                })

        validation["all_valid"] = validation["valid"] and len(validation["issues"]) == 0
        return validation


if __name__ == "__main__":
    resolver = ConflictResolver()
    resolutions = resolver.resolve_all_conflicts()

    print("=== 冲突裁决报告 ===")
    print(f"总冲突数: {len(resolutions)}")

    report = resolver.get_resolution_report()
    print(f"已裁决: {report['total_resolutions']}")
    print(f"全部裁决: {'是' if report['all_resolved'] else '否'}")

    validation = resolver.validate_resolutions()
    print(f"裁决有效: {'是' if validation['all_valid'] else '否'}")

    print("\n裁决详情 (前5):")
    for r in resolutions[:5]:
        print(f"  {r['winner']} 胜出 (vs {r['loser']}): {r['reason'][:30]}...")

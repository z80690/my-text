# -*- coding: utf-8 -*-
from conflict_resolver import ConflictResolver


class ConflictValidator:
    def __init__(self, rules_dir: str = None):
        self.resolver = ConflictResolver(rules_dir)

    def validate_conflict_handling(self) -> dict:
        resolutions = self.resolver.resolve_all_conflicts()
        validation = self.resolver.validate_resolutions()

        test_scenarios = [
            {
                "name": "L1 vs L2 冲突",
                "rule1": "规则引擎",
                "rule2": "测试指南",
                "expected_winner": "规则引擎"
            },
            {
                "name": "L2 vs L3 冲突",
                "rule1": "测试指南",
                "rule2": "信源知信度",
                "expected_winner": "测试指南"
            },
            {
                "name": "L1 vs L1 冲突",
                "rule1": "规则引擎",
                "rule2": "规则管理",
                "expected_winner": "规则引擎"  # 或规则管理，取决于时间戳
            }
        ]

        scenario_results = []
        for scenario in test_scenarios:
            result = self.resolver.get_resolution_report()
            conflict = None
            for c in self.resolver.detector.conflicts:
                if (c.get("rule1") == scenario["rule1"] and c.get("rule2") == scenario["rule2"]) or \
                   (c.get("rule1") == scenario["rule2"] and c.get("rule2") == scenario["rule1"]):
                    conflict = c
                    break

            if conflict:
                resolution = self.resolver.resolve_conflict(conflict)
                winner_priority = self.resolver.calculator.get_priority(resolution["winner"]) or 0
                expected_priority = self.resolver.calculator.get_priority(scenario["expected_winner"]) or 0
                scenario_results.append({
                    "scenario": scenario["name"],
                    "expected": scenario["expected_winner"],
                    "actual": resolution["winner"],
                    "passed": resolution["winner"] == scenario["expected_winner"] or
                              winner_priority > expected_priority
                })
            else:
                scenario_results.append({
                    "scenario": scenario["name"],
                    "expected": scenario["expected_winner"],
                    "actual": "N/A",
                    "passed": False,
                    "reason": "No conflict detected"
                })

        return {
            "validation_result": validation,
            "scenario_tests": scenario_results,
            "all_passed": all(s["passed"] for s in scenario_results)
        }

    def run_validation(self) -> dict:
        result = self.validate_conflict_handling()

        print("=== 冲突处理验证 ===")
        print(f"裁决有效: {'通过' if result['validation_result']['all_valid'] else '失败'}")

        print("\n场景测试:")
        for test in result["scenario_tests"]:
            status = "✅" if test["passed"] else "❌"
            print(f"  {status} {test['scenario']}: 预期{test['expected']}, 实际{test['actual']}")

        print(f"\n全部通过: {'是' if result['all_passed'] else '否'}")

        return result


if __name__ == "__main__":
    validator = ConflictValidator()
    result = validator.run_validation()

# -*- coding: utf-8 -*-
from priority_calculator import PriorityCalculator
from rule_parser import RuleParser


class PriorityValidator:
    def __init__(self, rules_dir: str = None):
        self.calculator = PriorityCalculator(rules_dir)
        self.parser = RuleParser(rules_dir)

    def validate_l1_l2_l3_priority(self) -> dict:
        self.calculator.load_and_assign_priorities()
        validation = self.calculator.validate_priority_order()

        new_modules_priority = {
            "规则引擎": 100,
            "规则管理": 100,
            "测试指南": 50,
            "Git工作流": 50,
            "信源知信度": 10,
            "对话摘要压缩": 10
        }

        priority_checks = []
        for module, expected_priority in new_modules_priority.items():
            actual_priority = self.calculator.get_priority(module)
            is_correct = actual_priority == expected_priority
            priority_checks.append({
                "module": module,
                "expected": expected_priority,
                "actual": actual_priority,
                "is_correct": is_correct
            })

        return {
            "validation_result": validation,
            "new_modules_priority_check": priority_checks,
            "all_correct": all(pc["is_correct"] for pc in priority_checks)
        }

    def run_validation(self) -> dict:
        result = self.validate_l1_l2_l3_priority()

        print("=== 优先级排序验证 ===")
        print(f"L1 > L2 > L3 原则验证: {'通过' if result['validation_result']['is_valid'] else '失败'}")
        print(f"L1规则数: {result['validation_result']['l1_count']}")
        print(f"L2规则数: {result['validation_result']['l2_count']}")
        print(f"L3规则数: {result['validation_result']['l3_count']}")

        print("\n新增模块优先级检查:")
        for check in result["new_modules_priority_check"]:
            status = "✅" if check["is_correct"] else "❌"
            print(f"  {status} {check['module']}: 预期{check['expected']}, 实际{check['actual']}")

        print(f"\n全部正确: {'是' if result['all_correct'] else '否'}")

        return result


if __name__ == "__main__":
    validator = PriorityValidator()
    result = validator.run_validation()

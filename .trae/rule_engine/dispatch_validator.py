# -*- coding: utf-8 -*-
from module_dispatcher import ModuleDispatcher


class DispatchValidator:
    def __init__(self, rules_dir: str = None):
        self.dispatcher = ModuleDispatcher(rules_dir)

    def validate_module_coordination(self) -> dict:
        test_tasks = [
            {
                "name": "规则验证任务",
                "task": {"type": "规则验证", "keywords": ["规则", "测试"]},
                "expected_order": ["规则管理", "规则引擎", "测试指南"]
            },
            {
                "name": "代码审查任务",
                "task": {"type": "代码审查", "keywords": ["编码", "Git"]},
                "expected_order": ["编码规范", "Git工作流"]
            },
            {
                "name": "安全审计任务",
                "task": {"type": "安全审计", "keywords": ["安全"]},
                "expected_order": ["安全审计"]
            }
        ]

        results = []
        for test in test_tasks:
            self.dispatcher.execution_log = []
            result = self.dispatcher.dispatch(test["task"])
            actual_order = [r["module"] for r in result["execution_order"]]

            priority_correct = self._verify_priority_order(actual_order)

            results.append({
                "test_name": test["name"],
                "expected_order": test["expected_order"],
                "actual_order": actual_order,
                "priority_correct": priority_correct,
                "success": result["success"]
            })

        return {
            "total_tests": len(results),
            "passed_tests": sum(1 for r in results if r["success"] and r["priority_correct"]),
            "results": results,
            "all_passed": all(r["success"] and r["priority_correct"] for r in results)
        }

    def _verify_priority_order(self, actual_order: list) -> bool:
        priorities = {
            "规则引擎": 100, "规则管理": 100, "安全审计": 100,
            "测试指南": 50, "Git工作流": 50, "编码规范": 50,
            "质量保障": 50, "6A项目流程": 50,
            "信源知信度": 10, "对话摘要压缩": 10
        }

        for i in range(len(actual_order) - 1):
            p1 = priorities.get(actual_order[i], 50)
            p2 = priorities.get(actual_order[i + 1], 50)
            if p1 < p2:
                return False
        return True

    def run_validation(self) -> dict:
        result = self.validate_module_coordination()

        print("=== 模块协同验证 ===")
        print(f"总测试: {result['total_tests']}")
        print(f"通过: {result['passed_tests']}")

        print("\n测试详情:")
        for r in result["results"]:
            status = "✅" if r["success"] and r["priority_correct"] else "❌"
            print(f"  {status} {r['test_name']}")
            print(f"     预期: {r['expected_order']}")
            print(f"     实际: {r['actual_order']}")

        print(f"\n全部通过: {'是' if result['all_passed'] else '否'}")

        return result


if __name__ == "__main__":
    validator = DispatchValidator()
    result = validator.run_validation()

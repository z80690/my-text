# -*- coding: utf-8 -*-
from typing import Dict, List, Any, Optional, Callable
from priority_calculator import PriorityCalculator
from conflict_detector import ConflictDetector
from conflict_resolver import ConflictResolver


class ModuleDispatcher:
    def __init__(self, rules_dir: str = None):
        self.calculator = PriorityCalculator(rules_dir)
        self.detector = ConflictDetector(rules_dir)
        self.resolver = ConflictResolver(rules_dir)
        self.rules = []
        self.execution_log: List[Dict[str, Any]] = []
        self.module_handlers: Dict[str, Callable] = {}

    def register_handler(self, module_name: str, handler: Callable):
        self.module_handlers[module_name] = handler

    def load_rules(self):
        self.rules = self.calculator.parser.load_all_rules()
        self.calculator.load_and_assign_priorities()
        self.detector.load_rules_and_detect()

    def dispatch(self, task: Dict[str, Any]) -> Dict[str, Any]:
        self.load_rules()

        required_modules = task.get("required_modules", [])
        if not required_modules:
            required_modules = self._infer_modules_from_task(task)

        sorted_modules = self._sort_modules_by_priority(required_modules)

        execution_order = []
        for module_name in sorted_modules:
            result = self._execute_module(module_name, task)
            execution_order.append(result)

        return {
            "task": task,
            "execution_order": execution_order,
            "success": all(r.get("success", False) for r in execution_order)
        }

    def _infer_modules_from_task(self, task: Dict) -> List[str]:
        keywords = task.get("keywords", [])
        inferred = []

        keyword_map = {
            "测试": ["测试指南"],
            "Git": ["Git工作流"],
            "规则": ["规则引擎", "规则管理"],
            "安全": ["安全审计"],
            "质量": ["质量保障"],
            "对话": ["对话摘要压缩"],
            "信源": ["信源知信度"],
            "编码": ["编码规范"],
            "6A": ["6A项目流程"]
        }

        for keyword in keywords:
            for key, modules in keyword_map.items():
                if key in keyword:
                    inferred.extend(modules)

        return list(set(inferred))

    def _sort_modules_by_priority(self, module_names: List[str]) -> List[str]:
        def get_priority(name):
            for rule in self.rules:
                if rule["name"] == name:
                    return self.calculator.get_priority(name) or 50
            return 50

        return sorted(module_names, key=get_priority, reverse=True)

    def _execute_module(self, module_name: str, task: Dict) -> Dict[str, Any]:
        handler = self.module_handlers.get(module_name)

        if handler:
            try:
                result = handler(task)
                self.execution_log.append({
                    "module": module_name,
                    "status": "success",
                    "result": result
                })
                return {"module": module_name, "success": True, "result": result}
            except Exception as e:
                self.execution_log.append({
                    "module": module_name,
                    "status": "error",
                    "error": str(e)
                })
                return {"module": module_name, "success": False, "error": str(e)}
        else:
            self.execution_log.append({
                "module": module_name,
                "status": "skipped",
                "reason": "No handler registered"
            })
            return {"module": module_name, "success": True, "skipped": True}

    def get_execution_report(self) -> Dict[str, Any]:
        return {
            "total_modules": len(set(log["module"] for log in self.execution_log)),
            "execution_log": self.execution_log,
            "success_count": sum(1 for log in self.execution_log if log["status"] == "success"),
            "error_count": sum(1 for log in self.execution_log if log["status"] == "error")
        }


if __name__ == "__main__":
    dispatcher = ModuleDispatcher()

    def mock_handler(task):
        return {"status": "ok", "data": task}

    dispatcher.register_handler("规则引擎", mock_handler)
    dispatcher.register_handler("规则管理", mock_handler)
    dispatcher.register_handler("测试指南", mock_handler)

    task = {
        "type": "规则验证",
        "keywords": ["规则", "测试"]
    }

    result = dispatcher.dispatch(task)

    print("=== 模块调度报告 ===")
    print(f"任务: {result['task']['type']}")
    print(f"成功: {result['success']}")
    print(f"执行顺序:")
    for i, r in enumerate(result["execution_order"], 1):
        print(f"  {i}. {r['module']}: {'成功' if r.get('success') else '失败'}")

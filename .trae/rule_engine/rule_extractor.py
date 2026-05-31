# -*- coding: utf-8 -*-
from typing import Dict, List, Any
from rule_parser import RuleParser


class RuleExtractor:
    def __init__(self, rules_dir: str = None):
        self.parser = RuleParser(rules_dir)
        self.rules = []
        self.l1_rules = []
        self.l2_rules = []
        self.l3_rules = []

    def load_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        self.rules = self.parser.load_all_rules()
        self._categorize_by_level()
        return {
            "all": self.rules,
            "l1": self.l1_rules,
            "l2": self.l2_rules,
            "l3": self.l3_rules
        }

    def _categorize_by_level(self):
        self.l1_rules = []
        self.l2_rules = []
        self.l3_rules = []

        for rule in self.rules:
            level = self._detect_level(rule)
            if level == 1:
                self.l1_rules.append(rule)
            elif level == 2:
                self.l2_rules.append(rule)
            elif level == 3:
                self.l3_rules.append(rule)

    def _detect_level(self, rule: Dict) -> int:
        file_name = rule["file_name"].lower()

        if "l1" in file_name or "硬约束" in rule["name"]:
            return 1
        elif "l2" in file_name or "软约束" in rule["name"]:
            return 2
        elif "l3" in file_name:
            return 3

        if "core" in file_name or "engine" in file_name:
            return 1

        return 2

    def extract_rule_metadata(self, rule: Dict) -> Dict[str, Any]:
        return {
            "name": rule["name"],
            "file_name": rule["file_name"],
            "core_functions_count": len(rule["core_functions"]),
            "execution_steps_count": len(rule["execution_steps"]),
            "constraint_rules_count": len(rule["constraint_rules"]),
            "related_modules_count": len(rule["related_modules"]),
            "related_modules": rule["related_modules"]
        }

    def get_extraction_report(self) -> Dict[str, Any]:
        self.load_rules()

        return {
            "total_rules": len(self.rules),
            "l1_count": len(self.l1_rules),
            "l2_count": len(self.l2_rules),
            "l3_count": len(self.l3_rules),
            "l1_rules": [self.extract_rule_metadata(r) for r in self.l1_rules],
            "l2_rules": [self.extract_rule_metadata(r) for r in self.l2_rules],
            "l3_rules": [self.extract_rule_metadata(r) for r in self.l3_rules]
        }


if __name__ == "__main__":
    extractor = RuleExtractor()
    report = extractor.get_extraction_report()

    print(f"Total rules: {report['total_rules']}")
    print(f"L1 rules: {report['l1_count']}")
    print(f"L2 rules: {report['l2_count']}")
    print(f"L3 rules: {report['l3_count']}")

    print("\nL1 Rules:")
    for r in report["l1_rules"][:3]:
        print(f"  - {r['name']} ({r['core_functions_count']} functions)")

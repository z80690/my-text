# -*- coding: utf-8 -*-
import json
from pathlib import Path
from rule_parser import RuleParser


class RuleParsingReport:
    def __init__(self, rules_dir: str = None):
        self.parser = RuleParser(rules_dir)
        self.rules = []

    def generate_report(self) -> dict:
        self.rules = self.parser.load_all_rules()
        validation = self.parser.validate_all_files()

        report = {
            "report_type": "规则解析报告",
            "version": "v1.0.0",
            "summary": {
                "total_files": validation["total_files"],
                "valid_files": validation["valid_files"],
                "total_rules": len(self.rules),
                "parsing_success_rate": self._calc_success_rate(validation)
            },
            "validation": {
                "utf8_lf_check": {
                    "valid": validation["valid_files"],
                    "invalid": len(validation["invalid_files"]),
                    "invalid_files": validation["invalid_files"]
                },
                "parse_errors": validation["parse_errors"]
            },
            "rules": self._build_rules_detail(),
            "new_modules": self._get_new_modules(),
            "all_modules": self._get_all_modules()
        }

        return report

    def _calc_success_rate(self, validation: dict) -> float:
        if validation["total_files"] == 0:
            return 0.0
        return round(validation["valid_files"] / validation["total_files"] * 100, 2)

    def _build_rules_detail(self) -> list:
        details = []
        for rule in self.rules:
            details.append({
                "name": rule["name"],
                "file_name": rule["file_name"],
                "core_functions": rule["core_functions"],
                "execution_steps": rule["execution_steps"],
                "constraint_rules": rule["constraint_rules"],
                "related_modules": rule["related_modules"]
            })
        return details

    def _get_new_modules(self) -> list:
        new_module_names = [
            "规则引擎", "规则管理", "测试指南", "Git工作流",
            "信源知信度", "对话摘要压缩"
        ]
        return [r for r in self.rules if r["name"] in new_module_names]

    def _get_all_modules(self) -> list:
        return [rule["name"] for rule in self.rules]

    def save_report(self, output_path: str = None):
        report = self.generate_report()

        if output_path is None:
            output_path = Path(__file__).parent / "parsing_report.json"

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        return report


if __name__ == "__main__":
    report_gen = RuleParsingReport()
    report = report_gen.generate_report()

    print("=== 规则解析报告 ===")
    print(f"总文件数: {report['summary']['total_files']}")
    print(f"有效文件: {report['summary']['valid_files']}")
    print(f"解析成功率: {report['summary']['parsing_success_rate']}%")
    print(f"新增模块: {len(report['new_modules'])}个")

    for mod in report["new_modules"]:
        print(f"  - {mod['name']}: {len(mod['core_functions'])}核心功能")

    report_gen.save_report()
    print("\n报告已保存至 parsing_report.json")

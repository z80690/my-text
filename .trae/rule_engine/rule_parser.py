# -*- coding: utf-8 -*-
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Any


class RuleParser:
    def __init__(self, rules_dir: str = None):
        if rules_dir is None:
            self.rules_dir = Path(__file__).parent.parent / "rules"
        else:
            self.rules_dir = Path(rules_dir)
        self.rules: List[Dict[str, Any]] = []
        self.errors: List[str] = []

    def load_all_rules(self) -> List[Dict[str, Any]]:
        self.rules = []
        self.errors = []

        if not self.rules_dir.exists():
            self.errors.append(f"Rules directory does not exist: {self.rules_dir}")
            return self.rules

        md_files = list(self.rules_dir.glob("*.md"))
        if not md_files:
            self.errors.append(f"No .md files found in {self.rules_dir}")
            return self.rules

        for md_file in md_files:
            try:
                rule = self.parse_rule_file(md_file)
                if rule:
                    self.rules.append(rule)
            except Exception as e:
                self.errors.append(f"Error parsing {md_file.name}: {str(e)}")

        return self.rules

    def parse_rule_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.split("\n")
        rule = {
            "file_name": file_path.name,
            "file_path": str(file_path),
            "name": "",
            "core_functions": [],
            "execution_steps": [],
            "constraint_rules": [],
            "related_modules": [],
            "raw_content": content
        }

        current_section = None
        section_content = []

        for line in lines:
            line = line.rstrip("\r\n")

            if line.startswith("# ") and current_section is None:
                rule["name"] = line[2:].strip()
                continue

            if line.startswith("## "):
                if current_section and section_content:
                    self._process_section(rule, current_section, section_content)

                section_name = line[3:].strip()
                current_section = self._get_section_type(section_name)
                section_content = []
            else:
                if current_section:
                    section_content.append(line)

        if current_section and section_content:
            self._process_section(rule, current_section, section_content)

        return rule if rule["name"] else None

    def _get_section_type(self, section_name: str) -> Optional[str]:
        section_map = {
            "核心功能": "core_functions",
            "执行步骤": "execution_steps",
            "约束规则": "constraint_rules",
            "关联模块": "related_modules"
        }
        return section_map.get(section_name)

    def _process_section(self, rule: Dict, section_type: str, content: List[str]):
        if section_type == "related_modules":
            modules = []
            for line in content:
                line = line.strip()
                if line and not line.startswith("#"):
                    modules.extend([m.strip() for m in line.split("、") if m.strip()])
            rule[section_type] = modules
        else:
            items = []
            for line in content:
                line = line.strip()
                if line and not line.startswith("#") and not line.startswith("-"):
                    items.append(line)
            rule[section_type] = items

    def get_rule_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        for rule in self.rules:
            if rule["name"] == name:
                return rule
        return None

    def get_rules_by_module(self, module_name: str) -> List[Dict[str, Any]]:
        results = []
        for rule in self.rules:
            if module_name in rule["related_modules"]:
                results.append(rule)
        return results

    def validate_utf8_lf(self, file_path: Path) -> bool:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            if "\r\n" in content:
                return False
            return True
        except UnicodeDecodeError:
            return False

    def validate_all_files(self) -> Dict[str, Any]:
        results = {
            "total_files": 0,
            "valid_files": 0,
            "invalid_files": [],
            "parse_errors": []
        }

        if not self.rules_dir.exists():
            return results

        md_files = list(self.rules_dir.glob("*.md"))
        results["total_files"] = len(md_files)

        for md_file in md_files:
            if self.validate_utf8_lf(md_file):
                results["valid_files"] += 1
            else:
                results["invalid_files"].append(str(md_file))

        results["parse_errors"] = self.errors

        return results

    def get_parsing_report(self) -> Dict[str, Any]:
        return {
            "total_rules": len(self.rules),
            "rules": [
                {
                    "name": r["name"],
                    "file_name": r["file_name"],
                    "core_functions_count": len(r["core_functions"]),
                    "execution_steps_count": len(r["execution_steps"]),
                    "constraint_rules_count": len(r["constraint_rules"]),
                    "related_modules_count": len(r["related_modules"])
                }
                for r in self.rules
            ],
            "errors": self.errors
        }


if __name__ == "__main__":
    parser = RuleParser()
    rules = parser.load_all_rules()
    print(f"Loaded {len(rules)} rules")

    validation = parser.validate_all_files()
    print(f"Valid files: {validation['valid_files']}/{validation['total_files']}")

    report = parser.get_parsing_report()
    print(f"Parsing report: {report['total_rules']} rules parsed")

    for rule_info in report["rules"][:3]:
        print(f"  - {rule_info['name']}: {rule_info['core_functions_count']} core functions")

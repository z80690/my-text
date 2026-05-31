# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r"c:\Users\Administrator\Desktop\my-text\.trae\rule_engine")

from rule_parser import RuleParser

parser = RuleParser()
rules = parser.load_all_rules()

for rule in rules:
    if rule["name"] == "规则引擎":
        print("=== 规则引擎 ===")
        print(f"core_functions: {rule['core_functions']}")
        print(f"execution_steps: {rule['execution_steps']}")
        print(f"constraint_rules: {rule['constraint_rules']}")
        print(f"related_modules: {rule['related_modules']}")
        break

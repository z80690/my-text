# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r"c:\Users\Administrator\Desktop\my-text\.trae\rule_engine")

from rule_parser import RuleParser

parser = RuleParser()
rules = parser.load_all_rules()

print(f"Total rules loaded: {len(rules)}")
print(f"First 5 rule names: {[r['name'] for r in rules[:5]]}")

target = parser.get_rule_by_name("规则引擎")
print(f"\nget_rule_by_name('规则引擎'): {target}")
print(f"target['core_functions']: {target['core_functions'] if target else 'None'}")

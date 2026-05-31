# -*- coding: utf-8 -*-
from rule_parser import RuleParser

parser = RuleParser()
rules = parser.load_all_rules()

target_rules = ['规则引擎', '规则管理', '测试指南', 'Git工作流', '信源知信度', '对话摘要压缩']

for name in target_rules:
    rule = parser.get_rule_by_name(name)
    if rule:
        print(f"✅ {name}:")
        print(f"   核心功能: {len(rule['core_functions'])}条")
        print(f"   执行步骤: {len(rule['execution_steps'])}条")
        print(f"   约束规则: {len(rule['constraint_rules'])}条")
        print(f"   关联模块: {len(rule['related_modules'])}个")
    else:
        print(f"❌ {name}: 未找到")

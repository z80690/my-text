# -*- coding: utf-8 -*-
"""测试规则文件加载"""

import sys
sys.path.insert(0, '.trae')

from monitor_system_v5 import RuleLoader

def test_rules_loading():
    print('=' * 70)
    print('测试规则文件加载')
    print('=' * 70)
    
    # 创建规则加载器
    loader = RuleLoader()
    
    # 加载所有规则
    rules = loader.load_all_rules()
    
    print('')
    print('已加载的规则列表:')
    print('-' * 50)
    
    if not rules:
        print('  ❌ 未加载到任何规则')
        return False
    
    for rule in rules:
        print(f'  [{rule.id}] {rule.name}')
        print(f'    级别: {rule.level}')
        print(f'    严重程度: {rule.severity}')
        print(f'    描述: {rule.description}')
        print('')
    
    print('=' * 70)
    print(f'测试结果: 成功加载 {len(rules)} 条规则')
    print('=' * 70)
    
    return True

if __name__ == '__main__':
    test_rules_loading()

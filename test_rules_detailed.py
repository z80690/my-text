# -*- coding: utf-8 -*-
"""测试规则文件加载 - 详细版"""

import sys
import os

# 设置路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.trae'))

from monitor_system import MonitorAgentV4

def test_rules():
    print('=' * 70)
    print('测试规则文件加载 - .trae/rules')
    print('=' * 70)
    
    # 创建监控智能体
    monitor = MonitorAgentV4()
    
    print('')
    print('规则加载统计:')
    print('-' * 50)
    
    l1_count = len([r for r in monitor.rules if r.level == 'L1'])
    l2_count = len([r for r in monitor.rules if r.level == 'L2'])
    l3_count = len([r for r in monitor.rules if r.level == 'L3'])
    total = len(monitor.rules)
    
    print(f'  L1 规则: {l1_count} 条')
    print(f'  L2 规则: {l2_count} 条')
    print(f'  L3 规则: {l3_count} 条')
    print(f'  总计: {total} 条')
    
    print('')
    print('规则详情:')
    print('-' * 50)
    
    # 按级别分组
    rules_by_level = {'L1': [], 'L2': [], 'L3': []}
    for rule in monitor.rules:
        rules_by_level[rule.level].append(rule)
    
    for level in ['L1', 'L2', 'L3']:
        print(f'\n  [{level}]')
        for rule in rules_by_level[level]:
            print(f'    [{rule.id}] {rule.name} ({rule.severity})')
    
    print('')
    print('=' * 70)
    
    # 验证测试
    if total > 0:
        print('✅ PASS: 规则文件已成功加载！')
        print(f'   共加载 {total} 条规则')
        return True
    else:
        print('❌ FAIL: 未加载到任何规则')
        return False

if __name__ == '__main__':
    test_rules()
    # 确保输出被刷新
    sys.stdout.flush()

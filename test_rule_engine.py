# -*- coding: utf-8 -*-
"""
规则引擎测试脚本
验证基于设计模式的规则体系重构
"""

import sys
sys.path.insert(0, '.trae')

from rule_engine import RuleEngine, RuleContext, ToolPriorityRule, AutoMemoryRule

def test_design_patterns():
    print('=' * 70)
    print('规则引擎设计模式测试')
    print('=' * 70)
    
    # 1. 测试策略模式 - 规则选择
    print('\n[测试1] 策略模式 - 规则选择')
    print('-' * 50)
    
    rules = [ToolPriorityRule(), AutoMemoryRule()]
    context = RuleContext(
        user_input='我喜欢用Python编程',
        agent_state={},
        tool_calls=[],
        context_history=[]
    )
    
    for rule in rules:
        result = rule.evaluate(context)
        print(f"规则 [{rule.get_id()}] {rule.get_name()}: {'触发' if result else '未触发'}")
    
    # 2. 测试规则引擎执行
    print('\n[测试2] 规则引擎执行')
    print('-' * 50)
    
    engine = RuleEngine()
    
    # 测试工具优先规则
    result1 = engine.execute_rules(
        user_input='搜索如何学习Python',
        agent_state={'agent_id': 'test_agent'},
        tool_calls=[],
        context_history=[],
        metadata={'context_id': 'test_001'}
    )
    print(f"输入: 搜索如何学习Python")
    print(f"执行规则数: {len(result1['evaluation'].get('results', []))}")
    
    # 测试自动记忆规则
    result2 = engine.execute_rules(
        user_input='我习惯使用VSCode编程',
        agent_state={'agent_id': 'test_agent'},
        tool_calls=[],
        context_history=[],
        metadata={'context_id': 'test_002'}
    )
    print(f"\n输入: 我习惯使用VSCode编程")
    print(f"执行规则数: {len(result2['evaluation'].get('results', []))}")
    
    # 3. 测试责任链模式
    print('\n[测试3] 责任链模式 - L1/L2规则链')
    print('-' * 50)
    
    result3 = engine.execute_rules(
        user_input='帮我分析一下这个数据，然后搜索相关资料',
        agent_state={'agent_id': 'test_agent'},
        tool_calls=['data_analyzer', 'web_search'],
        context_history=[{'role': 'user', 'content': '之前的消息'}],
        metadata={'context_id': 'test_003'}
    )
    
    results = result3['evaluation'].get('results', [])
    print(f"总规则执行数: {len(results)}")
    for r in results:
        print(f"  [{r['rule_id']}] {r['rule_name']} - {r['level']}")
    
    print('\n' + '=' * 70)
    print('✅ 设计模式规则引擎测试完成')
    print('=' * 70)

if __name__ == '__main__':
    test_design_patterns()

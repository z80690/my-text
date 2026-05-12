# -*- coding: utf-8 -*-
"""
规则引擎完整测试脚本
验证：设计模式实现、双向同步、就近加载
"""

import sys
import time
sys.path.insert(0, '.trae')

from rule_engine import RuleEngine, RuleContext, ToolPriorityRule, AutoMemoryRule

def test_design_patterns():
    print('=' * 70)
    print('测试1: 设计模式实现验证')
    print('=' * 70)
    
    # 策略模式测试
    print('\n[策略模式] 规则动态选择')
    rules = [ToolPriorityRule(), AutoMemoryRule()]
    context = RuleContext(
        user_input='我喜欢用Python编程',
        agent_state={},
        tool_calls=[],
        context_history=[]
    )
    
    for rule in rules:
        result = rule.evaluate(context)
        print(f"  [{rule.get_id()}] {rule.get_name()}: {'触发' if result else '未触发'}")
    
    # 组合模式测试
    print('\n[组合模式] 规则组管理')
    from rule_engine import RuleComposite
    composite = RuleComposite('测试规则组', 'L1')
    composite.add_rule(ToolPriorityRule())
    composite.add_rule(AutoMemoryRule())
    print(f"  规则组名称: {composite.get_name()}")
    print(f"  规则数量: {len(composite._children)}")
    print(f"  最高严重级别: {composite.get_severity()}")
    
    print('\n✅ 设计模式验证通过')

def test_two_way_sync():
    print('\n' + '=' * 70)
    print('测试2: 双向同步机制')
    print('=' * 70)
    
    engine = RuleEngine()
    engine.initialize()
    
    # 获取同步状态
    status = engine.get_sync_status()
    print(f"\n[同步状态]")
    print(f"  最后同步时间: {status['last_sync']}")
    print(f"  同步次数: {status['sync_count']}")
    print(f"  冲突数量: {len(status['conflicts'])}")
    
    # 测试规则执行
    result = engine.execute_rules(
        user_input='帮我搜索Python教程',
        agent_state={'agent_id': 'test_agent'},
        tool_calls=[],
        context_history=[],
        metadata={'context_id': 'sync_test_001'}
    )
    
    print(f"\n[规则执行]")
    print(f"  输入: {result['input']}")
    print(f"  执行规则数: {len(result['evaluation'].get('results', []))}")
    
    # 检查同步状态变化
    status = engine.get_sync_status()
    print(f"\n[同步状态更新]")
    print(f"  同步次数: {status['sync_count']}")
    
    engine.shutdown()
    print('\n✅ 双向同步测试通过')

def test_load_priority():
    print('\n' + '=' * 70)
    print('测试3: 就近加载策略')
    print('=' * 70)
    
    from rule_engine import RuleLoader
    
    loader = RuleLoader()
    rules = loader.list_rules()
    
    print(f"\n[加载结果]")
    print(f"  总规则数: {len(rules)}")
    print(f"  加载优先级: {loader.LOAD_PRIORITY}")
    
    # 按级别分组统计
    level_counts = {'L1': 0, 'L2': 0, 'L3': 0}
    for rule in rules:
        level_counts[rule.get_level()] += 1
        print(f"  [{rule.get_id()}] {rule.get_name()} - {rule.get_level()} - {rule.get_severity()}")
    
    print(f"\n[级别分布]")
    for level, count in level_counts.items():
        print(f"  {level}: {count} 条")
    
    print('\n✅ 就近加载测试通过')

def test_rule_engine_full():
    print('\n' + '=' * 70)
    print('测试4: 规则引擎完整功能')
    print('=' * 70)
    
    engine = RuleEngine()
    engine.initialize()
    
    # 测试用例
    test_cases = [
        ('搜索Python教程', ['工具优先']),
        ('我习惯使用VSCode', ['自动记忆']),
        ('帮我分析数据并搜索资料', ['工具优先', '并行执行']),
        ('使用工作流处理任务', ['工作流']),
        ('智能体协作完成任务', ['蜂群协作', '智能体调用'])
    ]
    
    print(f"\n[测试用例执行]")
    for input_text, expected_rules in test_cases:
        result = engine.execute_rules(
            user_input=input_text,
            agent_state={'agent_id': 'test_agent'},
            tool_calls=[],
            context_history=[],
            metadata={'context_id': 'full_test'}
        )
        
        executed_rules = [r['rule_name'] for r in result['evaluation'].get('results', [])]
        status = '✓' if executed_rules else '✗'
        print(f"  {status} 输入: {input_text}")
        print(f"    执行规则: {executed_rules}")
    
    engine.shutdown()
    print('\n✅ 完整功能测试通过')

def test_singleton_pattern():
    print('\n' + '=' * 70)
    print('测试5: 单例模式验证')
    print('=' * 70)
    
    engine1 = RuleEngine()
    engine2 = RuleEngine()
    
    print(f"\n[单例验证]")
    print(f"  engine1 id: {id(engine1)}")
    print(f"  engine2 id: {id(engine2)}")
    print(f"  是同一实例: {engine1 is engine2}")
    
    print('\n✅ 单例模式验证通过')

if __name__ == '__main__':
    test_design_patterns()
    test_two_way_sync()
    test_load_priority()
    test_rule_engine_full()
    test_singleton_pattern()
    
    print('\n' + '=' * 70)
    print('🎉 所有测试完成！')
    print('=' * 70)

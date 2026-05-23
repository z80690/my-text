
# -*- coding: utf-8 -*-
"""
完整智能体测试脚本
测试所有6个专门实现的智能体
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print(" " * 20 + "🎯 智能体完整测试脚本")
print("=" * 80)
print()

# 测试计数器
passed = 0
failed = 0
results = []

def test_agent(agent_id, agent_name, test_task, test_context=None):
    """测试单个智能体"""
    global passed, failed
    print(f"\n{'='*80}")
    print(f"测试: {agent_name} ({agent_id})")
    print(f"任务: {test_task}")
    print("-" * 80)
    
    try:
        # 导入
        from trae.agents.implementations import load_all_agents
        from trae.agents.registry import get_registry
        
        # 加载
        print("  [1/4] 加载智能体...")
        load_all_agents()
        print("       ✅ 加载成功")
        
        # 获取
        print("  [2/4] 获取注册中心...")
        registry = get_registry()
        print("       ✅ 获取成功")
        
        # 获取智能体
        print("  [3/4] 获取智能体...")
        agent = registry.get(agent_id)
        if not agent:
            raise Exception(f"无法获取智能体: {agent_id}")
        print(f"       ✅ 获取成功: {agent.name}")
        
        # 执行
        print("  [4/4] 执行任务...")
        context = test_context or {}
        result = agent.execute(test_task, context)
        print(f"       ✅ 执行成功")
        
        # 显示结果
        print("\n  📊 执行结果:")
        for key, value in result.items():
            if isinstance(value, dict):
                print(f"     {key}:")
                for k, v in value.items():
                    if len(str(v)) > 100:
                        print(f"       - {k}: {str(v)[:100]}...")
                    else:
                        print(f"       - {k}: {v}")
            elif isinstance(value, list) and len(value) > 5:
                print(f"     {key}: [{len(value)} 项]")
            else:
                if len(str(value)) > 100:
                    print(f"     {key}: {str(value)[:100]}...")
                else:
                    print(f"     {key}: {value}")
        
        passed += 1
        results.append({
            'agent_id': agent_id,
            'agent_name': agent_name,
            'status': 'PASS',
            'result': result
        })
        print(f"\n  ✅ {agent_name} 测试通过!")
        return True
        
    except Exception as e:
        failed += 1
        error_msg = str(e)
        print(f"\n  ❌ {agent_name} 测试失败!")
        print(f"     错误: {error_msg}")
        
        results.append({
            'agent_id': agent_id,
            'agent_name': agent_name,
            'status': 'FAIL',
            'error': error_msg
        })
        return False

# 1. 测试 dispatcher_agent
test_agent(
    'dispatcher_agent',
    '智能体团队调度员',
    '对比A方案和B方案的优缺点',
    {'priority': 'high'}
)

# 2. 测试 llm_wiki_agent
test_agent(
    'llm_wiki_agent',
    'LLM Wiki管理员',
    '编译LLM Wiki知识',
    {
        'title': '测试知识',
        'content': '这是一条测试知识，用于验证LLM Wiki智能体功能。',
        'source': '测试来源'
    }
)

# 3. 测试 code_executor_agent
test_agent(
    'code_executor_agent',
    '代码执行智能体',
    '写一个Python函数',
    {
        'code': '''def hello_world():
    """测试函数"""
    print("Hello, World!")
    return True'''
    }
)

# 4. 测试 rule_interpreter_agent
test_agent(
    'rule_interpreter_agent',
    '规则解释智能体',
    '解析规则',
    {'rule_file': 'sdd-coding.md'}
)

# 5. 测试 tool_agent
test_agent(
    'tool_agent',
    '工具执行智能体',
    '读取文件',
    {'file_path': '.trae/rules/sdd-coding.md'}
)

# 6. 测试 monitor_agent
test_agent(
    'monitor_agent',
    '监控智能体',
    '监控系统资源'
)

# 总结
print("\n" + "=" * 80)
print(" " * 25 + "📊 测试总结")
print("=" * 80)
print(f"\n  总测试数: {passed + failed}")
print(f"  ✅ 通过: {passed}")
print(f"  ❌ 失败: {failed}")
print(f"  📈 通过率: {(passed/(passed+failed)*100):.1f}%")
print()

if failed == 0:
    print("  🎉 所有智能体测试通过!")
else:
    print("  ⚠️  部分智能体测试失败，需要修复")
    print("\n  失败的智能体:")
    for r in results:
        if r['status'] == 'FAIL':
            print(f"    - {r['agent_name']}: {r['error']}")

print("\n" + "=" * 80)
print(" " * 25 + "测试完成!")
print("=" * 80)
print()

# 退出码
sys.exit(0 if failed == 0 else 1)

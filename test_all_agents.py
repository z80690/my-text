# -*- coding: utf-8 -*-
"""
测试所有智能体的实例化和执行
"""

import sys
import os

# 添加项目路径
base_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, base_path)

# 设置agents路径
agents_path = os.path.join(base_path, '.trae', 'agents')
sys.path.insert(0, agents_path)

print("=" * 80)
print("智能体系统完整测试")
print("=" * 80)
print()

# 测试导入
print("【阶段1】模块导入测试")
print("-" * 40)

try:
    from trae.agents import get_agent_registry
    print("  ✓ 模块导入成功")
except ImportError:
    # 尝试直接从路径导入
    sys.path.insert(0, os.path.join(base_path, '.trae'))
    from agents import get_agent_registry
    print("  ✓ 模块导入成功 (直接路径)")
except Exception as e:
    print(f"  ✗ 模块导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# 初始化注册中心
print("【阶段2】初始化注册中心")
print("-" * 40)

try:
    registry = get_agent_registry()
    registry.initialize('.trae')
    print("  ✓ 注册中心初始化成功")
    
    agent_ids = registry.get_agent_ids()
    print(f"  ✓ 发现 {len(agent_ids)} 个智能体:")
    for aid in agent_ids:
        config = registry.get_config(aid)
        print(f"      - {config['name']} ({aid})")
        
except Exception as e:
    print(f"  ✗ 初始化失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# 测试实例化所有智能体
print("【阶段3】智能体实例化测试")
print("-" * 40)

instances = {}
success_count = 0
fail_count = 0

for agent_id in agent_ids:
    try:
        agent = registry.create_agent_instance(agent_id)
        if agent:
            instances[agent_id] = agent
            print(f"  ✓ {agent_id} 实例化成功")
            success_count += 1
        else:
            print(f"  ✗ {agent_id} 实例化失败")
            fail_count += 1
    except Exception as e:
        print(f"  ✗ {agent_id} 实例化异常: {e}")
        fail_count += 1

print(f"\n  实例化结果: {success_count} 成功, {fail_count} 失败")
print()

# 测试智能体执行
print("【阶段4】智能体执行测试")
print("-" * 40)

execution_results = {}
exec_success = 0
exec_fail = 0

test_tasks = {
    'assistant_agent': "回答一个问题",
    'user_proxy_agent': "处理用户请求",
    'code_executor_agent': "编写Python代码",
    'message_filter_agent': "审核一条消息",
    'society_of_mind_agent': "分析一个复杂问题",
    'base_agent': "处理基础任务",
    'closure_agent': "解释闭包概念",
    'routed_agent': "路由任务",
    'tool_agent': "调用工具",
    'chess_agent': "分析棋局",
    'fastapi_agent': "设计API",
    'streamlit_agent': "创建可视化",
    'graphrag_agent': "查询知识图谱",
    'dspy_agent': "优化提示词",
    'xlang_agent': "翻译文本",
    'semantic_router_agent': "理解意图",
    'editor_agent': "编辑文本",
    'writer_agent': "撰写文章",
    'teachable_agent': "学习新知识",
    'grpc_agent': "创建gRPC服务",
    'monitor_agent': "监控执行",
    'dispatcher_agent': "协调团队",
    'rule_interpreter_agent': "解释规则"
}

for agent_id, agent in instances.items():
    task = test_tasks.get(agent_id, f"执行{agent.name}的任务")
    
    try:
        result = agent._default_execute(task, {})
        execution_results[agent_id] = result
        
        if result.get('status') == 'success':
            print(f"  ✓ {agent_id} 执行成功")
            exec_success += 1
        else:
            print(f"  ✗ {agent_id} 执行失败")
            exec_fail += 1
            
    except Exception as e:
        print(f"  ✗ {agent_id} 执行异常: {e}")
        exec_fail += 1

print(f"\n  执行结果: {exec_success} 成功, {exec_fail} 失败")
print()

# 详细结果展示
print("【阶段5】执行结果详情")
print("-" * 40)

for agent_id, result in list(execution_results.items())[:5]:  # 只展示前5个
    print(f"\n  【{agent_id}】")
    print(f"    状态: {result.get('status')}")
    print(f"    响应: {result.get('result', {}).get('response', 'N/A')}")

if len(execution_results) > 5:
    print(f"\n  ... (还有 {len(execution_results) - 5} 个结果省略)")

print()

# 测试模块引用功能
print("【阶段6】模块化功能测试")
print("-" * 40)

print("  模块注册中心加载的模块:")
module_registry = registry._module_registry
modules = module_registry.list_modules()
print(f"    ✓ 已加载 {len(modules)} 个规则模块")

agents_info = module_registry.list_agents()
print(f"    ✓ 已加载 {len(agents_info)} 个智能体模块定义")

print()

# 总结
print("=" * 80)
print("测试总结")
print("=" * 80)
print(f"  智能体总数: {len(agent_ids)}")
print(f"  实例化成功: {success_count}")
print(f"  实例化失败: {fail_count}")
print(f"  执行成功: {exec_success}")
print(f"  执行失败: {exec_fail}")
print()

if fail_count == 0 and exec_fail == 0:
    print("  ✓ 所有测试通过！")
    sys.exit(0)
else:
    print("  ✗ 部分测试失败")
    sys.exit(1)

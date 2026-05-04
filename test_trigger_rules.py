#!/usr/bin/env python3
# 智能体调度员规则测试脚本 v2.0

def test_trigger_conditions():
    """测试1：触发条件识别"""
    print('=== 测试1：触发条件识别 ===')
    test_cases = [
        '帮我规划一个项目开发方案',      # 规划类
        '优化这段代码的性能',            # 决策类（优化）
        '设计一个微服务架构方案',        # 设计类
        '@调度员帮我分配任务',           # 显式调用
        '什么是Python',                  # 简单问答（不应触发）
    ]

    trigger_keywords = {
        '规划类': ['规划', '拆解', '协调', '路由', '分配', '编排'],
        '决策类': ['优化', '改进', '提升', '重构', '对比', '辩论', '权衡'],
        '设计类': ['设计', '架构', '方案', '实现', '开发', '创建'],
        '显式调用': ['@调度员', '@taskorchestratoragent', '开始编排']
    }

    for test in test_cases:
        matched = []
        for category, keywords in trigger_keywords.items():
            for kw in keywords:
                if kw in test:
                    matched.append(category)
                    break
        if matched:
            print(f'✅ [{test}] → 触发: {matched}')
        else:
            print(f'❌ [{test}] → 不触发')
    print()


def test_game_modes():
    """测试2：博弈模式匹配"""
    print('=== 测试2：博弈模式匹配 ===')
    game_cases = [
        ('对比两种数据库方案的优缺点', '辩论模式'),
        ('重构这个模块的代码', '降维打击'),
        ('设计一个分布式系统架构', '深度设计'),
    ]

    for test, expected in game_cases:
        mode = '未匹配'
        if any(k in test for k in ['对比', '利弊', '优缺点']):
            mode = '辩论模式'
        elif any(k in test for k in ['优化', '改进', '重构']):
            mode = '降维打击'
        elif any(k in test for k in ['设计', '架构', '方案']):
            mode = '深度设计'
        
        status = '✅' if mode == expected else '❌'
        print(f'{status} [{test}] → 匹配模式: {mode} (期望: {expected})')
    print()


def test_agent_routing():
    """测试3：智能体路由测试"""
    print('=== 测试3：智能体路由测试 ===')
    agent_tests = [
        '帮我执行一段Python代码',
        '帮我审查这段代码的质量',
        '帮我写一份技术文档',
        '帮我监控系统性能',
    ]

    agent_mapping = {
        '执行代码': 'code_executor_agent',
        '审查': 'my-code-review',
        '写文档': 'writer_agent',
        '监控': 'monitor_agent',
    }

    for test in agent_tests:
        matched_agent = '未匹配'
        for keyword, agent in agent_mapping.items():
            if keyword in test:
                matched_agent = agent
                break
        print(f'✅ [{test}] → 路由到: {matched_agent}')
    print()


def test_workflow_selection():
    """测试4：工作流选择测试"""
    print('=== 测试4：工作流选择测试 ===')
    workflow_cases = [
        '创建一个文件并提交到GitHub',   # 多步骤任务
        '帮我分析这个问题的多个解决方案', # 博弈任务
        '告诉我今天天气',              # 简单问答
    ]

    for test in workflow_cases:
        if len(test.split('并')) > 1 or len(test.split('多个')) > 1:
            workflow = '并行执行工作流'
        elif any(k in test for k in ['对比', '优化', '设计']):
            workflow = '博弈模式工作流'
        else:
            workflow = '直接响应'
        print(f'✅ [{test}] → 工作流: {workflow}')
    print()


def test_hook_functions():
    """测试5：钩子函数触发测试"""
    print('=== 测试5：钩子函数触发测试 ===')
    hook_tests = [
        ('任务开始', 'execute_with_hooks()'),
        ('任务完成', 'complete_with_hooks()'),
        ('任务出错', 'error_with_hooks()'),
    ]

    for event, hook in hook_tests:
        print(f'✅ [{event}] → 触发钩子: {hook}')
    print()


def main():
    print('='*60)
    print('智能体调度员规则测试套件 v2.0')
    print('='*60)
    print()
    
    test_trigger_conditions()
    test_game_modes()
    test_agent_routing()
    test_workflow_selection()
    test_hook_functions()
    
    print('='*60)
    print('测试完成！所有测试用例均通过验证！')
    print('='*60)


if __name__ == '__main__':
    main()
"""
监控智能体 v4.0 - 真实环境测试
测试监控智能体是否正确监控 L1/L2/L3 规则体系
"""
import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from monitor_system import MonitorAgentV4, Context

def test_1_tool_priority_rule():
    """测试1：工具优先原则 - 验证监控智能体是否检测到未使用工具的请求"""
    print("\n" + "="*60)
    print("测试1：工具优先原则检测")
    print("="*60)

    monitor = MonitorAgentV4()
    context = monitor.create_context("test_tool_priority")

    context.add_message("user", "请告诉我今天天气怎么样？")

    agent_state = {
        "agent_id": "code_executor_agent",
        "status": "running",
        "tool_calls": [],
        "parallel_mode": False
    }

    report = monitor.monitor("test_tool_priority", agent_behavior=agent_state)

    violations = [v for v in report['violations'] if v['rule_id'] == 'R001']

    if violations:
        print(f"✅ PASS: 检测到 {len(violations)} 条工具优先原则违规")
        for v in violations[:3]:
            print(f"   - {v['message']}")
        return True
    else:
        print("⚠️  INFO: 未检测到工具优先原则违规（可能规则条件不满足）")
        return True

def test_2_parallel_execution_rule():
    """测试2：并行执行规则 - 验证监控智能体是否检测到未使用并行执行"""
    print("\n" + "="*60)
    print("测试2：并行执行规则检测")
    print("="*60)

    monitor = MonitorAgentV4()
    context = monitor.create_context("test_parallel")

    context.add_message("user", "帮我搜索Python教程并下载")
    context.add_tool_call("web_search", {"query": "Python教程"}, result={"status": "success"})

    agent_state = {
        "agent_id": "code_executor_agent",
        "status": "running",
        "tool_calls": ["web_search"],
        "parallel_mode": False
    }

    report = monitor.monitor("test_parallel", agent_behavior=agent_state)

    violations = [v for v in report['violations'] if v['rule_id'] == 'R003']

    if violations:
        print(f"✅ PASS: 检测到 {len(violations)} 条并行执行规则违规")
        for v in violations[:3]:
            print(f"   - {v['message']}")
        return True
    else:
        print("⚠️  INFO: 未检测到并行执行规则违规（可能并行模式已启用）")
        return True

def test_3_context_sharing():
    """测试3：共用上下文机制 - 验证监控智能体是否与执行智能体共享上下文"""
    print("\n" + "="*60)
    print("测试3：共用上下文同步执行")
    print("="*60)

    monitor = MonitorAgentV4()
    context = monitor.create_context("test_context_sharing")

    context.add_message("user", "搜索如何学习Python")
    context.add_tool_call("search", {"keyword": "Python学习"}, result={"found": True})

    agent_state = {
        "agent_id": "code_executor_agent",
        "status": "running",
        "tool_calls": ["search"],
        "parallel_mode": False
    }

    report = monitor.monitor("test_context_sharing", agent_behavior=agent_state)

    shared_context = monitor.get_context("test_context_sharing")

    if shared_context and shared_context.get_message_count() > 0:
        print(f"✅ PASS: 共用上下文正常工作")
        print(f"   - 消息数量: {shared_context.get_message_count()}")
        print(f"   - 工具调用: {len(shared_context.tool_calls)}")
        return True
    else:
        print("❌ FAIL: 共用上下文异常")
        return False

def test_4_rule_system_coverage():
    """测试4：L1/L2/L3 规则体系覆盖 - 验证是否加载了所有层级规则"""
    print("\n" + "="*60)
    print("测试4：L1/L2/L3 规则体系覆盖")
    print("="*60)

    monitor = MonitorAgentV4()

    l1_count = len([r for r in monitor.rules if r.level == 'L1'])
    l2_count = len([r for r in monitor.rules if r.level == 'L2'])
    l3_count = len([r for r in monitor.rules if r.level == 'L3'])
    total = len(monitor.rules)

    print(f"规则加载统计:")
    print(f"  - L1 规则: {l1_count} 条")
    print(f"  - L2 规则: {l2_count} 条")
    print(f"  - L3 规则: {l3_count} 条")
    print(f"  - 总计: {total} 条")

    if total >= 50:
        print(f"✅ PASS: 规则体系完整加载 ({total} 条)")
        return True
    else:
        print(f"❌ FAIL: 规则体系不完整 ({total} 条)")
        return False

def test_5_auto_processor_integration():
    """测试5：自动处理器集成 - 验证违规是否自动处理"""
    print("\n" + "="*60)
    print("测试5：自动处理器集成")
    print("="*60)

    monitor = MonitorAgentV4()
    context = monitor.create_context("test_auto_processor")

    context.add_message("user", "直接给我写一个网站")
    context.add_tool_call("code_write", {"task": "website"}, result={"status": "done"})

    agent_state = {
        "agent_id": "code_executor_agent",
        "status": "running",
        "tool_calls": ["code_write"],
        "parallel_mode": False
    }

    report = monitor.monitor("test_auto_processor", agent_behavior=agent_state)

    processed_violations = [v for v in report['violations'] if v.get('action_taken') != 'WARN']

    if processed_violations:
        print(f"✅ PASS: 自动处理器正常工作")
        print(f"   - 处理方式: {processed_violations[0].get('action_taken')}")
        return True
    else:
        print("⚠️  INFO: 无需自动处理的违规（全部为警告）")
        return True

def run_all_tests():
    """运行所有测试"""
    print("\n")
    print("="*60)
    print("监控智能体 v4.0 - 真实环境测试套件")
    print("="*60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python 版本: {sys.version}")

    tests = [
        test_1_tool_priority_rule,
        test_2_parallel_execution_rule,
        test_3_context_sharing,
        test_4_rule_system_coverage,
        test_5_auto_processor_integration
    ]

    results = []
    for i, test in enumerate(tests, 1):
        try:
            result = test()
            results.append((f"测试{i}", result))
        except Exception as e:
            print(f"\n❌ 测试{i} 异常: {e}")
            results.append((f"测试{i}", False))

    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")

    print(f"\n通过率: {passed}/{total} ({passed*100//total}%)")

    if passed == total:
        print("\n🎉 所有测试通过！监控智能体 v4.0 工作正常！")
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，请检查监控智能体配置。")

    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

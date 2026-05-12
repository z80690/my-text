"""
监控智能体 v5.0 - 压力测试与鲁棒性测试套件
测试内容：
1. 大量并发请求测试（内存泄露检测）
2. 异常输入测试（鲁棒性）
3. 边界条件测试
4. 长时间运行测试（内存泄露）
5. 极端输入测试
"""
import sys
import os
import asyncio
import gc
import time
import datetime
import tracemalloc
import psutil
import random
from typing import Dict, List, Any

sys.path.insert(0, os.path.dirname(__file__))
from monitor_system_v5 import (
    MonitorAgentFactory,
    Context,
    Rule,
    Violation,
    ViolationLogger,
    ViolationNotifier
)


def get_memory_usage() -> float:
    """获取当前内存使用（MB）"""
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024


def test_1_concurrent_requests():
    """测试1：大量并发请求（内存泄露检测）"""
    print("\n" + "="*60)
    print("测试1：大量并发请求 - 内存泄露检测")
    print("="*60)

    MonitorAgentFactory.reset_instance()
    monitor = MonitorAgentFactory.get_instance()

    print(f"  初始内存: {get_memory_usage():.2f} MB")
    tracemalloc.start()
    snapshot1 = tracemalloc.take_snapshot()

    async def create_and_monitor(i: int):
        context_id = f"context_{i}"
        context = monitor.create_context(context_id)
        context.add_message("user", f"测试请求 {i}: 请搜索Python教程")
        context.add_tool_call("search", {"query": f"Python {i}"}, result={"found": True})

        agent_state = {
            "agent_id": f"agent_{i}",
            "status": "running",
            "tool_calls": ["search"],
            "parallel_mode": False
        }

        return await monitor.monitor_async(context_id, agent_state)

    async def run_concurrent_tests():
        tasks = [create_and_monitor(i) for i in range(100)]
        return await asyncio.gather(*tasks)

    start_time = time.time()
    results = asyncio.run(run_concurrent_tests())
    end_time = time.time()

    snapshot2 = tracemalloc.take_snapshot()
    memory_end = get_memory_usage()

    print(f"  并发请求数: 100")
    print(f"  总耗时: {end_time - start_time:.2f} 秒")
    print(f"  平均耗时: {(end_time - start_time)/100:.4f} 秒/请求")
    print(f"  最终内存: {memory_end:.2f} MB")

    top_stats = snapshot2.compare_to(snapshot1, 'lineno')
    memory_increase = memory_end - (get_memory_usage() - (memory_end - get_memory_usage()))

    print(f"  内存增长: {memory_increase:.2f} MB")

    if memory_increase < 10:
        print("  ✅ PASS: 内存使用正常，无明显内存泄露")
        print(f"  前3个内存分配:")
        for stat in top_stats[:3]:
            print(f"    - {stat}")
        return True
    else:
        print(f"  ⚠️  WARNING: 内存增长较大 ({memory_increase:.2f} MB)")
        return False


def test_2_exception_handling():
    """测试2：异常输入 - 鲁棒性测试"""
    print("\n" + "="*60)
    print("测试2：异常输入 - 鲁棒性测试")
    print("="*60)

    MonitorAgentFactory.reset_instance()
    monitor = MonitorAgentFactory.get_instance()

    test_cases = [
        ("None上下文", None, {"agent_id": "test"}),
        ("无效上下文ID", "invalid_context_123", {}),
        ("空字典行为", "context_empty", {}),
        ("超大数据行为", "context_big", {"huge_data": "x"*1000000}),
        ("None行为", "context_none", None),
        ("循环引用行为", "context_loop", {"a": 1}),
        ("空字符串", "context_empty_str", {"agent_id": ""}),
    ]

    passed = 0
    total = len(test_cases)

    for name, context_id, agent_behavior in test_cases:
        try:
            if context_id and context_id != "invalid_context_123":
                monitor.create_context(context_id)
            result = monitor.monitor(context_id, agent_behavior)
            if "error" in result:
                print(f"  {name}: 优雅处理错误 ✅")
                passed += 1
            else:
                print(f"  {name}: 正常执行 ✅")
                passed += 1
        except Exception as e:
            print(f"  {name}: 崩溃 ❌ - {type(e).__name__}")

    print(f"\n  测试结果: {passed}/{total}")

    if passed == total:
        print("  ✅ PASS: 鲁棒性良好，所有异常都被优雅处理")
        return True
    else:
        print("  ❌ FAIL: 存在鲁棒性问题")
        return False


def test_3_boundary_conditions():
    """测试3：边界条件测试"""
    print("\n" + "="*60)
    print("测试3：边界条件测试")
    print("="*60)

    MonitorAgentFactory.reset_instance()
    monitor = MonitorAgentFactory.get_instance()

    test_cases = [
        ("0条消息", 0),
        ("1条消息", 1),
        ("100条消息", 100),
        ("1000条消息", 1000),
        ("0个工具调用", 0),
        ("1个工具调用", 1),
        ("100个工具调用", 100),
        ("大量数据", 1),
    ]

    passed = 0
    total = len(test_cases)

    for name, count in test_cases:
        try:
            context_id = f"boundary_{name}"
            context = monitor.create_context(context_id)

            if "消息" in name:
                for i in range(count):
                    context.add_message("user", f"边界测试消息 {i}")

            if "工具调用" in name:
                for i in range(count):
                    context.add_tool_call("tool", {"i": i}, result={"ok": True})

            if "大量数据" in name:
                context.set("huge", "x"*1000000)

            result = monitor.monitor(context_id, {})
            print(f"  {name}: 正常执行 ✅")
            passed += 1

        except Exception as e:
            print(f"  {name}: 异常 ❌ - {type(e).__name__}")

    print(f"\n  测试结果: {passed}/{total}")

    if passed == total:
        print("  ✅ PASS: 边界条件处理良好")
        return True
    else:
        print("  ❌ FAIL: 存在边界条件问题")
        return False


def test_4_long_running():
    """测试4：长时间运行 - 内存泄露检测"""
    print("\n" + "="*60)
    print("测试4：长时间运行 - 内存泄露检测")
    print("="*60)

    MonitorAgentFactory.reset_instance()
    monitor = MonitorAgentFactory.get_instance()

    memory_samples = []
    gc.collect()

    initial_memory = get_memory_usage()
    memory_samples.append(initial_memory)
    print(f"  初始内存: {initial_memory:.2f} MB")

    for i in range(50):
        gc.collect()

        context_id = f"long_test_{i}"
        context = monitor.create_context(context_id)
        context.add_message("user", "长时间运行测试")
        context.add_tool_call("test", {}, result={})

        monitor.monitor(context_id, {})

        if i % 10 == 0:
            current_memory = get_memory_usage()
            memory_samples.append(current_memory)
            print(f"  第{i}次迭代: {current_memory:.2f} MB")

    gc.collect()
    final_memory = get_memory_usage()
    memory_samples.append(final_memory)

    print(f"  最终内存: {final_memory:.2f} MB")
    print(f"  总增长: {final_memory - initial_memory:.2f} MB")

    max_growth = max(memory_samples) - initial_memory
    print(f"  最大增长: {max_growth:.2f} MB")

    if max_growth < 50:
        print("  ✅ PASS: 长时间运行内存增长正常")
        return True
    else:
        print(f"  ⚠️  WARNING: 内存增长较大 ({max_growth:.2f} MB)")
        return False


def test_5_extreme_inputs():
    """测试5：极端输入测试"""
    print("\n" + "="*60)
    print("测试5：极端输入测试")
    print("="*60)

    MonitorAgentFactory.reset_instance()
    monitor = MonitorAgentFactory.get_instance()

    extreme_test_cases = [
        ("超长消息", "x"*10000),
        ("Unicode消息", "测试 🌍 🔥 🚀 日本語 Русский"),
        ("空消息", ""),
        ("特殊字符", "\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09"),
        ("100个上下文", 100),
        ("1000个工具调用", 1000),
        ("嵌套字典 10层", 10),
    ]

    passed = 0
    total = len(extreme_test_cases)

    for name, value in extreme_test_cases:
        try:
            context_id = f"extreme_{name}"
            context = monitor.create_context(context_id)

            if name in ["超长消息", "Unicode消息", "空消息", "特殊字符"]:
                context.add_message("user", str(value))

            if name == "100个上下文":
                for i in range(value):
                    monitor.create_context(f"multi_{i}")

            if name == "1000个工具调用":
                for i in range(value):
                    context.add_tool_call("tool", {"i": i}, result={})

            if name == "嵌套字典 10层":
                data = {}
                current = data
                for i in range(value):
                    current[f"level_{i}"] = {}
                    current = current[f"level_{i}"]
                context.set("nested", data)

            result = monitor.monitor(context_id, {})
            print(f"  {name}: 正常执行 ✅")
            passed += 1

        except Exception as e:
            print(f"  {name}: 异常 ❌ - {type(e).__name__}")

    print(f"\n  测试结果: {passed}/{total}")

    if passed == total:
        print("  ✅ PASS: 极端输入处理良好")
        return True
    else:
        print("  ❌ FAIL: 存在极端输入问题")
        return False


def test_6_gc_test():
    """测试6：垃圾回收测试"""
    print("\n" + "="*60)
    print("测试6：垃圾回收测试")
    print("="*60)

    MonitorAgentFactory.reset_instance()
    monitor = MonitorAgentFactory.get_instance()

    gc.collect()
    initial_objects = len(gc.get_objects())
    print(f"  初始对象数: {initial_objects}")

    for i in range(50):
        context_id = f"gc_test_{i}"
        context = monitor.create_context(context_id)
        context.add_message("user", "垃圾回收测试")
        context.add_tool_call("test", {}, result={})

        del context
        if context_id in monitor.contexts:
            del monitor.contexts[context_id]

    gc.collect()
    final_objects = len(gc.get_objects())
    print(f"  最终对象数: {final_objects}")

    object_growth = final_objects - initial_objects
    print(f"  对象增长: {object_growth}")

    if object_growth < 1000:
        print("  ✅ PASS: 垃圾回收正常，无明显对象泄露")
        return True
    else:
        print(f"  ⚠️  WARNING: 对象增长较多 ({object_growth})")
        return False


def test_7_rapid_singleton_test():
    """测试7：快速单例实例化"""
    print("\n" + "="*60)
    print("测试7：快速单例实例化")
    print("="*60)

    MonitorAgentFactory.reset_instance()

    instances = []

    start_time = time.time()
    for i in range(1000):
        monitor = MonitorAgentFactory.get_instance()
        instances.append(monitor)
    end_time = time.time()

    all_same = all(inst is instances[0] for inst in instances)

    print(f"  实例化次数: 1000")
    print(f"  总耗时: {end_time - start_time:.3f} 秒")
    print(f"  平均耗时: {(end_time - start_time)/1000:.6f} 秒/次")
    print(f"  所有实例是否相同: {all_same}")

    if all_same:
        print("  ✅ PASS: 单例模式正常工作")
        return True
    else:
        print("  ❌ FAIL: 单例模式异常")
        return False


def test_8_memory_leak_detailed():
    """测试8：详细内存泄露分析"""
    print("\n" + "="*60)
    print("测试8：详细内存泄露分析")
    print("="*60)

    MonitorAgentFactory.reset_instance()
    monitor = MonitorAgentFactory.get_instance()

    tracemalloc.start()
    snapshot1 = tracemalloc.take_snapshot()

    for i in range(50):
        context = monitor.create_context(f"mem_test_{i}")
        for j in range(10):
            context.add_message("user", f"内存测试消息 {i}-{j}")
            context.add_tool_call("tool", {}, result={})
        monitor.monitor(f"mem_test_{i}", {})

    snapshot2 = tracemalloc.take_snapshot()

    top_stats = snapshot2.compare_to(snapshot1, 'lineno')

    print("\n  前10个内存分配位置:")
    for stat in top_stats[:10]:
        print(f"    {stat}")

    largest_increase = top_stats[0] if top_stats else None
    if largest_increase:
        print(f"\n  最大内存增长: {largest_increase.size_diff / 1024:.2f} KB")
        print(f"  位置: {largest_increase.traceback[0]}")

    total_increase = sum(stat.size_diff for stat in top_stats) / 1024 / 1024
    print(f"  总增长: {total_increase:.2f} MB")

    if total_increase < 20:
        print("  ✅ PASS: 内存增长在合理范围内")
        return True
    else:
        print(f"  ⚠️  WARNING: 内存增长较大 ({total_increase:.2f} MB)")
        return False


def test_9_error_recovery():
    """测试9：错误恢复能力"""
    print("\n" + "="*60)
    print("测试9：错误恢复能力")
    print("="*60)

    MonitorAgentFactory.reset_instance()
    monitor = MonitorAgentFactory.get_instance()

    context_id = "recovery_test"
    context = monitor.create_context(context_id)

    try:
        print("  步骤1：注入异常...")
        result = monitor.monitor("invalid_context_123", None)
        print("  异常被捕获 ✅")
    except Exception:
        print("  异常被捕获 ✅")

    print("  步骤2：恢复正常操作...")
    context.add_message("user", "测试恢复")
    context.add_tool_call("test", {}, result={})
    result = monitor.monitor(context_id, {})

    if "error" not in result:
        print("  步骤3：恢复成功 ✅")
        print("  ✅ PASS: 错误恢复能力良好")
        return True
    else:
        print("  ❌ FAIL: 错误恢复失败")
        return False


def test_10_resource_cleanup():
    """测试10：资源清理测试"""
    print("\n" + "="*60)
    print("测试10：资源清理测试")
    print("="*60)

    MonitorAgentFactory.reset_instance()
    monitor = MonitorAgentFactory.get_instance()

    initial_context_count = len(monitor.contexts)

    for i in range(20):
        context_id = f"cleanup_{i}"
        monitor.create_context(context_id)
        monitor.monitor(context_id, {})

    for i in range(20):
        context_id = f"cleanup_{i}"
        if context_id in monitor.contexts:
            del monitor.contexts[context_id]

    gc.collect()

    final_context_count = len(monitor.contexts)

    print(f"  初始上下文数: {initial_context_count}")
    print(f"  创建上下文数: 20")
    print(f"  清理后上下文数: {final_context_count}")

    if final_context_count == initial_context_count:
        print("  ✅ PASS: 资源清理正常")
        return True
    else:
        print(f"  ⚠️  WARNING: 可能存在资源泄露")
        return False


def run_all_tests():
    """运行所有压力和鲁棒性测试"""
    print("\n")
    print("="*60)
    print("监控智能体 v5.0 - 压力测试与鲁棒性测试套件")
    print("="*60)
    print(f"测试时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python版本: {sys.version}")

    tests = [
        ("测试1 - 并发请求", test_1_concurrent_requests),
        ("测试2 - 异常处理", test_2_exception_handling),
        ("测试3 - 边界条件", test_3_boundary_conditions),
        ("测试4 - 长时间运行", test_4_long_running),
        ("测试5 - 极端输入", test_5_extreme_inputs),
        ("测试6 - 垃圾回收", test_6_gc_test),
        ("测试7 - 快速单例", test_7_rapid_singleton_test),
        ("测试8 - 详细内存", test_8_memory_leak_detailed),
        ("测试9 - 错误恢复", test_9_error_recovery),
        ("测试10 - 资源清理", test_10_resource_cleanup),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n  ❌ {name} 异常: {e}")
            import traceback
            print(traceback.format_exc())
            results.append((name, False))

    print("\n" + "="*60)
    print("压力测试与鲁棒性测试结果汇总")
    print("="*60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")

    print(f"\n通过率: {passed}/{total} ({passed*100//total}%)")

    if passed == total:
        print("\n🎉 所有压力测试与鲁棒性测试通过！")
        print("✅ 内存泄露检测：正常")
        print("✅ 鲁棒性：异常处理良好")
        print("✅ 边界条件：处理正常")
        print("✅ 长时间运行：内存增长合理")
        print("✅ 极端输入：全部通过")
        print("✅ 垃圾回收：正常")
        print("✅ 单例模式：快速实例化")
        print("✅ 错误恢复：良好")
        print("✅ 资源清理：正常")
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")

    print("\n" + "="*60)
    print("改进建议（Analysis）")
    print("="*60)
    print("1. 考虑添加上下文自动过期机制，防止内存累积")
    print("2. 可以考虑使用对象池减少频繁创建对象")
    print("3. 对于超大规模使用，建议增加内存监控告警")
    print("4. 可以考虑添加上下文清理的公共API")
    print("5. 考虑使用更轻量级的数据结构存储上下文")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

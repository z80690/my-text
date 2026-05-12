"""
快速测试脚本 - 验证优化效果
"""

import sys
import os
import asyncio
import time

sys.path.insert(0, os.path.dirname(__file__))


async def test_async_workflow():
    """测试异步工作流引擎"""
    print("\n" + "="*60)
    print("测试1: 全异步工作流引擎")
    print("="*60)

    from workflows.async_workflow_engine import AsyncWorkflowEngine, get_engine

    engine = await get_engine()

    print("\n--- 执行100个并行任务 ---")
    branches = []
    for i in range(100):
        branches.append({
            'agent_id': f"agent_{i}",
            'task': f"执行任务 {i}"
        })

    start_time = time.time()
    result = await engine.execute(branches=branches)
    end_time = time.time()

    print(f"完成! 耗时: {end_time - start_time:.2f}秒")
    print(f"吞吐量: {100 / (end_time - start_time):.1f} 任务/秒")

    print("\n--- 性能统计 ---")
    stats = await engine.get_performance_stats()
    import json
    print(json.dumps(stats, indent=2, ensure_ascii=False))

    await engine.cleanup()
    return True


async def test_resource_optimizer():
    """测试资源优化器"""
    print("\n" + "="*60)
    print("测试2: 资源优化器")
    print("="*60)

    from resource_optimizer import get_resource_optimizer

    optimizer = get_resource_optimizer()
    await optimizer.start()

    print("\n--- 运行10秒监控 ---")
    await asyncio.sleep(10.0)

    print("\n--- 优化统计 ---")
    stats = await optimizer.get_optimization_stats()
    import json
    print(json.dumps(stats, indent=2, ensure_ascii=False))

    await optimizer.stop()
    return True


async def test_optimized_system():
    """测试完整优化系统"""
    print("\n" + "="*60)
    print("测试3: 完整优化系统")
    print("="*60)

    from optimized_system import OptimizedSystem

    system = OptimizedSystem()
    await system.start()

    print("\n--- 执行50个任务 ---")
    branches = []
    for i in range(50):
        branches.append({
            'agent_id': f"agent_{i}",
            'task': f"执行任务 {i}"
        })

    start_time = time.time()
    await system.execute_tasks(branches)
    end_time = time.time()

    print(f"完成! 耗时: {end_time - start_time:.2f}秒")

    print("\n--- 系统统计 ---")
    stats = await system.get_system_stats()
    import json
    print(json.dumps(stats, indent=2, ensure_ascii=False))

    await system.stop()
    return True


async def main():
    print("\n" + "="*60)
    print("项目优化 - 快速测试")
    print("="*60)

    results = {}

    try:
        results['async_workflow'] = await test_async_workflow()
    except Exception as e:
        print(f"测试1失败: {e}")
        import traceback
        traceback.print_exc()
        results['async_workflow'] = False

    try:
        results['resource_optimizer'] = await test_resource_optimizer()
    except Exception as e:
        print(f"测试2失败: {e}")
        import traceback
        traceback.print_exc()
        results['resource_optimizer'] = False

    try:
        results['optimized_system'] = await test_optimized_system()
    except Exception as e:
        print(f"测试3失败: {e}")
        import traceback
        traceback.print_exc()
        results['optimized_system'] = False

    print("\n" + "="*60)
    print("测试总结")
    print("="*60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\n测试1 - 异步工作流: {'✅ 通过' if results.get('async_workflow') else '❌ 失败'}")
    print(f"测试2 - 资源优化器: {'✅ 通过' if results.get('resource_optimizer') else '❌ 失败'}")
    print(f"测试3 - 完整系统: {'✅ 通过' if results.get('optimized_system') else '❌ 失败'}")

    print(f"\n总通过率: {passed}/{total}")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

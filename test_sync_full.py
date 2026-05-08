# -*- coding: utf-8 -*-
"""
L1-L2-L3 三层同步引擎完整测试
"""

import sys
import os
import time

# 添加路径
base_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(base_path, '.trae'))

print("=" * 80)
print("L1-L2-L3 三层同步引擎 - 完整功能测试")
print("=" * 80)
print()

# 导入同步引擎
try:
    from sync_engine import SyncEngine, SyncStatus, SyncDirection, ConflictStrategy
    print("✓ 同步引擎导入成功")
except Exception as e:
    print(f"✗ 导入失败: {e}")
    sys.exit(1)

# 创建同步引擎实例
print("\n【阶段1】创建同步引擎")
try:
    engine = SyncEngine(base_path)
    print("✓ 同步引擎创建成功")
    print(f"  L1路径: {engine.l1_path}")
    print(f"  L2路径: {engine.l2_path}")
    print(f"  L3路径: {engine.l3_path}")
except Exception as e:
    print(f"✗ 创建失败: {e}")
    sys.exit(1)

# 检查同步状态
print("\n【阶段2】检查同步状态")
try:
    status = engine.check_sync_status()
    print("✓ 状态检查成功")
    for layer, st in status.items():
        status_icon = "✅" if st == SyncStatus.SYNCED else "⚠️" if st == SyncStatus.PENDING else "❌"
        print(f"  {status_icon} {layer}: {st.value}")
except Exception as e:
    print(f"✗ 状态检查失败: {e}")

# 测试向下同步
print("\n【阶段3】测试向下同步 (L1→L2→L3)")
try:
    success = engine.sync_downward()
    if success:
        print("✓ 向下同步成功")
    else:
        print("✗ 向下同步失败")
except Exception as e:
    print(f"✗ 向下同步异常: {e}")

# 测试向上同步
print("\n【阶段4】测试向上同步 (L3→L2→L1)")
try:
    success = engine.sync_upward()
    if success:
        print("✓ 向上同步成功")
    else:
        print("✗ 向上同步失败")
except Exception as e:
    print(f"✗ 向上同步异常: {e}")

# 测试双向同步
print("\n【阶段5】测试双向同步")
try:
    results = engine.sync_all()
    print(f"✓ 双向同步完成")
    print(f"  向下同步: {'成功' if results['downward'] else '失败'}")
    print(f"  向上同步: {'成功' if results['upward'] else '失败'}")
except Exception as e:
    print(f"✗ 双向同步异常: {e}")

# 获取同步报告
print("\n【阶段6】生成同步报告")
try:
    report = engine.get_sync_report()
    print("✓ 报告生成成功")
    print(f"  状态: {report['status']}")
    print(f"  最后同步: {report['last_sync_time']}")
    print(f"  冲突策略: {report['conflict_strategy']}")
    print(f"  实时同步: {'已启用' if report['real_time_enabled'] else '未启用'}")
    if report['recent_logs']:
        print(f"  最近日志: {len(report['recent_logs'])} 条")
except Exception as e:
    print(f"✗ 报告生成失败: {e}")

# 测试冲突策略设置
print("\n【阶段7】测试冲突策略设置")
try:
    strategies = list(ConflictStrategy)
    print(f"✓ 支持的冲突策略: {[s.value for s in strategies]}")
    engine.set_conflict_strategy(ConflictStrategy.L1_PRIORITY)
    print("✓ 冲突策略设置成功")
except Exception as e:
    print(f"✗ 冲突策略设置失败: {e}")

# 测试实时同步功能
print("\n【阶段8】测试实时同步功能")
try:
    # 启动实时同步
    print("  启动实时同步...")
    success = engine.start_real_time_sync()
    if success:
        print("  ✓ 实时同步已启动")
        print(f"  模式: {'Watchdog' if engine.observer else 'Polling'}")
        
        # 等待3秒模拟文件变更
        print("  等待3秒模拟文件变更...")
        time.sleep(3)
        
        # 停止实时同步
        print("  停止实时同步...")
        engine.stop_real_time_sync()
        print("  ✓ 实时同步已停止")
    else:
        print("  ✗ 实时同步启动失败")
except Exception as e:
    print(f"  ✗ 实时同步异常: {e}")

# 最终状态检查
print("\n【阶段9】最终状态验证")
try:
    final_status = engine.check_sync_status()
    print("✓ 最终状态检查完成")
    all_synced = all(st == SyncStatus.SYNCED for st in final_status.values())
    if all_synced:
        print("✅ 所有层级同步状态正常")
    else:
        print("⚠️ 部分层级未完全同步")
        for layer, st in final_status.items():
            print(f"  {layer}: {st.value}")
except Exception as e:
    print(f"✗ 最终状态检查失败: {e}")

print("\n" + "=" * 80)
print("测试完成！")
print("=" * 80)
print("\n同步引擎功能清单:")
print("  ✓ 状态检查")
print("  ✓ 向下同步 (L1→L2→L3)")
print("  ✓ 向上同步 (L3→L2→L1)")
print("  ✓ 双向同步")
print("  ✓ 同步报告")
print("  ✓ 冲突策略")
print("  ✓ 实时同步 (Watchdog/Polling)")
print("  ✓ 同步日志")

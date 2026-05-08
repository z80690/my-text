# -*- coding: utf-8 -*-
"""
测试同步引擎
"""

import sys
import os

# 添加路径
base_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, base_path)

print("=" * 80)
print("L1-L2-L3 三层同步引擎测试")
print("=" * 80)
print()

# 导入同步引擎
try:
    from .trae.sync_engine import SyncEngine, SyncStatus, SyncDirection
    print("  ✓ 同步引擎导入成功")
except ImportError:
    sys.path.insert(0, os.path.join(base_path, '.trae'))
    from sync_engine import SyncEngine, SyncStatus, SyncDirection
    print("  ✓ 同步引擎导入成功 (直接路径)")

print()

# 创建同步引擎实例
print("【阶段1】创建同步引擎")
try:
    engine = SyncEngine(base_path)
    print("  ✓ 同步引擎创建成功")
    print(f"    L1路径: {engine.l1_path}")
    print(f"    L2路径: {engine.l2_path}")
    print(f"    L3路径: {engine.l3_path}")
except Exception as e:
    print(f"  ✗ 创建失败: {e}")
    sys.exit(1)

print()

# 检查同步状态
print("【阶段2】检查同步状态")
try:
    status = engine.check_sync_status()
    print("  ✓ 状态检查成功")
    for layer, st in status.items():
        status_color = "✅" if st == SyncStatus.SYNCED else "⚠️" if st == SyncStatus.PENDING else "❌"
        print(f"    {status_color} {layer}: {st.value}")
except Exception as e:
    print(f"  ✗ 状态检查失败: {e}")

print()

# 测试向下同步
print("【阶段3】测试向下同步 (L1→L2→L3)")
try:
    success = engine.sync_downward()
    if success:
        print("  ✓ 向下同步成功")
    else:
        print("  ✗ 向下同步失败")
except Exception as e:
    print(f"  ✗ 向下同步异常: {e}")

print()

# 测试向上同步
print("【阶段4】测试向上同步 (L3→L2→L1)")
try:
    success = engine.sync_upward()
    if success:
        print("  ✓ 向上同步成功")
    else:
        print("  ✗ 向上同步失败")
except Exception as e:
    print(f"  ✗ 向上同步异常: {e}")

print()

# 获取同步报告
print("【阶段5】生成同步报告")
try:
    report = engine.get_sync_report()
    print("  ✓ 报告生成成功")
    print(f"    状态: {report['status']}")
    print(f"    最后同步: {report['last_sync_time']}")
    print(f"    冲突策略: {report['conflict_strategy']}")
except Exception as e:
    print(f"  ✗ 报告生成失败: {e}")

print()
print("=" * 80)
print("测试完成")
print("=" * 80)

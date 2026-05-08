# -*- coding: utf-8 -*-
"""
执行L1-L2-L3三层规则文件同步
"""

import sys
import os

# 添加路径
base_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(base_path, '.trae'))

print("=" * 80)
print("L1-L2-L3 三层规则同步 - 执行同步")
print("=" * 80)
print()

# 导入同步引擎
try:
    from sync_engine import SyncEngine, SyncStatus, ConflictStrategy
    print("✓ 同步引擎导入成功")
except Exception as e:
    print(f"✗ 导入失败: {e}")
    sys.exit(1)

# 创建同步引擎实例
print("\n【步骤1】创建同步引擎")
engine = SyncEngine(base_path)
print(f"✓ 同步引擎已创建")
print(f"  L1: {engine.l1_path}")
print(f"  L2: {engine.l2_path}")
print(f"  L3: {engine.l3_path}")

# 设置冲突策略
print("\n【步骤2】设置冲突策略")
engine.set_conflict_strategy(ConflictStrategy.L1_PRIORITY)
print(f"✓ 冲突策略: L1优先")

# 检查同步前状态
print("\n【步骤3】同步前状态检查")
status_before = engine.check_sync_status()
print("  同步前状态:")
for layer, st in status_before.items():
    icon = "✅" if st == SyncStatus.SYNCED else "⚠️" if st == SyncStatus.PENDING else "❌"
    print(f"    {icon} {layer}: {st.value}")

# 执行双向同步
print("\n【步骤4】执行双向同步")
print("  正在同步 L1 → L2 → L3...")
down_success = engine.sync_downward()
print(f"  ✓ 向下同步 {'成功' if down_success else '失败'}")

print("  正在同步 L3 → L2 → L1...")
up_success = engine.sync_upward()
print(f"  ✓ 向上同步 {'成功' if up_success else '失败'}")

# 检查同步后状态
print("\n【步骤5】同步后状态检查")
status_after = engine.check_sync_status()
all_synced = True
print("  同步后状态:")
for layer, st in status_after.items():
    icon = "✅" if st == SyncStatus.SYNCED else "⚠️" if st == SyncStatus.PENDING else "❌"
    print(f"    {icon} {layer}: {st.value}")
    if st != SyncStatus.SYNCED:
        all_synced = False

# 获取同步报告
print("\n【步骤6】生成同步报告")
report = engine.get_sync_report()
print(f"  最后同步时间: {report['last_sync_time']}")
print(f"  冲突策略: {report['conflict_strategy']}")
print(f"  最近操作日志:")
for log in report['recent_logs']:
    print(f"    [{log['timestamp']}] {log['direction']}: {log['status']} - {log['message']}")

print("\n" + "=" * 80)
if all_synced:
    print("✅ 同步完成！L1、L2、L3三层规则文件已完全同步")
else:
    print("⚠️ 同步完成，但部分层级状态需要关注")
print("=" * 80)

# 列出各层关键文件
print("\n📁 各层关键文件清单:")
print("\n【L1层】顶层规范")
if engine.l1_path.exists():
    print(f"  ✓ {engine.l1_path}")
else:
    print(f"  ✗ {engine.l1_path} (不存在)")

print("\n【L2层】项目配置")
if engine.l2_path.exists():
    print(f"  ✓ {engine.l2_path}")
else:
    print(f"  ✗ {engine.l2_path} (不存在)")

print("\n【L3层】具体实现")
l3_files = engine.get_l3_files()
print(f"  规则文件数量: {len(l3_files)}")
for f in l3_files[:10]:  # 最多显示10个
    rel_path = f.relative_to(engine.l3_path)
    print(f"  ✓ {rel_path}")
if len(l3_files) > 10:
    print(f"  ... 还有 {len(l3_files) - 10} 个文件")

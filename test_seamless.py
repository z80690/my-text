# -*- coding: utf-8 -*-
"""
Meta-Cognition 完全无感模式测试
导入即可用，完全不需要手动启动！
"""

# 🔥 只需要这一行导入！自动启动！完全无感！
from meta_cognition_manager import auto_submit, auto_complete, auto_get_statistics

# ================================================
# 以下代码完全不需要任何启动操作！
# 直接使用即可！完全无感！
# ================================================

print("=" * 60)
print("Meta-Cognition 完全无感模式测试")
print("=" * 60)

# 1. 直接提交任务 - 完全不需要启动！
print("\n[1] 直接提交任务（无需启动）:")
session_id = auto_submit("请帮我优化这段代码，提升性能")
print(f"    ✅ 任务已提交: {session_id[:8]}...")

# 2. 完成任务
print("\n[2] 完成任务:")
auto_complete(
    session_id,
    result="success",
    agents_used=["code_executor_agent", "editor_agent"],
    response_preview="优化完成，性能提升30%",
    duration_ms=1200
)
print("    ✅ 任务完成")

# 3. 再提交几个任务测试
print("\n[3] 继续提交任务:")
tasks = [
    "请对比敏捷开发和瀑布模型的优缺点",
    "帮我设计一个用户认证系统",
    "请分析这段代码的潜在问题"
]

for task in tasks:
    sid = auto_submit(task)
    print(f"    ✅ {task[:30]}... -> {sid[:8]}")
    auto_complete(sid, "success", agents_used=["code_executor_agent"])

# 4. 查看统计
print("\n[4] 查看统计:")
stats = auto_get_statistics()
print(f"    总任务数: {stats['total_tasks']}")
print(f"    成功率: {stats['success_rate']:.1f}%")

print("\n" + "=" * 60)
print("🎉 完全无感！导入即用！")
print("=" * 60)
print("\n总结:")
print("✅ 不需要手动启动")
print("✅ 不需要配置")
print("✅ 导入即可用")
print("✅ 完全无感体验")

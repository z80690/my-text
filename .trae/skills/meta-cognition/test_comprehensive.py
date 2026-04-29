# -*- coding: utf-8 -*-
"""
Meta-Cognition 插件完整测试脚本
测试内容：
1. 基本功能测试
2. 博弈模块调用测试（5轮）
3. 日志记录功能验证
"""

import sys
import os
import json
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

LOG_FILE = os.path.join(os.path.dirname(__file__), "logs", "meta_cognition.json")


def load_log():
    """加载日志"""
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"sessions": [], "current_session": None}


def clear_log():
    """清空日志"""
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump({"sessions": [], "current_session": None, "statistics": {}}, f, ensure_ascii=False, indent=2)


def test_round(name, task_description, expected_mode):
    """执行单轮测试"""
    print(f"\n{'='*60}")
    print(f"【第{len(test_results)+1}轮测试】{name}")
    print(f"{'='*60}")
    print(f"任务描述: {task_description}")
    print(f"预期模式: {expected_mode}")

    try:
        from hooks.pre_task_hook import pre_task_hook
        from hooks.post_task_hook import post_task_hook

        # 执行前置钩子
        pre_result = pre_task_hook(task_description)
        detected_mode = pre_result.get("mode", "unknown")
        session_id = pre_result.get("session_id", "")

        # 检查博弈模块是否被调用
        game_theory_called = detected_mode.startswith("game_theory_")

        print(f"\n检测结果:")
        print(f"  - 会话ID: {session_id}")
        print(f"  - 检测到的模式: {detected_mode}")
        print(f"  - 博弈模块是否调用: {'✓ 是' if game_theory_called else '✗ 否'}")

        if detected_mode == expected_mode:
            print(f"  - 模式匹配: ✓ 成功")
            mode_match = True
        else:
            print(f"  - 模式匹配: ✗ 失败 (实际: {detected_mode})")
            mode_match = False

        # 执行后置钩子
        time.sleep(0.1)  # 模拟任务执行
        post_result = post_task_hook(
            session_id=session_id,
            result="success",
            agents_used=["code_executor_agent", "editor_agent"],
            response_preview="测试响应预览",
            duration_ms=100
        )

        print(f"\n后置钩子结果:")
        print(f"  - 记录成功: {'✓ 是' if post_result.get('logged') else '✗ 否'}")

        return {
            "name": name,
            "task": task_description,
            "expected_mode": expected_mode,
            "detected_mode": detected_mode,
            "mode_match": mode_match,
            "game_theory_called": game_theory_called,
            "session_id": session_id
        }

    except Exception as e:
        print(f"\n✗ 测试执行失败: {e}")
        import traceback
        traceback.print_exc()
        return {
            "name": name,
            "task": task_description,
            "expected_mode": expected_mode,
            "error": str(e)
        }


# 测试结果存储
test_results = []

print("="*60)
print("Meta-Cognition 插件完整测试")
print("="*60)

# 清空日志
clear_log()
print("\n[INFO] 日志已清空")

# 测试1: 导入模块测试
print("\n" + "="*60)
print("【模块导入测试】")
print("="*60)

try:
    from config.config import CONFIG
    print(f"✓ 配置模块导入成功")
    print(f"  - 博弈逻辑: {'启用' if CONFIG.enable_game_theory else '禁用'}")
    print(f"  - 统计功能: {'启用' if CONFIG.enable_statistics else '禁用'}")
    print(f"  - 自我更新: {'启用' if CONFIG.enable_self_update else '禁用'}")

    from hooks.utils import load_log, save_log
    print(f"✓ 工具模块导入成功")

    from hooks.pre_task_hook import pre_task_hook, detect_task_mode
    print(f"✓ 前置钩子模块导入成功")

    from hooks.post_task_hook import post_task_hook, get_statistics
    print(f"✓ 后置钩子模块导入成功")

    module_import_ok = True
except Exception as e:
    print(f"✗ 模块导入失败: {e}")
    module_import_ok = False

# 博弈模式测试用例（5轮）
game_theory_tests = [
    ("优化类任务", "请帮我优化这段代码，提升性能", "game_theory_mode2"),
    ("设计类任务", "帮我设计一个用户认证系统", "game_theory_mode3"),
    ("辩论类任务", "请对比敏捷开发和瀑布模型的优缺点", "game_theory_mode1"),
    ("修复类任务", "这个代码报错了，帮我修复一下", "game_theory_mode2"),
    ("复杂设计任务", "请从零开始实现一个分布式系统", "game_theory_mode3"),
]

# 执行5轮博弈模块测试
print("\n" + "="*60)
print("【博弈模块调用测试 - 5轮】")
print("="*60)

for name, task, expected_mode in game_theory_tests:
    result = test_round(name, task, expected_mode)
    test_results.append(result)
    time.sleep(0.2)

# 常规模式测试
normal_tests = [
    ("简单查询", "1+1等于几？", "normal"),
    ("时间查询", "现在几点了", "normal"),
]

print("\n" + "="*60)
print("【常规模式测试】")
print("="*60)

for name, task, expected_mode in normal_tests:
    result = test_round(name, task, expected_mode)
    test_results.append(result)
    time.sleep(0.2)

# 测试统计功能
print("\n" + "="*60)
print("【统计功能测试】")
print("="*60)

try:
    stats = get_statistics()
    print(f"统计信息:")
    print(f"  - 总任务数: {stats.get('total_tasks', 0)}")
    print(f"  - 成功率: {stats.get('success_rate', 0)}%")
    print(f"  - 博弈模式使用率: {stats.get('game_theory_usage_rate', 0)}%")
    print(f"  - 模式分布: {stats.get('mode_distribution', {})}")

    # 检查博弈模块使用情况
    gt_modes = ["game_theory_mode1", "game_theory_mode2", "game_theory_mode3"]
    gt_count = sum(1 for r in test_results if r.get("game_theory_called", False))
    total_gt_tests = len([t for t in game_theory_tests])

    print(f"\n博弈模块调用统计:")
    print(f"  - 博弈测试用例数: {total_gt_tests}")
    print(f"  - 实际调用博弈模块数: {gt_count}")
    print(f"  - 调用率: {gt_count/total_gt_tests*100:.1f}%")

    game_theory_usage_ok = gt_count >= total_gt_tests * 0.8  # 80%以上为合格

except Exception as e:
    print(f"✗ 统计功能测试失败: {e}")
    game_theory_usage_ok = False

# 测试日志记录
print("\n" + "="*60)
print("【日志记录功能测试】")
print("="*60)

final_log = load_log()
session_count = len([s for s in final_log.get("sessions", []) if s.get("phase") == "completed"])
print(f"已记录的会话数: {session_count}")

if session_count >= len(test_results):
    print(f"✓ 日志记录功能正常")
    log_write_ok = True
else:
    print(f"✗ 日志记录不完整 (预期: {len(test_results)}, 实际: {session_count})")
    log_write_ok = False

# 生成测试报告
print("\n" + "="*60)
print("【测试报告】")
print("="*60)

total_tests = len(test_results)
passed_tests = sum(1 for r in test_results if r.get("mode_match", False))
failed_tests = total_tests - passed_tests

print(f"\n总体结果:")
print(f"  - 总测试数: {total_tests}")
print(f"  - 通过测试: {passed_tests}")
print(f"  - 失败测试: {failed_tests}")
print(f"  - 通过率: {passed_tests/total_tests*100:.1f}%")

print(f"\n博弈模块调用情况:")
gt_tests = [r for r in test_results if r.get("expected_mode", "").startswith("game_theory")]
gt_passed = sum(1 for r in gt_tests if r.get("mode_match", False))
print(f"  - 博弈测试数: {len(gt_tests)}")
print(f"  - 博弈模式正确触发数: {gt_passed}")
print(f"  - 博弈模块调用率: {gt_count/len(game_theory_tests)*100:.1f}%")

print(f"\n功能状态:")
print(f"  - 模块导入: {'✓ 正常' if module_import_ok else '✗ 异常'}")
print(f"  - 博弈模块: {'✓ 正常' if game_theory_usage_ok else '✗ 异常'}")
print(f"  - 日志记录: {'✓ 正常' if log_write_ok else '✗ 异常'}")
print(f"  - 统计功能: {'✓ 正常' if stats else '✗ 异常'}")

# 最终结论
all_ok = module_import_ok and game_theory_usage_ok and log_write_ok
print(f"\n{'='*60}")
if all_ok:
    print("✓ Meta-Cognition 插件测试全部通过！")
else:
    print("✗ Meta-Cognition 插件存在部分问题，需要进一步检查")
print(f"{'='*60}")

# 保存测试结果到文件
test_report_path = os.path.join(os.path.dirname(__file__), "test_report.txt")
with open(test_report_path, "w", encoding="utf-8") as f:
    f.write("Meta-Cognition 插件测试报告\n")
    f.write(f"测试时间: {datetime.now().isoformat()}\n")
    f.write(f"\n总体结果:\n")
    f.write(f"  - 总测试数: {total_tests}\n")
    f.write(f"  - 通过测试: {passed_tests}\n")
    f.write(f"  - 失败测试: {failed_tests}\n")
    f.write(f"  - 通过率: {passed_tests/total_tests*100:.1f}%\n")
    f.write(f"\n各轮测试详情:\n")
    for i, r in enumerate(test_results, 1):
        f.write(f"\n第{i}轮: {r.get('name', 'unknown')}\n")
        f.write(f"  任务: {r.get('task', '')}\n")
        f.write(f"  预期: {r.get('expected_mode', '')}\n")
        f.write(f"  实际: {r.get('detected_mode', 'error')}\n")
        f.write(f"  博弈调用: {'是' if r.get('game_theory_called') else '否'}\n")
        f.write(f"  结果: {'通过' if r.get('mode_match') else '失败'}\n")

print(f"\n测试报告已保存到: {test_report_path}")

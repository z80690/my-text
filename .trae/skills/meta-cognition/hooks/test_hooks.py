# -*- coding: utf-8 -*-
"""
Meta-Cognition Hooks 测试脚本

测试所有核心功能：前置钩子、后置钩子、工具函数、配置管理等
"""

import sys
import os
import time
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from pre_task_hook import (
    pre_task_hook, detect_task_mode, get_scheduling_decision, get_task_recommendations
)
from post_task_hook import (
    post_task_hook, get_statistics, get_recent_sessions, get_session_by_id, export_sessions
)
from utils import (
    load_log, save_log, generate_session_id, get_current_timestamp,
    calculate_duration_ms, filter_sensitive_info, truncate_text, LOG_FILE
)
from ..config import get_config, CONFIG


class TestRunner:
    """测试运行器"""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []

    def run_test(self, name: str, test_func, *args):
        """运行单个测试"""
        print(f"\n{'='*60}")
        print(f"测试: {name}")
        print('='*60)
        try:
            result = test_func(*args)
            if result:
                self.passed += 1
                self.results.append((name, "PASSED", None))
                print(f"✓ {name} - 通过")
            else:
                self.failed += 1
                self.results.append((name, "FAILED", "Test returned False"))
                print(f"✗ {name} - 失败")
        except Exception as e:
            self.failed += 1
            self.results.append((name, "FAILED", str(e)))
            print(f"✗ {name} - 异常: {e}")
            import traceback
            traceback.print_exc()

    def print_summary(self):
        """打印测试摘要"""
        print(f"\n{'='*60}")
        print(f"测试摘要")
        print('='*60)
        print(f"通过: {self.passed}")
        print(f"失败: {self.failed}")
        print(f"总计: {self.passed + self.failed}")
        return self.failed == 0


def test_utils():
    """测试工具函数"""
    print("\n[1] 测试 generate_session_id")
    session_id1 = generate_session_id()
    session_id2 = generate_session_id()
    assert session_id1 != session_id2, "Session IDs should be unique"
    print(f"  ✓ 生成唯一会话ID: {session_id1[:8]}...")

    print("\n[2] 测试 get_current_timestamp")
    timestamp = get_current_timestamp()
    assert timestamp, "Timestamp should not be empty"
    print(f"  ✓ 生成时间戳: {timestamp}")

    print("\n[3] 测试 calculate_duration_ms")
    duration = calculate_duration_ms("2026-04-26T10:00:00", "2026-04-26T10:00:01")
    assert duration == 1000, f"Expected 1000ms, got {duration}"
    print(f"  ✓ 计算耗时: {duration}ms")

    duration_none = calculate_duration_ms(None, None)
    assert duration_none == 0, "Should return 0 for None inputs"
    print(f"  ✓ None输入处理: {duration_none}ms")

    print("\n[4] 测试 filter_sensitive_info")
    sensitive_text = "我的密码是 password123，API密钥是 abcdefghijklmnopqrstuv"
    filtered = filter_sensitive_info(sensitive_text)
    assert "password123" not in filtered, "Password should be filtered"
    assert "abcdefghijklmnopqrstuv" not in filtered, "API key should be filtered"
    print(f"  ✓ 敏感信息过滤成功")

    print("\n[5] 测试 truncate_text")
    long_text = "A" * 300
    truncated = truncate_text(long_text, 100)
    assert len(truncated) <= 103, "Truncated text should be <= max_length + '...' "
    print(f"  ✓ 文本截断: {len(truncated)} 字符")

    empty_truncated = truncate_text(None, 100)
    assert empty_truncated == "", "Should return empty string for None input"
    print(f"  ✓ None输入处理: '{empty_truncated}'")

    print("\n[6] 测试 load_log 和 save_log")
    test_data = {"sessions": [], "test": "data"}
    save_log(test_data)
    loaded_data = load_log()
    assert loaded_data.get("test") == "data", "Data should be saved and loaded"
    print(f"  ✓ 日志读写成功")

    return True


def test_config():
    """测试配置管理"""
    print("\n[1] 测试 get_config")
    config = get_config()
    assert config is not None, "Config should not be None"
    assert hasattr(config, "enable_game_theory"), "Config should have enable_game_theory"
    print(f"  ✓ 配置加载成功")
    print(f"    - 博弈模式: {config.enable_game_theory}")
    print(f"    - 统计功能: {config.enable_statistics}")
    print(f"    - 监控功能: {config.enable_monitoring}")

    print("\n[2] 测试关键词配置")
    keywords = config.keywords
    assert len(keywords.mode1_keywords) > 0, "Mode1 keywords should not be empty"
    assert len(keywords.mode2_keywords) > 0, "Mode2 keywords should not be empty"
    assert len(keywords.mode3_keywords) > 0, "Mode3 keywords should not be empty"
    print(f"  ✓ 博弈模式关键词已配置")
    print(f"    - 模式1关键词: {len(keywords.mode1_keywords)} 个")
    print(f"    - 模式2关键词: {len(keywords.mode2_keywords)} 个")
    print(f"    - 模式3关键词: {len(keywords.mode3_keywords)} 个")

    print("\n[3] 测试智能体配置")
    agents = config.agents
    assert len(agents.available_agents) > 0, "Available agents should not be empty"
    print(f"  ✓ 智能体配置已加载: {len(agents.available_agents)} 个智能体")

    return True


def test_pre_task_hook():
    """测试前置钩子"""
    test_cases = [
        ("请帮我优化这段代码，提升性能", "game_theory_mode2"),
        ("请对比敏捷开发和瀑布模型的优缺点", "game_theory_mode1"),
        ("帮我设计一个用户认证系统", "game_theory_mode3"),
        ("帮我写一个用户登录功能", "normal"),
        ("分析这个项目的风险和机会", "game_theory_mode1"),
        ("改进一下这个函数的性能", "game_theory_mode2"),
        ("创建一个新的数据库连接池", "game_theory_mode3"),
    ]

    print("\n[1] 测试任务模式检测")
    all_passed = True
    for task, expected_mode in test_cases:
        result = pre_task_hook(task)
        status = "✓" if result["mode"] == expected_mode else "✗"
        if result["mode"] != expected_mode:
            all_passed = False
        print(f"  {status} '{task[:20]}...' -> {result['mode']} (预期: {expected_mode})")

    assert all_passed, "Some mode detection tests failed"
    print(f"  ✓ 所有模式检测测试通过")

    print("\n[2] 测试 get_scheduling_decision")
    decision = get_scheduling_decision("game_theory_mode1")
    assert "mode" in decision, "Decision should contain 'mode'"
    assert "steps" in decision, "Decision should contain 'steps'"
    assert "recommended_agents" in decision, "Decision should contain 'recommended_agents'"
    print(f"  ✓ 调度决策生成成功: {decision['mode']}")

    print("\n[3] 测试 get_task_recommendations")
    recommendations = get_task_recommendations("请优化这个算法")
    assert "mode" in recommendations, "Recommendations should contain 'mode'"
    assert "recommended_agents" in recommendations, "Recommendations should contain 'recommended_agents'"
    print(f"  ✓ 任务推荐生成成功")
    print(f"    - 推荐模式: {recommendations['mode']}")
    print(f"    - 推荐智能体: {recommendations['recommended_agents']}")

    print("\n[4] 测试敏感信息过滤")
    sensitive_task = "我的密码是 secret123，请帮我优化代码"
    result = pre_task_hook(sensitive_task)
    assert "secret123" not in result.get("decision", {}).get("mode", ""), "Sensitive info should be filtered"
    print(f"  ✓ 敏感信息过滤正常工作")

    return True


def test_post_task_hook():
    """测试后置钩子"""
    print("\n[1] 测试完整流程")
    test_task = "测试任务 - 优化代码性能"
    pre_result = pre_task_hook(test_task)
    session_id = pre_result["session_id"]

    time.sleep(0.05)

    post_result = post_task_hook(
        session_id=session_id,
        result="success",
        agents_used=["code_executor_agent", "editor_agent"],
        response_preview="优化已完成，性能提升了50%",
        duration_ms=1500
    )

    assert post_result["logged"] == True, "Result should be logged"
    assert post_result["session_id"] == session_id, "Session ID should match"
    print(f"  ✓ 后置钩子执行成功")
    print(f"    - 会话ID: {session_id[:8]}...")
    print(f"    - 执行结果: {post_result['result']}")
    print(f"    - 使用智能体: {post_result['agents_used']}")

    print("\n[2] 测试 get_statistics")
    stats = get_statistics()
    assert "total_tasks" in stats, "Stats should contain 'total_tasks'"
    assert "success_rate" in stats, "Stats should contain 'success_rate'"
    assert "mode_distribution" in stats, "Stats should contain 'mode_distribution'"
    print(f"  ✓ 统计信息生成成功")
    print(f"    - 总任务数: {stats['total_tasks']}")
    print(f"    - 成功率: {stats['success_rate']}%")
    print(f"    - 博弈模式使用率: {stats['game_theory_usage_rate']}%")

    print("\n[3] 测试 get_session_by_id")
    session = get_session_by_id(session_id)
    assert session is not None, "Session should be found"
    assert session["session_id"] == session_id, "Session ID should match"
    print(f"  ✓ 会话查询成功")

    print("\n[4] 测试 get_recent_sessions")
    recent = get_recent_sessions(limit=5)
    assert isinstance(recent, list), "Should return a list"
    assert len(recent) > 0, "Should have at least one session"
    print(f"  ✓ 最近会话查询成功: {len(recent)} 条记录")

    print("\n[5] 测试 export_sessions")
    exported = export_sessions(filter_result="success")
    assert isinstance(exported, list), "Should return a list"
    print(f"  ✓ 导出会话成功: {len(exported)} 条记录")

    return True


def test_error_handling():
    """测试错误处理"""
    print("\n[1] 测试无效session_id")
    result = post_task_hook(
        session_id="invalid-session-id",
        result="failure",
        error="Test error message"
    )
    assert result["logged"] == True, "Should still log even with invalid session"
    print(f"  ✓ 无效session_id处理成功")

    print("\n[2] 测试空任务描述")
    pre_result = pre_task_hook("")
    assert pre_result["mode"] in ["normal", "game_theory_mode1", "game_theory_mode2", "game_theory_mode3"], "Should return a valid mode"
    print(f"  ✓ 空任务描述处理成功")

    print("\n[3] 测试 None duration_ms")
    log_data = load_log()
    if log_data["sessions"]:
        last_session = log_data["sessions"][-1]
        result = post_task_hook(
            session_id=last_session.get("session_id"),
            result="success",
            duration_ms=None
        )
        print(f"  ✓ None duration_ms处理成功")

    return True


def run_all_tests():
    """运行所有测试"""
    print("\n" + "#" * 60)
    print("# Meta-Cognition Hooks 完整测试套件")
    print("#" * 60)

    runner = TestRunner()

    print("\n" + "=" * 60)
    print("阶段 1: 工具函数测试")
    print("=" * 60)
    runner.run_test("工具函数", test_utils)

    print("\n" + "=" * 60)
    print("阶段 2: 配置管理测试")
    print("=" * 60)
    runner.run_test("配置管理", test_config)

    print("\n" + "=" * 60)
    print("阶段 3: 前置钩子测试")
    print("=" * 60)
    runner.run_test("前置钩子", test_pre_task_hook)

    print("\n" + "=" * 60)
    print("阶段 4: 后置钩子测试")
    print("=" * 60)
    runner.run_test("后置钩子", test_post_task_hook)

    print("\n" + "=" * 60)
    print("阶段 5: 错误处理测试")
    print("=" * 60)
    runner.run_test("错误处理", test_error_handling)

    success = runner.print_summary()

    print("\n" + "=" * 60)
    print("日志文件信息")
    print("=" * 60)
    print(f"日志文件位置: {LOG_FILE}")
    print(f"日志文件存在: {LOG_FILE.exists()}")

    if LOG_FILE.exists():
        log_data = load_log()
        print(f"总会话数: {len(log_data.get('sessions', []))}")

    return success


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

# -*- coding: utf-8 -*-
"""
测试Meta-Cognition技能的重构效果
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from meta_cognition.hooks.pre_task_hook import pre_task_hook, detect_task_mode
    from meta_cognition.hooks.post_task_hook import post_task_hook, get_statistics, get_task_statistics
    from meta_cognition.self_update import check_and_update, get_update_status
    from meta_cognition.auto_analyzer import check_and_analyze, get_analysis_status, generate_report
    from meta_cognition.active_learning import update_knowledge_graph, get_learning_status
    from meta_cognition.pattern_recognition import recognize_task_type, optimize_scheduling, generate_scheduling_recommendations
    from meta_cognition.config import CONFIG
    
    print("=== Meta-Cognition 技能测试 ===")
    print(f"自我更新功能: {'启用' if CONFIG.enable_self_update else '禁用'}")
    print(f"博弈逻辑功能: {'启用' if CONFIG.enable_game_theory else '禁用'}")
    print(f"统计功能: {'启用' if CONFIG.enable_statistics else '禁用'}")
    
    # 测试自我更新
    print("\n=== 测试自我更新 ===")
    update_status = get_update_status()
    print(f"更新状态: {update_status}")
    check_and_update()
    print("自我更新检查完成")
    
    # 测试自动分析
    print("\n=== 测试自动分析 ===")
    analysis_result = check_and_analyze()
    print(f"分析结果: {analysis_result}")
    analysis_status = get_analysis_status()
    print(f"分析状态: {analysis_status}")
    
    # 测试模式识别
    print("\n=== 测试模式识别 ===")
    test_tasks = [
        "请帮我优化这段代码，提升性能",
        "请对比敏捷开发和瀑布模型的优缺点",
        "帮我设计一个用户认证系统",
        "1+1等于几？",
        "现在几点了",
        "这个代码报错了，帮我修复一下",
        "帮我研究一下最新的AI技术"
    ]
    
    for task in test_tasks:
        task_type, confidence = recognize_task_type(task)
        scheduling = optimize_scheduling(task)
        print(f"任务: {task}")
        print(f"类型: {task_type}, 置信度: {confidence:.2f}")
        print(f"调度建议: {scheduling.get('adjusted_mode', 'normal')}")
        print()
    
    # 测试任务模式检测
    print("\n=== 测试任务模式检测 ===")
    mode_tests = [
        ("请帮我优化这段代码，提升性能", "game_theory_mode2"),
        ("请对比敏捷开发和瀑布模型的优缺点", "game_theory_mode1"),
        ("帮我设计一个用户认证系统", "game_theory_mode3"),
        ("1+1等于几？", "normal"),
        ("现在几点了", "normal"),
        ("这个代码报错了，帮我修复一下", "game_theory_mode2"),
        ("看看这个方案有什么问题", "game_theory_mode2"),
    ]
    
    for task, expected_mode in mode_tests:
        detected_mode = detect_task_mode(task)
        status = "✓" if detected_mode == expected_mode else "✗"
        print(f"{status} 任务: {task}")
        print(f"  预期: {expected_mode} -> 实际: {detected_mode}")
    
    # 测试前置钩子
    print("\n=== 测试前置钩子 ===")
    test_task = "请帮我优化这段代码，提升性能"
    pre_result = pre_task_hook(test_task)
    print(f"任务: {test_task}")
    print(f"会话ID: {pre_result['session_id']}")
    print(f"检测模式: {pre_result['mode']}")
    print(f"任务类型: {pre_result.get('task_type', 'normal')}")
    print(f"调度建议: {pre_result.get('scheduling_advice', {})}")
    print(f"工作流输出: {pre_result['workflow_output'][:200]}...")
    
    # 测试后置钩子
    print("\n=== 测试后置钩子 ===")
    post_result = post_task_hook(
        session_id=pre_result["session_id"],
        result="success",
        agents_used=["code_executor_agent", "editor_agent"],
        response_preview="优化建议已完成，应用了XYZ技术来提升性能...",
        duration_ms=1500
    )
    print(f"后置钩子结果: {post_result}")
    
    # 测试主动学习
    print("\n=== 测试主动学习 ===")
    learning_result = update_knowledge_graph()
    print(f"知识图谱更新: {learning_result}")
    learning_status = get_learning_status()
    print(f"学习状态: {learning_status}")
    
    # 测试调度建议
    print("\n=== 测试调度建议 ===")
    recommendations = generate_scheduling_recommendations()
    print(f"调度建议: {recommendations}")
    
    # 测试统计信息
    print("\n=== 测试统计信息 ===")
    stats = get_statistics()
    print(f"总任务数: {stats.get('total_tasks', 0)}")
    print(f"成功率: {stats.get('success_rate', 0)}%")
    print(f"博弈逻辑使用率: {stats.get('game_theory_usage_rate', 0)}%")
    
    task_stats = get_task_statistics()
    print(f"\n任务执行统计:")
    print(f"总任务: {task_stats.get('total', 0)}")
    print(f"成功任务: {task_stats.get('success', 0)}")
    print(f"失败任务: {task_stats.get('failure', 0)}")
    print(f"成功率: {task_stats.get('success_rate', 0)}%")
    
    # 生成分析报告
    print("\n=== 生成分析报告 ===")
    report_path = generate_report()
    print(f"报告生成路径: {report_path}")
    
    print("\n=== 测试完成 ===")
    
except Exception as e:
    print(f"测试失败: {e}")
    import traceback
    traceback.print_exc()

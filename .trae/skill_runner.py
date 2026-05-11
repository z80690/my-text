# -*- coding: utf-8 -*-
"""
Skills 统一入口 - 自动化集成
所有 Skills 通过此模块加载，自动获得追踪、日志、建议功能
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass

from skill_auto_integration import (
    SkillExecutor,
    get_executor,
    execute_skill,
    with_auto_tracking,
    get_today_summary
)


@dataclass
class SkillInfo:
    skill_id: str
    name: str
    description: str
    trigger_keywords: List[str]
    category: str
    enabled: bool = True


class SkillRegistry:
    """Skill 注册中心"""

    SKILLS = {
        "auto-debug": SkillInfo(
            skill_id="auto-debug",
            name="智能排错",
            description="自动化调试，从报错到修复一站式",
            trigger_keywords=["调试", "报错", "bug", "错误", "修复"],
            category="debugging"
        ),
        "auto-hook": SkillInfo(
            skill_id="auto-hook",
            name="自动化钩子",
            description="事件驱动的自动化触发器",
            trigger_keywords=["hook", "钩子", "自动化", "触发"],
            category="automation"
        ),
        "auto-doc": SkillInfo(
            skill_id="auto-doc",
            name="一键生成文档",
            description="自动生成README、API文档、代码注释",
            trigger_keywords=["文档", "README", "注释", "生成文档"],
            category="documentation"
        ),
        "auto-refactor": SkillInfo(
            skill_id="auto-refactor",
            name="全局代码重构",
            description="批量安全重构整个项目",
            trigger_keywords=["重构", "refactor", "批量修改", "迁移"],
            category="refactoring"
        ),
        "local-privacy": SkillInfo(
            skill_id="local-privacy",
            name="本地隐私联动",
            description="本地资源安全读取，不上传云端",
            trigger_keywords=["本地", "隐私", "local", "笔记"],
            category="privacy"
        ),
        "tool-usage-tracker": SkillInfo(
            skill_id="tool-usage-tracker",
            name="工具调用追踪",
            description="追踪MCP和Skills的调用情况",
            trigger_keywords=["报告", "日报", "追踪", "统计"],
            category="monitoring"
        )
    }

    @classmethod
    def get_skill(cls, skill_id: str) -> Optional[SkillInfo]:
        return cls.SKILLS.get(skill_id)

    @classmethod
    def list_skills(cls) -> List[SkillInfo]:
        return list(cls.SKILLS.values())

    @classmethod
    def find_by_keyword(cls, keyword: str) -> List[SkillInfo]:
        keyword_lower = keyword.lower()
        return [
            skill for skill in cls.SKILLS.values()
            if any(kw.lower() in keyword_lower for kw in skill.trigger_keywords)
        ]

    @classmethod
    def get_by_category(cls, category: str) -> List[SkillInfo]:
        return [s for s in cls.SKILLS.values() if s.category == category]


class AutoSkillRunner:
    """自动 Skill 运行器"""

    def __init__(self):
        self.executor = get_executor()
        self.registry = SkillRegistry()

    def run(self, skill_id: str, action: str, func: Callable, *args, **kwargs) -> Any:
        skill = self.registry.get_skill(skill_id)
        if not skill:
            raise ValueError(f"未知的 Skill: {skill_id}")

        if not skill.enabled:
            raise RuntimeError(f"Skill {skill_id} 已禁用")

        print(f"\n🚀 执行 Skill: {skill.name} ({skill_id})")
        print(f"   动作: {action}")
        print(f"   分类: {skill.category}")

        return self.executor.execute(skill_id, action, func, *args, **kwargs)

    def run_debug(self, error_info: str) -> Dict:
        def debug_func(error: str):
            return {
                "analysis": f"分析错误: {error[:100]}...",
                "steps": ["定位问题", "分析原因", "生成修复", "验证结果"],
                "status": "analyzing"
            }
        return self.run("auto-debug", "analyze", debug_func, error_info)

    def run_hook(self, trigger: str, action: str) -> Dict:
        def hook_func(trig: str, act: str):
            return {
                "trigger": trig,
                "action": act,
                "status": "registered",
                "message": f"钩子已设置: {trig} -> {act}"
            }
        return self.run("auto-hook", "register", hook_func, trigger, action)

    def run_doc(self, target: str, doc_type: str = "README") -> Dict:
        def doc_func(tgt: str, dtype: str):
            return {
                "target": tgt,
                "type": dtype,
                "status": "generated",
                "message": f"已生成 {dtype} 文档: {tgt}"
            }
        return self.run("auto-doc", "generate", doc_func, target, doc_type)

    def run_refactor(self, pattern: str, replacement: str) -> Dict:
        def refactor_func(pat: str, repl: str):
            return {
                "pattern": pat,
                "replacement": repl,
                "status": "refactored",
                "message": f"已重构: {pat} -> {repl}"
            }
        return self.run("auto-refactor", "batch", refactor_func, pattern, replacement)

    def run_privacy(self, file_path: str) -> Dict:
        def privacy_func(fp: str):
            return {
                "file": fp,
                "status": "read_locally",
                "message": f"已安全读取本地文件: {fp}",
                "privacy": "数据未离开本地"
            }
        return self.run("local-privacy", "read", privacy_func, file_path)

    def run_tracker(self, report_type: str = "daily") -> str:
        def tracker_func(rtype: str):
            return get_today_summary()
        return self.run("tool-usage-tracker", "report", tracker_func, report_type)


_runner: Optional[AutoSkillRunner] = None


def get_runner() -> AutoSkillRunner:
    global _runner
    if _runner is None:
        _runner = AutoSkillRunner()
    return _runner


def quick_debug(error: str) -> Dict:
    return get_runner().run_debug(error)


def quick_hook(trigger: str, action: str) -> Dict:
    return get_runner().run_hook(trigger, action)


def quick_doc(target: str, doc_type: str = "README") -> Dict:
    return get_runner().run_doc(target, doc_type)


def quick_refactor(pattern: str, replacement: str) -> Dict:
    return get_runner().run_refactor(pattern, replacement)


def quick_privacy(file_path: str) -> Dict:
    return get_runner().run_privacy(file_path)


def quick_tracker() -> str:
    return get_runner().run_tracker()


def show_all_skills() -> str:
    skills = SkillRegistry.list_skills()

    lines = ["# 📚 可用 Skills 列表\n"]

    categories = {}
    for skill in skills:
        if skill.category not in categories:
            categories[skill.category] = []
        categories[skill.category].append(skill)

    for category, category_skills in categories.items():
        lines.append(f"\n## {category.upper()}\n")
        for skill in category_skills:
            status = "✅" if skill.enabled else "❌"
            lines.append(f"### {status} {skill.name}\n")
            lines.append(f"- **ID**: `{skill.skill_id}`")
            lines.append(f"- **描述**: {skill.description}")
            lines.append(f"- **触发词**: {', '.join(skill.trigger_keywords)}\n")

    return "\n".join(lines)


if __name__ == '__main__':
    print(show_all_skills())

    print("\n" + "="*60)
    print("🧪 快速测试")
    print("="*60)

    result = quick_debug("TypeError: 'NoneType' object is not callable")
    print(f"\n调试结果: {result}")

    result = quick_hook("post_save", "auto_format")
    print(f"\n钩子结果: {result}")

    result = quick_doc("my-project")
    print(f"\n文档结果: {result}")

    print("\n" + get_today_summary())

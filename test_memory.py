#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from pathlib import Path
from datetime import datetime

class AutoMemorySystem:
    def __init__(self):
        self.memories_dir = Path(".trae") / "memories"
        for dir_name in ["user", "feedback", "project", "reference"]:
            (self.memories_dir / dir_name).mkdir(parents=True, exist_ok=True)
    
    def is_dark_knowledge(self, message: str) -> tuple[bool, str]:
        # 明知识模式（能从代码/git查到的）
        bright_patterns = [
            r"\b(React|Vue|Node|Python|Java|Go|Rust)\s+\d+\.\d+(\.\d+)?\b",
            r"\b(在|位于|路径|文件)\s*[\w./\\-]+\.(js|ts|py|md|json)\b",
            r"\b(def|function|class)\s+[\w_]+\b",
        ]
        for pattern in bright_patterns:
            if re.search(pattern, message):
                return False, "明知识"
        
        # 暗知识模式（需要记忆的）- 修复：更宽松的匹配
        dark_patterns = [
            (r"习惯|喜欢|偏好|风格", "用户偏好"),
            (r"很好|认可|以后都这样|建议|改进", "用户反馈"),
            (r"禁止|必须|我们团队", "团队规则"),
            (r"因为要|为了兼容|历史遗留|设计原因", "设计决策"),
            (r"系统|项目启动|项目背景", "项目背景"),
            (r"Jira|票号|文档在|链接|参考", "外部引用"),
        ]
        for pattern, reason in dark_patterns:
            if re.search(pattern, message):
                return True, reason
        return False, "无法分类"
    
    def classify(self, message: str) -> str:
        if re.search(r"习惯|喜欢|偏好|风格", message):
            return "user"
        if re.search(r"很好|认可|以后都这样|建议|改进", message):
            return "feedback"
        if re.search(r"禁止|必须|我们团队|因为要|为了兼容|历史遗留|设计原因|系统|项目启动|项目背景", message):
            return "project"
        if re.search(r"Jira|票号|文档在|链接|参考", message):
            return "reference"
        return "user"
    
    def write_memory(self, message: str, mem_type: str) -> str:
        filename = re.sub(r'[^\w\u4e00-\u9fa5\-_]', '_', message[:20])
        filename = re.sub(r'_+', '_', filename).strip('_') or "memory"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        dir_map = {"user": "user", "feedback": "feedback", "project": "project", "reference": "reference"}
        target_dir = self.memories_dir / dir_map[mem_type]
        
        content = f"""---
type: {mem_type}
created: {timestamp}
---

# {message[:30]}...

{message}

**Why:** 自动识别的暗知识
**How to apply:** 根据记忆类型自动触发
"""
        
        filepath = target_dir / f"{filename}.md"
        counter = 1
        while filepath.exists():
            filepath = target_dir / f"{filename}_{counter}.md"
            counter += 1
        
        filepath.write_text(content, encoding="utf-8")
        return str(filepath)
    
    def process(self, message: str) -> dict:
        is_dark, why = self.is_dark_knowledge(message)
        if is_dark:
            mem_type = self.classify(message)
            filepath = self.write_memory(message, mem_type)
            return {"auto_saved": True, "type": mem_type, "path": filepath, "reason": why}
        return {"auto_saved": False, "reason": why}

# 测试
memory_system = AutoMemorySystem()

# 测试用例
test_cases = [
    "我习惯用4空格缩进",
    "这个项目用的是React 18.2.0",
    "很好，以后都这样",
    "禁止用for循环",
    "因为要兼容旧版本",
    "这是电商后台系统",
    "Jira票号ABC-123",
]

print("=== 自动记忆系统测试 ===\n")
for msg in test_cases:
    result = memory_system.process(msg)
    print(f"消息: {msg}")
    print(f"结果: {result}")
    print("-" * 50)

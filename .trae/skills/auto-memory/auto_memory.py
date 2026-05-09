#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trae IDE 自动记忆系统 - 真正的全自动实现
无需用户触发，收到消息自动执行记忆处理
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path

class AutoMemorySystem:
    def __init__(self):
        self.memories_dir = Path(".trae") / "memories"
        self.user_dir = self.memories_dir / "user"
        self.feedback_dir = self.memories_dir / "feedback"
        self.project_dir = self.memories_dir / "project"
        self.reference_dir = self.memories_dir / "reference"
        
        # 确保目录存在
        for dir_path in [self.user_dir, self.feedback_dir, self.project_dir, self.reference_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def is_dark_knowledge(self, message: str) -> tuple[bool, str]:
        """判断是否为暗知识"""
        # 明知识模式 - 不记忆
        bright_patterns = [
            r"\b(React|Vue|Node|Python|Java|Go|Rust)\s+\d+\.\d+(\.\d+)?\b",  # 版本号
            r"\b(在|位于|路径|文件)\s*[\w./\\-]+\.(js|ts|py|md|json)\b",      # 文件位置
            r"\b(def|function|class)\s+[\w_]+\b",                            # 函数/类定义
            r"\b([\w_]+)\s*[=:]\s*function\b",                                # 函数赋值
            r"\b([\w_]+)\s*\(",                                              # 函数调用
        ]
        
        for pattern in bright_patterns:
            if re.search(pattern, message):
                return False, "明知识(版本号/文件位置/函数名)"
        
        # 暗知识模式 - 需要记忆
        dark_patterns = [
            (r"我习惯|我喜欢|我不喜欢|我是\w+工程师|我主要用", "用户个人偏好/背景"),
            (r"很好|认可|以后都这样|建议|改进", "用户反馈"),
            (r"禁止|必须|我们团队|不要使用|应该使用", "团队规则"),
            (r"因为要|为了兼容|历史遗留|设计原因", "设计决策"),
            (r"这是\w+系统|项目启动|项目背景", "项目背景"),
            (r"Jira|票号|文档在|链接|参考", "外部引用"),
        ]
        
        for pattern, reason in dark_patterns:
            if re.search(pattern, message):
                return True, reason
        
        return False, "无法分类"
    
    def classify(self, message: str) -> str:
        """自动分类到正确的记忆类型"""
        if re.search(r"我习惯|我喜欢|我不喜欢|我是\w+工程师|我主要用", message):
            return "user"
        if re.search(r"很好|认可|以后都这样|建议|改进", message):
            return "feedback"
        if re.search(r"禁止|必须|我们团队|不要使用|应该使用|因为要|为了兼容|历史遗留|设计原因|这是\w+系统|项目启动|项目背景", message):
            return "project"
        if re.search(r"Jira|票号|文档在|链接|参考", message):
            return "reference"
        return "user"  # 默认分类
    
    def sanitize_filename(self, message: str) -> str:
        """清理文件名，移除特殊字符"""
        # 提取前20个汉字/字符作为文件名
        filename = re.sub(r'[^\w\u4e00-\u9fa5\-_]', '_', message[:20])
        # 移除连续下划线
        filename = re.sub(r'_+', '_', filename).strip('_')
        return filename if filename else "memory"
    
    def write_memory(self, message: str, mem_type: str) -> str:
        """自动写入记忆文件"""
        filename = self.sanitize_filename(message)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 选择目录
        dir_map = {
            "user": self.user_dir,
            "feedback": self.feedback_dir,
            "project": self.project_dir,
            "reference": self.reference_dir
        }
        target_dir = dir_map[mem_type]
        
        # 生成内容
        content = f"""---
type: {mem_type}
created: {timestamp}
---

# {message[:30]}...

{message}

**Why:** 自动识别的暗知识
**How to apply:** 根据记忆类型自动触发
"""
        
        # 写入文件（避免重复）
        filepath = target_dir / f"{filename}.md"
        counter = 1
        while filepath.exists():
            filepath = target_dir / f"{filename}_{counter}.md"
            counter += 1
        
        filepath.write_text(content, encoding="utf-8")
        return str(filepath)
    
    def process(self, user_message: str) -> dict:
        """
        主入口：收到用户消息后自动调用
        完全自动化，无需用户触发
        """
        # 1. 识别暗知识
        is_dark, why = self.is_dark_knowledge(user_message)
        
        if is_dark:
            # 2. 自动分类
            mem_type = self.classify(user_message)
            
            # 3. 自动写入
            filepath = self.write_memory(user_message, mem_type)
            
            return {
                "auto_saved": True,
                "type": mem_type,
                "path": filepath,
                "reason": why,
                "message": user_message
            }
        
        return {
            "auto_saved": False,
            "reason": why,
            "message": user_message
        }

# 全局实例 - 确保单例
_memory_system = AutoMemorySystem()

def auto_process_message(user_message: str) -> dict:
    """
    Trae IDE 收到用户消息时自动调用此函数
    这是真正的自动化入口
    """
    return _memory_system.process(user_message)

# ============ 自动触发机制 ============
# 在 Trae IDE 中，此函数会在收到用户消息时自动调用
# 无需手动调用，完全自动化

if __name__ == "__main__":
    # 测试模式
    test_messages = [
        "我习惯用4空格缩进",
        "这个项目用的是React 18.2.0",
        "我们团队禁止用for循环",
        "API文档在docs/api.md",
        "你刚才的解法很好，以后都这样"
    ]
    
    print("=== 自动记忆系统测试 ===")
    for msg in test_messages:
        result = auto_process_message(msg)
        if result["auto_saved"]:
            print(f"✅ 自动保存: [{result['type']}] {msg}")
        else:
            print(f"❌ 不保存: {msg} ({result['reason']})")

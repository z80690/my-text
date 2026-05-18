#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trae IDE 自动记忆系统 - MCP 协议实现
基于规则体系 L3.4.7：记录→应用→反馈→进化闭环
"""

import os
import re
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class MemorySystem:
    def __init__(self):
        self.memories_dir = Path(".trae") / "memories"
        self.user_dir = self.memories_dir / "user"
        self.feedback_dir = self.memories_dir / "feedback"
        self.project_dir = self.memories_dir / "project"
        self.reference_dir = self.memories_dir / "reference"
        self.evolution_dir = self.memories_dir / "evolution"
        
        for dir_path in [self.user_dir, self.feedback_dir, self.project_dir, 
                        self.reference_dir, self.evolution_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def is_dark_knowledge(self, message: str) -> tuple[bool, str]:
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
        if re.search(r"我习惯|我喜欢|我不喜欢|我是\w+工程师|我主要用", message):
            return "user"
        if re.search(r"很好|认可|以后都这样|建议|改进", message):
            return "feedback"
        if re.search(r"禁止|必须|我们团队|不要使用|应该使用|因为要|为了兼容|历史遗留|设计原因|这是\w+系统|项目启动|项目背景", message):
            return "project"
        if re.search(r"Jira|票号|文档在|链接|参考", message):
            return "reference"
        return "user"
    
    def sanitize_filename(self, message: str) -> str:
        filename = re.sub(r'[^\w\u4e00-\u9fa5\-_]', '_', message[:20])
        filename = re.sub(r'_+', '_', filename).strip('_')
        return filename if filename else "memory"
    
    def record(self, message: str, mem_type: str) -> str:
        filename = self.sanitize_filename(message)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        dir_map = {
            "user": self.user_dir,
            "feedback": self.feedback_dir,
            "project": self.project_dir,
            "reference": self.reference_dir
        }
        target_dir = dir_map[mem_type]
        
        content = f"""---
type: {mem_type}
created: {timestamp}
phase: record
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
    
    def apply(self, query: str) -> List[Dict]:
        results = []
        for mem_type, mem_dir in [
            ("user", self.user_dir),
            ("feedback", self.feedback_dir),
            ("project", self.project_dir),
            ("reference", self.reference_dir)
        ]:
            for file in mem_dir.glob("*.md"):
                content = file.read_text(encoding="utf-8")
                if query.lower() in content.lower():
                    results.append({
                        "type": mem_type,
                        "path": str(file),
                        "content": content
                    })
        return results
    
    def feedback(self, memory_path: str, effect: str) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        feedback_file = self.evolution_dir / f"feedback_{timestamp.replace(':', '-')}.md"
        
        content = f"""---
type: feedback
created: {timestamp}
phase: feedback
memory_path: {memory_path}
---

# 应用效果反馈

**记忆文件:** {memory_path}
**效果:** {effect}
**时间:** {timestamp}
"""
        
        feedback_file.write_text(content, encoding="utf-8")
        return str(feedback_file)
    
    def evolve(self, feedback_path: str) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        evolve_file = self.evolution_dir / f"evolve_{timestamp.replace(':', '-')}.md"
        
        feedback_content = Path(feedback_path).read_text(encoding="utf-8")
        
        content = f"""---
type: evolution
created: {timestamp}
phase: evolution
feedback_path: {feedback_path}
---

# 知识进化记录

**反馈文件:** {feedback_path}
**反馈内容:**
{feedback_content}

**进化方向:** 根据反馈持续优化知识库
**时间:** {timestamp}
"""
        
        evolve_file.write_text(content, encoding="utf-8")
        return str(evolve_file)

_memory_system = MemorySystem()

def process_message(message: str) -> dict:
    is_dark, why = _memory_system.is_dark_knowledge(message)
    
    if is_dark:
        mem_type = _memory_system.classify(message)
        filepath = _memory_system.record(message, mem_type)
        
        return {
            "success": True,
            "phase": "record",
            "type": mem_type,
            "path": filepath,
            "reason": why,
            "message": message
        }
    
    return {
        "success": False,
        "reason": why,
        "message": message
    }

def search_memory(query: str) -> dict:
    results = _memory_system.apply(query)
    
    return {
        "success": True,
        "phase": "apply",
        "query": query,
        "results": results,
        "count": len(results)
    }

def record_feedback(memory_path: str, effect: str) -> dict:
    filepath = _memory_system.feedback(memory_path, effect)
    
    return {
        "success": True,
        "phase": "feedback",
        "path": filepath,
        "memory_path": memory_path,
        "effect": effect
    }

def evolve_knowledge(feedback_path: str) -> dict:
    filepath = _memory_system.evolve(feedback_path)
    
    return {
        "success": True,
        "phase": "evolve",
        "path": filepath,
        "feedback_path": feedback_path
    }

def main():
    for line in sys.stdin:
        try:
            data = json.loads(line.strip())
            
            if data.get("method") == "process_message":
                result = process_message(data.get("message", ""))
            elif data.get("method") == "search_memory":
                result = search_memory(data.get("query", ""))
            elif data.get("method") == "record_feedback":
                result = record_feedback(
                    data.get("memory_path", ""),
                    data.get("effect", "")
                )
            elif data.get("method") == "evolve_knowledge":
                result = evolve_knowledge(data.get("feedback_path", ""))
            else:
                result = {"success": False, "error": "Unknown method"}
            
            print(json.dumps(result, ensure_ascii=False))
            sys.stdout.flush()
            
        except Exception as e:
            print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
            sys.stdout.flush()

if __name__ == "__main__":
    main()
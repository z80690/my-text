"""
Cloud Code 记忆系统自动管理工具
实现自动记忆写入、检索、验证、Dream整合功能
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class MemorySystem:
    def __init__(self, base_path: str = ".trae/memories"):
        self.base_path = Path(base_path)
        self.user_path = self.base_path / "user"
        self.feedback_path = self.base_path / "feedback"
        self.project_path = self.base_path / "project"
        self.reference_path = self.base_path / "reference"

    def init_directories(self):
        """初始化记忆目录"""
        for path in [self.user_path, self.feedback_path, self.project_path, self.reference_path]:
            path.mkdir(parents=True, exist_ok=True)
        return True

    def is_dark_knowledge(self, text: str) -> bool:
        """
        判断是否为暗知识（应该记忆的知识）
        暗知识：无法从代码/git历史中推导出的信息
        """
        dark_patterns = [
            r"我(是|习惯|喜欢|希望|要求|禁止)",
            r"团队",
            r"以后",
            r"以后都这样",
            r"因为要",
            r"这是.*系统",
            r"以后只要",
        ]
        bright_patterns = [
            r'用的是.*\d+\.\d+\.\d+',  # 版本号
            r'在.*\.js里',
            r'有个.*函数',
            r'可以用.*查',
        ]

        for pattern in dark_patterns:
            if re.search(pattern, text):
                return True
        for pattern in bright_patterns:
            if re.search(pattern, text):
                return False
        return True

    def classify_knowledge(self, text: str) -> str:
        """分类知识类型"""
        if re.search(r'好|认可|确认|以后都这样', text):
            return "feedback"
        if re.search(r'在.*\.(md|json|yml|yaml|txt|doc)', text):
            return "reference"
        if re.search(r'项目|系统|模块|设计|原因|因为|背景', text):
            return "project"
        return "user"

    def write_memory(self, text: str, memory_type: str, title: str = None) -> str:
        """写入记忆文件"""
        type_path = getattr(self, f"{memory_type}_path")
        if title is None:
            title = text[:30] + "..." if len(text) > 30 else text
        safe_name = re.sub(r'[^\w\-_.]', '_', title[:50])
        filepath = type_path / f"{safe_name}.md"

        content = f"""---
type: {memory_type}
created: {datetime.now().strftime('%Y-%m-%d')}
---

# {title}

{text}

**Why:** 自动从对话中提取
**How to apply:** 根据内容类型触发
"""
        filepath.write_text(content, encoding='utf-8')
        return str(filepath)

    def read_memory(self, filepath: str) -> Optional[Dict]:
        """读取记忆文件"""
        path = Path(filepath)
        if not path.exists():
            return None
        content = path.read_text(encoding='utf-8')
        return {
            "path": str(path),
            "content": content,
            "type": self._extract_type(content),
            "title": self._extract_title(content)
        }

    def _extract_type(self, content: str) -> str:
        match = re.search(r'type:\s*(\w+)', content)
        return match.group(1) if match else "unknown"

    def _extract_title(self, content: str) -> str:
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        return match.group(1) if match else "Untitled"

    def verify_memory(self, memory_path: str) -> bool:
        """验证记忆中的路径是否存在"""
        content = Path(memory_path).read_text(encoding='utf-8')
        paths = re.findall(r'([a-zA-Z0-9_/\\.]+\.[a-z]+)', content)
        for p in paths:
            if not Path(p).exists():
                return False
        return True

    def dream_consolidate(self) -> Dict:
        """Dream记忆整合"""
        report = {
            "time": datetime.now().isoformat(),
            "scanned": {},
            "merged": [],
            "pruned": [],
            "total_lines": 0
        }
        for mem_type in ["user", "feedback", "project", "reference"]:
            path = getattr(self, f"{mem_type}_path")
            files = list(path.glob("*.md"))
            report["scanned"][mem_type] = len(files)
            total_lines = sum(len(f.read_text(encoding='utf-8').splitlines()) for f in files)
            report["total_lines"] += total_lines
        report["status"] = "OK" if report["total_lines"] <= 200 else "需要剪枝"
        return report

    def search_memories(self, query: str) -> List[Dict]:
        """搜索记忆"""
        results = []
        for mem_type in ["user", "feedback", "project", "reference"]:
            path = getattr(self, f"{mem_type}_path")
            for f in path.glob("*.md"):
                content = f.read_text(encoding='utf-8')
                if query.lower() in content.lower():
                    results.append({
                        "type": mem_type,
                        "file": str(f),
                        "title": self._extract_title(content)
                    })
        return results

if __name__ == "__main__":
    ms = MemorySystem()
    ms.init_directories()
    print("Cloud Code 记忆系统已初始化")
    print(f"记忆目录: {ms.base_path}")
    print(f"可用命令: init, write, read, verify, dream, search")

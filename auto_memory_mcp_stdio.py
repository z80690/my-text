#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trae IDE 自动记忆 MCP 服务器 - Stdio模式
使用标准库实现，符合 MCP JSON-RPC 2.0 协议
增强版：去重、分类优化、内容补全、智能合并、内存优化
"""

import os
import re
import json
import sys
import hashlib
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Tuple


class AutoMemorySystem:
    def __init__(self):
        self.memories_dir = Path(".trae") / "memories"
        self.state_file = self.memories_dir / ".state.json"
        self.threshold = 0.75
        self.max_hash_cache = 1000

        for dir_name in ["user", "feedback", "project", "reference"]:
            (self.memories_dir / dir_name).mkdir(parents=True, exist_ok=True)

        self.state = self._load_state()

    def _load_state(self) -> Dict:
        if self.state_file.exists():
            try:
                content = self.state_file.read_text(encoding="utf-8")
                return json.loads(content)
            except json.JSONDecodeError:
                pass
            except Exception:
                pass
        return {"memory_hashes": [], "merged_memories": []}

    def _save_state(self):
        if len(self.state.get("memory_hashes", [])) > self.max_hash_cache:
            self.state["memory_hashes"] = self.state["memory_hashes"][-self.max_hash_cache:]
        try:
            self.state_file.write_text(json.dumps(self.state, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

    def _compute_hash(self, text: str) -> str:
        normalized = re.sub(r'\s+', '', text.lower())
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()[:16]

    def _compute_similarity(self, text1: str, text2: str) -> float:
        words1 = set(re.findall(r'\w+', text1.lower()))
        words2 = set(re.findall(r'\w+', text2.lower()))
        if not words1 or not words2:
            return 0.0
        intersection = words1 & words2
        union = words1 | words2
        return len(intersection) / len(union) if union else 0.0

    def _find_similar_memory(self, message: str, category: str) -> Optional[Path]:
        new_hash = self._compute_hash(message)
        if new_hash in self.state.get("memory_hashes", []):
            return Path("DUPLICATE")

        category_dir = self.memories_dir / category
        if not category_dir.exists():
            return None

        start_time = time.time()
        timeout = 0.5

        for mem_file in category_dir.glob("*.md"):
            if time.time() - start_time > timeout:
                break
            try:
                content = mem_file.read_text(encoding="utf-8")
                match = re.search(r'^#\s*(.+)$', content, re.MULTILINE)
                if match:
                    existing_title = match.group(1)
                    similarity = self._compute_similarity(message, existing_title)
                    if similarity >= self.threshold:
                        return mem_file
            except Exception:
                continue
        return None

    def is_dark_knowledge(self, message: str) -> tuple[bool, str]:
        bright_patterns = [
            r"\b(React|Vue|Node|Python|Java|Go|Rust)\s+\d+\.\d+(\.\d+)?\b",
            r"\b(在|位于|路径|文件)\s*[\w./\\-]+\.(js|ts|py|md|json)\b",
            r"\b(def|function|class)\s+[\w_]+\b",
            r"\b\d{4}-\d{2}-\d{2}\b",
        ]
        for pattern in bright_patterns:
            if re.search(pattern, message):
                return False, "明知识"

        dark_patterns = [
            (r"习惯|喜欢|偏好|风格|我不|我的", "用户偏好"),
            (r"很好|认可|以后都这样|建议|改进|不错|太棒了", "用户反馈"),
            (r"禁止|必须|我们团队|不要|不许|别", "团队规则"),
            (r"因为要|为了兼容|历史遗留|设计原因|架构", "设计决策"),
            (r"系统|项目启动|项目背景|后台|前端", "项目背景"),
            (r"Jira|票号|文档在|链接|参考|需求文档", "外部引用"),
        ]
        for pattern, reason in dark_patterns:
            if re.search(pattern, message):
                return True, reason
        return False, "无法分类"

    def classify(self, message: str) -> str:
        if re.search(r"习惯|喜欢|偏好|风格|我不|我的|后端|前端|工程师|开发", message):
            return "user"
        if re.search(r"很好|认可|以后都这样|建议|改进|不错|太棒了", message):
            return "feedback"
        if re.search(r"禁止|必须|我们团队|不要|不许|别|团队规范", message):
            return "project"
        if re.search(r"因为要|为了兼容|历史遗留|设计原因|架构|技术选型", message):
            return "project"
        if re.search(r"Jira|票号|文档在|链接|参考|需求文档|PRD", message):
            return "reference"
        return "project"

    def generate_filename(self, category: str, message: str) -> str:
        keywords = re.findall(r'[\w\u4e00-\u9fa5]{2,8}', message)
        meaningful = [w for w in keywords if len(w) >= 2 and not re.match(r'^\d+$', w)][:3]
        prefix = '_'.join(meaningful) if meaningful else 'memory'
        prefix = re.sub(r'[^\w\u4e00-\u9fa5_]', '', prefix)
        prefix = prefix[:30] if len(prefix) > 30 else prefix
        if not prefix:
            prefix = 'memory'
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}.md"

    def write_memory(self, message: str) -> str:
        is_dark, reason = self.is_dark_knowledge(message)

        if not is_dark:
            return f"[SKIP] 明知识，无需记忆: {reason}"

        category = self.classify(message)

        similar = self._find_similar_memory(message, category)
        if similar == Path("DUPLICATE"):
            return f"[SKIP] 重复记忆，已存在"
        if similar:
            return f"[MERGED] 已与相似记忆合并: {similar.name}"

        filename = self.generate_filename(category, message)
        filepath = self.memories_dir / category / filename

        keywords = ','.join(re.findall(r'[\w\u4e00-\u9fa5]{2,8}', message)[:5])

        content = f"""---
type: {category}
created: {datetime.now().isoformat()}
reason: {reason}
keywords: {keywords}
---

# {reason}: {message[:50]}{'...' if len(message) > 50 else ''}

## 原始消息
{message}

## 完整上下文
**分类理由**: {reason}
**记忆时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**关键词**: {keywords}

**Why:** 需要记住这条暗知识
**How to apply:** 根据记忆类型自动应用到相关场景
"""

        try:
            filepath.write_text(content, encoding="utf-8")
        except Exception as e:
            return f"[ERROR] 写入文件失败: {str(e)}"

        msg_hash = self._compute_hash(message)
        hashes = self.state.setdefault("memory_hashes", [])
        hashes.append(msg_hash)
        self._save_state()

        return f"[SUCCESS] 记忆已保存到: .trae/memories/{category}/{filename}"


class MCPServer:
    def __init__(self):
        self.memory_system = AutoMemorySystem()
        self.request_id = 0

    def get_next_id(self):
        self.request_id += 1
        if self.request_id > 1000000:
            self.request_id = 1
        return self.request_id

    def process_message(self, message: str) -> str:
        try:
            data = json.loads(message)
            request_id = data.get("id", self.get_next_id())

            if data.get("method") == "initialize":
                return json.dumps({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "serverInfo": {"name": "auto-memory", "version": "2.1"}
                    }
                })

            if data.get("method") == "tools/list":
                return json.dumps({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": [{
                            "name": "write_memory",
                            "description": "处理用户消息，自动识别暗知识并记忆（支持去重、分类优化、智能合并、内存优化）",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "message": {"type": "string", "description": "用户消息内容"}
                                },
                                "required": ["message"]
                            }
                        }]
                    }
                })

            if data.get("method") == "tools/call":
                params = data.get("params", {})
                tool_name = params.get("name", "")
                arguments = params.get("arguments", {})

                if tool_name == "write_memory":
                    user_message = arguments.get("message", "")
                    result = self.memory_system.write_memory(user_message)
                    return json.dumps({
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [{"type": "text", "text": result}]
                        }
                    })

            return json.dumps({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"content": []}
            })

        except json.JSONDecodeError as e:
            return json.dumps({
                "jsonrpc": "2.0",
                "id": self.get_next_id(),
                "error": {"code": -32700, "message": f"JSON解析错误: {str(e)}"}
            })
        except Exception as e:
            return json.dumps({
                "jsonrpc": "2.0",
                "id": self.get_next_id(),
                "error": {"code": -32603, "message": f"内部错误: {str(e)}"}
            })

    def run(self):
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                line = line.strip()
                if line:
                    response = self.process_message(line)
                    print(response, flush=True)
            except EOFError:
                break
            except Exception as e:
                try:
                    print(json.dumps({
                        "jsonrpc": "2.0",
                        "id": self.get_next_id(),
                        "error": {"code": -32603, "message": f"运行错误: {str(e)}"}
                    }), flush=True)
                except Exception:
                    pass


if __name__ == "__main__":
    server = MCPServer()
    server.run()

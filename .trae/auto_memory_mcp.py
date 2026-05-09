#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trae IDE 自动记忆 MCP 服务器
使用标准库实现，无需外部依赖
"""

import os
import re
import json
import socket
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

class AutoMemorySystem:
    def __init__(self):
        self.memories_dir = Path(".trae") / "memories"
        for dir_name in ["user", "feedback", "project", "reference"]:
            (self.memories_dir / dir_name).mkdir(parents=True, exist_ok=True)
    
    def is_dark_knowledge(self, message: str) -> tuple[bool, str]:
        bright_patterns = [
            r"\b(React|Vue|Node|Python|Java|Go|Rust)\s+\d+\.\d+(\.\d+)?\b",
            r"\b(在|位于|路径|文件)\s*[\w./\\-]+\.(js|ts|py|md|json)\b",
            r"\b(def|function|class)\s+[\w_]+\b",
        ]
        for pattern in bright_patterns:
            if re.search(pattern, message):
                return False, "明知识"
        
        dark_patterns = [
            (r"我习惯|我喜欢|我不喜欢|我是\w+工程师|我主要用", "用户偏好"),
            (r"很好|认可|以后都这样|建议|改进", "用户反馈"),
            (r"禁止|必须|我们团队", "团队规则"),
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
        if re.search(r"禁止|必须|我们团队|因为要|为了兼容|历史遗留|设计原因|这是\w+系统|项目启动|项目背景", message):
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

memory_system = AutoMemorySystem()

class MemoryHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            
            data = json.loads(body)
            message = data.get('message', '')
            
            result = memory_system.process(message)
            
            response = json.dumps(result, ensure_ascii=False)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(response.encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            error_response = json.dumps({"error": str(e)}, ensure_ascii=False)
            self.wfile.write(error_response.encode('utf-8'))
    
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "service": "auto-memory-mcp"}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def run_server(port=8000):
    server_address = ('127.0.0.1', port)
    httpd = HTTPServer(server_address, MemoryHandler)
    print(f"🚀 自动记忆MCP服务器启动，端口: {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()

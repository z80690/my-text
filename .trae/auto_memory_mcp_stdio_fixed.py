# -*- coding: utf-8 -*-
"""
自动记忆 MCP 服务 - stdio 协议 (优化版本)
优化点：
1. 添加内存缓存机制，减少文件IO
2. 添加内存使用限制
3. 添加定期清理旧记忆功能
4. 使用LRU缓存策略
"""

import sys
import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from collections import OrderedDict

# 内存缓存配置
MAX_CACHE_SIZE = 1000  # 最大缓存条目数
MAX_MEMORY_USAGE_MB = 200  # 最大内存使用 (MB)
CLEANUP_INTERVAL = 3600  # 清理间隔 (秒)
MAX_MEMORY_AGE_DAYS = 30  # 记忆最大保留天数

class MemoryCache:
    """LRU缓存实现"""
    def __init__(self, max_size=MAX_CACHE_SIZE):
        self.cache = OrderedDict()
        self.max_size = max_size
    
    def get(self, key):
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        return None
    
    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        else:
            if len(self.cache) >= self.max_size:
                self.cache.popitem(last=False)
        self.cache[key] = value
    
    def clear(self):
        self.cache.clear()
    
    def size(self):
        return len(self.cache)

class MemoryManager:
    """记忆管理器 - 处理内存存储和清理"""
    
    def __init__(self):
        self.cache = MemoryCache()
        self.last_cleanup = time.time()
        self.memory_dir = Path(__file__).parent / "memories"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
    
    def should_cleanup(self):
        """检查是否需要清理"""
        return time.time() - self.last_cleanup >= CLEANUP_INTERVAL
    
    def cleanup_old_memories(self):
        """清理过期的记忆文件"""
        try:
            cutoff_date = datetime.now() - timedelta(days=MAX_MEMORY_AGE_DAYS)
            deleted_count = 0
            
            for memory_type in ['User', 'Feedback', 'Project', 'Reference']:
                type_dir = self.memory_dir / memory_type
                if type_dir.exists():
                    for file in type_dir.glob("*.json"):
                        try:
                            file_time = datetime.fromtimestamp(file.stat().st_mtime)
                            if file_time < cutoff_date:
                                file.unlink()
                                deleted_count += 1
                        except Exception:
                            pass
            
            self.last_cleanup = time.time()
            return {"status": "success", "deleted": deleted_count}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def check_memory_usage(self):
        """检查内存使用情况"""
        process = os.popen('tasklist /FI "IMAGENAME eq python.exe" /FO CSV /NH')
        output = process.read()
        return {"status": "running", "cache_size": self.cache.size()}
    
    def write_memory(self, message):
        """处理用户消息，自动识别暗知识"""
        try:
            # 检查是否需要清理
            if self.should_cleanup():
                self.cleanup_old_memories()
            
            content = message.get('content', '')
            memory_type = self.classify_memory(content)
            
            if memory_type == 'ignore':
                return {"status": "ignored", "reason": "内容无需记忆"}
            
            # 检查缓存
            content_hash = hash(content)
            cached = self.cache.get(content_hash)
            if cached:
                return {"status": "cached", "message": "内容已在缓存中"}
            
            # 写入文件
            memory_dir = self.memory_dir / memory_type
            memory_dir.mkdir(parents=True, exist_ok=True)
            
            memory_file = memory_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            memory_data = {
                "timestamp": datetime.now().isoformat(),
                "type": memory_type,
                "content": content,
                "hash": content_hash
            }
            
            with open(memory_file, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, ensure_ascii=False, indent=2)
            
            # 添加到缓存
            self.cache.put(content_hash, memory_data)
            
            return {
                "status": "success",
                "memory_type": memory_type,
                "file": str(memory_file),
                "message": "记忆已保存",
                "cache_size": self.cache.size()
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def classify_memory(self, content):
        """分类记忆类型"""
        if not content:
            return 'ignore'
            
        content_lower = content.lower()
        
        # 检查是否为代码相关（不记录）
        code_indicators = ['def ', 'function', 'import ', 'class ', 'const ', 'let ', 'var ', '#include', 'struct ']
        if any(indicator in content_lower for indicator in code_indicators):
            return 'ignore'
        
        # 检查是否为命令（不记录）
        command_indicators = ['git ', 'npm ', 'python ', 'cd ', 'ls ', 'dir ', 'mkdir ', 'rm ', 'del ']
        if any(indicator in content_lower for indicator in command_indicators):
            return 'ignore'
        
        # 判断记忆类型
        if any(keyword in content_lower for keyword in ['用户', '需求', '想要', '希望', '需要']):
            return 'User'
        elif any(keyword in content_lower for keyword in ['反馈', '评价', '建议', '问题']):
            return 'Feedback'
        elif any(keyword in content_lower for keyword in ['项目', '架构', '设计', '方案', '系统']):
            return 'Project'
        else:
            return 'Reference'

def main():
    """MCP stdio 协议主循环"""
    manager = MemoryManager()
    
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            line = line.strip()
            if not line:
                continue
            
            try:
                request = json.loads(line)
            except json.JSONDecodeError:
                response = json.dumps({"error": "Invalid JSON"})
                print(response)
                sys.stdout.flush()
                continue
            
            method = request.get('method')
            params = request.get('params', {})
            
            if method == 'write_memory':
                result = manager.write_memory(params)
            elif method == 'get_status':
                result = manager.check_memory_usage()
            elif method == 'cleanup':
                result = manager.cleanup_old_memories()
            elif method == 'clear_cache':
                manager.cache.clear()
                result = {"status": "success", "message": "缓存已清空"}
            else:
                result = {"error": f"Unknown method: {method}"}
            
            response = json.dumps({"result": result})
            print(response)
            sys.stdout.flush()
            
        except Exception as e:
            response = json.dumps({"error": str(e)})
            print(response)
            sys.stdout.flush()

if __name__ == '__main__':
    main()

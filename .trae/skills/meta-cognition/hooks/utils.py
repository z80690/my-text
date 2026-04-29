# -*- coding: utf-8 -*-
"""
Meta-Cognition 公共工具模块

提供日志读写、时间计算、敏感信息过滤等公共功能
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


LOG_FILE = Path(__file__).parent.parent / "logs" / "meta_cognition.json"


def load_log() -> Dict[str, Any]:
    """加载现有日志，若不存在则创建空结构"""
    try:
        if LOG_FILE.exists():
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError, ValueError) as e:
        print(f"[WARNING] 加载日志失败: {e}")
    return {"sessions": [], "current_session": None, "statistics": {}}


def save_log(data: Dict[str, Any]) -> bool:
    """保存日志到文件"""
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except (IOError, TypeError, ValueError) as e:
        print(f"[ERROR] 保存日志失败: {e}")
        return False


def generate_session_id() -> str:
    """生成唯一的会话ID"""
    return str(uuid.uuid4())


def get_current_timestamp() -> str:
    """获取当前时间戳（ISO格式）"""
    return datetime.now().isoformat()


def calculate_duration_ms(start_time: Optional[str] = None, end_time: Optional[str] = None) -> int:
    """计算执行耗时（毫秒）"""
    if not start_time:
        return 0
    try:
        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time) if end_time else datetime.now()
        return int((end - start).total_seconds() * 1000)
    except (ValueError, TypeError):
        return 0


import re

# 预编译正则表达式以提高性能
SENSITIVE_PATTERNS = [
    (re.compile(r'api[_-]?key["\']?\s*[:=]\s*["\']?[\w\-]{20,}["\']?', re.IGNORECASE), '[API_KEY]'),
    (re.compile(r'password["\']?\s*[:=]\s*["\']?[^\s"\']{6,}["\']?', re.IGNORECASE), '[PASSWORD]'),
    (re.compile(r'token["\']?\s*[:=]\s*["\']?[\w\-]{20,}["\']?', re.IGNORECASE), '[TOKEN]'),
    (re.compile(r'secret["\']?\s*[:=]\s*["\']?[\w\-]{20,}["\']?', re.IGNORECASE), '[SECRET]'),
]

def filter_sensitive_info(text: Optional[str], patterns: Optional[list] = None) -> str:
    """过滤敏感信息"""
    if not text:
        return ""
    filtered = text
    for pattern, replacement in (patterns or SENSITIVE_PATTERNS):
        filtered = pattern.sub(replacement, filtered)
    return filtered


def truncate_text(text: Optional[str], max_length: int = 200) -> str:
    """截断文本到指定长度"""
    if not text:
        return ""
    return text[:max_length] + "..." if len(text) > max_length else text


def get_file_age_days(file_path: Path) -> Optional[int]:
    """获取文件年龄（天）"""
    if not file_path.exists():
        return None
    try:
        modified_time = datetime.fromtimestamp(file_path.stat().st_mtime)
        return (datetime.now() - modified_time).days
    except (OSError, ValueError):
        return None


def rotate_log_if_needed(max_size_mb: float = 10.0, max_age_days: int = 30) -> bool:
    """检查日志文件是否需要轮转"""
    if not LOG_FILE.exists():
        return False

    try:
        file_size_mb = LOG_FILE.stat().st_size / (1024 * 1024)
        if file_size_mb > max_size_mb:
            return True

        age_days = get_file_age_days(LOG_FILE)
        if age_days is not None and age_days > max_age_days:
            return True
    except (OSError, ValueError):
        pass
    return False


def backup_log() -> Optional[str]:
    """备份日志文件"""
    if not LOG_FILE.exists():
        return None
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = LOG_FILE.parent / f"meta_cognition_backup_{timestamp}.json"
        with open(LOG_FILE, "r", encoding="utf-8") as src:
            with open(backup_path, "w", encoding="utf-8") as dst:
                dst.write(src.read())
        return str(backup_path)
    except IOError:
        return None

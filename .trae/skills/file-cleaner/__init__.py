# -*- coding: utf-8 -*-
"""
File Cleaner Skill - 文件清理技能（增强版）
用于扫描和清理项目中的垃圾文件，支持全自动智能清理
"""

from .file_cleaner import (
    __version__,
    FileCleaner,
    CleanupConfig,
    FileInfo,
    ScanResult,
    CleanupResult,
    scan,
    clean,
    get_report,
    auto_clean,
    create_cleaner_with_protection,
    DEFAULT_PATTERNS
)

__all__ = [
    "__version__",
    "FileCleaner",
    "CleanupConfig",
    "FileInfo",
    "ScanResult",
    "CleanupResult",
    "scan",
    "clean",
    "get_report",
    "auto_clean",
    "create_cleaner_with_protection",
    "DEFAULT_PATTERNS"
]

# -*- coding: utf-8 -*-
"""
File Cleaner Skill - 文件清理技能
用于扫描和清理项目中的垃圾文件
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
    "DEFAULT_PATTERNS"
]

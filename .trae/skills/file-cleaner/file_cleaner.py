# -*- coding: utf-8 -*-
"""
File Cleaner Skill - 文件清理技能
用于扫描和清理项目中的垃圾文件
"""

import os
import shutil
import fnmatch
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

__version__ = "1.0.0"

# 默认清理模式
DEFAULT_PATTERNS = {
    "logs": [
        "*.log",
        "*.log.*",
        "*.txt",
        "*.out",
        "*.err",
        "logs/",
        "log/",
    ],
    "python": [
        "*.pyc",
        "__pycache__/",
        ".pytest_cache/",
        ".tox/",
        "*.egg-info/",
        ".eggs/",
    ],
    "node": [
        "node_modules/",  # 谨慎使用！
        "package-lock.json",
        "yarn.lock",
    ],
    "build": [
        "dist/",
        "build/",
        "out/",
        "*.dist-info/",
    ],
    "temp": [
        "*.tmp",
        "*.temp",
        "*.bak",
        "*.backup",
        "Thumbs.db",
        ".DS_Store",
    ],
    "ide": [
        ".idea/",
        ".vscode/",
        "*.swp",
        "*.swo",
        "*~",
    ],
    "version_control": [
        ".git/",  # 谨慎使用！
        ".svn/",
        ".hg/",
    ],
}


@dataclass
class CleanupConfig:
    """清理配置"""
    patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    max_file_size_mb: Optional[float] = None
    dry_run: bool = True
    verbose: bool = True
    protect_important: bool = True
    important_dirs: List[str] = field(default_factory=lambda: [
        ".git", "node_modules", ".venv", "venv", "__pycache__"
    ])


@dataclass
class FileInfo:
    """文件信息"""
    path: str
    size: int
    type: str  # 'file' or 'dir'
    age_days: Optional[int] = None


@dataclass
class ScanResult:
    """扫描结果"""
    files_found: List[FileInfo]
    total_size: int
    total_count: int
    directories_found: List[FileInfo]
    dir_count: int


@dataclass
class CleanupResult:
    """清理结果"""
    success: bool
    files_deleted: int
    dirs_deleted: int
    bytes_freed: int
    errors: List[str]
    dry_run: bool
    deleted_items: List[str]


class FileCleaner:
    """文件清理器"""
    
    def __init__(self, config: Optional[CleanupConfig] = None):
        self._config = config or CleanupConfig()
        print(f"[FileCleaner] v{__version__} 初始化完成")
    
    def scan(self, directory: str, patterns: Optional[List[str]] = None) -> ScanResult:
        """扫描目录中的垃圾文件"""
        directory = os.path.abspath(directory)
        all_patterns = patterns if patterns else self._get_default_patterns()
        
        files_found = []
        dirs_found = []
        total_size = 0
        
        for root, dirs, files in os.walk(directory):
            # 过滤保护目录
            if self._config.protect_important:
                dirs[:] = [d for d in dirs if d not in self._config.important_dirs]
            
            # 检查目录是否匹配模式
            rel_root = os.path.relpath(root, directory)
            if rel_root != '.':
                for pattern in all_patterns:
                    if self._matches_pattern(rel_root, pattern):
                        dir_size = self._get_dir_size(root)
                        dirs_found.append(FileInfo(
                            path=root,
                            size=dir_size,
                            type='dir',
                            age_days=self._get_file_age_days(root)
                        ))
                        total_size += dir_size
                        dirs[:] = []  # 不再递归
                        break
            
            # 检查文件
            for filename in files:
                filepath = os.path.join(root, filename)
                for pattern in all_patterns:
                    if self._matches_pattern(filename, pattern):
                        try:
                            file_size = os.path.getsize(filepath)
                            # 检查文件大小限制
                            if self._config.max_file_size_mb and \
                               file_size > self._config.max_file_size_mb * 1024 * 1024:
                                continue
                            
                            files_found.append(FileInfo(
                                path=filepath,
                                size=file_size,
                                type='file',
                                age_days=self._get_file_age_days(filepath)
                            ))
                            total_size += file_size
                        except (OSError, PermissionError):
                            continue
                        break
        
        return ScanResult(
            files_found=files_found,
            total_size=total_size,
            total_count=len(files_found),
            directories_found=dirs_found,
            dir_count=len(dirs_found)
        )
    
    def clean(self, directory: str, patterns: Optional[List[str]] = None, 
              dry_run: Optional[bool] = None) -> CleanupResult:
        """清理目录中的垃圾文件"""
        directory = os.path.abspath(directory)
        dry_run = dry_run if dry_run is not None else self._config.dry_run
        
        scan_result = self.scan(directory, patterns)
        errors = []
        deleted_items = []
        files_deleted = 0
        dirs_deleted = 0
        bytes_freed = 0
        
        if dry_run:
            return CleanupResult(
                success=True,
                files_deleted=0,
                dirs_deleted=0,
                bytes_freed=0,
                errors=[],
                dry_run=True,
                deleted_items=[f.path for f in scan_result.files_found] + 
                             [d.path for d in scan_result.directories_found]
            )
        
        # 删除文件
        for file_info in scan_result.files_found:
            try:
                os.remove(file_info.path)
                files_deleted += 1
                bytes_freed += file_info.size
                deleted_items.append(file_info.path)
                if self._config.verbose:
                    print(f"[FileCleaner] 删除文件: {file_info.path}")
            except (OSError, PermissionError) as e:
                errors.append(f"无法删除文件 {file_info.path}: {str(e)}")
        
        # 删除目录（逆序删除，先删除子目录）
        for dir_info in reversed(scan_result.directories_found):
            try:
                shutil.rmtree(dir_info.path)
                dirs_deleted += 1
                bytes_freed += dir_info.size
                deleted_items.append(dir_info.path)
                if self._config.verbose:
                    print(f"[FileCleaner] 删除目录: {dir_info.path}")
            except (OSError, PermissionError) as e:
                errors.append(f"无法删除目录 {dir_info.path}: {str(e)}")
        
        return CleanupResult(
            success=len(errors) == 0,
            files_deleted=files_deleted,
            dirs_deleted=dirs_deleted,
            bytes_freed=bytes_freed,
            errors=errors,
            dry_run=dry_run,
            deleted_items=deleted_items
        )
    
    def get_cleanup_report(self, directory: str, patterns: Optional[List[str]] = None) -> Dict[str, Any]:
        """获取清理报告"""
        scan_result = self.scan(directory, patterns)
        
        return {
            "directory": directory,
            "timestamp": datetime.now().isoformat(),
            "total_files": scan_result.total_count,
            "total_dirs": scan_result.dir_count,
            "total_size_bytes": scan_result.total_size,
            "total_size_human": self._format_size(scan_result.total_size),
            "files": [
                {
                    "path": f.path,
                    "size": f.size,
                    "size_human": self._format_size(f.size),
                    "type": f.type,
                    "age_days": f.age_days
                } for f in scan_result.files_found
            ],
            "directories": [
                {
                    "path": d.path,
                    "size": d.size,
                    "size_human": self._format_size(d.size),
                    "age_days": d.age_days
                } for d in scan_result.directories_found
            ]
        }
    
    def _get_default_patterns(self) -> List[str]:
        """获取默认清理模式"""
        patterns = []
        # 不包含危险的模式（node_modules, .git等）
        for category, items in DEFAULT_PATTERNS.items():
            if category not in ['node', 'version_control']:
                patterns.extend(items)
        return patterns
    
    def _matches_pattern(self, name: str, pattern: str) -> bool:
        """检查名称是否匹配模式"""
        # 处理目录模式（以/结尾）
        if pattern.endswith('/'):
            pattern = pattern[:-1]
            return fnmatch.fnmatch(name, pattern)
        return fnmatch.fnmatch(name, pattern)
    
    def _get_dir_size(self, dir_path: str) -> int:
        """计算目录大小"""
        total_size = 0
        try:
            for root, dirs, files in os.walk(dir_path):
                for f in files:
                    fp = os.path.join(root, f)
                    total_size += os.path.getsize(fp)
        except (OSError, PermissionError):
            pass
        return total_size
    
    def _get_file_age_days(self, filepath: str) -> Optional[int]:
        """获取文件年龄（天数）"""
        try:
            mtime = os.path.getmtime(filepath)
            age_seconds = datetime.now().timestamp() - mtime
            return int(age_seconds // (24 * 3600))
        except (OSError, PermissionError):
            return None
    
    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


# 快捷函数
def scan(directory: str = ".", patterns: Optional[List[str]] = None) -> ScanResult:
    """快捷扫描"""
    cleaner = FileCleaner()
    return cleaner.scan(directory, patterns)


def clean(directory: str = ".", patterns: Optional[List[str]] = None, 
          dry_run: bool = True) -> CleanupResult:
    """快捷清理"""
    cleaner = FileCleaner()
    return cleaner.clean(directory, patterns, dry_run)


def get_report(directory: str = ".", patterns: Optional[List[str]] = None) -> Dict[str, Any]:
    """快捷获取报告"""
    cleaner = FileCleaner()
    return cleaner.get_cleanup_report(directory, patterns)


# 测试
if __name__ == "__main__":
    print(f"[FileCleaner] 测试模式")
    
    # 扫描当前目录
    result = scan(".")
    print(f"\n扫描结果:")
    print(f"  文件数量: {result.total_count}")
    print(f"  目录数量: {result.dir_count}")
    print(f"  总大小: {result.total_size / 1024:.1f} KB")
    
    # 打印找到的文件
    print("\n找到的文件:")
    for f in result.files_found[:10]:
        print(f"  - {f.path} ({f.size} B)")
    
    print("\n找到的目录:")
    for d in result.directories_found[:5]:
        print(f"  - {d.path} ({d.size / 1024:.1f} KB)")

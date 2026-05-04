# -*- coding: utf-8 -*-
"""
File Cleaner Skill - 文件清理技能（增强版）
用于扫描和清理项目中的垃圾文件，支持智能保护机制
"""

import os
import shutil
import fnmatch
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

__version__ = "2.0.0"

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

# 智能保护规则
SAFE_EXTENSIONS = [
    # 配置文件 - 永远不删除
    ".env", ".env.*", ".config", ".conf", ".ini", ".yaml", ".yml", ".json",
    # 源代码文件 - 永远不删除
    ".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".scss", ".md",
    # 数据文件 - 谨慎处理
    ".csv", ".json", ".xml", ".sqlite", ".db",
]

DANGEROUS_PATTERNS = [
    # 高风险目录
    ".git/", ".svn/", ".hg/",
    # 依赖目录
    "node_modules/", ".venv/", "venv/", "env/",
    # 配置目录
    ".trae/", ".idea/", ".vscode/",
]


class ProtectionLevel(Enum):
    """保护级别"""
    NONE = "none"           # 无保护
    LOW = "low"             # 低保护（基本检查）
    MEDIUM = "medium"       # 中等保护（路径检查）
    HIGH = "high"           # 高保护（内容检查）
    CRITICAL = "critical"   # 最高保护（多层验证）


class CleanupStatus(Enum):
    """清理状态"""
    SUCCESS = "success"
    PARTIAL = "partial"
    SKIPPED = "skipped"
    BLOCKED = "blocked"
    ERROR = "error"


@dataclass
class ProtectedPath:
    """受保护路径"""
    path: str
    reason: str
    protection_level: ProtectionLevel


@dataclass
class CleanupConfig:
    """清理配置"""
    patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    max_file_size_mb: Optional[float] = None
    dry_run: bool = True
    verbose: bool = True
    
    # 智能保护配置
    protect_important: bool = True
    important_dirs: List[str] = field(default_factory=lambda: [
        ".git", "node_modules", ".venv", "venv", "__pycache__", ".trae"
    ])
    
    # 用户自定义保护路径
    protected_paths: List[str] = field(default_factory=list)
    
    # 保护级别
    protection_level: ProtectionLevel = ProtectionLevel.HIGH
    
    # 备份配置
    enable_backup: bool = False
    backup_dir: str = ".backup_trash"
    
    # 自动确认阈值（小于此数量自动确认）
    auto_confirm_threshold: int = 10


@dataclass
class FileInfo:
    """文件信息"""
    path: str
    size: int
    type: str  # 'file' or 'dir'
    age_days: Optional[int] = None
    is_protected: bool = False
    protection_reason: str = ""


@dataclass
class ScanResult:
    """扫描结果"""
    files_found: List[FileInfo]
    protected_files: List[FileInfo]
    total_size: int
    total_count: int
    protected_count: int
    directories_found: List[FileInfo]
    protected_dirs: List[FileInfo]
    dir_count: int


@dataclass
class CleanupResult:
    """清理结果"""
    status: CleanupStatus
    files_deleted: int
    files_skipped: int
    dirs_deleted: int
    dirs_skipped: int
    bytes_freed: int
    errors: List[str]
    dry_run: bool
    deleted_items: List[str]
    skipped_items: List[str]
    protected_items: List[str]


class FileCleaner:
    """智能文件清理器"""
    
    def __init__(self, config: Optional[CleanupConfig] = None):
        self._config = config or CleanupConfig()
        # 初始化保护路径
        self._protected_paths = self._initialize_protected_paths()
        print(f"[FileCleaner] v{__version__} 初始化完成")
        print(f"[FileCleaner] 保护级别: {self._config.protection_level.value}")
        print(f"[FileCleaner] 已保护 {len(self._protected_paths)} 个关键路径")
    
    def _initialize_protected_paths(self) -> List[ProtectedPath]:
        """初始化受保护路径"""
        paths = []
        
        # 1. 默认重要目录
        for dir_name in self._config.important_dirs:
            paths.append(ProtectedPath(
                path=dir_name,
                reason=f"默认重要目录",
                protection_level=ProtectionLevel.HIGH
            ))
        
        # 2. 用户自定义保护路径
        for path in self._config.protected_paths:
            paths.append(ProtectedPath(
                path=path,
                reason="用户自定义保护",
                protection_level=ProtectionLevel.CRITICAL
            ))
        
        # 3. 配置文件
        paths.append(ProtectedPath(
            path=".env",
            reason="环境变量配置文件",
            protection_level=ProtectionLevel.CRITICAL
        ))
        
        # 4. 智能体配置目录
        paths.append(ProtectedPath(
            path=".trae/",
            reason="智能体核心配置目录",
            protection_level=ProtectionLevel.CRITICAL
        ))
        
        # 5. Git 版本控制相关文件
        paths.append(ProtectedPath(
            path=".git/",
            reason="Git版本控制目录",
            protection_level=ProtectionLevel.CRITICAL
        ))
        paths.append(ProtectedPath(
            path=".gitignore",
            reason="Git忽略配置文件",
            protection_level=ProtectionLevel.CRITICAL
        ))
        
        return paths
    
    def is_path_protected(self, filepath: str) -> Tuple[bool, str]:
        """检查路径是否受保护"""
        filepath_lower = filepath.lower()
        
        # 检查保护路径列表
        for protected in self._protected_paths:
            protected_path = protected.path.lower()
            # 检查是否匹配
            if protected_path in filepath_lower or filepath_lower.endswith(protected_path):
                return True, protected.reason
        
        # 检查文件扩展名
        if self._config.protection_level in [ProtectionLevel.HIGH, ProtectionLevel.CRITICAL]:
            for ext in SAFE_EXTENSIONS:
                if filepath.endswith(ext):
                    return True, f"安全文件类型 ({ext})"
        
        # 检查危险模式
        if self._config.protection_level in [ProtectionLevel.MEDIUM, ProtectionLevel.HIGH, ProtectionLevel.CRITICAL]:
            for pattern in DANGEROUS_PATTERNS:
                if pattern in filepath:
                    return True, f"危险路径模式 ({pattern})"
        
        # 检查是否为目录中的重要文件
        if self._config.protection_level == ProtectionLevel.CRITICAL:
            # 检查 .trae 目录下的文件
            if ".trae" in filepath:
                return True, ".trae 目录受最高级别保护"
            
            # 检查配置文件
            filename = os.path.basename(filepath)
            config_files = ["agent.md", "config.json", "workflow.json", "skills.json"]
            if filename in config_files:
                return True, f"核心配置文件 ({filename})"
        
        return False, ""
    
    def scan(self, directory: str, patterns: Optional[List[str]] = None) -> ScanResult:
        """智能扫描目录中的垃圾文件（带保护检测）"""
        directory = os.path.abspath(directory)
        all_patterns = patterns if patterns else self._get_default_patterns()
        
        files_found = []
        protected_files = []
        dirs_found = []
        protected_dirs = []
        total_size = 0
        
        for root, dirs, files in os.walk(directory):
            # 智能过滤：跳过受保护的目录
            if self._config.protect_important:
                dirs[:] = self._filter_protected_dirs(directory, root, dirs)
            
            # 检查目录是否匹配模式
            rel_root = os.path.relpath(root, directory)
            if rel_root != '.':
                is_protected, reason = self.is_path_protected(root)
                for pattern in all_patterns:
                    if self._matches_pattern(rel_root, pattern):
                        dir_size = self._get_dir_size(root)
                        if is_protected:
                            protected_dirs.append(FileInfo(
                                path=root,
                                size=dir_size,
                                type='dir',
                                age_days=self._get_file_age_days(root),
                                is_protected=True,
                                protection_reason=reason
                            ))
                        else:
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
                is_protected, reason = self.is_path_protected(filepath)
                
                for pattern in all_patterns:
                    if self._matches_pattern(filename, pattern):
                        try:
                            file_size = os.path.getsize(filepath)
                            # 检查文件大小限制
                            if self._config.max_file_size_mb and \
                               file_size > self._config.max_file_size_mb * 1024 * 1024:
                                continue
                            
                            if is_protected:
                                protected_files.append(FileInfo(
                                    path=filepath,
                                    size=file_size,
                                    type='file',
                                    age_days=self._get_file_age_days(filepath),
                                    is_protected=True,
                                    protection_reason=reason
                                ))
                            else:
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
            protected_files=protected_files,
            total_size=total_size,
            total_count=len(files_found),
            protected_count=len(protected_files),
            directories_found=dirs_found,
            protected_dirs=protected_dirs,
            dir_count=len(dirs_found)
        )
    
    def _filter_protected_dirs(self, base_dir: str, current_root: str, dirs: List[str]) -> List[str]:
        """过滤受保护的目录"""
        filtered = []
        for d in dirs:
            full_path = os.path.join(current_root, d)
            is_protected, _ = self.is_path_protected(full_path)
            if not is_protected:
                filtered.append(d)
            elif self._config.verbose:
                print(f"[FileCleaner] 跳过受保护目录: {full_path}")
        return filtered
    
    def clean(self, directory: str, patterns: Optional[List[str]] = None, 
              dry_run: Optional[bool] = None, confirm_callback=None) -> CleanupResult:
        """智能清理目录中的垃圾文件"""
        directory = os.path.abspath(directory)
        dry_run = dry_run if dry_run is not None else self._config.dry_run
        
        scan_result = self.scan(directory, patterns)
        
        # 如果有受保护的项目，记录警告
        if scan_result.protected_count > 0 or len(scan_result.protected_dirs) > 0:
            print(f"[FileCleaner] 警告: 发现 {scan_result.protected_count} 个受保护文件和 {len(scan_result.protected_dirs)} 个受保护目录")
        
        errors = []
        deleted_items = []
        skipped_items = []
        protected_items = []
        files_deleted = 0
        files_skipped = 0
        dirs_deleted = 0
        dirs_skipped = 0
        bytes_freed = 0
        
        # 预览模式
        if dry_run:
            return CleanupResult(
                status=CleanupStatus.SUCCESS,
                files_deleted=0,
                files_skipped=0,
                dirs_deleted=0,
                dirs_skipped=0,
                bytes_freed=0,
                errors=[],
                dry_run=True,
                deleted_items=[f.path for f in scan_result.files_found] + 
                             [d.path for d in scan_result.directories_found],
                skipped_items=[],
                protected_items=[f.path for f in scan_result.protected_files] + 
                               [d.path for d in scan_result.protected_dirs]
            )
        
        # 真实删除模式
        # 检查是否需要用户确认
        total_to_delete = len(scan_result.files_found) + len(scan_result.directories_found)
        if total_to_delete > self._config.auto_confirm_threshold and confirm_callback:
            confirmed = confirm_callback(total_to_delete)
            if not confirmed:
                return CleanupResult(
                    status=CleanupStatus.BLOCKED,
                    files_deleted=0,
                    files_skipped=0,
                    dirs_deleted=0,
                    dirs_skipped=0,
                    bytes_freed=0,
                    errors=["用户取消操作"],
                    dry_run=False,
                    deleted_items=[],
                    skipped_items=[],
                    protected_items=[]
                )
        
        # 删除文件
        for file_info in scan_result.files_found:
            try:
                # 再次检查保护状态（双重验证）
                is_protected, reason = self.is_path_protected(file_info.path)
                if is_protected:
                    protected_items.append(file_info.path)
                    files_skipped += 1
                    if self._config.verbose:
                        print(f"[FileCleaner] 跳过受保护文件: {file_info.path} ({reason})")
                    continue
                
                # 备份（如果启用）
                if self._config.enable_backup:
                    self._backup_file(file_info.path)
                
                os.remove(file_info.path)
                files_deleted += 1
                bytes_freed += file_info.size
                deleted_items.append(file_info.path)
                if self._config.verbose:
                    print(f"[FileCleaner] 删除文件: {file_info.path}")
            except (OSError, PermissionError) as e:
                errors.append(f"无法删除文件 {file_info.path}: {str(e)}")
                files_skipped += 1
                skipped_items.append(file_info.path)
        
        # 删除目录（逆序删除）
        for dir_info in reversed(scan_result.directories_found):
            try:
                # 再次检查保护状态（双重验证）
                is_protected, reason = self.is_path_protected(dir_info.path)
                if is_protected:
                    protected_items.append(dir_info.path)
                    dirs_skipped += 1
                    if self._config.verbose:
                        print(f"[FileCleaner] 跳过受保护目录: {dir_info.path} ({reason})")
                    continue
                
                # 备份（如果启用）
                if self._config.enable_backup:
                    self._backup_dir(dir_info.path)
                
                shutil.rmtree(dir_info.path)
                dirs_deleted += 1
                bytes_freed += dir_info.size
                deleted_items.append(dir_info.path)
                if self._config.verbose:
                    print(f"[FileCleaner] 删除目录: {dir_info.path}")
            except (OSError, PermissionError) as e:
                errors.append(f"无法删除目录 {dir_info.path}: {str(e)}")
                dirs_skipped += 1
                skipped_items.append(dir_info.path)
        
        # 确定最终状态
        if len(errors) == 0:
            status = CleanupStatus.SUCCESS
        elif files_deleted > 0 or dirs_deleted > 0:
            status = CleanupStatus.PARTIAL
        else:
            status = CleanupStatus.ERROR
        
        return CleanupResult(
            status=status,
            files_deleted=files_deleted,
            files_skipped=files_skipped,
            dirs_deleted=dirs_deleted,
            dirs_skipped=dirs_skipped,
            bytes_freed=bytes_freed,
            errors=errors,
            dry_run=dry_run,
            deleted_items=deleted_items,
            skipped_items=skipped_items,
            protected_items=protected_items
        )
    
    def _backup_file(self, filepath: str):
        """备份文件到回收站"""
        backup_path = os.path.join(self._config.backup_dir, filepath.replace(os.sep, "_"))
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        shutil.copy2(filepath, backup_path)
        if self._config.verbose:
            print(f"[FileCleaner] 备份文件: {filepath} -> {backup_path}")
    
    def _backup_dir(self, dirpath: str):
        """备份目录到回收站"""
        backup_path = os.path.join(self._config.backup_dir, dirpath.replace(os.sep, "_"))
        shutil.copytree(dirpath, backup_path)
        if self._config.verbose:
            print(f"[FileCleaner] 备份目录: {dirpath} -> {backup_path}")
    
    def get_cleanup_report(self, directory: str, patterns: Optional[List[str]] = None) -> Dict[str, Any]:
        """获取详细清理报告"""
        scan_result = self.scan(directory, patterns)
        
        return {
            "directory": directory,
            "timestamp": datetime.now().isoformat(),
            "protection_level": self._config.protection_level.value,
            "summary": {
                "total_files_found": scan_result.total_count,
                "total_dirs_found": scan_result.dir_count,
                "total_size_bytes": scan_result.total_size,
                "total_size_human": self._format_size(scan_result.total_size),
                "protected_files": len(scan_result.protected_files),
                "protected_dirs": len(scan_result.protected_dirs)
            },
            "files_to_delete": [
                {
                    "path": f.path,
                    "size": f.size,
                    "size_human": self._format_size(f.size),
                    "age_days": f.age_days,
                    "is_protected": f.is_protected,
                    "protection_reason": f.protection_reason
                } for f in scan_result.files_found
            ],
            "dirs_to_delete": [
                {
                    "path": d.path,
                    "size": d.size,
                    "size_human": self._format_size(d.size),
                    "age_days": d.age_days,
                    "is_protected": d.is_protected,
                    "protection_reason": d.protection_reason
                } for d in scan_result.directories_found
            ],
            "protected_files": [
                {
                    "path": f.path,
                    "reason": f.protection_reason
                } for f in scan_result.protected_files
            ],
            "protected_dirs": [
                {
                    "path": d.path,
                    "reason": d.protection_reason
                } for d in scan_result.protected_dirs
            ],
            "protected_paths_summary": [
                {"path": p.path, "reason": p.reason, "level": p.protection_level.value}
                for p in self._protected_paths
            ]
        }
    
    def add_protected_path(self, path: str, reason: str = "用户自定义"):
        """添加自定义保护路径"""
        self._protected_paths.append(ProtectedPath(
            path=path,
            reason=reason,
            protection_level=ProtectionLevel.CRITICAL
        ))
        if self._config.verbose:
            print(f"[FileCleaner] 添加保护路径: {path}")
    
    def remove_protected_path(self, path: str):
        """移除保护路径"""
        self._protected_paths = [p for p in self._protected_paths if p.path != path]
        if self._config.verbose:
            print(f"[FileCleaner] 移除保护路径: {path}")
    
    def get_protected_paths(self) -> List[Dict[str, str]]:
        """获取所有保护路径"""
        return [
            {"path": p.path, "reason": p.reason, "level": p.protection_level.value}
            for p in self._protected_paths
        ]
    
    def _get_default_patterns(self) -> List[str]:
        """获取默认清理模式（安全模式）"""
        patterns = []
        # 默认不包含危险的模式
        for category, items in DEFAULT_PATTERNS.items():
            if category not in ['node', 'version_control']:
                patterns.extend(items)
        return patterns
    
    def _matches_pattern(self, name: str, pattern: str) -> bool:
        """检查名称是否匹配模式"""
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
def scan(directory: str = ".", patterns: Optional[List[str]] = None, 
         protected_paths: Optional[List[str]] = None) -> ScanResult:
    """快捷扫描"""
    config = CleanupConfig(protected_paths=protected_paths or [])
    cleaner = FileCleaner(config)
    return cleaner.scan(directory, patterns)


def clean(directory: str = ".", patterns: Optional[List[str]] = None, 
          dry_run: bool = True, protected_paths: Optional[List[str]] = None,
          confirm_callback=None) -> CleanupResult:
    """快捷清理"""
    config = CleanupConfig(
        protected_paths=protected_paths or [],
        protection_level=ProtectionLevel.CRITICAL
    )
    cleaner = FileCleaner(config)
    return cleaner.clean(directory, patterns, dry_run, confirm_callback)


def get_report(directory: str = ".", patterns: Optional[List[str]] = None,
               protected_paths: Optional[List[str]] = None) -> Dict[str, Any]:
    """快捷获取报告"""
    config = CleanupConfig(protected_paths=protected_paths or [])
    cleaner = FileCleaner(config)
    return cleaner.get_cleanup_report(directory, patterns)


def create_cleaner_with_protection(protected_paths: List[str]) -> FileCleaner:
    """创建带有保护路径的清理器"""
    config = CleanupConfig(
        protected_paths=protected_paths,
        protection_level=ProtectionLevel.CRITICAL,
        dry_run=True
    )
    return FileCleaner(config)


# 测试
if __name__ == "__main__":
    print(f"[FileCleaner] v{__version__} 测试模式")
    
    # 定义重点保护路径
    protected = [
        ".trae",
        ".env",
        "新建文件夹",
        "agent.md"
    ]
    
    # 创建清理器
    cleaner = create_cleaner_with_protection(protected)
    
    # 扫描当前目录
    result = cleaner.scan(".")
    print(f"\n=== 扫描结果 ===")
    print(f"  可删除文件: {result.total_count}")
    print(f"  可删除目录: {result.dir_count}")
    print(f"  总大小: {cleaner._format_size(result.total_size)}")
    print(f"  受保护文件: {len(result.protected_files)}")
    print(f"  受保护目录: {len(result.protected_dirs)}")
    
    # 打印找到的文件
    if result.files_found:
        print("\n找到的可删除文件:")
        for f in result.files_found[:10]:
            print(f"  - {f.path} ({cleaner._format_size(f.size)})")
    
    if result.protected_files:
        print("\n受保护的文件:")
        for f in result.protected_files[:5]:
            print(f"  - {f.path} ({f.protection_reason})")
    
    if result.protected_dirs:
        print("\n受保护的目录:")
        for d in result.protected_dirs[:5]:
            print(f"  - {d.path} ({d.protection_reason})")
    
    # 显示保护路径列表
    print("\n=== 保护路径列表 ===")
    for p in cleaner.get_protected_paths():
        print(f"  [{p['level']}] {p['path']} - {p['reason']}")
# -*- coding: utf-8 -*-
"""
File Cleaner Skill - 文件清理技能（Knip增强版）
集成Knip核心功能：未使用文件检测、未使用依赖检测、未使用导出检测
"""

import os
import shutil
import fnmatch
import json
import ast
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

__version__ = "3.0.0"  # Knip增强版

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
        ".venv/",
        "venv/",
        "env/",
        "my_clean_venv/",
    ],
    "node": [
        "node_modules/",
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
    "large_dirs": [
        "pwsh7/",
        "supabase_check/",
        "qgis/",
        "qgis-*",
        "agent-harness/",
    ],
}

# 智能保护规则
SAFE_EXTENSIONS = [
    ".env", ".env.*", ".config", ".conf", ".ini", ".yaml", ".yml", ".json",
    ".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".scss", ".md",
    ".csv", ".xml", ".sqlite", ".db",
]

DANGEROUS_PATTERNS = [
    ".git/", ".svn/", ".hg/",
    "node_modules/", ".venv/", "venv/", "env/",
    ".trae/", ".idea/", ".vscode/",
]


class ProtectionLevel(Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CleanupStatus(Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    SKIPPED = "skipped"
    BLOCKED = "blocked"
    ERROR = "error"


class IssueType(Enum):
    """Knip风格的问题类型"""
    UNUSED_FILE = "unused-file"
    UNUSED_DEPENDENCY = "unused-dependency"
    UNUSED_EXPORT = "unused-export"
    UNUSED_TYPE = "unused-type"
    CIRCULAR_DEPENDENCY = "circular-dependency"
    DUPLICATE_EXPORT = "duplicate-export"


@dataclass
class ProtectedPath:
    path: str
    reason: str
    protection_level: ProtectionLevel


@dataclass
class CleanupConfig:
    patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    max_file_size_mb: Optional[float] = None
    dry_run: bool = True
    verbose: bool = True
    protect_important: bool = True
    important_dirs: List[str] = field(default_factory=lambda: [".git", ".trae"])
    clean_dependencies: bool = True
    protected_paths: List[str] = field(default_factory=list)
    protection_level: ProtectionLevel = ProtectionLevel.HIGH
    enable_backup: bool = False
    backup_dir: str = ".backup_trash"
    auto_confirm_threshold: int = 10
    
    # Knip增强配置
    analyze_unused_files: bool = True
    analyze_unused_dependencies: bool = True
    analyze_unused_exports: bool = True
    entry_patterns: List[str] = field(default_factory=lambda: [
        "src/**/*.{js,ts,jsx,tsx}",
        "*.{js,ts,jsx,tsx}",
        "bin/**/*.{js,ts}",
        "scripts/**/*.{js,ts}"
    ])


@dataclass
class FileInfo:
    path: str
    size: int
    type: str
    age_days: Optional[int] = None
    is_protected: bool = False
    protection_reason: str = ""


@dataclass
class ScanResult:
    files_found: List[FileInfo]
    protected_files: List[FileInfo]
    total_size: int
    total_count: int
    protected_count: int
    directories_found: List[FileInfo]
    protected_dirs: List[FileInfo]
    dir_count: int
    
    # Knip增强字段
    unused_files: List[str] = field(default_factory=list)
    unused_dependencies: List[str] = field(default_factory=list)
    unused_exports: List[Dict[str, Any]] = field(default_factory=list)
    circular_dependencies: List[List[str]] = field(default_factory=list)


@dataclass
class CleanupResult:
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
    
    # Knip增强字段
    unused_files_found: int = 0
    unused_dependencies_found: int = 0
    unused_exports_found: int = 0


class FileCleaner:
    """智能文件清理器（Knip增强版）"""
    
    def __init__(self, config: Optional[CleanupConfig] = None):
        self._config = config or CleanupConfig()
        self._protected_paths = self._initialize_protected_paths()
        # Knip分析缓存
        self._import_graph: Dict[str, Set[str]] = {}  # file -> imports
        self._export_graph: Dict[str, Set[str]] = {}  # file -> exports
        self._reverse_import_graph: Dict[str, Set[str]] = {}  # import -> files_that_import_it
        print(f"[FileCleaner] v{__version__} (Knip增强版) 初始化完成")
        print(f"[FileCleaner] 保护级别: {self._config.protection_level.value}")
        print(f"[FileCleaner] 已保护 {len(self._protected_paths)} 个关键路径")
    
    def _initialize_protected_paths(self) -> List[ProtectedPath]:
        paths = []
        for dir_name in self._config.important_dirs:
            paths.append(ProtectedPath(dir_name, f"默认重要目录", ProtectionLevel.HIGH))
        for path in self._config.protected_paths:
            paths.append(ProtectedPath(path, "用户自定义保护", ProtectionLevel.CRITICAL))
        paths.append(ProtectedPath(".env", "环境变量配置文件", ProtectionLevel.CRITICAL))
        paths.append(ProtectedPath(".trae/", "智能体核心配置目录", ProtectionLevel.CRITICAL))
        paths.append(ProtectedPath(".git/", "Git版本控制目录", ProtectionLevel.CRITICAL))
        paths.append(ProtectedPath(".gitignore", "Git忽略配置文件", ProtectionLevel.CRITICAL))
        return paths
    
    def is_path_protected(self, filepath: str) -> Tuple[bool, str]:
        filepath_lower = filepath.lower()
        for protected in self._protected_paths:
            protected_path = protected.path.lower()
            if protected_path in filepath_lower or filepath_lower.endswith(protected_path):
                return True, protected.reason
        if self._config.protection_level in [ProtectionLevel.HIGH, ProtectionLevel.CRITICAL]:
            for ext in SAFE_EXTENSIONS:
                if filepath.endswith(ext):
                    return True, f"安全文件类型 ({ext})"
        if self._config.protection_level in [ProtectionLevel.MEDIUM, ProtectionLevel.HIGH, ProtectionLevel.CRITICAL]:
            for pattern in DANGEROUS_PATTERNS:
                if self._config.clean_dependencies and pattern in ["node_modules/", ".venv/", "venv/", "env/"]:
                    continue
                if pattern in filepath:
                    return True, f"危险路径模式 ({pattern})"
        if self._config.protection_level == ProtectionLevel.CRITICAL:
            if ".trae" in filepath:
                return True, ".trae 目录受最高级别保护"
            filename = os.path.basename(filepath)
            config_files = ["agent.md", "config.json", "workflow.json", "skills.json"]
            if filename in config_files:
                return True, f"核心配置文件 ({filename})"
        return False, ""
    
    def scan(self, directory: str, patterns: Optional[List[str]] = None) -> ScanResult:
        directory = os.path.abspath(directory)
        all_patterns = patterns if patterns else self._get_default_patterns()
        
        files_found = []
        protected_files = []
        dirs_found = []
        protected_dirs = []
        total_size = 0
        
        for root, dirs, files in os.walk(directory):
            if self._config.protect_important:
                dirs[:] = self._filter_protected_dirs(directory, root, dirs)
            
            rel_root = os.path.relpath(root, directory)
            if rel_root != '.':
                is_protected, reason = self.is_path_protected(root)
                for pattern in all_patterns:
                    if self._matches_pattern(rel_root, pattern):
                        dir_size = self._get_dir_size(root)
                        if is_protected:
                            protected_dirs.append(FileInfo(root, dir_size, 'dir', self._get_file_age_days(root), True, reason))
                        else:
                            dirs_found.append(FileInfo(root, dir_size, 'dir', self._get_file_age_days(root)))
                            total_size += dir_size
                        dirs[:] = []
                        break
            
            for filename in files:
                filepath = os.path.join(root, filename)
                is_protected, reason = self.is_path_protected(filepath)
                
                for pattern in all_patterns:
                    if self._matches_pattern(filename, pattern):
                        try:
                            file_size = os.path.getsize(filepath)
                            if self._config.max_file_size_mb and file_size > self._config.max_file_size_mb * 1024 * 1024:
                                continue
                            
                            if is_protected:
                                protected_files.append(FileInfo(filepath, file_size, 'file', self._get_file_age_days(filepath), True, reason))
                            else:
                                files_found.append(FileInfo(filepath, file_size, 'file', self._get_file_age_days(filepath)))
                                total_size += file_size
                        except (OSError, PermissionError):
                            continue
                        break
        
        # Knip增强：分析未使用的文件、依赖和导出
        unused_files = []
        unused_dependencies = []
        unused_exports = []
        circular_dependencies = []
        
        if self._config.analyze_unused_files:
            unused_files = self._find_unused_files(directory)
        
        if self._config.analyze_unused_dependencies:
            unused_dependencies = self._find_unused_dependencies(directory)
        
        if self._config.analyze_unused_exports:
            unused_exports = self._find_unused_exports(directory)
        
        return ScanResult(
            files_found=files_found,
            protected_files=protected_files,
            total_size=total_size,
            total_count=len(files_found),
            protected_count=len(protected_files),
            directories_found=dirs_found,
            protected_dirs=protected_dirs,
            dir_count=len(dirs_found),
            unused_files=unused_files,
            unused_dependencies=unused_dependencies,
            unused_exports=unused_exports,
            circular_dependencies=circular_dependencies
        )
    
    # ==================== Knip核心功能 ====================
    
    def _build_module_graph(self, directory: str) -> None:
        """构建模块依赖图（Knip风格）"""
        self._import_graph = {}
        self._export_graph = {}
        self._reverse_import_graph = {}
        
        js_ts_files = []
        for root, _, files in os.walk(directory):
            for f in files:
                if f.endswith(('.js', '.ts', '.jsx', '.tsx')):
                    js_ts_files.append(os.path.join(root, f))
        
        for filepath in js_ts_files:
            imports = self._extract_imports(filepath)
            exports = self._extract_exports(filepath)
            
            rel_path = os.path.relpath(filepath, directory)
            self._import_graph[rel_path] = imports
            self._export_graph[rel_path] = exports
            
            for imp in imports:
                if imp not in self._reverse_import_graph:
                    self._reverse_import_graph[imp] = set()
                self._reverse_import_graph[imp].add(rel_path)
    
    def _extract_imports(self, filepath: str) -> Set[str]:
        """提取文件中的导入语句"""
        imports = set()
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if filepath.endswith('.py'):
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.add(alias.name.split('.')[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.add(node.module.split('.')[0])
            else:
                import re
                patterns = [
                    r"import\s+.*from\s+['\"]([^'\"]+)['\"]",
                    r"import\s+(['\"][^'\"]+['\"])",
                    r"require\(['\"]([^'\"]+)['\"]\)"
                ]
                for pattern in patterns:
                    for match in re.findall(pattern, content):
                        if match.startswith('"') or match.startswith("'"):
                            match = match[1:-1]
                        imports.add(match.split('/')[0].split('\\')[0].split('.')[0])
        except Exception:
            pass
        return imports
    
    def _extract_exports(self, filepath: str) -> Set[str]:
        """提取文件中的导出"""
        exports = set()
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if filepath.endswith('.py'):
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                exports.add(target.id)
                    elif isinstance(node, ast.FunctionDef):
                        exports.add(node.name)
                    elif isinstance(node, ast.ClassDef):
                        exports.add(node.name)
            else:
                import re
                patterns = [
                    r"export\s+(?:const|let|var|function|class)\s+(\w+)",
                    r"export\s+\{\s*([^}]+)\s*\}",
                    r"module\.exports\s*=\s*(\w+)",
                    r"exports\.(\w+)\s*="
                ]
                for pattern in patterns:
                    for match in re.findall(pattern, content):
                        if isinstance(match, tuple):
                            for m in match:
                                exports.add(m.strip())
                        else:
                            exports.add(match.strip())
        except Exception:
            pass
        return exports
    
    def _find_unused_files(self, directory: str) -> List[str]:
        """查找未使用的文件（Knip风格）"""
        self._build_module_graph(directory)
        
        entry_files = []
        for pattern in self._config.entry_patterns:
            for filepath in Path(directory).glob(pattern):
                entry_files.append(os.path.relpath(filepath, directory))
        
        used_files = set(entry_files)
        queue = entry_files.copy()
        
        while queue:
            current = queue.pop(0)
            if current in self._import_graph:
                for imp in self._import_graph[current]:
                    found = False
                    for f in self._import_graph:
                        if f.startswith(imp) or imp.split('/')[0] in f.split('/')[0]:
                            if f not in used_files:
                                used_files.add(f)
                                queue.append(f)
                            found = True
                    if not found:
                        for f in self._import_graph:
                            filename = os.path.basename(f).replace('.js', '').replace('.ts', '')
                            if imp == filename and f not in used_files:
                                used_files.add(f)
                                queue.append(f)
        
        all_files = set(self._import_graph.keys())
        unused = [f for f in all_files if f not in used_files]
        return unused
    
    def _find_unused_dependencies(self, directory: str) -> List[str]:
        """查找未使用的依赖（Knip风格）"""
        package_json_path = os.path.join(directory, 'package.json')
        if not os.path.exists(package_json_path):
            return []
        
        try:
            with open(package_json_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
            
            dependencies = set()
            if 'dependencies' in package_data:
                dependencies.update(package_data['dependencies'].keys())
            if 'devDependencies' in package_data:
                dependencies.update(package_data['devDependencies'].keys())
            
            if not self._import_graph:
                self._build_module_graph(directory)
            
            used_deps = set()
            for imports in self._import_graph.values():
                used_deps.update(imports)
            
            unused = [dep for dep in dependencies if dep not in used_deps]
            return unused
        except Exception:
            return []
    
    def _find_unused_exports(self, directory: str) -> List[Dict[str, Any]]:
        """查找未使用的导出（Knip风格）"""
        if not self._import_graph:
            self._build_module_graph(directory)
        
        unused_exports = []
        
        for filepath, exports in self._export_graph.items():
            for exp in exports:
                used = False
                for other_file, imports in self._import_graph.items():
                    if exp in imports or any(exp in imp for imp in imports):
                        used = True
                        break
                if not used:
                    unused_exports.append({
                        'file': filepath,
                        'export': exp,
                        'type': 'export'
                    })
        
        return unused_exports
    
    def _detect_circular_dependencies(self, directory: str) -> List[List[str]]:
        """检测循环依赖（Knip风格）"""
        if not self._import_graph:
            self._build_module_graph(directory)
        
        cycles = []
        visited = set()
        
        def dfs(node, path):
            if node in visited:
                if node in path:
                    idx = path.index(node)
                    cycles.append(path[idx:])
                return
            visited.add(node)
            if node in self._import_graph:
                for imp in self._import_graph[node]:
                    for f in self._import_graph:
                        if f.startswith(imp.split('/')[0]):
                            dfs(f, path + [node])
        
        for node in self._import_graph:
            visited = set()
            dfs(node, [])
        
        unique_cycles = []
        seen = set()
        for cycle in cycles:
            key = tuple(sorted(cycle))
            if key not in seen:
                seen.add(key)
                unique_cycles.append(cycle)
        
        return unique_cycles
    
    # ==================== 原有功能 ====================
    
    def _filter_protected_dirs(self, base_dir: str, current_root: str, dirs: List[str]) -> List[str]:
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
        directory = os.path.abspath(directory)
        dry_run = dry_run if dry_run is not None else self._config.dry_run
        
        scan_result = self.scan(directory, patterns)
        
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
                deleted_items=[f.path for f in scan_result.files_found] + [d.path for d in scan_result.directories_found],
                skipped_items=[],
                protected_items=[f.path for f in scan_result.protected_files] + [d.path for d in scan_result.protected_dirs],
                unused_files_found=len(scan_result.unused_files),
                unused_dependencies_found=len(scan_result.unused_dependencies),
                unused_exports_found=len(scan_result.unused_exports)
            )
        
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
        
        for file_info in scan_result.files_found:
            try:
                is_protected, reason = self.is_path_protected(file_info.path)
                if is_protected:
                    protected_items.append(file_info.path)
                    files_skipped += 1
                    if self._config.verbose:
                        print(f"[FileCleaner] 跳过受保护文件: {file_info.path} ({reason})")
                    continue
                
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
        
        for dir_info in reversed(scan_result.directories_found):
            try:
                is_protected, reason = self.is_path_protected(dir_info.path)
                if is_protected:
                    protected_items.append(dir_info.path)
                    dirs_skipped += 1
                    if self._config.verbose:
                        print(f"[FileCleaner] 跳过受保护目录: {dir_info.path} ({reason})")
                    continue
                
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
            protected_items=protected_items,
            unused_files_found=len(scan_result.unused_files),
            unused_dependencies_found=len(scan_result.unused_dependencies),
            unused_exports_found=len(scan_result.unused_exports)
        )
    
    def _backup_file(self, filepath: str):
        backup_path = os.path.join(self._config.backup_dir, filepath.replace(os.sep, "_"))
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        shutil.copy2(filepath, backup_path)
        if self._config.verbose:
            print(f"[FileCleaner] 备份文件: {filepath} -> {backup_path}")
    
    def _backup_dir(self, dirpath: str):
        backup_path = os.path.join(self._config.backup_dir, dirpath.replace(os.sep, "_"))
        shutil.copytree(dirpath, backup_path)
        if self._config.verbose:
            print(f"[FileCleaner] 备份目录: {dirpath} -> {backup_path}")
    
    def auto_clean(self, directory: str = ".") -> Dict[str, Any]:
        directory = os.path.abspath(directory)
        
        print("="*70)
        print(f"🔮 智能文件清理器 v{__version__} (Knip增强版)")
        print("="*70)
        print(f"📂 目标目录: {directory}")
        print(f"🛡️ 保护级别: {self._config.protection_level.value.upper()}")
        print()
        
        print("🔍 步骤1: 正在扫描垃圾文件...")
        scan_result = self.scan(directory)
        
        print(f"✅ 扫描完成！")
        print(f"   - 可删除文件: {scan_result.total_count} 个")
        print(f"   - 可删除目录: {scan_result.dir_count} 个")
        print(f"   - 总大小: {self._format_size(scan_result.total_size)}")
        print(f"   - 受保护文件: {scan_result.protected_count} 个")
        print(f"   - 受保护目录: {len(scan_result.protected_dirs)} 个")
        
        # Knip分析结果
        if scan_result.unused_files:
            print(f"\n🔍 Knip分析 - 未使用文件: {len(scan_result.unused_files)} 个")
            for f in scan_result.unused_files[:5]:
                print(f"   - {f}")
            if len(scan_result.unused_files) > 5:
                print(f"   - ... 还有 {len(scan_result.unused_files) - 5} 个")
        
        if scan_result.unused_dependencies:
            print(f"\n🔍 Knip分析 - 未使用依赖: {len(scan_result.unused_dependencies)} 个")
            for dep in scan_result.unused_dependencies[:5]:
                print(f"   - {dep}")
            if len(scan_result.unused_dependencies) > 5:
                print(f"   - ... 还有 {len(scan_result.unused_dependencies) - 5} 个")
        
        if scan_result.unused_exports:
            print(f"\n🔍 Knip分析 - 未使用导出: {len(scan_result.unused_exports)} 个")
            for exp in scan_result.unused_exports[:5]:
                print(f"   - {exp['file']}: {exp['export']}")
            if len(scan_result.unused_exports) > 5:
                print(f"   - ... 还有 {len(scan_result.unused_exports) - 5} 个")
        
        if scan_result.total_count == 0 and scan_result.dir_count == 0:
            print("\n🎉 目录已经很干净了！没有需要清理的文件。")
            print("="*70)
            return {
                "status": "clean",
                "message": "目录已经很干净了",
                "details": {
                    "files_deleted": 0,
                    "dirs_deleted": 0,
                    "bytes_freed": 0,
                    "protected_items": len(scan_result.protected_files) + len(scan_result.protected_dirs),
                    "unused_files_found": len(scan_result.unused_files),
                    "unused_dependencies_found": len(scan_result.unused_dependencies),
                    "unused_exports_found": len(scan_result.unused_exports)
                }
            }
        
        print("\n🤖 智能分析:")
        print("   - 受保护项目已自动跳过")
        print("   - 安全文件类型已自动保护")
        
        print("\n🗑️ 步骤2: 开始清理...")
        result = self.clean(directory, dry_run=False)
        
        print("\n📊 清理报告:")
        print(f"   ┌─────────────────────────────────────┐")
        print(f"   │ 状态: {result.status.value}")
        print(f"   │ 删除文件: {result.files_deleted} 个")
        print(f"   │ 删除目录: {result.dirs_deleted} 个")
        print(f"   │ 释放空间: {self._format_size(result.bytes_freed)}")
        print(f"   │ 跳过文件: {result.files_skipped} 个")
        print(f"   │ 跳过目录: {result.dirs_skipped} 个")
        print(f"   └─────────────────────────────────────┘")
        
        if result.protected_items:
            print("\n🛡️ 受保护项目（已跳过）:")
            for item in result.protected_items[:5]:
                print(f"   - {os.path.basename(item)}")
            if len(result.protected_items) > 5:
                print(f"   - ... 还有 {len(result.protected_items) - 5} 个")
        
        if result.errors:
            print("\n⚠️ 警告:")
            for error in result.errors:
                print(f"   - {error}")
        
        print("\n✅ 清理完成！")
        print("="*70)
        
        return {
            "status": result.status.value,
            "message": "清理完成",
            "details": {
                "files_deleted": result.files_deleted,
                "dirs_deleted": result.dirs_deleted,
                "bytes_freed": result.bytes_freed,
                "bytes_freed_human": self._format_size(result.bytes_freed),
                "files_skipped": result.files_skipped,
                "dirs_skipped": result.dirs_skipped,
                "protected_items_count": len(result.protected_items),
                "errors": result.errors,
                "unused_files_found": result.unused_files_found,
                "unused_dependencies_found": result.unused_dependencies_found,
                "unused_exports_found": result.unused_exports_found
            }
        }
    
    def get_cleanup_report(self, directory: str, patterns: Optional[List[str]] = None) -> Dict[str, Any]:
        scan_result = self.scan(directory)
        
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
                "protected_dirs": len(scan_result.protected_dirs),
                "unused_files": len(scan_result.unused_files),
                "unused_dependencies": len(scan_result.unused_dependencies),
                "unused_exports": len(scan_result.unused_exports)
            },
            "files_to_delete": [{"path": f.path, "size": f.size, "size_human": self._format_size(f.size), "age_days": f.age_days, "is_protected": f.is_protected, "protection_reason": f.protection_reason} for f in scan_result.files_found],
            "dirs_to_delete": [{"path": d.path, "size": d.size, "size_human": self._format_size(d.size), "age_days": d.age_days, "is_protected": d.is_protected, "protection_reason": d.protection_reason} for d in scan_result.directories_found],
            "protected_files": [{"path": f.path, "reason": f.protection_reason} for f in scan_result.protected_files],
            "protected_dirs": [{"path": d.path, "reason": d.protection_reason} for d in scan_result.protected_dirs],
            "knip_analysis": {
                "unused_files": scan_result.unused_files,
                "unused_dependencies": scan_result.unused_dependencies,
                "unused_exports": scan_result.unused_exports,
                "circular_dependencies": scan_result.circular_dependencies
            },
            "protected_paths_summary": [{"path": p.path, "reason": p.reason, "level": p.protection_level.value} for p in self._protected_paths]
        }
    
    def add_protected_path(self, path: str, reason: str = "用户自定义"):
        self._protected_paths.append(ProtectedPath(path, reason, ProtectionLevel.CRITICAL))
        if self._config.verbose:
            print(f"[FileCleaner] 添加保护路径: {path}")
    
    def remove_protected_path(self, path: str):
        self._protected_paths = [p for p in self._protected_paths if p.path != path]
        if self._config.verbose:
            print(f"[FileCleaner] 移除保护路径: {path}")
    
    def get_protected_paths(self) -> List[Dict[str, str]]:
        return [{"path": p.path, "reason": p.reason, "level": p.protection_level.value} for p in self._protected_paths]
    
    def _get_default_patterns(self) -> List[str]:
        patterns = []
        for category, items in DEFAULT_PATTERNS.items():
            if category not in ['node', 'version_control']:
                patterns.extend(items)
        return patterns
    
    def _matches_pattern(self, name: str, pattern: str) -> bool:
        if pattern.endswith('/'):
            pattern = pattern[:-1]
            return fnmatch.fnmatch(name, pattern)
        return fnmatch.fnmatch(name, pattern)
    
    def _get_dir_size(self, dir_path: str) -> int:
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
        try:
            mtime = os.path.getmtime(filepath)
            age_seconds = datetime.now().timestamp() - mtime
            return int(age_seconds // (24 * 3600))
        except (OSError, PermissionError):
            return None
    
    def _format_size(self, size_bytes: int) -> str:
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def scan(directory: str = ".", patterns: Optional[List[str]] = None, 
         protected_paths: Optional[List[str]] = None) -> ScanResult:
    config = CleanupConfig(protected_paths=protected_paths or [])
    cleaner = FileCleaner(config)
    return cleaner.scan(directory, patterns)


def clean(directory: str = ".", patterns: Optional[List[str]] = None, 
          dry_run: bool = True, protected_paths: Optional[List[str]] = None,
          confirm_callback=None) -> CleanupResult:
    config = CleanupConfig(
        protected_paths=protected_paths or [],
        protection_level=ProtectionLevel.CRITICAL
    )
    cleaner = FileCleaner(config)
    return cleaner.clean(directory, patterns, dry_run, confirm_callback)


def get_report(directory: str = ".", patterns: Optional[List[str]] = None,
               protected_paths: Optional[List[str]] = None) -> Dict[str, Any]:
    config = CleanupConfig(protected_paths=protected_paths or [])
    cleaner = FileCleaner(config)
    return cleaner.get_cleanup_report(directory, patterns)


def create_cleaner_with_protection(protected_paths: List[str]) -> FileCleaner:
    config = CleanupConfig(
        protected_paths=protected_paths,
        protection_level=ProtectionLevel.CRITICAL,
        dry_run=True
    )
    return FileCleaner(config)


def auto_clean(directory: str = ".", protected_paths: Optional[List[str]] = None,
               clean_dependencies: bool = True, clean_large_dirs: bool = True) -> Dict[str, Any]:
    if protected_paths is None:
        protected_paths = [".trae", ".env", "新建文件夹", "agent.md"]
    
    config = CleanupConfig(
        protected_paths=protected_paths,
        protection_level=ProtectionLevel.CRITICAL,
        dry_run=False,
        clean_dependencies=clean_dependencies
    )
    cleaner = FileCleaner(config)
    return cleaner.auto_clean(directory)


# 测试
if __name__ == "__main__":
    print(f"[FileCleaner] v{__version__} (Knip增强版) 测试模式")
    
    protected = [".trae", ".env", "新建文件夹", "agent.md"]
    cleaner = create_cleaner_with_protection(protected)
    
    result = cleaner.scan(".")
    print(f"\n=== 扫描结果 ===")
    print(f"  可删除文件: {result.total_count}")
    print(f"  可删除目录: {result.dir_count}")
    print(f"  总大小: {cleaner._format_size(result.total_size)}")
    print(f"  受保护文件: {len(result.protected_files)}")
    print(f"  受保护目录: {len(result.protected_dirs)}")
    
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
    
    print("\n=== Knip分析结果 ===")
    print(f"  未使用文件: {len(result.unused_files)}")
    if result.unused_files:
        for f in result.unused_files[:5]:
            print(f"    - {f}")
    
    print(f"  未使用依赖: {len(result.unused_dependencies)}")
    if result.unused_dependencies:
        for dep in result.unused_dependencies[:5]:
            print(f"    - {dep}")
    
    print(f"  未使用导出: {len(result.unused_exports)}")
    if result.unused_exports:
        for exp in result.unused_exports[:5]:
            print(f"    - {exp['file']}: {exp['export']}")
    
    print("\n=== 保护路径列表 ===")
    for p in cleaner.get_protected_paths():
        print(f"  [{p['level']}] {p['path']} - {p['reason']}")
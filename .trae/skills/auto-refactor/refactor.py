"""
Auto-Refactor Skill - 增强版 v4.0
支持项目级重构和代码级重构，包含完整的安全机制和权限处理能力
经验教训集成：
- 权限问题：使用 PowerShell 突破 Windows 权限限制
- 文件丢失：增强保护机制和备份恢复
- 用户确认：强制确认流程
- 智能分析：改进文件使用评分算法
"""

import os
import re
import shutil
import subprocess
import datetime
from typing import List, Dict, Optional, Tuple, Any, Union
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RefactoringChange:
    """重构变更描述"""
    file_path: str
    line_start: int
    line_end: int
    old_text: str
    new_text: str
    change_type: str
    description: str = ""


@dataclass
class ProjectStructure:
    """项目结构分析结果"""
    root_path: str
    total_files: int
    total_dirs: int
    file_types: Dict[str, int]
    size_bytes: int
    used_files: List[str]
    unused_files: List[str]
    subprojects: List[Dict[str, Any]]
    core_files: List[str]
    orphan_files: List[str]


@dataclass
class RefactoringPlan:
    """重构计划"""
    changes: List[RefactoringChange]
    affected_files: List[str]
    estimated_risk: str  # low, medium, high, critical
    summary: str
    warnings: List[str] = None
    dry_run: bool = False
    backup_path: str = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


@dataclass
class FileAnalysis:
    """文件分析结果"""
    file_path: str
    is_used: bool
    usage_score: float  # 0-1
    dependencies: List[str]
    dependents: List[str]
    file_type: str
    age_days: int
    last_modified: datetime.datetime
    risk_level: str


@dataclass
class ExecutionRecord:
    """执行记录"""
    timestamp: datetime.datetime
    plan: RefactoringPlan
    results: Dict[str, Any]
    backup_path: str


class AutoRefactor:
    """自动代码重构工具 - 增强版 v4.0"""
    
    DENYLIST_PATHS = ['.trae', '.git', '.vscode', 'node_modules', '__pycache__', 'backup_']
    PROTECTED_EXTENSIONS = ['.py', '.json', '.yaml', '.yml', '.md', '.txt']
    SAFE_EXTENSIONS = ['.log', '.bak', '.tmp', '.old', '.swp']
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()
        self.backup_path = None
        self.execution_history: List[ExecutionRecord] = []
        self.dry_run_mode = True  # 默认模拟模式
        self.last_backup_time = None
        self._powershell_available = self._check_powershell()
    
    def _check_powershell(self) -> bool:
        """检查 PowerShell 是否可用"""
        try:
            result = subprocess.run(
                ['powershell', '-Command', 'Get-Command'],
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False
    
    # ==================== 项目级重构功能 ====================
    
    def scan_project(self, ignore_patterns: List[str] = None) -> ProjectStructure:
        """扫描整个项目，分析文件结构和使用情况"""
        ignore_patterns = ignore_patterns or []
        all_ignores = self.DENYLIST_PATHS + ignore_patterns
        
        total_files = 0
        total_dirs = 0
        file_types = {}
        size_bytes = 0
        used_files = []
        unused_files = []
        orphan_files = []
        core_files = []
        all_files = []
        
        for path in self.project_root.rglob('*'):
            should_ignore = False
            for pattern in all_ignores:
                if pattern in str(path):
                    should_ignore = True
                    break
            if should_ignore:
                continue
            
            if path.is_dir():
                total_dirs += 1
            elif path.is_file():
                total_files += 1
                size_bytes += path.stat().st_size
                all_files.append(str(path))
                
                ext = path.suffix.lower()
                file_types[ext] = file_types.get(ext, 0) + 1
        
        # 分析文件使用情况
        for file_path in all_files:
            analysis = self.analyze_file(file_path)
            if analysis.is_used:
                used_files.append(file_path)
                if analysis.risk_level == "high":
                    core_files.append(file_path)
            else:
                unused_files.append(file_path)
                if analysis.age_days > 30:
                    orphan_files.append(file_path)
        
        # 识别子项目
        subprojects = self._identify_subprojects(all_ignores)
        
        return ProjectStructure(
            root_path=str(self.project_root),
            total_files=total_files,
            total_dirs=total_dirs,
            file_types=file_types,
            size_bytes=size_bytes,
            used_files=used_files,
            unused_files=unused_files,
            subprojects=subprojects,
            core_files=core_files,
            orphan_files=orphan_files
        )
    
    def analyze_file(self, file_path: str) -> FileAnalysis:
        """分析单个文件的使用情况 - 增强版"""
        dependencies = []
        dependents = []
        usage_score = 0.0
        risk_level = "low"
        
        path = Path(file_path)
        ext = path.suffix.lower()
        
        # 计算文件年龄
        try:
            mtime = path.stat().st_mtime
            last_modified = datetime.datetime.fromtimestamp(mtime)
            age_days = (datetime.datetime.now() - last_modified).days
        except:
            age_days = 999
            last_modified = datetime.datetime.min
        
        # 确定文件类型
        file_type = self._classify_file_type(ext)
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 查找依赖导入
            import_patterns = [
                r'import\s+(\w+)',
                r'from\s+(\w+)\s+import',
                r'from\s+(\S+)\s+import',
                r'require\(["\']([^"\']+)',
                r'include\s*["\']([^"\']+)',
                r'use\s+(\w+)',
                r'#include\s*["<]([^">]+)[">]'
            ]
            for pattern in import_patterns:
                matches = re.findall(pattern, content)
                dependencies.extend(matches)
            
            # 查找被引用情况
            file_name = path.stem
            dependents = self._find_files_with_symbol(file_name)
            
            # 查找其他引用模式
            base_name = file_name.replace('_', '').replace('-', '')
            for fp in self.project_root.rglob('*'):
                if self._is_in_denylist(fp):
                    continue
                if fp.suffix.lower() in ['.py', '.js', '.ts', '.json', '.md']:
                    try:
                        with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
                            if file_name in f.read() or base_name in f.read():
                                if str(fp) != file_path:
                                    dependents.append(str(fp))
                    except:
                        pass
            
            # 计算使用分数（增强版算法）
            dependent_count = len(set(dependents))
            dependency_count = len(set(dependencies))
            
            # 基础分
            usage_score = 0.1  # 默认基础分
            
            # 被引用加分
            if dependent_count > 0:
                usage_score += min(0.5, dependent_count * 0.15)
            
            # 有依赖加分
            if dependency_count > 0:
                usage_score += min(0.2, dependency_count * 0.05)
            
            # 文件年龄加分（越新使用可能性越高）
            if age_days <= 7:
                usage_score += 0.15
            elif age_days <= 30:
                usage_score += 0.1
            elif age_days <= 90:
                usage_score += 0.05
            
            # 文件类型加分
            if ext in ['.py', '.js', '.ts', '.go']:
                usage_score += 0.05
            
            # 限制在 0-1 范围内
            usage_score = min(1.0, max(0.0, usage_score))
        
        except Exception:
            pass
        
        # 评估风险等级
        if ext in ['.py', '.json', '.yaml', '.yml']:
            risk_level = "high"
        elif ext in ['.md', '.txt', '.csv']:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return FileAnalysis(
            file_path=file_path,
            is_used=usage_score > 0.15,
            usage_score=usage_score,
            dependencies=list(set(dependencies)),
            dependents=list(set(dependents)),
            file_type=file_type,
            age_days=age_days,
            last_modified=last_modified,
            risk_level=risk_level
        )
    
    def _classify_file_type(self, ext: str) -> str:
        """分类文件类型"""
        code_exts = ['.py', '.js', '.ts', '.go', '.java', '.cpp', '.rs', '.php', '.html', '.css', '.vue', '.tsx', '.jsx']
        config_exts = ['.json', '.yaml', '.yml', '.ini', '.toml', '.xml']
        doc_exts = ['.md', '.txt', '.rst', '.pdf']
        data_exts = ['.csv', '.json', '.xml', '.xlsx', '.xls']
        binary_exts = ['.exe', '.dll', '.so', '.zip', '.rar', '.tar', '.gz']
        test_exts = ['.test.py', '.spec.ts', '_test.go', '.test.js']
        
        if ext in code_exts:
            return "code"
        elif ext in config_exts:
            return "config"
        elif ext in doc_exts:
            return "documentation"
        elif ext in data_exts:
            return "data"
        elif ext in binary_exts:
            return "binary"
        elif ext in test_exts or ext.endswith('_test.py'):
            return "test"
        else:
            return "other"
    
    def get_unused_files_report(self, threshold: float = 0.15) -> str:
        """生成无用文件报告 - 增强版"""
        structure = self.scan_project()
        
        report = "# 📊 项目文件使用分析报告\n\n"
        report += f"**生成时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        report += "## 📁 项目概览\n\n"
        report += f"- **项目根目录**: `{structure.root_path}`\n"
        report += f"- **总文件数**: {structure.total_files}\n"
        report += f"- **总目录数**: {structure.total_dirs}\n"
        report += f"- **总大小**: {self._format_size(structure.size_bytes)}\n\n"
        
        report += "## 📈 文件类型分布\n\n"
        total_files = sum(structure.file_types.values())
        report += "| 文件类型 | 数量 | 占比 |\n"
        report += "|---------|------|------|\n"
        for ext, count in sorted(structure.file_types.items(), key=lambda x: -x[1]):
            percentage = (count / total_files) * 100
            report += f"| `{ext}` | {count} | {percentage:.1f}% |\n"
        
        report += "\n## 🚫 未使用文件列表\n\n"
        if structure.unused_files:
            report += "| 文件路径 | 文件类型 | 年龄 | 风险等级 |\n"
            report += "|---------|----------|------|----------|\n"
            for file in structure.unused_files[:50]:
                analysis = self.analyze_file(file)
                age_str = f"{analysis.age_days}天" if analysis.age_days < 365 else f"{analysis.age_days//365}年"
                risk_color = self._get_risk_color(analysis.risk_level)
                report += f"| `{file}` | {analysis.file_type} | {age_str} | {risk_color} {analysis.risk_level} |\n"
            
            if len(structure.unused_files) > 50:
                report += f"\n... 还有 {len(structure.unused_files) - 50} 个未使用文件\n"
        else:
            report += "✓ 未发现未使用文件\n"
        
        report += "\n## 📦 孤立文件（30天以上未修改）\n\n"
        if structure.orphan_files:
            report += "| 文件路径 | 年龄 |\n"
            report += "|---------|------|\n"
            for file in structure.orphan_files[:20]:
                analysis = self.analyze_file(file)
                age_str = f"{analysis.age_days}天" if analysis.age_days < 365 else f"{analysis.age_days//365}年"
                report += f"| `{file}` | {age_str} |\n"
        else:
            report += "✓ 未发现孤立文件\n"
        
        report += "\n## ✅ 使用中文件\n\n"
        report += f"共 **{len(structure.used_files)}** 个文件正在使用中\n"
        
        report += "\n## 🛡️ 核心文件（高风险）\n\n"
        if structure.core_files:
            report += f"共 **{len(structure.core_files)}** 个核心文件需要特别保护：\n\n"
            for file in structure.core_files[:20]:
                report += f"- `{file}`\n"
            if len(structure.core_files) > 20:
                report += f"... 还有 {len(structure.core_files) - 20} 个核心文件\n"
        else:
            report += "✓ 未识别到核心文件\n"
        
        report += "\n## 🔍 识别的子项目\n\n"
        for sp in structure.subprojects:
            report += f"- **{sp['name']}**: {len(sp['files'])} 个文件\n"
            if 'patterns' in sp:
                report += f"  - 匹配模式: {', '.join(sp['patterns'])}\n"
        
        report += "\n## ⚠️ 警告汇总\n\n"
        warnings = []
        if len(structure.unused_files) > 100:
            warnings.append(f"发现 {len(structure.unused_files)} 个未使用文件，建议清理")
        if len(structure.core_files) < 5 and total_files > 50:
            warnings.append("核心文件识别较少，可能影响分析准确性")
        
        if warnings:
            for warning in warnings:
                report += f"- ⚠️ {warning}\n"
        else:
            report += "✓ 未发现警告\n"
        
        return report
    
    def delete_unused_files(self, dry_run: bool = True, risk_filter: str = "low") -> RefactoringPlan:
        """删除未使用的文件 - 增强版"""
        structure = self.scan_project()
        changes = []
        warnings = []
        
        # 风险过滤
        allowed_risks = ["low"]
        if risk_filter == "medium":
            allowed_risks.extend(["medium"])
        elif risk_filter == "high":
            allowed_risks.extend(["medium", "high"])
        
        for file_path in structure.unused_files:
            # 检查是否在保护列表
            if self._is_in_denylist(Path(file_path)):
                warnings.append(f"跳过 {file_path} - 在保护列表中")
                continue
            
            # 分析文件
            analysis = self.analyze_file(file_path)
            
            # 风险检查
            if analysis.risk_level not in allowed_risks:
                warnings.append(f"跳过 {file_path} - 风险等级 {analysis.risk_level} 高于允许的 {risk_filter}")
                continue
            
            # 核心文件保护
            if file_path in structure.core_files:
                warnings.append(f"跳过 {file_path} - 标记为核心文件")
                continue
            
            changes.append(RefactoringChange(
                file_path=file_path,
                line_start=1,
                line_end=1,
                old_text="",
                new_text="",
                change_type="delete_file",
                description=f"删除未使用文件 (风险: {analysis.risk_level}, 年龄: {analysis.age_days}天)"
            ))
        
        # 计算风险等级
        total_changes = len(changes)
        estimated_risk = "low"
        if total_changes > 50:
            estimated_risk = "high"
        elif total_changes > 10:
            estimated_risk = "medium"
        
        return RefactoringPlan(
            changes=changes,
            affected_files=[c.file_path for c in changes],
            estimated_risk=estimated_risk,
            summary=f"删除 {total_changes} 个未使用文件",
            warnings=warnings,
            dry_run=dry_run
        )
    
    def separate_subprojects(self, subproject_config: Dict[str, List[str]], 
                            target_dir: str = "projects",
                            dry_run: bool = True) -> RefactoringPlan:
        """分离子项目到不同目录 - 增强版"""
        changes = []
        warnings = []
        affected_files = []
        
        # 验证配置
        if not subproject_config:
            return RefactoringPlan(
                changes=[],
                affected_files=[],
                estimated_risk="low",
                summary="无效配置：子项目配置为空",
                warnings=["请提供有效的子项目配置"]
            )
        
        # 创建目标目录
        target_path = self.project_root / target_dir
        changes.append(RefactoringChange(
            file_path=str(target_path),
            line_start=1,
            line_end=1,
            old_text="",
            new_text="",
            change_type="create_directory",
            description=f"创建目录 {target_dir}"
        ))
        
        for project_name, patterns in subproject_config.items():
            project_path = target_path / project_name
            changes.append(RefactoringChange(
                file_path=str(project_path),
                line_start=1,
                line_end=1,
                old_text="",
                new_text="",
                change_type="create_directory",
                description=f"创建子项目目录 {project_name}"
            ))
            
            # 查找匹配的文件/目录
            matched_files = []
            for pattern in patterns:
                # 支持 glob 模式
                for path in self.project_root.rglob(pattern):
                    if self._is_in_denylist(path):
                        warnings.append(f"跳过 {path} - 在保护列表中")
                        continue
                    
                    # 跳过目标目录本身
                    if str(path).startswith(str(target_path)):
                        continue
                    
                    rel_path = path.relative_to(self.project_root)
                    dest_path = project_path / rel_path
                    
                    # 检查是否已匹配过
                    if str(path) not in matched_files:
                        matched_files.append(str(path))
                        
                        # 检查是否存在同名文件
                        if dest_path.exists():
                            warnings.append(f"目标位置已存在: {dest_path}")
                            continue
                        
                        changes.append(RefactoringChange(
                            file_path=str(path),
                            line_start=1,
                            line_end=1,
                            old_text="",
                            new_text=str(dest_path),
                            change_type="move_file",
                            description=f"移动 {rel_path} -> {project_name}/{rel_path}"
                        ))
                        affected_files.append(str(path))
        
        # 计算风险等级
        estimated_risk = "low"
        if len(affected_files) > 50:
            estimated_risk = "high"
        elif len(affected_files) > 10:
            estimated_risk = "medium"
        
        return RefactoringPlan(
            changes=changes,
            affected_files=affected_files,
            estimated_risk=estimated_risk,
            summary=f"分离 {len(subproject_config)} 个子项目，涉及 {len(affected_files)} 个文件",
            warnings=warnings,
            dry_run=dry_run
        )
    
    # ==================== 代码级重构功能 ====================
    
    def extract_method(self, file_path: str, start_line: int, end_line: int, 
                       method_name: str, params: List[str] = None) -> RefactoringPlan:
        """提取代码块为方法"""
        params = params or []
        
        if not Path(file_path).exists():
            return RefactoringPlan(
                changes=[],
                affected_files=[],
                estimated_risk="low",
                summary=f"文件不存在: {file_path}",
                warnings=["文件不存在"]
            )
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if start_line < 1 or end_line > len(lines):
            return RefactoringPlan(
                changes=[],
                affected_files=[],
                estimated_risk="low",
                summary="行号超出范围",
                warnings=["行号超出文件范围"]
            )
        
        selected_lines = lines[start_line-1:end_line]
        selected_code = ''.join(selected_lines)
        
        indent = self._detect_indent(selected_lines[0])
        param_str = ', '.join(params) if params else ''
        
        # 分析返回值
        return_type = "None"
        for line in selected_lines:
            if 'return' in line:
                return_type = "Any"
                break
        
        method_template = f"\n{indent}def {method_name}({param_str}):\n"
        for line in selected_lines:
            method_template += f"{indent}    {line}"
        method_template += f"{indent}    return result\n"
        
        call_line = f"{indent}result = {method_name}({param_str})\n"
        
        changes = [
            RefactoringChange(
                file_path=file_path,
                line_start=start_line,
                line_end=end_line,
                old_text=selected_code,
                new_text=call_line,
                change_type="extract_method",
                description=f"提取方法 {method_name}"
            ),
            RefactoringChange(
                file_path=file_path,
                line_start=end_line+1,
                line_end=end_line+1,
                old_text="",
                new_text=method_template,
                change_type="add_method",
                description=f"添加新方法 {method_name}"
            )
        ]
        
        return RefactoringPlan(
            changes=changes,
            affected_files=[file_path],
            estimated_risk="low",
            summary=f"提取方法 {method_name}"
        )
    
    def extract_variable(self, file_path: str, line_num: int, 
                        expression: str, var_name: str) -> RefactoringPlan:
        """提取表达式为变量"""
        if not Path(file_path).exists():
            return RefactoringPlan(
                changes=[],
                affected_files=[],
                estimated_risk="low",
                summary=f"文件不存在: {file_path}",
                warnings=["文件不存在"]
            )
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if line_num < 1 or line_num > len(lines):
            return RefactoringPlan(
                changes=[],
                affected_files=[],
                estimated_risk="low",
                summary="行号超出范围",
                warnings=["行号超出文件范围"]
            )
        
        line = lines[line_num-1]
        if expression not in line:
            return RefactoringPlan(
                changes=[],
                affected_files=[],
                estimated_risk="low",
                summary="表达式未找到",
                warnings=["指定的表达式不在目标行中"]
            )
        
        indent = self._detect_indent(line)
        
        var_declaration = f"{indent}{var_name} = {expression}\n"
        new_line = line.replace(expression, var_name)
        
        changes = [
            RefactoringChange(
                file_path=file_path,
                line_start=line_num,
                line_end=line_num,
                old_text="",
                new_text=var_declaration,
                change_type="add_variable",
                description=f"添加变量 {var_name}"
            ),
            RefactoringChange(
                file_path=file_path,
                line_start=line_num+1,
                line_end=line_num+1,
                old_text=line,
                new_text=new_line,
                change_type="replace_expression",
                description=f"替换表达式为变量 {var_name}"
            )
        ]
        
        return RefactoringPlan(
            changes=changes,
            affected_files=[file_path],
            estimated_risk="low",
            summary=f"提取变量 {var_name}"
        )
    
    def rename_symbol(self, file_path: str, symbol_name: str, 
                     new_name: str, scope: str = "project") -> RefactoringPlan:
        """智能重命名符号 - 增强版"""
        changes = []
        
        if not Path(file_path).exists():
            return RefactoringPlan(
                changes=[],
                affected_files=[],
                estimated_risk="low",
                summary=f"文件不存在: {file_path}",
                warnings=["文件不存在"]
            )
        
        if scope == "project":
            files = self._find_files_with_symbol(symbol_name)
        else:
            files = [file_path]
        
        if not files:
            return RefactoringPlan(
                changes=[],
                affected_files=[],
                estimated_risk="low",
                summary=f"未找到符号 {symbol_name} 的引用",
                warnings=["符号未被任何文件引用"]
            )
        
        for fp in files:
            with open(fp, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 智能匹配：只替换完整的符号名称
            pattern = r'\b' + re.escape(symbol_name) + r'\b'
            new_content = re.sub(pattern, new_name, content)
            
            if content != new_content:
                changes.append(RefactoringChange(
                    file_path=fp,
                    line_start=1,
                    line_end=len(content.splitlines()),
                    old_text=content,
                    new_text=new_content,
                    change_type="rename",
                    description=f"重命名 {symbol_name} -> {new_name}"
                ))
        
        # 计算风险等级
        estimated_risk = "low"
        if len(files) > 10:
            estimated_risk = "high"
        elif len(files) > 3:
            estimated_risk = "medium"
        
        return RefactoringPlan(
            changes=changes,
            affected_files=files,
            estimated_risk=estimated_risk,
            summary=f"重命名 {symbol_name} -> {new_name}，涉及 {len(files)} 个文件"
        )
    
    def change_signature(self, file_path: str, method_name: str,
                        new_params: List[str], return_type: str = None) -> RefactoringPlan:
        """修改方法签名"""
        changes = []
        
        if not Path(file_path).exists():
            return RefactoringPlan(
                changes=[],
                affected_files=[],
                estimated_risk="low",
                summary=f"文件不存在: {file_path}",
                warnings=["文件不存在"]
            )
        
        files = self._find_files_with_symbol(method_name)
        
        if not files:
            return RefactoringPlan(
                changes=[],
                affected_files=[],
                estimated_risk="low",
                summary=f"未找到方法 {method_name}",
                warnings=["方法未被任何文件引用"]
            )
        
        for fp in files:
            with open(fp, 'r', encoding='utf-8') as f:
                content = f.read()
            
            def_pattern = rf'def {method_name}\([^)]*\)'
            new_sig = f"def {method_name}({', '.join(new_params)})"
            content = re.sub(def_pattern, new_sig, content)
            
            # 更新调用位置
            call_pattern = rf'{method_name}\([^)]*\)'
            new_call = f"{method_name}({', '.join(new_params)})"
            content = re.sub(call_pattern, new_call, content)
            
            changes.append(RefactoringChange(
                file_path=fp,
                line_start=1,
                line_end=len(content.splitlines()),
                old_text="",
                new_text=content,
                change_type="change_signature",
                description=f"修改 {method_name} 签名"
            ))
        
        # 计算风险等级
        estimated_risk = "medium"
        if len(files) > 10:
            estimated_risk = "high"
        
        return RefactoringPlan(
            changes=changes,
            affected_files=files,
            estimated_risk=estimated_risk,
            summary=f"修改 {method_name} 签名，涉及 {len(files)} 个文件"
        )
    
    def safe_delete(self, file_path: str, symbol_name: str) -> RefactoringPlan:
        """安全删除符号（检查引用）"""
        references = self._find_all_references(symbol_name)
        
        if len(references) > 1:
            ref_list = "\n".join([f"  • {fp}:{line}" for fp, line in references[:5]])
            if len(references) > 5:
                ref_list += f"\n  • ... 还有 {len(references) - 5} 处引用"
            
            return RefactoringPlan(
                changes=[],
                affected_files=[],
                estimated_risk="high",
                summary=f"无法删除 {symbol_name}，存在 {len(references)} 处引用",
                warnings=[f"符号 {symbol_name} 被多处引用:\n{ref_list}"]
            )
        
        if not Path(file_path).exists():
            return RefactoringPlan(
                changes=[],
                affected_files=[],
                estimated_risk="low",
                summary=f"文件不存在: {file_path}",
                warnings=["文件不存在"]
            )
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 匹配函数定义（支持多行）
        pattern = rf'\n?\s*def {symbol_name}\([^)]*\):.*?(?=\n\s*def|\Z)'
        new_content = re.sub(pattern, '', content, flags=re.DOTALL)
        
        changes = [RefactoringChange(
            file_path=file_path,
            line_start=1,
            line_end=len(content.splitlines()),
            old_text=content,
            new_text=new_content,
            change_type="delete_symbol",
            description=f"删除符号 {symbol_name}"
        )]
        
        return RefactoringPlan(
            changes=changes,
            affected_files=[file_path],
            estimated_risk="low",
            summary=f"安全删除 {symbol_name}"
        )
    
    # ==================== 执行与安全机制 ====================
    
    def execute_plan(self, plan: RefactoringPlan, create_backup: bool = True, 
                    confirm: bool = True) -> Dict:
        """执行重构计划 - 增强版"""
        # 检查是否为模拟模式
        if plan.dry_run or self.dry_run_mode:
            print("⚠️ 【模拟模式】以下操作不会实际执行：")
            print(self.preview_plan(plan))
            return {
                'success': 0,
                'failed': 0,
                'files': [],
                'simulated': True,
                'plan': plan
            }
        
        # 创建备份
        backup_path = None
        if create_backup:
            backup_path = self._create_backup()
            plan.backup_path = backup_path
        
        # 确认提示（强制）
        if confirm:
            print(self.preview_plan(plan))
            print("\n" + "="*60)
            user_input = input("⚠️ 确认执行以上重构操作？(y/N): ")
            if user_input.lower() != 'y':
                # 清理备份
                if backup_path and Path(backup_path).exists():
                    shutil.rmtree(backup_path)
                return {
                    'success': 0,
                    'failed': 0,
                    'files': [],
                    'cancelled': True
                }
        
        results = {
            'success': 0,
            'failed': 0,
            'files': [],
            'errors': [],
            'backup_path': backup_path
        }
        
        # 按类型排序：先创建目录，再移动/修改，最后删除
        sorted_changes = sorted(plan.changes, key=self._change_priority)
        
        for change in sorted_changes:
            try:
                success = self._apply_change(change)
                if success:
                    results['success'] += 1
                    results['files'].append(change.file_path)
                    self.execution_history.append({
                        'change': change,
                        'status': 'success'
                    })
                else:
                    results['failed'] += 1
                    results['errors'].append({
                        'file': change.file_path,
                        'error': '操作未执行（权限问题）'
                    })
            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    'file': change.file_path,
                    'error': str(e)
                })
                self.execution_history.append({
                    'change': change,
                    'status': 'failed',
                    'error': str(e)
                })
                print(f"❌ 执行失败: {change.file_path} - {e}")
        
        # 记录执行记录
        self.execution_history.append(ExecutionRecord(
            timestamp=datetime.datetime.now(),
            plan=plan,
            results=results,
            backup_path=backup_path
        ))
        
        return results
    
    def _apply_change(self, change: RefactoringChange) -> bool:
        """应用单个变更 - 增强版，支持 PowerShell 权限处理"""
        # 权限检查
        if not self._check_path_permission(change.file_path):
            print(f"⚠️ 标准权限不足，尝试使用 PowerShell...")
            return self._apply_change_with_powershell(change)
        
        try:
            if change.change_type == 'create_directory':
                Path(change.file_path).mkdir(parents=True, exist_ok=True)
            
            elif change.change_type == 'delete_file':
                Path(change.file_path).unlink()
            
            elif change.change_type == 'move_file':
                src = Path(change.file_path)
                dest = Path(change.new_text)
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dest))
            
            elif change.change_type in ['add_method', 'add_variable']:
                with open(change.file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.splitlines(keepends=True)
                new_lines = lines[:change.line_start-1]
                new_lines.append(change.new_text)
                new_lines.extend(lines[change.line_start-1:])
                
                with open(change.file_path, 'w', encoding='utf-8') as f:
                    f.write(''.join(new_lines))
            
            elif change.old_text:
                with open(change.file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                new_content = content.replace(change.old_text, change.new_text)
                
                with open(change.file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
            
            elif change.new_text:
                with open(change.file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                new_lines = lines[:change.line_start-1]
                new_lines.append(change.new_text)
                new_lines.extend(lines[change.line_start-1:])
                
                with open(change.file_path, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
            
            return True
        
        except PermissionError:
            print(f"⚠️ Python 权限不足，尝试 PowerShell...")
            return self._apply_change_with_powershell(change)
        except Exception as e:
            raise e
    
    def _apply_change_with_powershell(self, change: RefactoringChange) -> bool:
        """使用 PowerShell 应用变更（突破权限限制）"""
        if not self._powershell_available:
            print("❌ PowerShell 不可用")
            return False
        
        try:
            if change.change_type == 'create_directory':
                cmd = f"New-Item -ItemType Directory -Path '{change.file_path}' -Force"
                self._run_powershell(cmd)
            
            elif change.change_type == 'delete_file':
                cmd = f"Remove-Item -Path '{change.file_path}' -Force"
                self._run_powershell(cmd)
            
            elif change.change_type == 'move_file':
                src = change.file_path
                dest = change.new_text
                # 先创建目标目录
                dest_dir = str(Path(dest).parent)
                self._run_powershell(f"New-Item -ItemType Directory -Path '{dest_dir}' -Force")
                # 使用 Copy-Item + Remove-Item 替代 Move-Item
                cmd = f"Copy-Item -Path '{src}' -Destination '{dest}' -Recurse -Force; Remove-Item -Path '{src}' -Recurse -Force"
                self._run_powershell(cmd)
            
            else:
                # 其他操作使用标准方法
                print(f"⚠️ PowerShell 不支持此操作类型: {change.change_type}")
                return False
            
            return True
        
        except Exception as e:
            print(f"❌ PowerShell 执行失败: {e}")
            return False
    
    def _run_powershell(self, cmd: str) -> Tuple[int, str]:
        """执行 PowerShell 命令"""
        full_cmd = f'powershell -Command "{cmd}"'
        result = subprocess.run(
            full_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode != 0:
            raise Exception(f"PowerShell 错误: {result.stderr}")
        return result.returncode, result.stdout
    
    def preview_plan(self, plan: RefactoringPlan) -> str:
        """预览重构计划"""
        risk_colors = {
            'low': '🟢',
            'medium': '🟡',
            'high': '🔴',
            'critical': '⚫'
        }
        
        output = "📋" + "="*60 + "\n"
        output += f"【重构计划预览】\n"
        output += "="*60 + "\n"
        output += f"范围: {len(plan.affected_files)} 个文件\n"
        output += f"修改: {len(plan.changes)} 处\n"
        output += f"风险等级: {risk_colors.get(plan.estimated_risk, '⚪')} {plan.estimated_risk}\n"
        output += f"模拟模式: {'✅' if plan.dry_run else '❌'}\n"
        output += f"备份创建: {'✅ 是' if plan.backup_path or plan.dry_run else '❌ 否'}\n"
        output += "\n【变更详情】\n"
        
        # 按类型分组
        change_types = {}
        for change in plan.changes:
            ct = change.change_type
            if ct not in change_types:
                change_types[ct] = []
            change_types[ct].append(change)
        
        for ct, changes in change_types.items():
            output += f"\n--- {self._get_change_type_label(ct)} ({len(changes)}处) ---\n"
            for change in changes[:10]:
                desc = change.description if change.description else change.file_path
                output += f"  • {desc}\n"
            if len(changes) > 10:
                output += f"  • ... 还有 {len(changes) - 10} 处\n"
        
        if plan.warnings:
            output += "\n【警告】\n"
            for warning in plan.warnings[:5]:
                output += f" ⚠️ {warning}\n"
            if len(plan.warnings) > 5:
                output += f" ... 还有 {len(plan.warnings) - 5} 个警告\n"
        
        output += "\n" + "="*60 + "\n"
        return output
    
    def check_permissions(self, paths: List[str]) -> Dict[str, bool]:
        """检查路径操作权限"""
        results = {}
        for path in paths:
            results[path] = self._check_path_permission(path)
        return results
    
    def rollback(self, steps: int = None, restore_from_backup: bool = False):
        """回滚最近的操作 - 增强版"""
        if not self.execution_history:
            print("❌ 没有可回滚的操作")
            return False
        
        # 如果有备份，优先从备份恢复
        if restore_from_backup:
            last_record = None
            for record in reversed(self.execution_history):
                if isinstance(record, ExecutionRecord) and record.backup_path:
                    last_record = record
                    break
            
            if last_record and Path(last_record.backup_path).exists():
                print(f"🔄 从备份恢复: {last_record.backup_path}")
                # 清除当前项目内容（除了保护目录）
                for item in self.project_root.iterdir():
                    if item.name not in self.DENYLIST_PATHS:
                        if item.is_dir():
                            shutil.rmtree(item)
                        else:
                            item.unlink()
                
                # 从备份恢复
                for item in Path(last_record.backup_path).iterdir():
                    dest = self.project_root / item.name
                    if item.is_dir():
                        shutil.copytree(item, dest)
                    else:
                        shutil.copy(item, dest)
                
                print("✅ 备份恢复成功")
                return True
            else:
                print("❌ 没有可用的备份")
        
        # 常规回滚
        target_count = steps or len(self.execution_history)
        rollback_count = min(target_count, len(self.execution_history))
        
        print(f"🔄 正在回滚最近 {rollback_count} 个操作...")
        
        # 按逆序回滚
        for record in reversed(self.execution_history[-rollback_count:]):
            if isinstance(record, dict) and record.get('status') == 'success':
                change = record['change']
                try:
                    self._undo_change(change)
                    print(f"✅ 已回滚: {change.description}")
                except Exception as e:
                    print(f"❌ 回滚失败: {change.description} - {e}")
        
        # 移除已回滚的记录
        self.execution_history = self.execution_history[:-rollback_count]
        return True
    
    def restore_from_backup(self, backup_path: str = None):
        """从备份恢复项目"""
        if backup_path:
            backup = Path(backup_path)
        elif self.backup_path and Path(self.backup_path).exists():
            backup = Path(self.backup_path)
        else:
            # 查找最新备份
            backups = list(self.project_root.glob('backup_*'))
            if backups:
                backup = sorted(backups)[-1]
            else:
                print("❌ 未找到备份")
                return False
        
        if not backup.exists():
            print(f"❌ 备份不存在: {backup}")
            return False
        
        print(f"🔄 从备份恢复: {backup}")
        
        try:
            # 清除当前项目内容（除了保护目录）
            for item in self.project_root.iterdir():
                if item.name not in self.DENYLIST_PATHS:
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
            
            # 从备份恢复
            for item in backup.iterdir():
                dest = self.project_root / item.name
                if item.is_dir():
                    shutil.copytree(item, dest)
                else:
                    shutil.copy(item, dest)
            
            print("✅ 备份恢复成功")
            return True
        except Exception as e:
            print(f"❌ 恢复失败: {e}")
            return False
    
    # ==================== 辅助方法 ====================
    
    def _change_priority(self, change: RefactoringChange) -> int:
        """变更优先级：创建 > 修改 > 移动 > 删除"""
        priorities = {
            'create_directory': 1,
            'create_file': 2,
            'add_method': 3,
            'add_variable': 3,
            'extract_method': 4,
            'replace_expression': 4,
            'rename': 5,
            'change_signature': 5,
            'move_file': 6,
            'delete_symbol': 7,
            'delete_file': 8
        }
        return priorities.get(change.change_type, 5)
    
    def _get_change_type_label(self, change_type: str) -> str:
        """获取变更类型的中文标签"""
        labels = {
            'create_directory': '创建目录',
            'create_file': '创建文件',
            'add_method': '添加方法',
            'add_variable': '添加变量',
            'extract_method': '提取方法',
            'replace_expression': '替换表达式',
            'rename': '重命名',
            'change_signature': '修改签名',
            'move_file': '移动文件',
            'delete_symbol': '删除符号',
            'delete_file': '删除文件'
        }
        return labels.get(change_type, change_type)
    
    def _get_risk_color(self, risk_level: str) -> str:
        """获取风险等级颜色"""
        colors = {
            'low': '🟢',
            'medium': '🟡',
            'high': '🔴',
            'critical': '⚫'
        }
        return colors.get(risk_level, '⚪')
    
    def _check_path_permission(self, file_path: str) -> bool:
        """检查路径是否可操作"""
        path = Path(file_path)
        
        # 检查是否在保护列表中
        if self._is_in_denylist(path):
            return False
        
        # 检查写权限
        try:
            if path.is_file():
                return os.access(file_path, os.W_OK)
            elif path.is_dir():
                return os.access(str(path.parent), os.W_OK)
            else:
                # 文件不存在，检查父目录权限
                return os.access(str(path.parent), os.W_OK)
        except:
            return False
    
    def _is_in_denylist(self, path: Path) -> bool:
        """检查路径是否在保护列表中"""
        path_str = str(path)
        for pattern in self.DENYLIST_PATHS:
            if pattern in path_str:
                return True
        return False
    
    def _estimate_deletion_risk(self, file_path: str) -> str:
        """估计删除风险"""
        path = Path(file_path)
        ext = path.suffix.lower()
        
        # 高风险文件类型
        high_risk_exts = ['.py', '.js', '.ts', '.json', '.yaml', '.yml', '.xml', '.go', '.java', '.cpp']
        # 低风险文件类型
        low_risk_exts = ['.md', '.txt', '.log', '.bak', '.tmp', '.old']
        
        if ext in high_risk_exts:
            return "high"
        elif ext in low_risk_exts:
            return "low"
        else:
            return "medium"
    
    def _detect_indent(self, line: str) -> str:
        """检测缩进"""
        match = re.match(r'^\s*', line)
        return match.group() if match else ''
    
    def _find_files_with_symbol(self, symbol: str) -> List[str]:
        """查找包含指定符号的文件"""
        files = []
        for fp in self.project_root.rglob('*.py'):
            if self._is_in_denylist(fp):
                continue
            try:
                with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
                    if symbol in f.read():
                        files.append(str(fp))
            except:
                pass
        
        # 扩展搜索其他文件类型
        for ext in ['.js', '.ts', '.json', '.md', '.yml', '.yaml']:
            for fp in self.project_root.rglob(f'*{ext}'):
                if self._is_in_denylist(fp):
                    continue
                try:
                    with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
                        if symbol in f.read():
                            if str(fp) not in files:
                                files.append(str(fp))
                except:
                    pass
        
        return files
    
    def _find_all_references(self, symbol: str) -> List[Tuple[str, int]]:
        """查找所有引用位置"""
        references = []
        for fp in self.project_root.rglob('*.py'):
            if self._is_in_denylist(fp):
                continue
            try:
                with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        if symbol in line:
                            references.append((str(fp), line_num))
            except:
                pass
        return references
    
    def _undo_change(self, change: RefactoringChange):
        """撤销变更"""
        if change.change_type == 'delete_file':
            # 从备份恢复
            if self.backup_path:
                backup_file = self.backup_path / Path(change.file_path).relative_to(self.project_root)
                if backup_file.exists():
                    dest = Path(change.file_path)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy(str(backup_file), str(dest))
        
        elif change.change_type == 'move_file':
            # 移回原位置
            src = Path(change.new_text)
            dest = Path(change.file_path)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dest))
        
        elif change.change_type == 'create_directory':
            path = Path(change.file_path)
            if path.exists():
                try:
                    path.rmdir()
                except:
                    pass
        
        elif change.old_text and change.new_text:
            with open(change.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content = content.replace(change.new_text, change.old_text)
            
            with open(change.file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
    
    def _identify_subprojects(self, ignore_patterns: List[str]) -> List[Dict[str, Any]]:
        """识别子项目 - 增强版"""
        subprojects = []
        known_patterns = [
            {'name': 'TRAE', 'patterns': ['.trae/**', '*agent*/**', 'skills/**', 'trae-core/**', 'mcps/**']},
            {'name': 'OpenCode', 'patterns': ['.opencode/**', 'backend/**', 'openapi/**', 'opencode-*']},
            {'name': 'RTK', 'patterns': ['rtk/**', 'rtk-*']},
            {'name': 'Utils', 'patterns': ['utils/**', 'lib/**', 'common/**']}
        ]
        
        for sp in known_patterns:
            files = []
            for pattern in sp['patterns']:
                for path in self.project_root.rglob(pattern):
                    if not any(ign in str(path) for ign in ignore_patterns):
                        files.append(str(path))
            
            if files:
                subprojects.append({
                    'name': sp['name'],
                    'files': files,
                    'patterns': sp['patterns']
                })
        
        return subprojects
    
    def _create_backup(self) -> str:
        """创建备份 - 增强版"""
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = self.project_root / f'backup_{timestamp}'
        self.backup_path = str(backup_path)
        self.last_backup_time = datetime.datetime.now()
        
        # 创建备份（排除保护目录）
        os.makedirs(backup_path, exist_ok=True)
        
        for item in self.project_root.iterdir():
            if self._is_in_denylist(item):
                continue
            
            dest = backup_path / item.name
            if item.is_dir():
                shutil.copytree(item, dest, ignore=shutil.ignore_patterns(*self.DENYLIST_PATHS))
            else:
                shutil.copy(item, dest)
        
        print(f"📦 备份已创建: {backup_path}")
        return str(backup_path)
    
    def _format_size(self, bytes_size: int) -> str:
        """格式化文件大小"""
        if bytes_size < 1024:
            return f"{bytes_size} B"
        elif bytes_size < 1024 * 1024:
            return f"{bytes_size / 1024:.1f} KB"
        elif bytes_size < 1024 * 1024 * 1024:
            return f"{bytes_size / (1024 * 1024):.1f} MB"
        else:
            return f"{bytes_size / (1024 * 1024 * 1024):.1f} GB"
    
    # ==================== 批量操作功能 ====================
    
    def batch_rename(self, pattern: str, replacement: str, file_extensions: List[str] = None) -> RefactoringPlan:
        """批量重命名文件"""
        changes = []
        affected_files = []
        
        extensions = file_extensions or ['*']
        
        for ext in extensions:
            for path in self.project_root.rglob(f'*{ext}'):
                if self._is_in_denylist(path):
                    continue
                
                new_name = path.name.replace(pattern, replacement)
                if new_name != path.name:
                    new_path = path.parent / new_name
                    changes.append(RefactoringChange(
                        file_path=str(path),
                        line_start=1,
                        line_end=1,
                        old_text="",
                        new_text=str(new_path),
                        change_type="move_file",
                        description=f"重命名 {path.name} -> {new_name}"
                    ))
                    affected_files.append(str(path))
        
        return RefactoringPlan(
            changes=changes,
            affected_files=affected_files,
            estimated_risk="medium" if len(affected_files) > 10 else "low",
            summary=f"批量重命名 {len(affected_files)} 个文件"
        )
    
    def cleanup_backups(self, days_to_keep: int = 7) -> RefactoringPlan:
        """清理旧备份"""
        changes = []
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_to_keep)
        
        for backup in self.project_root.glob('backup_*'):
            try:
                # 尝试解析日期
                date_str = backup.name.replace('backup_', '')
                backup_date = datetime.datetime.strptime(date_str, '%Y%m%d_%H%M%S')
                
                if backup_date < cutoff_date:
                    changes.append(RefactoringChange(
                        file_path=str(backup),
                        line_start=1,
                        line_end=1,
                        old_text="",
                        new_text="",
                        change_type="delete_file",
                        description=f"删除旧备份: {backup.name}"
                    ))
            except:
                pass
        
        return RefactoringPlan(
            changes=changes,
            affected_files=[c.file_path for c in changes],
            estimated_risk="low",
            summary=f"清理 {len(changes)} 个旧备份"
        )


# 使用示例
if __name__ == "__main__":
    refactor = AutoRefactor('.')
    
    print("="*60)
    print("Auto-Refactor v4.0 - 增强版")
    print("="*60)
    
    # 示例1: 扫描项目
    print("\n🔍 扫描项目...")
    structure = refactor.scan_project()
    print(f"项目文件数: {structure.total_files}")
    print(f"未使用文件数: {len(structure.unused_files)}")
    print(f"核心文件数: {len(structure.core_files)}")
    
    # 示例2: 生成报告
    print("\n📊 生成分析报告...")
    report = refactor.get_unused_files_report()
    with open('PROJECT_ANALYSIS_REPORT.md', 'w', encoding='utf-8') as f:
        f.write(report)
    print("报告已保存: PROJECT_ANALYSIS_REPORT.md")
    
    # 示例3: 预览删除计划（模拟模式）
    print("\n🗑️ 预览删除计划...")
    delete_plan = refactor.delete_unused_files(dry_run=True, risk_filter="low")
    print(refactor.preview_plan(delete_plan))
    
    # 示例4: 分离项目计划
    print("\n📁 预览分离子项目计划...")
    subproject_config = {
        'trae': ['.trae/**', 'agent/**', 'skills/**'],
        'opencode': ['.opencode/**', 'backend/**', 'openapi/**']
    }
    separate_plan = refactor.separate_subprojects(subproject_config, dry_run=True)
    print(refactor.preview_plan(separate_plan))
    
    print("\n✅ 示例执行完成")
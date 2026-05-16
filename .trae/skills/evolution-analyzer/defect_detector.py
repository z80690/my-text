# -*- coding: utf-8 -*-
"""
缺陷检测器 - 检查子模块功能缺陷
"""

import ast
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class Defect:
    """缺陷定义"""
    module: str
    severity: str  # critical, high, medium, low
    defect_type: str
    description: str
    suggestion: str
    line_number: Optional[int] = None


class DefectDetector:
    """
    缺陷检测器
    功能：
    1. 代码质量检查
    2. 功能完整性验证
    3. 最佳实践符合度检查
    """
    
    def __init__(self):
        self.defects = []
        self.severity_levels = ["critical", "high", "medium", "low"]
    
    def detect(self, module_path: str) -> List[Defect]:
        """
        检测模块缺陷
        """
        self.defects = []
        path = Path(module_path)
        
        if path.is_file() and path.suffix == '.py':
            self._analyze_python_file(path)
        elif path.is_dir():
            self._analyze_directory(path)
        
        return self.defects
    
    def _analyze_python_file(self, file_path: Path):
        """分析 Python 文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # AST 分析
            tree = ast.parse(content)
            
            # 检查函数是否有文档字符串
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not ast.get_docstring(node):
                        self.defects.append(Defect(
                            module=str(file_path),
                            severity="low",
                            defect_type="missing_docstring",
                            description=f"函数 {node.name} 缺少文档字符串",
                            suggestion="添加详细的文档字符串",
                            line_number=node.lineno
                        ))
            
            # 检查是否有 TODO 注释
            for i, line in enumerate(content.split('\n'), 1):
                if 'TODO' in line and 'FIXME' not in line:
                    self.defects.append(Defect(
                        module=str(file_path),
                        severity="medium",
                        defect_type="unfinished_code",
                        description=f"第{i}行有未完成的 TODO",
                        suggestion="完成 TODO 标记的任务或删除注释",
                        line_number=i
                    ))
        
        except Exception as e:
            self.defects.append(Defect(
                module=str(file_path),
                severity="high",
                defect_type="parse_error",
                description=f"无法解析文件：{str(e)}",
                suggestion="检查语法错误"
            ))
    
    def _analyze_directory(self, dir_path: Path):
        """分析目录"""
        for py_file in dir_path.rglob('*.py'):
            self._analyze_python_file(py_file)
        
        # 检查是否有 __init__.py
        if not (dir_path / '__init__.py').exists():
            self.defects.append(Defect(
                module=str(dir_path),
                severity="medium",
                defect_type="missing_init",
                description="缺少 __init__.py 文件",
                suggestion="创建 __init__.py 以使其成为 Python 包"
            ))
    
    def get_defects_by_severity(self) -> Dict[str, List[Defect]]:
        """按严重程度分类缺陷"""
        result = {level: [] for level in self.severity_levels}
        for defect in self.defects:
            result[defect.severity].append(defect)
        return result
    
    def get_critical_defects(self) -> List[Defect]:
        """获取严重缺陷"""
        return [d for d in self.defects if d.severity == "critical"]
    
    def generate_report(self) -> Dict[str, Any]:
        """生成缺陷报告"""
        by_severity = self.get_defects_by_severity()
        
        return {
            "total_defects": len(self.defects),
            "by_severity": {
                level: len(defects) for level, defects in by_severity.items()
            },
            "critical_defects": by_severity["critical"],
            "high_defects": by_severity["high"],
            "medium_defects": by_severity["medium"],
            "low_defects": by_severity["low"],
            "defects": self.defects
        }
    
    def export_to_markdown(self, output_path: str):
        """导出缺陷报告为 Markdown"""
        report = self.generate_report()
        
        md_content = f"""# 缺陷检测报告

**总缺陷数**: {report['total_defects']}

## 按严重程度分类

| 严重程度 | 数量 |
|----------|------|
| Critical | {report['by_severity']['critical']} |
| High | {report['by_severity']['high']} |
| Medium | {report['by_severity']['medium']} |
| Low | {report['by_severity']['low']} |

## 严重缺陷

"""
        for defect in report["critical_defects"]:
            md_content += f"""
### {defect.defect_type}
- **模块**: {defect.module}
- **描述**: {defect.description}
- **建议**: {defect.suggestion}
- **行号**: {defect.line_number or 'N/A'}

"""
        
        Path(output_path).write_text(md_content, encoding='utf-8')

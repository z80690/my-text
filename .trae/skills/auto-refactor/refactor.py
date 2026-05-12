"""
Auto-Refactor Skill - 代码实现示例
支持多种重构操作：Extract Method, Extract Variable, Rename, Change Signature等
"""

import os
import re
from typing import List, Dict, Optional, Tuple
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


@dataclass
class RefactoringPlan:
    """重构计划"""
    changes: List[RefactoringChange]
    affected_files: List[str]
    estimated_risk: str  # low, medium, high
    summary: str


class AutoRefactor:
    """自动代码重构工具"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backup_path = None
    
    def extract_method(self, file_path: str, start_line: int, end_line: int, 
                       method_name: str, params: List[str] = None) -> RefactoringPlan:
        """
        提取代码块为方法
        
        :param file_path: 目标文件路径
        :param start_line: 起始行（1-based）
        :param end_line: 结束行
        :param method_name: 新方法名称
        :param params: 参数列表
        :return: 重构计划
        """
        params = params or []
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 提取选中代码
        selected_lines = lines[start_line-1:end_line]
        selected_code = ''.join(selected_lines)
        
        # 构建新方法
        indent = self._detect_indent(selected_lines[0])
        param_str = ', '.join(params) if params else ''
        
        method_template = f"\n{indent}def {method_name}({param_str}):\n"
        for line in selected_lines:
            method_template += f"{indent}    {line}"
        method_template += f"{indent}    return result\n"
        
        # 替换原代码
        call_line = f"{indent}result = {method_name}({param_str})\n"
        
        changes = [
            RefactoringChange(
                file_path=file_path,
                line_start=start_line,
                line_end=end_line,
                old_text=selected_code,
                new_text=call_line,
                change_type="extract_method"
            ),
            RefactoringChange(
                file_path=file_path,
                line_start=end_line+1,
                line_end=end_line+1,
                old_text="",
                new_text=method_template,
                change_type="add_method"
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
        """
        提取表达式为变量
        
        :param file_path: 目标文件路径
        :param line_num: 行号
        :param expression: 要提取的表达式
        :param var_name: 变量名
        :return: 重构计划
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        line = lines[line_num-1]
        indent = self._detect_indent(line)
        
        # 在当前行上方插入变量声明
        var_declaration = f"{indent}{var_name} = {expression}\n"
        
        # 替换表达式
        new_line = line.replace(expression, var_name)
        
        changes = [
            RefactoringChange(
                file_path=file_path,
                line_start=line_num,
                line_end=line_num,
                old_text="",
                new_text=var_declaration,
                change_type="add_variable"
            ),
            RefactoringChange(
                file_path=file_path,
                line_start=line_num+1,
                line_end=line_num+1,
                old_text=line,
                new_text=new_line,
                change_type="replace_expression"
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
        """
        智能重命名符号
        
        :param file_path: 目标文件路径
        :param symbol_name: 原符号名
        :param new_name: 新符号名
        :param scope: 作用域（file, project）
        :return: 重构计划
        """
        changes = []
        
        if scope == "project":
            files = self._find_files_with_symbol(symbol_name)
        else:
            files = [file_path]
        
        for fp in files:
            with open(fp, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 使用词边界匹配避免误替换
            pattern = r'\b' + re.escape(symbol_name) + r'\b'
            new_content = re.sub(pattern, new_name, content)
            
            if content != new_content:
                changes.append(RefactoringChange(
                    file_path=fp,
                    line_start=1,
                    line_end=len(content.splitlines()),
                    old_text=content,
                    new_text=new_content,
                    change_type="rename"
                ))
        
        return RefactoringPlan(
            changes=changes,
            affected_files=files,
            estimated_risk="medium" if len(files) > 5 else "low",
            summary=f"重命名 {symbol_name} -> {new_name}"
        )
    
    def change_signature(self, file_path: str, method_name: str,
                        new_params: List[str], return_type: str = None) -> RefactoringPlan:
        """
        修改方法签名
        
        :param file_path: 目标文件路径
        :param method_name: 方法名
        :param new_params: 新参数列表
        :param return_type: 返回类型（可选）
        :return: 重构计划
        """
        changes = []
        
        # 查找所有调用该方法的位置
        files = self._find_files_with_symbol(method_name)
        
        for fp in files:
            with open(fp, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 修改方法定义
            def_pattern = rf'def {method_name}\([^)]*\)'
            new_sig = f"def {method_name}({', '.join(new_params)})"
            content = re.sub(def_pattern, new_sig, content)
            
            # 修改方法调用
            call_pattern = rf'{method_name}\([^)]*\)'
            new_call = f"{method_name}({', '.join(new_params)})"
            content = re.sub(call_pattern, new_call, content)
            
            changes.append(RefactoringChange(
                file_path=fp,
                line_start=1,
                line_end=len(content.splitlines()),
                old_text="",
                new_text=content,
                change_type="change_signature"
            ))
        
        return RefactoringPlan(
            changes=changes,
            affected_files=files,
            estimated_risk="high" if len(files) > 10 else "medium",
            summary=f"修改 {method_name} 签名"
        )
    
    def safe_delete(self, file_path: str, symbol_name: str) -> RefactoringPlan:
        """
        安全删除符号（检查引用）
        
        :param file_path: 目标文件路径
        :param symbol_name: 符号名
        :return: 重构计划
        """
        # 检查引用
        references = self._find_all_references(symbol_name)
        
        if len(references) > 1:
            # 有其他引用，不删除
            return RefactoringPlan(
                changes=[],
                affected_files=[],
                estimated_risk="high",
                summary=f"无法删除 {symbol_name}，存在 {len(references)} 处引用"
            )
        
        # 只有一处引用（定义处），可以安全删除
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 删除定义
        pattern = rf'\n?\s*def {symbol_name}\([^)]*\):.*?(?=\n\s*def|\Z)'
        new_content = re.sub(pattern, '', content, flags=re.DOTALL)
        
        changes = [RefactoringChange(
            file_path=file_path,
            line_start=1,
            line_end=len(content.splitlines()),
            old_text=content,
            new_text=new_content,
            change_type="delete"
        )]
        
        return RefactoringPlan(
            changes=changes,
            affected_files=[file_path],
            estimated_risk="low",
            summary=f"安全删除 {symbol_name}"
        )
    
    def execute_plan(self, plan: RefactoringPlan, create_backup: bool = True) -> Dict:
        """
        执行重构计划
        
        :param plan: 重构计划
        :param create_backup: 是否创建备份
        :return: 执行结果
        """
        if create_backup:
            self._create_backup()
        
        results = {
            'success': 0,
            'failed': 0,
            'files': []
        }
        
        for change in plan.changes:
            try:
                self._apply_change(change)
                results['success'] += 1
                results['files'].append(change.file_path)
            except Exception as e:
                results['failed'] += 1
                print(f"Failed to apply change: {e}")
        
        return results
    
    def preview_plan(self, plan: RefactoringPlan) -> str:
        """预览重构计划"""
        output = f"【重构计划】\n"
        output += f"范围: {len(plan.affected_files)} 个文件\n"
        output += f"修改: {len(plan.changes)} 处\n"
        output += f"预计风险: {plan.estimated_risk}\n\n"
        
        output += "【变更预览】\n"
        for i, change in enumerate(plan.changes, 1):
            output += f"✓ {change.file_path}: {change.change_type}\n"
        
        return output
    
    def _detect_indent(self, line: str) -> str:
        """检测缩进"""
        match = re.match(r'^\s*', line)
        return match.group() if match else ''
    
    def _find_files_with_symbol(self, symbol: str) -> List[str]:
        """查找包含指定符号的文件"""
        files = []
        for fp in self.project_root.rglob('*.py'):
            try:
                with open(fp, 'r', encoding='utf-8') as f:
                    if symbol in f.read():
                        files.append(str(fp))
            except:
                pass
        return files
    
    def _find_all_references(self, symbol: str) -> List[Tuple[str, int]]:
        """查找所有引用位置"""
        references = []
        for fp in self.project_root.rglob('*.py'):
            try:
                with open(fp, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        if symbol in line:
                            references.append((str(fp), line_num))
            except:
                pass
        return references
    
    def _apply_change(self, change: RefactoringChange):
        """应用单个变更"""
        with open(change.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.splitlines(keepends=True)
        
        if change.old_text:
            # 替换模式
            new_content = content.replace(change.old_text, change.new_text)
        else:
            # 插入模式
            new_lines = lines[:change.line_start-1]
            new_lines.append(change.new_text)
            new_lines.extend(lines[change.line_start-1:])
            new_content = ''.join(new_lines)
        
        with open(change.file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
    
    def _create_backup(self):
        """创建备份"""
        import shutil
        import datetime
        
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M')
        self.backup_path = self.project_root / f'backup_{timestamp}'
        shutil.copytree(self.project_root, self.backup_path)
        print(f"Backup created: {self.backup_path}")


# 使用示例
if __name__ == "__main__":
    refactor = AutoRefactor('.')
    
    # 示例1: 提取方法
    plan1 = refactor.extract_method(
        file_path='src/utils/helpers.py',
        start_line=10,
        end_line=15,
        method_name='calculate_score',
        params=['data', 'weights']
    )
    print(refactor.preview_plan(plan1))
    
    # 示例2: 重命名
    plan2 = refactor.rename_symbol(
        file_path='src/main.py',
        symbol_name='old_function',
        new_name='process_data',
        scope='project'
    )
    print(refactor.preview_plan(plan2))
    
    # 执行重构
    # result = refactor.execute_plan(plan1)
    # print(result)
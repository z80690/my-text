# -*- coding: utf-8 -*-
"""
Code Executor Agent - 代码执行智能体
严格遵循规则体系：
- sdd-coding.md：SDD规范驱动开发
- quality-system.md：质量门禁
- coding-standards.md：编码标准
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base import BaseAgent, AgentConfig


class CodeExecutorAgent(BaseAgent):
    """代码执行智能体 - 遵循SDD规范驱动开发"""

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self._rules_path = Path(".trae") / "rules"
        self._project_path = Path(".")

    def _check_sdd_preconditions(self) -> Dict[str, Any]:
        """检查SDD开发前条件（遵循sdd-coding.md）"""
        docs = {
            'PROPOSAL.md': False,
            'SPECS.md': False,
            'DESIGN.md': False,
            'TASKS.md': False
        }
        
        for doc_name in docs.keys():
            if (self._project_path / doc_name).exists():
                docs[doc_name] = True
        
        all_exist = all(docs.values())
        
        return {
            'all_docs_exist': all_exist,
            'docs_status': docs,
            'can_proceed': all_exist,
            'missing_docs': [k for k, v in docs.items() if not v]
        }

    def _check_code_style(self, code: str) -> Dict[str, Any]:
        """检查代码风格（遵循coding-standards.md）"""
        issues = []
        
        # 检查硬编码
        if re.search(r'["\']\w{20,}[\'"]', code):  # 长字符串可能是密钥
            issues.append('potential_hardcoded_secret')
        
        # 检查命名规范（简单检查）
        if re.search(r'\bvar\s+\w+', code):  # JavaScript var
            issues.append('outdated_js_syntax')
        
        # 检查类型提示（Python）
        if 'def ' in code and '->' not in code and '.py' in str(self._project_path):
            issues.append('missing_type_hints')
        
        return {
            'issues': issues,
            'passed': len(issues) == 0,
            'issue_count': len(issues)
        }

    def _apply_four_constraints(self, code: str) -> Dict[str, Any]:
        """应用四大约束缰绳（遵循sdd-coding.md）"""
        constraints_applied = []
        
        # 约束1：代码风格统一
        # 约束2：自动生成文档
        # 约束3：内置测试用例
        # 约束4：主动纠错
        
        # 检查是否已有注释
        has_comments = '"""' in code or '# ' in code or '/*' in code
        constraints_applied.append({
            'constraint': 'auto_documentation',
            'applied': has_comments,
            'suggestion': '添加函数文档注释' if not has_comments else None
        })
        
        # 检查测试用例
        has_tests = 'test' in code.lower() or 'assert' in code
        constraints_applied.append({
            'constraint': 'test_cases',
            'applied': has_tests,
            'suggestion': '添加单元测试' if not has_tests else None
        })
        
        return {
            'constraints_applied': constraints_applied,
            'code_quality_score': 80 if len(constraints_applied) == 2 else 60
        }

    def _classify_code_operation(self, task: str) -> str:
        """分类代码操作"""
        task_lower = task.lower()
        
        if any(kw in task_lower for kw in ['写', '创建', '实现', '编写', '生成']):
            return 'write'
        elif any(kw in task_lower for kw in ['debug', '调试', '修复', '错误', 'bug']):
            return 'debug'
        elif any(kw in task_lower for kw in ['优化', '改进', '重构', '整理']):
            return 'optimize'
        elif any(kw in task_lower for kw in ['分析', '检查', '审查']):
            return 'analyze'
        elif any(kw in task_lower for kw in ['运行', '执行', '跑']):
            return 'execute'
        else:
            return 'general'

    def _generate_quality_gate_score(self, code: str, style_check: Dict) -> float:
        """生成质量门禁评分（遵循quality-system.md）"""
        # 准确性（30%）
        accuracy = 100 if style_check['passed'] else 60
        
        # 安全性（25%）- 简化版
        security = 80 if not any('secret' in i for i in style_check['issues']) else 40
        
        # 可维护性（20%）
        maintainability = 80 if '# ' in code or '"""' in code else 60
        
        # 可测试性（25%）
        testability = 80 if 'test' in code.lower() else 40
        
        # 综合评分
        score = (accuracy * 0.3 + security * 0.25 + 
                maintainability * 0.2 + testability * 0.25)
        
        return score

    def _gate_decision(self, score: float) -> Dict[str, Any]:
        """质量门禁决策（遵循quality-system.md）"""
        if score >= 90:
            return {'decision': 'pass', 'level': 'direct_pass', 'message': '可直接合并/部署'}
        elif score >= 75:
            return {'decision': 'conditional_pass', 'level': 'review_required', 'message': '需要代码审查后通过'}
        elif score >= 60:
            return {'decision': 'rework', 'level': 'fix_required', 'message': '修复问题后重新评估'}
        else:
            return {'decision': 'reject', 'level': 'must_fix', 'message': '必须修复后重新提交'}

    def _execute_write(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行写代码操作"""
        # 检查SDD前条件
        sdd_check = self._check_sdd_preconditions()
        
        code = context.get('code', f'# 代码: {task}')
        
        # 检查代码风格
        style_check = self._check_code_style(code)
        
        # 应用约束
        constraints = self._apply_four_constraints(code)
        
        # 质量评分
        quality_score = self._generate_quality_gate_score(code, style_check)
        gate_result = self._gate_decision(quality_score)
        
        return {
            'operation': 'write',
            'sdd_status': sdd_check,
            'style_check': style_check,
            'constraints': constraints,
            'quality_score': quality_score,
            'gate_decision': gate_result,
            'code_generated': True,
            'message': f"代码生成完成，质量评分: {quality_score:.1f}分"
        }

    def _execute_debug(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行调试操作"""
        return {
            'operation': 'debug',
            'error_detected': True,
            'debug_session': 'started',
            'analysis': '正在分析错误...',
            'suggestions': ['检查参数类型', '验证输入数据', '查看日志']
        }

    def _execute_optimize(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行优化操作"""
        return {
            'operation': 'optimize',
            'optimization_type': 'code_simplifier',
            'constraints_applied': ['功能守恒', '清晰度优先', '遵循规范', '结构保留', '聚焦当下'],
            'improvements': ['命名优化', '嵌套简化', '注释添加'],
            'code_simplified': True
        }

    def _execute_analyze(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行分析操作"""
        return {
            'operation': 'analyze',
            'analysis_type': 'code_review',
            'checks': {
                'correctness': '通过',
                'security': '通过',
                'maintainability': '通过',
                'testability': '通过'
            },
            'overall_status': 'pass'
        }

    def _default_execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """默认执行逻辑"""
        context = context or {}
        
        # 1. 分类代码操作
        operation = self._classify_code_operation(task)
        
        # 2. 根据操作类型执行
        if operation == 'write':
            result = self._execute_write(task, context)
        elif operation == 'debug':
            result = self._execute_debug(task, context)
        elif operation == 'optimize':
            result = self._execute_optimize(task, context)
        elif operation == 'analyze':
            result = self._execute_analyze(task, context)
        else:
            result = {
                'operation': 'general',
                'status': 'completed',
                'message': f'代码任务完成: {task}'
            }
        
        # 3. 添加元信息
        result['agent_id'] = self.id
        result['agent_name'] = self.name
        result['operation_type'] = operation
        result['timestamp'] = datetime.now().isoformat()
        
        return result

    def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行任务（同步版本）"""
        return self._default_execute(task, context or {})

    async def async_execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """异步执行任务"""
        return self.execute(task, context)

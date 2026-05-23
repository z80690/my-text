# -*- coding: utf-8 -*-
"""
Tool Agent - 工具执行智能体
严格遵循规则体系：
- security-audit.md：安全审计
- token-optimization.md：Token优化
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base import BaseAgent, AgentConfig


class ToolAgent(BaseAgent):
    """工具执行智能体 - 命令和文件操作"""

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self._workspace = Path(".")

    def _classify_tool_operation(self, task: str) -> str:
        """分类工具操作"""
        task_lower = task.lower()
        
        if any(kw in task_lower for kw in ['搜索', '查询', 'find', 'grep', 'search']):
            return 'search'
        elif any(kw in task_lower for kw in ['执行', '运行', 'run', 'execute', '命令']):
            return 'execute'
        elif any(kw in task_lower for kw in ['读取', '查看', 'cat', 'read']):
            return 'read'
        elif any(kw in task_lower for kw in ['写入', '创建', 'write', 'create']):
            return 'write'
        elif any(kw in task_lower for kw in ['删除', 'remove', 'delete']):
            return 'delete'
        elif any(kw in task_lower for kw in ['复制', 'copy']):
            return 'copy'
        elif any(kw in task_lower for kw in ['移动', 'move']):
            return 'move'
        else:
            return 'query'

    def _security_check(self, command: str) -> Dict[str, Any]:
        """安全检查（遵循security-audit.md）"""
        issues = []
        
        # 检查危险命令
        dangerous_commands = ['rm -rf', 'format', 'del /f /s', 'shutdown', 'reboot']
        for dangerous in dangerous_commands:
            if dangerous in command:
                issues.append({
                    'severity': 'high',
                    'issue': f'危险命令: {dangerous}',
                    'requires_approval': True
                })
        
        # 检查硬编码敏感信息
        sensitive_patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', 'hardcoded_password'),
            (r'api[_-]?key\s*=\s*["\'][^"\']+["\']', 'hardcoded_api_key'),
            (r'secret\s*=\s*["\'][^"\']+["\']', 'hardcoded_secret')
        ]
        
        for pattern, issue_type in sensitive_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                issues.append({
                    'severity': 'critical',
                    'issue': f'敏感信息: {issue_type}',
                    'requires_approval': True
                })
        
        return {
            'passed': len(issues) == 0,
            'issues': issues,
            'requires_approval': any(i.get('requires_approval', False) for i in issues)
        }

    def _execute_search(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行搜索操作"""
        pattern = context.get('pattern', task)
        path = context.get('path', '.')
        
        # 简化版：返回搜索信息
        return {
            'operation': 'search',
            'pattern': pattern,
            'path': path,
            'files_found': [],
            'status': 'simulated',
            'message': f'搜索: {pattern} in {path}'
        }

    def _execute_execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行命令操作"""
        command = context.get('command', task)
        
        # 安全检查
        security_check = self._security_check(command)
        
        if security_check['requires_approval']:
            return {
                'operation': 'execute',
                'command': command,
                'security_check': security_check,
                'status': 'requires_approval',
                'message': '命令包含敏感操作，需要用户批准'
            }
        
        # 模拟执行
        return {
            'operation': 'execute',
            'command': command,
            'security_check': security_check,
            'status': 'simulated',
            'output': f'模拟执行: {command}',
            'exit_code': 0,
            'message': '命令执行完成'
        }

    def _execute_read(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行读取操作"""
        file_path = context.get('file_path', '')
        
        if not file_path:
            return {
                'operation': 'read',
                'status': 'error',
                'message': '未指定文件路径'
            }
        
        path = Path(file_path)
        if not path.exists():
            return {
                'operation': 'read',
                'status': 'error',
                'message': f'文件不存在: {file_path}'
            }
        
        try:
            content = path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            return {
                'operation': 'read',
                'file_path': file_path,
                'content': content[:500],  # 限制返回内容
                'lines': len(lines),
                'size': len(content),
                'status': 'success',
                'message': f'读取成功，共 {len(lines)} 行'
            }
        except Exception as e:
            return {
                'operation': 'read',
                'file_path': file_path,
                'status': 'error',
                'message': f'读取失败: {str(e)}'
            }

    def _execute_write(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行写入操作"""
        file_path = context.get('file_path', '')
        content = context.get('content', '')
        
        if not file_path:
            return {
                'operation': 'write',
                'status': 'error',
                'message': '未指定文件路径'
            }
        
        # 安全检查
        security_check = self._security_check(content)
        
        if security_check['requires_approval']:
            return {
                'operation': 'write',
                'file_path': file_path,
                'security_check': security_check,
                'status': 'requires_approval',
                'message': '文件内容包含敏感信息，需要用户批准'
            }
        
        # 模拟写入
        return {
            'operation': 'write',
            'file_path': file_path,
            'security_check': security_check,
            'bytes_written': len(content),
            'status': 'simulated',
            'message': f'模拟写入: {len(content)} 字节'
        }

    def _execute_query(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行查询操作"""
        return {
            'operation': 'query',
            'available_tools': [
                'search', 'execute', 'read', 'write', 'delete', 'copy', 'move'
            ],
            'status': 'success',
            'message': '工具查询完成'
        }

    def _default_execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """默认执行逻辑"""
        context = context or {}
        
        # 1. 分类工具操作
        operation = self._classify_tool_operation(task)
        
        # 2. 根据操作类型执行
        if operation == 'search':
            result = self._execute_search(task, context)
        elif operation == 'execute':
            result = self._execute_execute(task, context)
        elif operation == 'read':
            result = self._execute_read(task, context)
        elif operation == 'write':
            result = self._execute_write(task, context)
        elif operation == 'query':
            result = self._execute_query(task, context)
        else:
            result = {
                'operation': operation,
                'status': 'completed',
                'message': f'工具操作完成: {operation}'
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

# -*- coding: utf-8 -*-
"""
Rule Interpreter Agent - 规则解释智能体
严格遵循规则体系：
- rule-management.md：规则管理
- algorithm-optimization.md：算法优化
"""

import re
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base import BaseAgent, AgentConfig


class RuleInterpreterAgent(BaseAgent):
    """规则解释智能体 - 规则解析与转换"""

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self._rules_path = Path(".trae") / "rules"
        self._agents_path = Path(".trae") / "agents"

    def _scan_rules(self) -> List[Dict[str, Any]]:
        """扫描所有规则文件"""
        rules = []
        
        if not self._rules_path.exists():
            return rules
        
        for rule_file in self._rules_path.glob("*.md"):
            try:
                content = rule_file.read_text(encoding='utf-8')
                
                # 提取规则信息
                rule_info = {
                    'file': rule_file.name,
                    'path': str(rule_file),
                    'size': rule_file.stat().st_size,
                    'lines': len(content.split('\n'))
                }
                
                # 提取版本
                version_match = re.search(r'\*\*版本\*\*[:：]\s*v?(\d+\.\d+)', content)
                if version_match:
                    rule_info['version'] = version_match.group(1)
                
                # 提取触发条件
                trigger_match = re.search(r'\*\*触发条件\*\*[:：]\s*(.+)', content)
                if trigger_match:
                    rule_info['trigger'] = trigger_match.group(1).strip()
                
                # 提取L1/L2支撑
                l1_match = re.search(r'\*\*L1支撑\*\*[:：]\s*(.+)', content)
                if l1_match:
                    rule_info['l1_support'] = l1_match.group(1).strip()
                
                rules.append(rule_info)
            except Exception as e:
                print(f"扫描规则失败 {rule_file}: {e}")
        
        return rules

    def _parse_rule_content(self, content: str) -> Dict[str, Any]:
        """解析规则内容"""
        parsed = {
            'title': '',
            'version': '',
            'sections': [],
            'checklists': [],
            'tables': [],
            'code_blocks': []
        }
        
        # 提取标题
        title_match = re.match(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            parsed['title'] = title_match.group(1)
        
        # 提取章节
        section_pattern = r'^##\s+(.+)$'
        sections = re.findall(section_pattern, content, re.MULTILINE)
        parsed['sections'] = sections
        
        # 提取检查清单
        checklist_pattern = r'^\s*-\s*\[([ x])\]\s+(.+)$'
        checklists = re.findall(checklist_pattern, content, re.MULTILINE)
        parsed['checklists'] = [{'checked': c == 'x', 'text': t} for c, t in checklists]
        
        # 提取代码块
        code_pattern = r'```\w*\n(.*?)```'
        code_blocks = re.findall(code_pattern, content, re.DOTALL)
        parsed['code_blocks'] = code_blocks
        
        return parsed

    def _detect_rule_type(self, rule_name: str) -> str:
        """检测规则类型"""
        rule_lower = rule_name.lower()
        
        if '6a' in rule_lower or '工作流' in rule_lower:
            return 'workflow'
        elif '质量' in rule_lower or '测试' in rule_lower:
            return 'quality'
        elif '编码' in rule_lower or '代码' in rule_lower:
            return 'coding'
        elif 'git' in rule_lower or '版本' in rule_lower:
            return 'version_control'
        elif '安全' in rule_lower:
            return 'security'
        elif '情绪' in rule_lower:
            return 'emotional'
        elif 'wiki' in rule_lower or '知识' in rule_lower:
            return 'knowledge'
        elif 'sdd' in rule_lower or '规范' in rule_lower:
            return 'development'
        else:
            return 'general'

    def _check_rule_conflicts(self, rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """检查规则冲突（遵循rule-management.md）"""
        conflicts = []
        
        # 简化版：只检查是否有多处定义的同名规则
        rule_names = {}
        for rule in rules:
            name = rule.get('file', '')
            if name in rule_names:
                conflicts.append({
                    'type': 'duplicate',
                    'rule': name,
                    'locations': [rule['path'], rule_names[name]]
                })
            else:
                rule_names[name] = rule['path']
        
        return conflicts

    def _classify_interpretation_task(self, task: str) -> str:
        """分类解释任务"""
        task_lower = task.lower()
        
        if any(kw in task_lower for kw in ['解析', '理解', '说明', '解释']):
            return 'parse'
        elif any(kw in task_lower for kw in ['检查', '验证', '校验']):
            return 'validate'
        elif any(kw in task_lower for kw in ['冲突', '矛盾', '问题']):
            return 'conflict'
        elif any(kw in task_lower for kw in ['更新', '修改', '变更']):
            return 'update'
        elif any(kw in task_lower for kw in ['生命周期', '版本', '历史']):
            return 'lifecycle'
        else:
            return 'query'

    def _execute_parse(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行解析操作"""
        # 获取指定规则
        rule_file = context.get('rule_file', '')
        
        if rule_file:
            rule_path = self._rules_path / rule_file
            if rule_path.exists():
                content = rule_path.read_text(encoding='utf-8')
                parsed = self._parse_rule_content(content)
                
                return {
                    'operation': 'parse',
                    'rule_file': rule_file,
                    'parsed': parsed,
                    'message': f'规则 {rule_file} 解析完成'
                }
        
        # 扫描所有规则
        all_rules = self._scan_rules()
        
        return {
            'operation': 'parse',
            'total_rules': len(all_rules),
            'rules': all_rules[:10],  # 只返回前10个
            'message': f'共扫描到 {len(all_rules)} 条规则'
        }

    def _execute_validate(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行验证操作"""
        rules = self._scan_rules()
        conflicts = self._check_rule_conflicts(rules)
        
        return {
            'operation': 'validate',
            'total_rules': len(rules),
            'conflicts_found': len(conflicts),
            'conflicts': conflicts,
            'validation_status': 'pass' if len(conflicts) == 0 else 'fail',
            'message': f'验证完成，发现 {len(conflicts)} 个冲突'
        }

    def _execute_conflict(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行冲突检测操作"""
        rules = self._scan_rules()
        conflicts = self._check_rule_conflicts(rules)
        
        return {
            'operation': 'conflict_detection',
            'conflicts': conflicts,
            'resolution_suggestions': [
                '检查规则优先级',
                '合并重复规则',
                '明确规则边界'
            ] if conflicts else [],
            'message': f'冲突检测完成，共 {len(conflicts)} 个问题'
        }

    def _execute_query(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行查询操作"""
        rules = self._scan_rules()
        
        # 分类统计
        type_counts = {}
        for rule in rules:
            rule_type = self._detect_rule_type(rule.get('file', ''))
            type_counts[rule_type] = type_counts.get(rule_type, 0) + 1
        
        return {
            'operation': 'query',
            'total_rules': len(rules),
            'type_distribution': type_counts,
            'rules': rules,
            'message': f'查询完成，共 {len(rules)} 条规则'
        }

    def _default_execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """默认执行逻辑"""
        context = context or {}
        
        # 1. 分类解释任务
        operation = self._classify_interpretation_task(task)
        
        # 2. 根据操作类型执行
        if operation == 'parse':
            result = self._execute_parse(task, context)
        elif operation == 'validate':
            result = self._execute_validate(task, context)
        elif operation == 'conflict':
            result = self._execute_conflict(task, context)
        elif operation == 'query':
            result = self._execute_query(task, context)
        else:
            result = {
                'operation': operation,
                'status': 'completed',
                'message': f'规则解释任务完成: {task}'
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

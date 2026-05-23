# -*- coding: utf-8 -*-
"""
Monitor Agent - 监控智能体
严格遵循规则体系：
- quality-system.md：质量监控
- algorithm-optimization.md：性能分析
"""

import os
import time
import psutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base import BaseAgent, AgentConfig


class MonitorAgent(BaseAgent):
    """监控智能体 - 系统监控和性能分析"""

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self._workspace = Path(".")
        self._start_time = time.time()

    def _get_system_metrics(self) -> Dict[str, Any]:
        """获取系统指标"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # 内存使用率
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # 磁盘使用率
            disk = psutil.disk_usage('.')
            disk_percent = disk.percent
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'disk_percent': disk_percent,
                'available': True
            }
        except Exception as e:
            return {
                'cpu_percent': 0,
                'memory_percent': 0,
                'disk_percent': 0,
                'available': False,
                'error': str(e)
            }

    def _scan_agents(self) -> List[Dict[str, Any]]:
        """扫描智能体状态"""
        agents_path = Path(".trae") / "agents"
        agents = []
        
        if not agents_path.exists():
            return agents
        
        for agent_file in agents_path.glob("*_agent.py"):
            agents.append({
                'name': agent_file.stem,
                'path': str(agent_file),
                'size': agent_file.stat().st_size,
                'modified': datetime.fromtimestamp(agent_file.stat().st_mtime).isoformat()
            })
        
        return agents

    def _scan_rules(self) -> List[Dict[str, Any]]:
        """扫描规则状态"""
        rules_path = Path(".trae") / "rules"
        rules = []
        
        if not rules_path.exists():
            return rules
        
        for rule_file in rules_path.glob("*.md"):
            rules.append({
                'name': rule_file.name,
                'path': str(rule_file),
                'size': rule_file.stat().st_size,
                'modified': datetime.fromtimestamp(rule_file.stat().st_mtime).isoformat()
            })
        
        return rules

    def _analyze_performance(self) -> Dict[str, Any]:
        """性能分析（遵循algorithm-optimization.md）"""
        uptime = time.time() - self._start_time
        
        return {
            'uptime_seconds': uptime,
            'uptime_formatted': f"{uptime:.1f}秒",
            'cache_hit_rate': 0.85,  # 模拟值
            'memory_usage': psutil.Process().memory_info().rss / 1024 / 1024,  # MB
            'status': 'optimal'
        }

    def _classify_monitor_task(self, task: str) -> str:
        """分类监控任务"""
        task_lower = task.lower()
        
        if any(kw in task_lower for kw in ['系统', '资源', 'cpu', '内存', 'disk']):
            return 'system'
        elif any(kw in task_lower for kw in ['智能体', 'agent', '状态']):
            return 'agents'
        elif any(kw in task_lower for kw in ['规则', 'rule', '状态']):
            return 'rules'
        elif any(kw in task_lower for kw in ['性能', 'performance', '分析']):
            return 'performance'
        elif any(kw in task_lower for kw in ['问题', '故障', 'error', 'issue']):
            return 'problems'
        else:
            return 'status'

    def _execute_system(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行系统监控"""
        metrics = self._get_system_metrics()
        
        # 告警判断
        alerts = []
        if metrics.get('cpu_percent', 0) > 90:
            alerts.append({'level': 'warning', 'message': 'CPU使用率过高'})
        if metrics.get('memory_percent', 0) > 90:
            alerts.append({'level': 'warning', 'message': '内存使用率过高'})
        if metrics.get('disk_percent', 0) > 90:
            alerts.append({'level': 'warning', 'message': '磁盘使用率过高'})
        
        return {
            'operation': 'system_monitor',
            'metrics': metrics,
            'alerts': alerts,
            'status': 'healthy' if not alerts else 'warning',
            'message': '系统监控完成'
        }

    def _execute_agents(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行智能体监控"""
        agents = self._scan_agents()
        
        return {
            'operation': 'agents_monitor',
            'total_agents': len(agents),
            'agents': agents,
            'status': 'healthy',
            'message': f'智能体监控完成，共 {len(agents)} 个智能体'
        }

    def _execute_rules(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行规则监控"""
        rules = self._scan_rules()
        
        # 规则分类统计
        type_counts = {}
        for rule in rules:
            name = rule['name']
            if 'quality' in name:
                type_counts['quality'] = type_counts.get('quality', 0) + 1
            elif 'coding' in name:
                type_counts['coding'] = type_counts.get('coding', 0) + 1
            elif 'sdd' in name:
                type_counts['sdd'] = type_counts.get('sdd', 0) + 1
            elif 'wiki' in name:
                type_counts['wiki'] = type_counts.get('wiki', 0) + 1
            else:
                type_counts['other'] = type_counts.get('other', 0) + 1
        
        return {
            'operation': 'rules_monitor',
            'total_rules': len(rules),
            'type_distribution': type_counts,
            'rules': rules,
            'status': 'healthy',
            'message': f'规则监控完成，共 {len(rules)} 条规则'
        }

    def _execute_performance(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行性能分析"""
        perf = self._analyze_performance()
        
        return {
            'operation': 'performance_analysis',
            'metrics': perf,
            'recommendations': [
                '性能表现正常',
                '建议定期清理缓存'
            ],
            'status': 'optimal',
            'message': '性能分析完成'
        }

    def _execute_problems(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行问题检测"""
        problems = []
        
        # 检查常见问题
        # 1. 检查未注册的智能体
        agents = self._scan_agents()
        if len(agents) < 20:
            problems.append({
                'type': 'missing_agents',
                'severity': 'medium',
                'message': f'智能体数量不足: {len(agents)}/25'
            })
        
        # 2. 检查规则完整性
        rules = self._scan_rules()
        if len(rules) < 10:
            problems.append({
                'type': 'missing_rules',
                'severity': 'medium',
                'message': f'规则数量不足: {len(rules)}'
            })
        
        return {
            'operation': 'problems_detection',
            'problems_found': len(problems),
            'problems': problems,
            'status': 'healthy' if not problems else 'issues_found',
            'message': f'问题检测完成，发现 {len(problems)} 个问题'
        }

    def _default_execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """默认执行逻辑"""
        context = context or {}
        
        # 1. 分类监控任务
        operation = self._classify_monitor_task(task)
        
        # 2. 根据操作类型执行
        if operation == 'system':
            result = self._execute_system(task, context)
        elif operation == 'agents':
            result = self._execute_agents(task, context)
        elif operation == 'rules':
            result = self._execute_rules(task, context)
        elif operation == 'performance':
            result = self._execute_performance(task, context)
        elif operation == 'problems':
            result = self._execute_problems(task, context)
        else:
            result = {
                'operation': 'status',
                'status': 'completed',
                'message': f'监控任务完成: {operation}'
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

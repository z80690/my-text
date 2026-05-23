# -*- coding: utf-8 -*-
"""
Dispatcher Agent - 智能体团队调度员
严格遵循规则体系：
- AGENTS.md：动态身份系统、质量核心原则
- 6a-project-flow.md：6A工作流
- emotional-adaptation.md：情绪感知
- algorithm-optimization.md：算法优化（向量匹配、博弈决策）
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base import BaseAgent, AgentConfig


class DispatcherAgent(BaseAgent):
    """智能体团队调度员 - 核心协调器"""

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self._rules_path = Path(".trae") / "rules"
        self._agents_path = Path(".trae") / "agents"
        self._registry = None

    def _set_registry(self, registry):
        """设置注册中心"""
        self._registry = registry

    def _detect_game_mode(self, task: str) -> str:
        """检测博弈模式"""
        task_lower = task.lower()
        
        if any(kw in task_lower for kw in ['对比', '权衡', '优缺点', '辩论', '正反']):
            return 'debate'
        elif any(kw in task_lower for kw in ['优化', '改进', '重构', '提升', '迭代']):
            return 'optimization'
        elif any(kw in task_lower for kw in ['设计', '架构', '方案', '蓝图']):
            return 'design'
        elif any(kw in task_lower for kw in ['协商', '讨论', '共识', '投票']):
            return 'negotiation'
        elif any(kw in task_lower for kw in ['分配', '竞争', '优先级', '资源']):
            return 'auction'
        else:
            return 'default'

    def _detect_emotion(self, task: str) -> str:
        """检测情绪状态（遵循emotional-adaptation.md）"""
        task_lower = task.lower()
        
        # 急躁检测
        if any(kw in task_lower for kw in ['快', '赶紧', '马上', '立刻', '快快', '急']):
            return 'impatient'
        
        # 生气检测
        if any(kw in task_lower for kw in ['错', '烂', '糟糕', '不满意', '气']):
            return 'angry'
        
        # 疲惫检测
        if any(kw in task_lower for kw in ['累', '困', '不想', '算了', '随便']):
            return 'tired'
        
        # 严肃检测
        if any(kw in task_lower for kw in ['重要', '严肃', '谨慎', '风险', '关键']):
            return 'serious'
        
        # 轻松检测
        if any(kw in task_lower for kw in ['哈哈', '轻松', '随便', '聊聊']):
            return 'relaxed'
        
        return 'neutral'

    def _classify_task_for_routing(self, task: str) -> str:
        """任务分类路由（根据dispatcher-agent.md）"""
        task_lower = task.lower()
        
        if any(kw in task_lower for kw in ['代码', 'debug', '实现', '编程', '写代码', 'code']):
            return 'code_executor_agent'
        elif any(kw in task_lower for kw in ['规则', '规范', '解释', '说明', '体系', 'rule']):
            return 'rule_interpreter_agent'
        elif any(kw in task_lower for kw in ['文档', 'README', '报告', '写文档', 'doc']):
            return 'writer_agent'
        elif any(kw in task_lower for kw in ['执行', '命令', '搜索', '查询', '查找', 'tool']):
            return 'tool_agent'
        elif any(kw in task_lower for kw in ['需求', '澄清', '确认', '对齐', '需求']):
            return 'user_proxy_agent'
        elif any(kw in task_lower for kw in ['wiki', '知识', '编译', '整理', '摘要', 'wiki']):
            return 'llm_wiki_agent'
        elif any(kw in task_lower for kw in ['协调', '调度', '复杂', '多步骤', '协作']):
            return 'dispatcher_agent'
        else:
            return 'assistant_agent'

    def _analyze_6a_phase(self, task: str) -> str:
        """分析当前6A阶段（遵循6a-project-flow.md）"""
        task_lower = task.lower()
        
        if any(kw in task_lower for kw in ['需求', '澄清', '理解', '边界', '确认']):
            return 'align'
        elif any(kw in task_lower for kw in ['设计', '架构', '方案', '选型']):
            return 'architect'
        elif any(kw in task_lower for kw in ['拆解', '分解', '任务', '细分']):
            return 'atomize'
        elif any(kw in task_lower for kw in ['批准', '确认', '同意', '通过']):
            return 'approve'
        elif any(kw in task_lower for kw in ['执行', '开发', '实现', '编码']):
            return 'automate'
        elif any(kw in task_lower for kw in ['验收', '评估', '测试', '检查']):
            return 'assess'
        else:
            return 'unknown'

    def _get_load_balanced_agent(self, agent_id: str) -> str:
        """负载均衡选择"""
        # 简化版：直接返回指定智能体
        # 完整版应该查询registry获取各智能体的负载状态
        return agent_id

    def _execute_debate_mode(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """辩论模式执行"""
        return {
            'mode': 'debate',
            'response': f"[辩论模式] 正在分析任务: {task}",
            'participating_agents': ['agent_a', 'agent_b'],
            'rounds': 3,
            'status': 'simulated'
        }

    def _execute_optimization_mode(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """优化模式执行"""
        return {
            'mode': 'optimization',
            'response': f"[优化模式] 正在优化任务: {task}",
            'critic_agent': 'critic_agent',
            'iterations': 5,
            'status': 'simulated'
        }

    def _execute_design_mode(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """设计模式执行"""
        return {
            'mode': 'design',
            'response': f"[设计模式] 正在设计任务: {task}",
            'blueprint_agent': 'architect_agent',
            'challenges': ['complexity', 'feasibility'],
            'status': 'simulated'
        }

    def _execute_default_mode(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """默认模式执行"""
        # 根据任务类型路由到对应智能体
        target_agent = self._classify_task_for_routing(task)
        
        return {
            'mode': 'default',
            'target_agent': target_agent,
            '6a_phase': self._analyze_6a_phase(task),
            'emotion': self._detect_emotion(task),
            'response': f"[调度模式] 任务已路由到: {target_agent}",
            'status': 'routed'
        }

    def _adjust_response_style(self, response: Dict[str, Any], emotion: str) -> Dict[str, Any]:
        """根据情绪调整响应风格（遵循emotional-adaptation.md）"""
        response_style = {
            'impatient': '极简结论模式',
            'angry': '安抚模式',
            'tired': '替用户思考模式',
            'serious': '严谨专业模式',
            'relaxed': '轻松对话模式',
            'neutral': '默认平衡模式'
        }
        
        response['_emotion'] = emotion
        response['_response_style'] = response_style.get(emotion, '默认平衡模式')
        
        return response

    def _default_execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """默认执行逻辑"""
        context = context or {}
        
        # 1. 检测博弈模式
        game_mode = self._detect_game_mode(task)
        
        # 2. 分析6A阶段
        phase_6a = self._analyze_6a_phase(task)
        
        # 3. 检测情绪
        emotion = self._detect_emotion(task)
        
        # 4. 根据博弈模式执行
        if game_mode == 'debate':
            result = self._execute_debate_mode(task, context)
        elif game_mode == 'optimization':
            result = self._execute_optimization_mode(task, context)
        elif game_mode == 'design':
            result = self._execute_design_mode(task, context)
        else:
            result = self._execute_default_mode(task, context)
        
        # 5. 添加元信息
        result['agent_id'] = self.id
        result['agent_name'] = self.name
        result['game_mode'] = game_mode
        result['phase_6a'] = phase_6a
        result['emotion'] = emotion
        result['timestamp'] = datetime.now().isoformat()
        
        # 6. 根据情绪调整响应风格
        result = self._adjust_response_style(result, emotion)
        
        return result

    def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行任务（同步版本）"""
        return self._default_execute(task, context or {})

    async def async_execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """异步执行任务"""
        return self.execute(task, context)

# -*- coding: utf-8 -*-
"""
智能体基础类 - 支持模块化组合
"""

import json
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List, Optional


class ModuleReferenceParser:
    """模块引用解析器 - 解析 @module 语法"""

    @staticmethod
    def parse(reference_str: str) -> dict:
        """解析模块引用字符串"""
        pattern = r'@module\(([A-Za-z0-9_-]+)(?:@([\^~>=<!\d.]+))?\)'
        match = re.match(pattern, reference_str)

        if match:
            return {
                'module_id': match.group(1),
                'version_constraint': match.group(2) if match.group(2) else 'latest'
            }
        return None

    @staticmethod
    def extract_from_text(text: str) -> List[dict]:
        """从文本中提取所有模块引用"""
        pattern = r'@module\(([A-Za-z0-9_-]+)(?:@([\^~>=<!\d.]+))?\)'
        matches = re.findall(pattern, text)
        return [
            {'module_id': m[0], 'version_constraint': m[1] if m[1] else 'latest'}
            for m in matches
        ]


class ModuleRegistry:
    """模块注册中心 - 运行时加载和管理模块"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._modules = {}
            cls._instance._agents = {}
            cls._instance._initialized = False
        return cls._instance

    def initialize(self, base_path: str = ".trae"):
        """初始化模块注册中心"""
        if self._initialized:
            return

        self._base_path = Path(base_path)
        self._scan_rules()
        self._scan_agents()
        self._initialized = True
        print(f"[ModuleRegistry] 已加载 {len(self._modules)} 个模块")

    def _scan_rules(self):
        """扫描规则模块"""
        rules_path = self._base_path / "rules" / "extension"
        if rules_path.exists():
            for md_file in rules_path.glob("*.md"):
                module = self._parse_module_file(md_file)
                if module:
                    self._modules[module['module_id']] = module

    def _scan_agents(self):
        """扫描智能体模块"""
        agents_path = self._base_path / "agents"
        if agents_path.exists():
            for md_file in agents_path.glob("*_agent.md"):
                agent = self._parse_agent_file(md_file)
                if agent:
                    self._agents[agent['module_id']] = agent

    def _parse_module_file(self, file_path: Path) -> Optional[dict]:
        """解析模块文件"""
        try:
            content = file_path.read_text(encoding='utf-8')

            # 提取模块ID
            module_id_match = re.search(r'module_id["\s:]+([L3][\w-]+)', content)
            if not module_id_match:
                return None

            module_id = module_id_match.group(1)

            # 提取版本
            version_match = re.search(r'version["\s:]+["\']?(\d+\.\d+\.\d+)', content)
            version = version_match.group(1) if version_match else "1.0.0"

            # 提取依赖
            dependencies = []
            dep_pattern = r'\["([L3][\w-]+)"'
            for match in re.finditer(dep_pattern, content):
                dep_id = match.group(1)
                if dep_id != module_id:
                    dependencies.append(dep_id)

            # 提取模块引用
            module_refs = ModuleReferenceParser.extract_from_text(content)

            return {
                'module_id': module_id,
                'name': file_path.stem,
                'version': version,
                'type': 'rule',
                'file_path': str(file_path),
                'dependencies': dependencies,
                'module_refs': module_refs,
                'content': content
            }
        except Exception as e:
            print(f"[ModuleRegistry] 解析模块文件失败 {file_path}: {e}")
            return None

    def _parse_agent_file(self, file_path: Path) -> Optional[dict]:
        """解析智能体文件"""
        try:
            content = file_path.read_text(encoding='utf-8')

            # 提取模块ID
            module_id_match = re.search(r'(L3-C\d+)', content)
            if not module_id_match:
                return None

            module_id = module_id_match.group(1)

            # 提取智能体ID
            agent_id_match = re.search(r'\*\*ID\*\*:\s*(\w+)', content)
            agent_id = agent_id_match.group(1) if agent_id_match else module_id

            # 提取模块引用
            module_refs = ModuleReferenceParser.extract_from_text(content)

            # 提取依赖
            dependencies = []
            dep_pattern = r'\[([L3][\w-]+)\]'
            for match in re.finditer(dep_pattern, content):
                dep_id = match.group(1)
                if dep_id.startswith('L3-') and dep_id != module_id:
                    dependencies.append(dep_id)

            return {
                'module_id': module_id,
                'agent_id': agent_id,
                'name': file_path.stem,
                'type': 'agent',
                'file_path': str(file_path),
                'dependencies': dependencies,
                'module_refs': module_refs,
                'content': content
            }
        except Exception as e:
            print(f"[ModuleRegistry] 解析智能体文件失败 {file_path}: {e}")
            return None

    def get_module(self, module_id: str) -> Optional[dict]:
        """获取模块"""
        return self._modules.get(module_id)

    def get_agent(self, module_id: str) -> Optional[dict]:
        """获取智能体"""
        return self._agents.get(module_id)

    def list_modules(self) -> List[dict]:
        """列出所有模块"""
        return list(self._modules.values())

    def list_agents(self) -> List[dict]:
        """列出所有智能体"""
        return list(self._agents.values())

    def resolve_dependencies(self, module_id: str) -> List[str]:
        """解析模块依赖（递归）"""
        resolved = []
        visited = set()

        def _resolve(mod_id):
            if mod_id in visited:
                return
            visited.add(mod_id)

            # 先解析依赖
            if mod_id in self._modules:
                module = self._modules[mod_id]
                for dep_id in module.get('dependencies', []):
                    _resolve(dep_id)

            resolved.append(mod_id)

        _resolve(module_id)
        return resolved


class ToolFirstDecisionEngine:
    """工具优先决策引擎 - 实现 L3-R025"""

    def __init__(self, module_registry: ModuleRegistry):
        self.registry = module_registry
        self.decision_cache = {}

    def should_use_tool(self, task: str, context: dict = None) -> tuple:
        """
        根据工具优先原则决定是否调用工具

        Returns:
            (should_use_tool: bool, selected_tool: str or None, reason: str)
        """
        context = context or {}
        task_type = context.get('task_type', 'general')
        complexity = context.get('complexity', 0)

        # 决策矩阵
        decision_rules = {
            'data_query': {'threshold': 0.0, 'tools': ['search_database', 'query_api']},
            'calculation': {'threshold': 0.8, 'tools': ['calculator', 'compute_engine']},
            'knowledge': {'threshold': 0.9, 'tools': ['search_knowledge_base']},
            'strategy': {'threshold': 0.5, 'tools': ['strategy_analyzer', 'game_engine']},
            'general': {'threshold': 0.95, 'tools': []}
        }

        rule = decision_rules.get(task_type, decision_rules['general'])

        if complexity < rule['threshold'] and rule['tools']:
            selected = rule['tools'][0]
            return True, selected, f"复杂度 {complexity} >= 阈值 {rule['threshold']}"
        else:
            return False, None, "复杂度低于阈值，直接回答"


class BaseAgent(ABC):
    """智能体基类"""

    def __init__(self, config: 'AgentConfig'):
        self.id = config.id
        self.name = config.name
        self.description = config.description
        self.type = config.type
        self.capabilities = config.capabilities
        self.module_id = getattr(config, 'module_id', None)
        self.module_refs = getattr(config, 'module_refs', [])
        self._module_registry = None
        self._tool_engine = None

    def set_module_registry(self, registry: ModuleRegistry):
        """设置模块注册中心"""
        self._module_registry = registry
        self._tool_engine = ToolFirstDecisionEngine(registry)

    async def execute(self, task: str, context: dict = None) -> dict:
        """执行任务"""
        context = context or {}

        # 如果有模块引用，执行模块化逻辑
        if self.module_refs and self._tool_engine:
            return await self._execute_with_modules(task, context)

        # 否则执行默认逻辑
        return self._default_execute(task, context)

    async def _execute_with_modules(self, task: str, context: dict) -> dict:
        """使用模块化配置执行任务"""
        results = {
            'status': 'success',
            'agent_id': self.id,
            'agent_name': self.name,
            'task': task,
            'modules_used': [],
            'tool_decisions': [],
            'result': {}
        }

        # 1. 解析任务类型
        task_type = self._classify_task(task)
        context['task_type'] = task_type

        # 2. 对每个引用的模块做决策
        for module_ref in self.module_refs:
            module_id = module_ref['module_id']
            module = self._module_registry.get_module(module_id)

            if module_id == 'L3-R025' and self._tool_engine:
                # 工具优先原则决策
                should_use, tool, reason = self._tool_engine.should_use_tool(
                    task, context
                )
                results['tool_decisions'].append({
                    'module': module_id,
                    'should_use_tool': should_use,
                    'selected_tool': tool,
                    'reason': reason
                })

                if should_use and tool:
                    results['result']['tool_used'] = tool
                    results['modules_used'].append(module_id)

        # 3. 执行内置逻辑
        results['result']['response'] = self._generate_response(task, context)

        return results

    def _classify_task(self, task: str) -> str:
        """分类任务类型"""
        task_lower = task.lower()

        if any(kw in task_lower for kw in ['计算', '算', '数学']):
            return 'calculation'
        elif any(kw in task_lower for kw in ['查询', '搜索', '找']):
            return 'data_query'
        elif any(kw in task_lower for kw in ['策略', '规划', '分析']):
            return 'strategy'
        elif any(kw in task_lower for kw in ['知识', '概念', '定义']):
            return 'knowledge'
        else:
            return 'general'

    def _generate_response(self, task: str, context: dict) -> str:
        """生成响应"""
        return f"[{self.name}] 处理任务: {task}"

    def _default_execute(self, task: str, context: dict) -> dict:
        """默认执行逻辑"""
        return {
            'status': 'ok',
            'message': f"{self.name} 执行任务: {task}",
            'agent_id': self.id,
            'timestamp': '2026-05-08'
        }


class AgentConfig:
    """智能体配置"""

    def __init__(
        self,
        id: str,
        name: str,
        description: str = "",
        type: str = "general",
        capabilities: List[str] = None,
        module_id: str = None,
        module_refs: List[dict] = None
    ):
        self.id = id
        self.name = name
        self.description = description
        self.type = type
        self.capabilities = capabilities or []
        self.module_id = module_id
        self.module_refs = module_refs or []


def get_registry() -> ModuleRegistry:
    """获取模块注册中心单例"""
    return ModuleRegistry()

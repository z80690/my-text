# -*- coding: utf-8 -*-
"""智能体注册中心 - 增强版本
支持从markdown文件解析智能体并动态注册
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Optional

from .base import BaseAgent, AgentConfig, ModuleRegistry


class AgentRegistry:
    """智能体注册中心"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._agents = {}
            cls._instance._agent_instances = {}
            cls._instance._initialized = False
        return cls._instance
    
    def initialize(self, base_path: str = ".trae"):
        """初始化注册中心"""
        if self._initialized:
            return
        
        self._base_path = Path(base_path)
        
        # 先初始化模块注册表
        self._module_registry = ModuleRegistry()
        self._module_registry.initialize(base_path)
        
        # 扫描智能体markdown文件
        self._scan_agent_markdowns()
        
        self._initialized = True
        print(f"[AgentRegistry] 已加载 {len(self._agents)} 个智能体")
    
    def _scan_agent_markdowns(self):
        """扫描智能体markdown文件"""
        agents_path = self._base_path / "agents"
        if not agents_path.exists():
            return
        
        for md_file in agents_path.glob("*_agent.md"):
            agent_data = self._parse_agent_markdown(md_file)
            if agent_data:
                agent_id = agent_data['id']
                self._agents[agent_id] = agent_data
                print(f"  [+] 解析智能体: {agent_data['name']} ({agent_id})")
    
    def _parse_agent_markdown(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """解析智能体markdown文件"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # 提取ID
            id_match = re.search(r'\*\*ID\*\*:\s*(\w+)', content)
            if not id_match:
                return None
            
            agent_id = id_match.group(1)
            
            # 提取名称
            name_match = re.search(r'\*\*名称 / Name\*\*:\s*([^\n]+)', content)
            name = name_match.group(1) if name_match else agent_id.replace('_agent', '')
            
            # 提取模块ID (L3-Cxxx)
            module_id_match = re.search(r'(L3-C\d+)', content)
            module_id = module_id_match.group(1) if module_id_match else None
            
            # 提取类型
            type_match = re.search(r'\*\*类型 / Type\*\*:\s*(\w+)', content)
            agent_type = type_match.group(1) if type_match else "general"
            
            # 提取描述
            desc_match = re.search(r'\*\*描述 / Description\*\*:\s*([^\n]+)', content)
            description = desc_match.group(1) if desc_match else ""
            
            # 提取能力
            capabilities = []
            capability_section = re.search(r'## 能力 / Capabilities\n([\s\S]*?)(?:##|$)', content)
            if capability_section:
                for line in capability_section.group(1).strip().split('\n'):
                    if line.strip().startswith('-'):
                        cap = line.strip()[1:].split(':')[0].strip()
                        capabilities.append(cap)
            
            # 提取模块引用
            module_refs = []
            ref_pattern = r'@module\(([A-Za-z0-9_-]+)(?:@([\^~>=<!\d.]+))?\)'
            for match in re.finditer(ref_pattern, content):
                module_refs.append({
                    'module_id': match.group(1),
                    'version_constraint': match.group(2) if match.group(2) else 'latest'
                })
            
            return {
                'id': agent_id,
                'name': name,
                'type': agent_type,
                'description': description,
                'capabilities': capabilities,
                'module_id': module_id,
                'module_refs': module_refs,
                'file_path': str(file_path),
                'content': content
            }
            
        except Exception as e:
            print(f"[AgentRegistry] 解析失败 {file_path.name}: {e}")
            return None
    
    def register(self, agent: BaseAgent):
        """注册智能体实例"""
        self._agent_instances[agent.id] = agent
    
    def get(self, agent_id: str) -> Optional[BaseAgent]:
        """获取智能体实例"""
        return self._agent_instances.get(agent_id)
    
    def get_config(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """获取智能体配置"""
        return self._agents.get(agent_id)
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """列出所有智能体"""
        return list(self._agents.values())
    
    def get_agent_ids(self) -> List[str]:
        """获取所有智能体ID"""
        return list(self._agents.keys())
    
    def create_agent_instance(self, agent_id: str) -> Optional[BaseAgent]:
        """创建智能体实例"""
        agent_config = self._agents.get(agent_id)
        if not agent_config:
            return None
        
        config = AgentConfig(
            id=agent_config['id'],
            name=agent_config['name'],
            description=agent_config['description'],
            type=agent_config['type'],
            capabilities=agent_config['capabilities'],
            module_id=agent_config.get('module_id'),
            module_refs=agent_config.get('module_refs', [])
        )
        
        # 根据agent_id选择合适的实现类
        agent_class = self._get_agent_class(agent_id)
        agent = agent_class(config)
        agent.set_module_registry(self._module_registry)
        
        return agent
    
    def _get_agent_class(self, agent_id: str):
        """获取智能体实现类"""
        # 导入实现类（延迟导入避免循环依赖）
        from .implementations_v2 import (
            AssistantAgent, UserProxyAgent, CodeExecutorAgent,
            MessageFilterAgent, SocietyOfMindAgent, BaseAgentImpl,
            ClosureAgent, RoutedAgent, ToolAgent, ChessAgent,
            FastAPIAgent, StreamlitAgent, GraphRAGAgent,
            DSPyAgent, XlangAgent, SemanticRouterAgent,
            EditorAgent, WriterAgent, TeachableAgent, GRPCAgent,
            MonitorAgent, DispatcherAgent, RuleInterpreterAgent,
            NuwaAgent
        )
        
        agent_class_map = {
            'assistant_agent': AssistantAgent,
            'user_proxy_agent': UserProxyAgent,
            'code_executor_agent': CodeExecutorAgent,
            'message_filter_agent': MessageFilterAgent,
            'society_of_mind_agent': SocietyOfMindAgent,
            'base_agent': BaseAgentImpl,
            'closure_agent': ClosureAgent,
            'routed_agent': RoutedAgent,
            'tool_agent': ToolAgent,
            'chess_agent': ChessAgent,
            'fastapi_agent': FastAPIAgent,
            'streamlit_agent': StreamlitAgent,
            'graphrag_agent': GraphRAGAgent,
            'dspy_agent': DSPyAgent,
            'xlang_agent': XlangAgent,
            'semantic_router_agent': SemanticRouterAgent,
            'editor_agent': EditorAgent,
            'writer_agent': WriterAgent,
            'teachable_agent': TeachableAgent,
            'grpc_agent': GRPCAgent,
            'monitor_agent': MonitorAgent,
            'dispatcher_agent': DispatcherAgent,
            'rule_interpreter_agent': RuleInterpreterAgent,
            'nuwa_agent': NuwaAgent,
        }
        
        return agent_class_map.get(agent_id, BaseAgentImpl)


def get_registry() -> AgentRegistry:
    """获取注册中心单例"""
    return AgentRegistry()

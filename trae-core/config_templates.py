# -*- coding: utf-8 -*-
"""
一键配置模板系统 - Config Template System

提供多种预定义的配置模板，支持一键应用到项目中。
"""

import yaml
import json
from typing import Dict, Any, List
from pathlib import Path


# ============================================
# 配置模板定义
# ============================================

class ConfigTemplate:
    """配置模板"""
    
    def __init__(
        self,
        name: str,
        description: str,
        category: str,
        config: Dict[str, Any],
        recommended_agents: List[str] = None,
        recommended_skills: List[str] = None
    ):
        self.name = name
        self.description = description
        self.category = category
        self.config = config
        self.recommended_agents = recommended_agents or []
        self.recommended_skills = recommended_skills or []
    
    def apply(self, target_path: str = ".trae") -> bool:
        """
        应用配置模板
        
        Args:
            target_path: 目标路径
        
        Returns:
            是否应用成功
        """
        try:
            # 写入配置文件
            config_path = Path(target_path) / "config.yaml"
            
            # 如果配置文件已存在，备份并合并
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    existing_config = yaml.safe_load(f) or {}
                # 合并配置
                merged_config = {**existing_config, **self.config}
            else:
                merged_config = self.config
            
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(merged_config, f, default_flow_style=False, allow_unicode=True)
            
            return True
        except Exception as e:
            print(f"Failed to apply template: {e}")
            return False


# ============================================
# 预定义模板
# ============================================

class TemplateLibrary:
    """模板库"""
    
    def __init__(self):
        self._templates = {}
        self._load_default_templates()
    
    def _load_default_templates(self):
        """加载默认模板"""
        
        # 模板1：开发团队配置
        self._templates["development_team"] = ConfigTemplate(
            name="开发团队",
            description="适合软件开发团队的配置，包含代码执行、测试、部署等智能体",
            category="team",
            config={
                "bus": {"timeout": 30, "retry_limit": 3, "load_threshold": 0.8},
                "context": {"ttl_hours": 24, "history_retention_days": 30},
                "game_theory": {"enable": True, "complexity_threshold": 3},
                "monitoring": {"enable": True, "default_parallel": True},
                "workflows": {"default_template": "parallel_execution"}
            },
            recommended_agents=[
                "code_executor_agent",
                "monitor_agent",
                "dispatcher_agent",
                "tool_agent",
                "fastapi_agent"
            ],
            recommended_skills=["tdd", "improve-codebase"]
        )
        
        # 模板2：研究团队配置
        self._templates["research_team"] = ConfigTemplate(
            name="研究团队",
            description="适合研究团队的配置，包含调研、分析、文档撰写等智能体",
            category="team",
            config={
                "bus": {"timeout": 60, "retry_limit": 5, "load_threshold": 0.7},
                "context": {"ttl_hours": 72, "history_retention_days": 90},
                "game_theory": {"enable": True, "complexity_threshold": 2},
                "monitoring": {"enable": True, "default_parallel": True},
                "workflows": {"default_template": "game_theory"}
            },
            recommended_agents=[
                "society_of_mind_agent",
                "graphrag_agent",
                "writer_agent",
                "editor_agent",
                "semantic_router_agent"
            ],
            recommended_skills=["zoom-out", "grill-me", "domain-model"]
        )
        
        # 模板3：审核团队配置
        self._templates["audit_team"] = ConfigTemplate(
            name="审核团队",
            description="适合审核团队的配置，包含内容审核、质量把控等智能体",
            category="team",
            config={
                "bus": {"timeout": 30, "retry_limit": 2, "load_threshold": 0.9},
                "context": {"ttl_hours": 48, "history_retention_days": 60},
                "game_theory": {"enable": False, "complexity_threshold": 2},
                "monitoring": {"enable": True, "default_parallel": False},
                "workflows": {"default_template": "seq_flow"}
            },
            recommended_agents=[
                "message_filter_agent",
                "monitor_agent",
                "closure_agent",
                "editor_agent"
            ],
            recommended_skills=["caveman", "ubiquitous-language"]
        )
        
        # 模板4：产品设计配置
        self._templates["product_design"] = ConfigTemplate(
            name="产品设计",
            description="适合产品设计团队的配置，包含设计、用户研究、原型开发等智能体",
            category="project",
            config={
                "bus": {"timeout": 45, "retry_limit": 3, "load_threshold": 0.75},
                "context": {"ttl_hours": 24, "history_retention_days": 30},
                "game_theory": {"enable": True, "complexity_threshold": 3},
                "monitoring": {"enable": True, "default_parallel": True},
                "workflows": {"default_template": "design-an-interface"}
            },
            recommended_agents=[
                "rule_interpreter_agent",
                "graphrag_agent",
                "streamlit_agent",
                "writer_agent"
            ],
            recommended_skills=["design-an-interface", "domain-model"]
        )
        
        # 模板5：快速开发配置
        self._templates["rapid_development"] = ConfigTemplate(
            name="快速开发",
            description="适合快速原型开发的轻量配置",
            category="project",
            config={
                "bus": {"timeout": 15, "retry_limit": 2, "load_threshold": 0.9},
                "context": {"ttl_hours": 12, "history_retention_days": 14},
                "game_theory": {"enable": False, "complexity_threshold": 2},
                "monitoring": {"enable": False, "default_parallel": False},
                "workflows": {"default_template": "seq_flow"}
            },
            recommended_agents=[
                "code_executor_agent",
                "fastapi_agent",
                "streamlit_agent",
                "tool_agent"
            ],
            recommended_skills=["tdd", "caveman"]
        )
        
        # 模板6：企业级配置
        self._templates["enterprise"] = ConfigTemplate(
            name="企业级配置",
            description="适合大型企业的完整配置，包含所有高级功能",
            category="scale",
            config={
                "bus": {"timeout": 30, "retry_limit": 5, "load_threshold": 0.7},
                "context": {"ttl_hours": 72, "history_retention_days": 180},
                "game_theory": {"enable": True, "complexity_threshold": 4},
                "monitoring": {"enable": True, "default_parallel": True},
                "workflows": {"default_template": "parallel_gateway"},
                "scaling": {"enable": True, "min_instances": 3, "max_instances": 10},
                "security": {"enable": True, "audit_logs": True, "encryption": True}
            },
            recommended_agents=[
                "dispatcher_agent",
                "monitor_agent",
                "code_executor_agent",
                "message_filter_agent",
                "grpc_agent",
                "semantic_router_agent",
                "graphrag_agent",
                "nuwa_agent"
            ],
            recommended_skills=["improve-codebase", "github-triage", "to-prd", "to-issues"]
        )
        
        # 模板7：个人开发者配置
        self._templates["personal"] = ConfigTemplate(
            name="个人开发者",
            description="适合个人开发者的轻量配置",
            category="scale",
            config={
                "bus": {"timeout": 20, "retry_limit": 2, "load_threshold": 0.85},
                "context": {"ttl_hours": 12, "history_retention_days": 14},
                "game_theory": {"enable": False, "complexity_threshold": 2},
                "monitoring": {"enable": False, "default_parallel": False},
                "workflows": {"default_template": "seq_flow"}
            },
            recommended_agents=[
                "assistant_agent",
                "code_executor_agent",
                "writer_agent"
            ],
            recommended_skills=["caveman", "tdd"]
        )
    
    def get_template(self, name: str) -> Optional[ConfigTemplate]:
        """
        获取指定模板
        
        Args:
            name: 模板名称
        
        Returns:
            配置模板
        """
        return self._templates.get(name)
    
    def list_templates(self, category: str = None) -> List[Dict[str, Any]]:
        """
        列出所有模板
        
        Args:
            category: 分类过滤
        
        Returns:
            模板列表
        """
        result = []
        for name, template in self._templates.items():
            if category and template.category != category:
                continue
            result.append({
                "name": name,
                "display_name": template.name,
                "description": template.description,
                "category": template.category,
                "recommended_agents": template.recommended_agents,
                "recommended_skills": template.recommended_skills
            })
        return result
    
    def apply_template(self, name: str, target_path: str = ".trae") -> bool:
        """
        应用指定模板
        
        Args:
            name: 模板名称
            target_path: 目标路径
        
        Returns:
            是否应用成功
        """
        template = self.get_template(name)
        if not template:
            return False
        
        return template.apply(target_path)


# ============================================
# 模板管理器
# ============================================

class TemplateManager:
    """模板管理器"""
    
    def __init__(self):
        self._library = TemplateLibrary()
        self._applied_templates = []
    
    def list_available_templates(self) -> List[Dict[str, Any]]:
        """列出可用模板"""
        return self._library.list_templates()
    
    def get_template_details(self, name: str) -> Optional[Dict[str, Any]]:
        """获取模板详情"""
        template = self._library.get_template(name)
        if not template:
            return None
        
        return {
            "name": name,
            "display_name": template.name,
            "description": template.description,
            "category": template.category,
            "config": template.config,
            "recommended_agents": template.recommended_agents,
            "recommended_skills": template.recommended_skills
        }
    
    def apply_template(self, name: str) -> Dict[str, Any]:
        """
        应用模板
        
        Args:
            name: 模板名称
        
        Returns:
            应用结果
        """
        template = self._library.get_template(name)
        
        if not template:
            return {
                "status": "error",
                "message": f"模板 '{name}' 不存在"
            }
        
        success = self._library.apply_template(name)
        
        if success:
            self._applied_templates.append(name)
            return {
                "status": "success",
                "message": f"模板 '{template.name}' 应用成功",
                "applied_at": __import__('datetime').datetime.now().isoformat(),
                "recommended_agents": template.recommended_agents,
                "recommended_skills": template.recommended_skills
            }
        else:
            return {
                "status": "error",
                "message": f"模板 '{template.name}' 应用失败"
            }
    
    def batch_apply(self, templates: List[str]) -> List[Dict[str, Any]]:
        """
        批量应用模板
        
        Args:
            templates: 模板名称列表
        
        Returns:
            应用结果列表
        """
        results = []
        for name in templates:
            result = self.apply_template(name)
            results.append(result)
        return results
    
    def get_applied_templates(self) -> List[str]:
        """获取已应用的模板列表"""
        return self._applied_templates


# ============================================
# 快捷函数
# ============================================

def list_templates() -> List[Dict[str, Any]]:
    """列出所有可用模板"""
    manager = TemplateManager()
    return manager.list_available_templates()


def apply_template(name: str) -> Dict[str, Any]:
    """应用指定模板"""
    manager = TemplateManager()
    return manager.apply_template(name)


def get_template_info(name: str) -> Optional[Dict[str, Any]]:
    """获取模板信息"""
    manager = TemplateManager()
    return manager.get_template_details(name)


__all__ = [
    "ConfigTemplate",
    "TemplateLibrary",
    "TemplateManager",
    "list_templates",
    "apply_template",
    "get_template_info"
]

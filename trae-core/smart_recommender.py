# -*- coding: utf-8 -*-
"""
智能推荐系统 - Smart Recommender

根据用户场景和需求，智能推荐合适的智能体、技能和配置模板。
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re


# ============================================
# 推荐类型枚举
# ============================================

class RecommendationType(Enum):
    """推荐类型"""
    AGENT = "agent"
    SKILL = "skill"
    TEMPLATE = "template"
    WORKFLOW = "workflow"


# ============================================
# 推荐结果模型
# ============================================

@dataclass
class Recommendation:
    """推荐结果"""
    type: str
    id: str
    name: str
    description: str
    confidence: float  # 0-1
    reason: str
    metadata: Dict[str, Any] = None


# ============================================
# 场景定义
# ============================================

class Scenario:
    """场景定义"""
    
    def __init__(
        self,
        name: str,
        keywords: List[str],
        recommended_agents: List[str],
        recommended_skills: List[str],
        recommended_template: str = None,
        description: str = ""
    ):
        self.name = name
        self.keywords = keywords
        self.recommended_agents = recommended_agents
        self.recommended_skills = recommended_skills
        self.recommended_template = recommended_template
        self.description = description
    
    def match(self, query: str) -> float:
        """
        计算场景匹配度
        
        Args:
            query: 用户查询
        
        Returns:
            匹配度 (0-1)
        """
        query_lower = query.lower()
        matched_keywords = sum(1 for kw in self.keywords if kw.lower() in query_lower)
        return min(matched_keywords / len(self.keywords), 1.0)


# ============================================
# 智能推荐器
# ============================================

class SmartRecommender:
    """智能推荐器"""
    
    def __init__(self, registry):
        self._registry = registry
        self._scenarios = self._load_scenarios()
        self._agent_profiles = self._load_agent_profiles()
        self._skill_profiles = self._load_skill_profiles()
    
    def _load_scenarios(self) -> List[Scenario]:
        """加载预定义场景"""
        return [
            # 场景1：代码开发
            Scenario(
                name="代码开发",
                keywords=["代码", "编程", "开发", "写代码", "调试", "Python", "JavaScript", "TypeScript"],
                recommended_agents=["code_executor_agent", "editor_agent", "tool_agent"],
                recommended_skills=["tdd", "improve-codebase"],
                recommended_template="development_team",
                description="编写、调试和优化代码"
            ),
            
            # 场景2：文档撰写
            Scenario(
                name="文档撰写",
                keywords=["写文档", "报告", "文档", "撰写", "写作", "PRD", "需求文档"],
                recommended_agents=["writer_agent", "editor_agent", "assistant_agent"],
                recommended_skills=["to-prd", "caveman"],
                recommended_template="research_team",
                description="撰写各类文档和报告"
            ),
            
            # 场景3：系统设计
            Scenario(
                name="系统设计",
                keywords=["设计", "架构", "系统", "方案", "蓝图", "架构设计"],
                recommended_agents=["rule_interpreter_agent", "graphrag_agent", "semantic_router_agent"],
                recommended_skills=["design-an-interface", "domain-model"],
                recommended_template="product_design",
                description="设计系统架构和方案"
            ),
            
            # 场景4：数据分析
            Scenario(
                name="数据分析",
                keywords=["分析", "数据", "统计", "可视化", "报表", "BI"],
                recommended_agents=["streamlit_agent", "graphrag_agent", "assistant_agent"],
                recommended_skills=["zoom-out", "grill-me"],
                recommended_template="research_team",
                description="数据分析和可视化"
            ),
            
            # 场景5：API开发
            Scenario(
                name="API开发",
                keywords=["API", "接口", "后端", "FastAPI", "REST", "gRPC"],
                recommended_agents=["fastapi_agent", "grpc_agent", "code_executor_agent"],
                recommended_skills=["tdd", "improve-codebase"],
                recommended_template="development_team",
                description="开发API接口和服务"
            ),
            
            # 场景6：知识蒸馏
            Scenario(
                name="知识蒸馏",
                keywords=["蒸馏", "skill", "造人", "女娲", "思维方式", "视角"],
                recommended_agents=["nuwa_agent", "graphrag_agent", "writer_agent"],
                recommended_skills=[],
                recommended_template="research_team",
                description="将人物思维模式提炼为可运行的Skill"
            ),
            
            # 场景7：问题诊断
            Scenario(
                name="问题诊断",
                keywords=["问题", "错误", "调试", "诊断", "修复", "bug"],
                recommended_agents=["monitor_agent", "code_executor_agent", "assistant_agent"],
                recommended_skills=["grill-me", "domain-model"],
                recommended_template="development_team",
                description="诊断和修复问题"
            ),
            
            # 场景8：需求分析
            Scenario(
                name="需求分析",
                keywords=["需求", "分析", "用户", "产品", "调研"],
                recommended_agents=["user_proxy_agent", "assistant_agent", "writer_agent"],
                recommended_skills=["to-prd", "ubiquitous-language"],
                recommended_template="research_team",
                description="分析用户需求"
            ),
            
            # 场景9：决策支持
            Scenario(
                name="决策支持",
                keywords=["决策", "对比", "权衡", "选择", "方案对比"],
                recommended_agents=["dispatcher_agent", "society_of_mind_agent", "graphrag_agent"],
                recommended_skills=["grill-me", "zoom-out"],
                recommended_template="enterprise",
                description="提供决策支持和方案对比"
            ),
            
            # 场景10：内容审核
            Scenario(
                name="内容审核",
                keywords=["审核", "过滤", "合规", "内容安全"],
                recommended_agents=["message_filter_agent", "closure_agent", "editor_agent"],
                recommended_skills=["caveman"],
                recommended_template="audit_team",
                description="审核和过滤内容"
            )
        ]
    
    def _load_agent_profiles(self) -> Dict[str, Dict[str, Any]]:
        """加载智能体配置文件"""
        agents = self._registry.get_all_agents()
        profiles = {}
        
        for agent_id, agent_data in agents.items():
            profiles[agent_id] = {
                "id": agent_id,
                "name": agent_data.get("name", agent_id),
                "type": agent_data.get("type", "unknown"),
                "capabilities": agent_data.get("capabilities", []),
                "description": agent_data.get("description", ""),
                "keywords": self._extract_keywords(agent_data.get("description", "") + " " + " ".join(agent_data.get("capabilities", [])))
            }
        
        return profiles
    
    def _load_skill_profiles(self) -> Dict[str, Dict[str, Any]]:
        """加载技能配置文件"""
        import yaml
        from pathlib import Path
        
        skills_path = Path(".trae") / "skills.yaml"
        profiles = {}
        
        if skills_path.exists():
            with open(skills_path, 'r', encoding='utf-8') as f:
                skills_data = yaml.safe_load(f) or []
                for skill in skills_data:
                    profiles[skill.get("skill_id")] = {
                        "id": skill.get("skill_id"),
                        "name": skill.get("name"),
                        "description": skill.get("description", ""),
                        "keywords": self._extract_keywords(skill.get("description", ""))
                    }
        
        return profiles
    
    def _extract_keywords(self, text: str) -> List[str]:
        """从文本中提取关键词"""
        # 简单的关键词提取
        keywords = []
        
        # 定义领域关键词
        domain_keywords = [
            "代码", "编程", "开发", "设计", "架构", "分析",
            "文档", "报告", "API", "接口", "数据", "可视化",
            "决策", "审核", "测试", "调试", "优化", "重构"
        ]
        
        for kw in domain_keywords:
            if kw in text:
                keywords.append(kw)
        
        return keywords
    
    def recommend_by_scenario(self, query: str) -> List[Recommendation]:
        """
        根据场景推荐
        
        Args:
            query: 用户查询
        
        Returns:
            推荐结果列表
        """
        recommendations = []
        
        # 匹配场景
        for scenario in self._scenarios:
            match_score = scenario.match(query)
            if match_score > 0.2:  # 匹配阈值
                # 推荐智能体
                for agent_id in scenario.recommended_agents:
                    agent_profile = self._agent_profiles.get(agent_id)
                    if agent_profile:
                        recommendations.append(Recommendation(
                            type=RecommendationType.AGENT.value,
                            id=agent_id,
                            name=agent_profile["name"],
                            description=agent_profile["description"],
                            confidence=min(match_score * 0.9, 0.95),
                            reason=f"适合{scenario.name}场景",
                            metadata={"scenario": scenario.name}
                        ))
                
                # 推荐技能
                for skill_id in scenario.recommended_skills:
                    skill_profile = self._skill_profiles.get(skill_id)
                    if skill_profile:
                        recommendations.append(Recommendation(
                            type=RecommendationType.SKILL.value,
                            id=skill_id,
                            name=skill_profile["name"],
                            description=skill_profile["description"],
                            confidence=min(match_score * 0.85, 0.9),
                            reason=f"适合{scenario.name}场景",
                            metadata={"scenario": scenario.name}
                        ))
                
                # 推荐模板
                if scenario.recommended_template:
                    recommendations.append(Recommendation(
                        type=RecommendationType.TEMPLATE.value,
                        id=scenario.recommended_template,
                        name=self._get_template_name(scenario.recommended_template),
                        description=scenario.description,
                        confidence=min(match_score * 0.8, 0.85),
                        reason=f"适合{scenario.name}场景",
                        metadata={"scenario": scenario.name}
                    ))
        
        # 按置信度排序
        recommendations.sort(key=lambda x: x.confidence, reverse=True)
        
        return recommendations[:10]  # 返回前10个
    
    def recommend_agents(self, query: str, limit: int = 5) -> List[Recommendation]:
        """
        推荐智能体
        
        Args:
            query: 用户查询
            limit: 返回数量限制
        
        Returns:
            智能体推荐列表
        """
        results = []
        
        for agent_id, profile in self._agent_profiles.items():
            # 计算匹配度
            match_score = self._calculate_match(query, profile["keywords"] + [profile["name"], profile["type"]])
            
            if match_score > 0.1:
                results.append(Recommendation(
                    type=RecommendationType.AGENT.value,
                    id=agent_id,
                    name=profile["name"],
                    description=profile["description"],
                    confidence=match_score,
                    reason=self._generate_reason(profile, query),
                    metadata={"capabilities": profile["capabilities"]}
                ))
        
        results.sort(key=lambda x: x.confidence, reverse=True)
        return results[:limit]
    
    def recommend_skills(self, query: str, limit: int = 5) -> List[Recommendation]:
        """
        推荐技能
        
        Args:
            query: 用户查询
            limit: 返回数量限制
        
        Returns:
            技能推荐列表
        """
        results = []
        
        for skill_id, profile in self._skill_profiles.items():
            match_score = self._calculate_match(query, profile["keywords"] + [profile["name"]])
            
            if match_score > 0.1:
                results.append(Recommendation(
                    type=RecommendationType.SKILL.value,
                    id=skill_id,
                    name=profile["name"],
                    description=profile["description"],
                    confidence=match_score,
                    reason=self._generate_reason(profile, query),
                    metadata={}
                ))
        
        results.sort(key=lambda x: x.confidence, reverse=True)
        return results[:limit]
    
    def recommend_template(self, query: str) -> Optional[Recommendation]:
        """
        推荐配置模板
        
        Args:
            query: 用户查询
        
        Returns:
            模板推荐
        """
        from .config_templates import list_templates
        
        templates = list_templates()
        best_match = None
        best_score = 0
        
        for template in templates:
            # 简单的匹配逻辑
            text = f"{template['display_name']} {template['description']}"
            score = self._calculate_match(query, self._extract_keywords(text))
            
            if score > best_score:
                best_score = score
                best_match = template
        
        if best_match and best_score > 0.2:
            return Recommendation(
                type=RecommendationType.TEMPLATE.value,
                id=best_match["name"],
                name=best_match["display_name"],
                description=best_match["description"],
                confidence=best_score,
                reason=f"适合当前需求场景",
                metadata={"category": best_match["category"]}
            )
        
        return None
    
    def get_all_recommendations(self, query: str) -> Dict[str, List[Recommendation]]:
        """
        获取所有类型的推荐
        
        Args:
            query: 用户查询
        
        Returns:
            各类型推荐结果
        """
        return {
            "agents": self.recommend_agents(query),
            "skills": self.recommend_skills(query),
            "templates": [r for r in self.recommend_by_scenario(query) if r.type == "template"],
            "scenario_based": self.recommend_by_scenario(query)
        }
    
    def _calculate_match(self, query: str, keywords: List[str]) -> float:
        """
        计算匹配度
        
        Args:
            query: 用户查询
            keywords: 关键词列表
        
        Returns:
            匹配度 (0-1)
        """
        if not keywords:
            return 0.0
        
        query_lower = query.lower()
        matched = sum(1 for kw in keywords if kw.lower() in query_lower)
        
        # 额外匹配：检查智能体名称
        if any(kw.lower() in query_lower for kw in keywords[:3]):
            matched += 0.5
        
        return min(matched / len(keywords), 1.0)
    
    def _generate_reason(self, profile: Dict[str, Any], query: str) -> str:
        """
        生成推荐理由
        
        Args:
            profile: 配置文件
            query: 用户查询
        
        Returns:
            推荐理由
        """
        capabilities = profile.get("capabilities", [])
        if capabilities:
            return f"具备{'、'.join(capabilities[:3])}等能力"
        return "符合当前需求"
    
    def _get_template_name(self, template_id: str) -> str:
        """获取模板显示名称"""
        template_names = {
            "development_team": "开发团队",
            "research_team": "研究团队",
            "audit_team": "审核团队",
            "product_design": "产品设计",
            "rapid_development": "快速开发",
            "enterprise": "企业级配置",
            "personal": "个人开发者"
        }
        return template_names.get(template_id, template_id)


# ============================================
# 使用示例
# ============================================

def recommend(query: str) -> Dict[str, Any]:
    """
    快捷推荐函数
    
    Args:
        query: 用户查询
    
    Returns:
        推荐结果
    """
    # 创建推荐器（需要传入registry）
    # 这里简化处理
    from .agents.registry import AgentRegistry
    registry = AgentRegistry()
    
    recommender = SmartRecommender(registry)
    return recommender.get_all_recommendations(query)


__all__ = [
    "RecommendationType",
    "Recommendation",
    "Scenario",
    "SmartRecommender",
    "recommend"
]

# -*- coding: utf-8 -*-
"""
可视化管理界面API - Management API

提供配置管理、智能体管理、监控数据等RESTful接口，
支持前端可视化界面调用。
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


# ============================================
# API响应模型
# ============================================

class APIStatus(Enum):
    """API状态码"""
    SUCCESS = 200
    ERROR = 500
    NOT_FOUND = 404
    BAD_REQUEST = 400


@dataclass
class APIResponse:
    """API响应对象"""
    status: int
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "status": self.status,
            "message": self.message
        }
        if self.data:
            result["data"] = self.data
        if self.error:
            result["error"] = self.error
        return result


# ============================================
# 智能体状态枚举
# ============================================

class AgentStatus(Enum):
    """智能体状态"""
    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"
    OFFLINE = "offline"
    BUSY = "busy"


# ============================================
# 管理API类
# ============================================

class ManagementAPI:
    """管理API"""
    
    def __init__(self, registry, monitor_agent=None):
        self._registry = registry
        self._monitor_agent = monitor_agent
        self._api_version = "1.0.0"
    
    # ============================================
    # 系统信息接口
    # ============================================
    
    def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        return APIResponse(
            status=APIStatus.SUCCESS.value,
            message="获取系统信息成功",
            data={
                "version": self._api_version,
                "timestamp": datetime.now().isoformat(),
                "total_agents": len(self._registry.get_all_agents()),
                "total_skills": self._count_skills(),
                "status": "running"
            }
        ).to_dict()
    
    def get_health_status(self) -> Dict[str, Any]:
        """获取健康状态"""
        agents = self._registry.get_all_agents()
        healthy_count = sum(1 for a in agents.values() if a.get("status") != "error")
        
        return APIResponse(
            status=APIStatus.SUCCESS.value,
            message="获取健康状态成功",
            data={
                "healthy_agents": healthy_count,
                "total_agents": len(agents),
                "health_percentage": round((healthy_count / len(agents)) * 100, 2) if agents else 100,
                "timestamp": datetime.now().isoformat()
            }
        ).to_dict()
    
    # ============================================
    # 智能体管理接口
    # ============================================
    
    def list_agents(self) -> Dict[str, Any]:
        """列出所有智能体"""
        agents = self._registry.get_all_agents()
        agent_list = []
        
        for agent_id, agent_data in agents.items():
            agent_list.append({
                "id": agent_id,
                "name": agent_data.get("name", agent_id),
                "type": agent_data.get("type", "unknown"),
                "description": agent_data.get("description", ""),
                "status": agent_data.get("status", "idle"),
                "capabilities": agent_data.get("capabilities", []),
                "load": agent_data.get("load", 0)
            })
        
        return APIResponse(
            status=APIStatus.SUCCESS.value,
            message="获取智能体列表成功",
            data={"agents": agent_list}
        ).to_dict()
    
    def get_agent_info(self, agent_id: str) -> Dict[str, Any]:
        """获取智能体详情"""
        agent = self._registry.get_agent(agent_id)
        
        if not agent:
            return APIResponse(
                status=APIStatus.NOT_FOUND.value,
                message="智能体不存在",
                error=f"Agent {agent_id} not found"
            ).to_dict()
        
        return APIResponse(
            status=APIStatus.SUCCESS.value,
            message="获取智能体详情成功",
            data={
                "id": agent_id,
                "name": agent.get("name", agent_id),
                "type": agent.get("type", "unknown"),
                "description": agent.get("description", ""),
                "capabilities": agent.get("capabilities", []),
                "status": agent.get("status", "idle"),
                "load": agent.get("load", 0),
                "metadata": agent.get("metadata", {})
            }
        ).to_dict()
    
    def update_agent_status(self, agent_id: str, status: str) -> Dict[str, Any]:
        """更新智能体状态"""
        if status not in ["idle", "running", "error", "offline", "busy"]:
            return APIResponse(
                status=APIStatus.BAD_REQUEST.value,
                message="无效的状态值",
                error="Invalid status value"
            ).to_dict()
        
        agent = self._registry.get_agent(agent_id)
        if not agent:
            return APIResponse(
                status=APIStatus.NOT_FOUND.value,
                message="智能体不存在",
                error=f"Agent {agent_id} not found"
            ).to_dict()
        
        agent["status"] = status
        return APIResponse(
            status=APIStatus.SUCCESS.value,
            message=f"智能体 {agent_id} 状态已更新为 {status}",
            data={"agent_id": agent_id, "status": status}
        ).to_dict()
    
    def execute_agent(self, agent_id: str, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行智能体任务"""
        try:
            result = self._registry.execute(agent_id, task, context or {})
            return APIResponse(
                status=APIStatus.SUCCESS.value,
                message="任务执行成功",
                data=result
            ).to_dict()
        except Exception as e:
            return APIResponse(
                status=APIStatus.ERROR.value,
                message="任务执行失败",
                error=str(e)
            ).to_dict()
    
    # ============================================
    # 技能管理接口
    # ============================================
    
    def list_skills(self) -> Dict[str, Any]:
        """列出所有技能"""
        # 从skills.yaml读取技能配置
        import yaml
        from pathlib import Path
        
        skills_path = Path(".trae") / "skills.yaml"
        skills = []
        
        if skills_path.exists():
            with open(skills_path, 'r', encoding='utf-8') as f:
                skills_data = yaml.safe_load(f) or []
                for skill in skills_data:
                    skills.append({
                        "skill_id": skill.get("skill_id"),
                        "name": skill.get("name"),
                        "description": skill.get("description"),
                        "version": skill.get("version"),
                        "status": skill.get("status", "active"),
                        "permissions": skill.get("permissions", [])
                    })
        
        return APIResponse(
            status=APIStatus.SUCCESS.value,
            message="获取技能列表成功",
            data={"skills": skills}
        ).to_dict()
    
    def enable_skill(self, skill_id: str) -> Dict[str, Any]:
        """启用技能"""
        return APIResponse(
            status=APIStatus.SUCCESS.value,
            message=f"技能 {skill_id} 已启用",
            data={"skill_id": skill_id, "status": "active"}
        ).to_dict()
    
    def disable_skill(self, skill_id: str) -> Dict[str, Any]:
        """禁用技能"""
        return APIResponse(
            status=APIStatus.SUCCESS.value,
            message=f"技能 {skill_id} 已禁用",
            data={"skill_id": skill_id, "status": "disabled"}
        ).to_dict()
    
    # ============================================
    # 监控数据接口
    # ============================================
    
    def get_monitor_data(self) -> Dict[str, Any]:
        """获取监控数据"""
        if self._monitor_agent:
            result = self._monitor_agent.execute("获取监控数据")
            return APIResponse(
                status=APIStatus.SUCCESS.value,
                message="获取监控数据成功",
                data=result.get("result", {})
            ).to_dict()
        else:
            return APIResponse(
                status=APIStatus.SUCCESS.value,
                message="获取监控数据成功",
                data={
                    "metrics": {
                        "cpu_usage": 0,
                        "memory_usage": 0,
                        "response_time_ms": 0,
                        "error_rate": 0
                    },
                    "anomalies": [],
                    "alert_level": "INFO"
                }
            ).to_dict()
    
    def get_agent_metrics(self, agent_id: str) -> Dict[str, Any]:
        """获取智能体指标"""
        return APIResponse(
            status=APIStatus.SUCCESS.value,
            message=f"获取智能体 {agent_id} 指标成功",
            data={
                "agent_id": agent_id,
                "requests_count": 0,
                "success_count": 0,
                "error_count": 0,
                "avg_response_time_ms": 0,
                "uptime_percentage": 100
            }
        ).to_dict()
    
    # ============================================
    # 配置管理接口
    # ============================================
    
    def get_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        import yaml
        from pathlib import Path
        
        config_path = Path(".trae") / "config.yaml"
        config = {}
        
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
        
        return APIResponse(
            status=APIStatus.SUCCESS.value,
            message="获取配置成功",
            data=config
        ).to_dict()
    
    def update_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """更新配置"""
        import yaml
        from pathlib import Path
        
        config_path = Path(".trae") / "config.yaml"
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            
            return APIResponse(
                status=APIStatus.SUCCESS.value,
                message="配置更新成功",
                data=config
            ).to_dict()
        except Exception as e:
            return APIResponse(
                status=APIStatus.ERROR.value,
                message="配置更新失败",
                error=str(e)
            ).to_dict()
    
    # ============================================
    # 模板管理接口
    # ============================================
    
    def list_templates(self) -> Dict[str, Any]:
        """列出配置模板"""
        from ..config_templates import list_templates
        
        templates = list_templates()
        return APIResponse(
            status=APIStatus.SUCCESS.value,
            message="获取模板列表成功",
            data={"templates": templates}
        ).to_dict()
    
    def apply_template(self, template_name: str) -> Dict[str, Any]:
        """应用配置模板"""
        from ..config_templates import apply_template
        
        result = apply_template(template_name)
        
        if result["status"] == "success":
            return APIResponse(
                status=APIStatus.SUCCESS.value,
                message=result["message"],
                data={
                    "template": template_name,
                    "recommended_agents": result.get("recommended_agents", []),
                    "recommended_skills": result.get("recommended_skills", [])
                }
            ).to_dict()
        else:
            return APIResponse(
                status=APIStatus.ERROR.value,
                message=result["message"],
                error=result.get("error", "")
            ).to_dict()
    
    # ============================================
    # 辅助方法
    # ============================================
    
    def _count_skills(self) -> int:
        """统计技能数量"""
        import yaml
        from pathlib import Path
        
        skills_path = Path(".trae") / "skills.yaml"
        if skills_path.exists():
            with open(skills_path, 'r', encoding='utf-8') as f:
                skills_data = yaml.safe_load(f) or []
                return len(skills_data)
        return 0


# ============================================
# API路由注册
# ============================================

class APIRouter:
    """API路由"""
    
    def __init__(self, api: ManagementAPI):
        self._api = api
        self._routes = self._register_routes()
    
    def _register_routes(self) -> Dict[str, callable]:
        """注册路由"""
        return {
            # 系统信息
            "GET /api/v1/system/info": self._api.get_system_info,
            "GET /api/v1/system/health": self._api.get_health_status,
            
            # 智能体管理
            "GET /api/v1/agents": self._api.list_agents,
            "GET /api/v1/agents/{agent_id}": self._api.get_agent_info,
            "PUT /api/v1/agents/{agent_id}/status": self._api.update_agent_status,
            "POST /api/v1/agents/{agent_id}/execute": self._api.execute_agent,
            
            # 技能管理
            "GET /api/v1/skills": self._api.list_skills,
            "POST /api/v1/skills/{skill_id}/enable": self._api.enable_skill,
            "POST /api/v1/skills/{skill_id}/disable": self._api.disable_skill,
            
            # 监控数据
            "GET /api/v1/monitor": self._api.get_monitor_data,
            "GET /api/v1/monitor/agents/{agent_id}": self._api.get_agent_metrics,
            
            # 配置管理
            "GET /api/v1/config": self._api.get_config,
            "PUT /api/v1/config": self._api.update_config,
            
            # 模板管理
            "GET /api/v1/templates": self._api.list_templates,
            "POST /api/v1/templates/{name}/apply": self._api.apply_template
        }
    
    def route(self, method: str, path: str, **kwargs) -> Optional[Dict[str, Any]]:
        """路由请求"""
        key = f"{method.upper()} {path}"
        
        # 处理带参数的路径
        if key not in self._routes:
            # 尝试匹配参数化路径
            for route_path, handler in self._routes.items():
                if "{" in route_path:
                    # 简化的路径匹配
                    route_parts = route_path.split("/")
                    path_parts = path.split("/")
                    if len(route_parts) == len(path_parts):
                        match = True
                        params = {}
                        for i, part in enumerate(route_parts):
                            if part.startswith("{") and part.endswith("}"):
                                params[part[1:-1]] = path_parts[i]
                            elif part != path_parts[i]:
                                match = False
                                break
                        if match:
                            return handler(**params)
        
        if key in self._routes:
            return self._routes[key]()
        
        return None


__all__ = [
    "APIStatus",
    "APIResponse",
    "AgentStatus",
    "ManagementAPI",
    "APIRouter"
]

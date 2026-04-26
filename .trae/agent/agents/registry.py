from typing import Dict, List, Any, Optional
import os
import importlib
import inspect
from .base import BaseAgent, AgentConfig

class AgentRegistry:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._agents = {}
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._agents: Dict[str, BaseAgent] = {}
            self._initialized = True

    def register(self, agent: BaseAgent):
        self._agents[agent.id] = agent
        print(f"Registered agent: {agent.name} ({agent.id})")

    def unregister(self, agent_id: str):
        if agent_id in self._agents:
            del self._agents[agent_id]

    def get(self, agent_id: str) -> Optional[BaseAgent]:
        return self._agents.get(agent_id)

    def list_agents(self) -> List[Dict[str, Any]]:
        return [agent.get_metadata() for agent in self._agents.values()]

    def execute(self, agent_id: str, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        agent = self.get(agent_id)
        if not agent:
            return {"status": "error", "message": f"Agent {agent_id} not found"}
        try:
            result = agent.execute(task, context or {})
            return {
                "status": "success",
                "agent_id": agent_id,
                "agent_name": agent.name,
                "task": task,
                "result": result
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def load_agents_from_module(self, module):
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, BaseAgent) and obj != BaseAgent:
                if hasattr(module, '_agent_config'):
                    config = module._agent_config
                    agent = obj(config)
                    self.register(agent)

_registry = AgentRegistry()

def get_registry() -> AgentRegistry:
    return _registry

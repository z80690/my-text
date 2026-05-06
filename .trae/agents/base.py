from abc import ABC, abstractmethod
from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class AgentConfig:
    id: str
    name: str
    description: str
    type: str
    capabilities: List[str] = field(default_factory=list)

class BaseAgent(ABC):
    def __init__(self, config: AgentConfig):
        self.config = config
        self.id = config.id
        self.name = config.name
        self.description = config.description
        self.type = config.type
        self.capabilities = config.capabilities

    @abstractmethod
    def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        pass

    def get_info(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "capabilities": self.capabilities
        }

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.type
        }

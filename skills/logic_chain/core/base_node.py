# -*- coding: utf-8 -*-
"""Base node classes for Logic Chain Framework."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional
from datetime import datetime


class NodeType(Enum):
    """Types of nodes in the chain."""

    SKILL = "skill"
    CONDITION = "condition"
    IF_ELSE = "if_else"
    PARALLEL = "parallel"
    SEQUENTIAL = "sequential"
    START = "start"
    END = "end"


class NodeStatus(Enum):
    """Execution status of a node."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class NodeResult:
    """Result of node execution."""

    success: bool
    data: Any = None
    error: Optional[str] = None
    node_id: str = ""
    node_name: str = ""
    status: NodeStatus = NodeStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "node_name": self.node_name,
            "success": self.success,
            "status": self.status.value,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata,
        }


class BaseNode(ABC):
    """Abstract base class for all chain nodes."""

    def __init__(
        self,
        node_id: str,
        node_type: NodeType,
        name: str,
        description: str = "",
        metadata: Dict[str, Any] = None,
    ):
        self.node_id = node_id
        self.node_type = node_type
        self.name = name
        self.description = description
        self.metadata = metadata or {}
        self.status = NodeStatus.PENDING
        self.result: Optional[NodeResult] = None

    @abstractmethod
    async def execute(self, context: "ChainContext") -> NodeResult:
        """Execute the node logic.

        Args:
            context: Chain execution context containing shared state.

        Returns:
            NodeResult containing execution outcome.
        """
        pass

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} '{self.name}' ({self.node_id})>"

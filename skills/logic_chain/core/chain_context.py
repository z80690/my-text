# -*- coding: utf-8 -*-
"""Chain execution context for sharing state between nodes."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from datetime import datetime


@dataclass
class ChainContext:
    """Context shared across all nodes in a chain execution.

    Attributes:
        chain_id: Unique identifier for this chain execution.
        chain_name: Name of the chain being executed.
        variables: Shared variables dictionary for data passing.
        node_results: Results from previously executed nodes.
        current_node_id: ID of the currently executing node.
        start_time: When the chain execution started.
        user_data: User-provided input data.
        metadata: Additional metadata for the execution.
    """

    chain_id: str
    chain_name: str
    variables: Dict[str, Any] = field(default_factory=dict)
    node_results: Dict[str, Any] = field(default_factory=dict)
    current_node_id: str = ""
    start_time: Optional[datetime] = None
    user_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a variable value from context."""
        return self.variables.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a variable value in context."""
        self.variables[key] = value

    def has(self, key: str) -> bool:
        """Check if a variable exists in context."""
        return key in self.variables

    def update_node_result(self, node_id: str, result: Any) -> None:
        """Store a node's execution result."""
        self.node_results[node_id] = result

    def get_node_result(self, node_id: str, default: Any = None) -> Any:
        """Get a previously stored node result."""
        return self.node_results.get(node_id, default)

    def to_dict(self) -> dict:
        return {
            "chain_id": self.chain_id,
            "chain_name": self.chain_name,
            "variables": self.variables,
            "node_results": self.node_results,
            "user_data": self.user_data,
            "metadata": self.metadata,
        }

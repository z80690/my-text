# -*- coding: utf-8 -*-
"""Chain Executor - Core execution engine for Logic Chain Framework."""

import asyncio
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from .base_node import BaseNode, NodeResult, NodeStatus, NodeType
from .chain_context import ChainContext


@dataclass
class ExecutionConfig:
    """Configuration for chain execution."""

    max_retries: int = 3
    timeout_seconds: int = 300
    continue_on_error: bool = False
    debug_mode: bool = False


class ChainExecutor:
    """Core executor for running logic chains.

    Supports:
    - Sequential execution of nodes
    - Conditional branching (IF/ELSE)
    - Parallel execution
    - Error handling and retries
    - Debug and tracing
    """

    def __init__(self, config: ExecutionConfig = None):
        self.config = config or ExecutionConfig()
        self.nodes: Dict[str, BaseNode] = {}
        self.execution_history: List[Dict] = []

    def register_node(self, node: BaseNode) -> None:
        """Register a node to the executor.

        Args:
            node: The node to register.
        """
        self.nodes[node.node_id] = node

    def register_nodes(self, nodes: List[BaseNode]) -> None:
        """Register multiple nodes at once.

        Args:
            nodes: List of nodes to register.
        """
        for node in nodes:
            self.register_node(node)

    def get_node(self, node_id: str) -> Optional[BaseNode]:
        """Get a node by ID.

        Args:
            node_id: The node identifier.

        Returns:
            The node if found, None otherwise.
        """
        return self.nodes.get(node_id)

    async def execute_chain(
        self,
        chain_name: str,
        start_node_id: str,
        user_data: Dict[str, Any] = None,
        initial_variables: Dict[str, Any] = None,
    ) -> ChainContext:
        """Execute a chain from a starting node.

        Args:
            chain_name: Name of the chain.
            start_node_id: ID of the node to start execution from.
            user_data: Input data for the chain.
            initial_variables: Initial variables to set in context.

        Returns:
            ChainContext containing execution results and state.
        """
        chain_id = str(uuid.uuid4())[:8]
        context = ChainContext(
            chain_id=chain_id,
            chain_name=chain_name,
            user_data=user_data or {},
            variables=initial_variables or {},
            start_time=datetime.now(),
        )

        if self.config.debug_mode:
            print(f"[DEBUG] Starting chain '{chain_name}' (ID: {chain_id})")

        await self._execute_node(start_node_id, context)

        context.end_time = datetime.now()
        self.execution_history.append(context.to_dict())

        return context

    async def _execute_node(self, node_id: str, context: ChainContext) -> NodeResult:
        """Execute a single node and handle its result.

        Args:
            node_id: ID of the node to execute.
            context: Chain execution context.

        Returns:
            NodeResult from the execution.
        """
        node = self.nodes.get(node_id)
        if not node:
            return NodeResult(
                success=False,
                error=f"Node '{node_id}' not found",
                node_id=node_id,
                status=NodeStatus.FAILED,
            )

        context.current_node_id = node_id
        node.status = NodeStatus.RUNNING
        node.result = None

        if self.config.debug_mode:
            print(f"[DEBUG] Executing node '{node.name}' ({node.node_type.value})")

        try:
            result = await self._execute_with_retry(node, context)
            node.result = result
            node.status = NodeStatus.COMPLETED if result.success else NodeStatus.FAILED
            context.update_node_result(node_id, result.to_dict())

            if node.status == NodeStatus.FAILED and not self.config.continue_on_error:
                return result

            next_node_id = self._get_next_node(node, result, context)
            if next_node_id:
                await self._execute_node(next_node_id, context)

            return result

        except Exception as e:
            error_result = NodeResult(
                success=False,
                error=str(e),
                node_id=node_id,
                node_name=node.name,
                status=NodeStatus.FAILED,
            )
            node.result = error_result
            node.status = NodeStatus.FAILED
            return error_result

    async def _execute_with_retry(
        self, node: BaseNode, context: ChainContext
    ) -> NodeResult:
        """Execute a node with retry logic.

        Args:
            node: The node to execute.
            context: Chain execution context.

        Returns:
            NodeResult from the execution.
        """
        last_error = None

        for attempt in range(self.config.max_retries):
            try:
                return await node.execute(context)
            except Exception as e:
                last_error = e
                if self.config.debug_mode:
                    print(f"[DEBUG] Retry {attempt + 1}/{self.config.max_retries} for node '{node.name}'")

        return NodeResult(
            success=False,
            error=f"Failed after {self.config.max_retries} attempts: {str(last_error)}",
            node_id=node.node_id,
            node_name=node.name,
            status=NodeStatus.FAILED,
        )

    def _get_next_node(
        self, node: BaseNode, result: NodeResult, context: ChainContext
    ) -> Optional[str]:
        """Determine the next node to execute based on current node result.

        Args:
            node: The current node.
            result: Result from the node execution.
            context: Chain execution context.

        Returns:
            ID of the next node to execute, or None to stop.
        """
        next_mapping = node.metadata.get("next", {})
        node_id = result.node_id

        if result.node_type == NodeType.IF_ELSE:
            condition_passed = result.data.get("condition_met", False)
            return next_mapping.get("true") if condition_passed else next_mapping.get("false")

        if result.node_type in (NodeType.SKILL, NodeType.CONDITION, NodeType.SEQUENTIAL):
            return next_mapping.get("default")

        if result.node_type == NodeType.END:
            return None

        return next_mapping.get("default")

    def load_from_dict(self, chain_config: Dict) -> None:
        """Load and build a chain from a dictionary configuration.

        Args:
            chain_config: Chain configuration dictionary.
        """
        from ..steps.skill_node import SkillNode
        from ..steps.condition_node import ConditionNode, IfElseNode
        from ..steps.parallel_node import ParallelNode

        for node_data in chain_config.get("nodes", []):
            node_type = NodeType(node_data.get("node_type", "skill"))

            if node_type == NodeType.SKILL:
                node = SkillNode(
                    node_id=node_data["node_id"],
                    name=node_data["name"],
                    skill_name=node_data.get("skill_name", ""),
                    parameters=node_data.get("parameters", {}),
                    output_key=node_data.get("output_key"),
                )
            elif node_type == NodeType.CONDITION:
                node = ConditionNode(
                    node_id=node_data["node_id"],
                    name=node_data["name"],
                    condition=node_data.get("condition", ""),
                    output_key=node_data.get("output_key"),
                )
            elif node_type == NodeType.IF_ELSE:
                node = IfElseNode(
                    node_id=node_data["node_id"],
                    name=node_data["name"],
                )
            elif node_type == NodeType.PARALLEL:
                node = ParallelNode(
                    node_id=node_data["node_id"],
                    name=node_data["name"],
                    parallel_nodes=node_data.get("parallel_nodes", []),
                )
            else:
                continue

            node.metadata = node_data.get("metadata", {})
            self.register_node(node)

    def visualize_chain(self, start_node_id: str) -> str:
        """Generate a text-based visualization of the chain.

        Args:
            start_node_id: Starting node ID.

        Returns:
            String representation of the chain.
        """
        lines = []
        visited = set()

        def build_viz(node_id: str, indent: int = 0) -> None:
            if node_id in visited:
                lines.append(f"{'  ' * indent}[{node_id}] -> (circular)")
                return
            visited.add(node_id)

            node = self.nodes.get(node_id)
            if not node:
                return

            prefix = "  " * indent
            status_icon = {
                NodeStatus.PENDING: "○",
                NodeStatus.RUNNING: "◐",
                NodeStatus.COMPLETED: "✓",
                NodeStatus.FAILED: "✗",
                NodeStatus.SKIPPED: "⊘",
            }.get(node.status, "?")

            lines.append(f"{prefix}{status_icon} [{node.node_id}] {node.name} ({node.node_type.value})")

            if node.metadata.get("next"):
                for key, next_id in node.metadata["next"].items():
                    if key == "default":
                        build_viz(next_id, indent + 1)
                    else:
                        lines.append(f"{prefix}  └─{key}:")
                        build_viz(next_id, indent + 2)

        build_viz(start_node_id)
        return "\n".join(lines)

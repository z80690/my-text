# -*- coding: utf-8 -*-
"""Parallel Node - Executes multiple nodes concurrently."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime

from ..core.base_node import BaseNode, NodeType, NodeResult, NodeStatus
from ..core.chain_context import ChainContext


@dataclass
class ParallelResult:
    """Result of parallel node execution."""

    node_id: str
    results: List[NodeResult] = field(default_factory=list)
    success_count: int = 0
    failure_count: int = 0


class ParallelNode(BaseNode):
    """Node that executes multiple child nodes in parallel.

    Waits for all children to complete before returning.
    """

    def __init__(
        self,
        node_id: str,
        name: str,
        parallel_nodes: List[str] = None,
        wait_for_all: bool = True,
    ):
        super().__init__(node_id, NodeType.PARALLEL, name)
        self.parallel_nodes = parallel_nodes or []
        self.wait_for_all = wait_for_all

    async def execute(self, context: ChainContext) -> NodeResult:
        """Execute multiple nodes in parallel.

        Args:
            context: Chain execution context.

        Returns:
            NodeResult with parallel execution outcomes.
        """
        result = NodeResult(
            node_id=self.node_id,
            node_name=self.name,
            status=NodeStatus.RUNNING,
            start_time=datetime.now(),
        )

        try:
            executor = context.get("executor")
            if not executor:
                result.success = False
                result.error = "No executor available in context"
                result.status = NodeStatus.FAILED
                return result

            from ..core.chain_executor import ChainExecutor

            if not isinstance(executor, ChainExecutor):
                result.success = False
                result.error = "Invalid executor in context"
                result.status = NodeStatus.FAILED
                return result

            tasks = []
            for node_id in self.parallel_nodes:
                task = self._execute_branch(node_id, context)
                tasks.append(task)

            branch_results = await asyncio.gather(*tasks, return_exceptions=True)

            processed_results = []
            success_count = 0
            failure_count = 0

            for i, branch_result in enumerate(branch_results):
                if isinstance(branch_result, Exception):
                    node_id = self.parallel_nodes[i] if i < len(self.parallel_nodes) else "unknown"
                    error_result = NodeResult(
                        success=False,
                        error=str(branch_result),
                        node_id=node_id,
                        status=NodeStatus.FAILED,
                    )
                    processed_results.append(error_result)
                    failure_count += 1
                else:
                    processed_results.append(branch_result)
                    if branch_result.success:
                        success_count += 1
                    else:
                        failure_count += 1

            parallel_result = ParallelResult(
                node_id=self.node_id,
                results=processed_results,
                success_count=success_count,
                failure_count=failure_count,
            )

            result.success = self.wait_for_all or failure_count == 0
            result.data = {
                "parallel_result": {
                    "node_id": parallel_result.node_id,
                    "success_count": parallel_result.success_count,
                    "failure_count": parallel_result.failure_count,
                    "total": len(processed_results),
                },
                "branch_results": [r.to_dict() for r in processed_results],
            }
            result.status = NodeStatus.COMPLETED

        except Exception as e:
            result.success = False
            result.error = str(e)
            result.status = NodeStatus.FAILED

        result.end_time = datetime.now()
        return result

    async def _execute_branch(self, node_id: str, context: ChainContext) -> NodeResult:
        """Execute a single branch in the parallel node.

        Args:
            node_id: ID of the node to execute.
            context: Chain execution context.

        Returns:
            NodeResult from the branch execution.
        """
        executor = context.get("executor")
        if not executor:
            return NodeResult(
                success=False,
                error="No executor available",
                node_id=node_id,
                status=NodeStatus.FAILED,
            )
        return await executor._execute_node(node_id, context)

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "parallel_nodes": self.parallel_nodes,
            "wait_for_all": self.wait_for_all,
        }

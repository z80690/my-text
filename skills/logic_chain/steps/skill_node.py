# -*- coding: utf-8 -*-
"""Skill Node - Executes a skill as part of the chain."""

from typing import Any, Dict, Optional
from datetime import datetime

from ..core.base_node import BaseNode, NodeType, NodeResult, NodeStatus
from ..core.chain_context import ChainContext


class SkillNode(BaseNode):
    """Node that executes a skill handler.

    Attributes:
        skill_name: Name of the skill to execute.
        parameters: Parameters to pass to the skill.
        output_key: Key to store result in context variables.
    """

    def __init__(
        self,
        node_id: str,
        name: str,
        skill_name: str = "",
        parameters: Dict[str, Any] = None,
        output_key: str = None,
    ):
        super().__init__(node_id, NodeType.SKILL, name)
        self.skill_name = skill_name
        self.parameters = parameters or {}
        self.output_key = output_key

    async def execute(self, context: ChainContext) -> NodeResult:
        """Execute the skill node.

        Args:
            context: Chain execution context.

        Returns:
            NodeResult containing skill execution outcome.
        """
        result = NodeResult(
            node_id=self.node_id,
            node_name=self.name,
            status=NodeStatus.RUNNING,
            start_time=datetime.now(),
        )

        try:
            input_data = self._build_input(context)
            resolved_skill = self._resolve_skill(context)

            if resolved_skill:
                if hasattr(resolved_skill, "handle"):
                    output = resolved_skill.handle(input_data)
                else:
                    output = resolved_skill(input_data)
            else:
                output = self._simulate_execution(input_data)

            result.success = True
            result.data = output
            result.status = NodeStatus.COMPLETED

            if self.output_key:
                context.set(self.output_key, output)

        except Exception as e:
            result.success = False
            result.error = str(e)
            result.status = NodeStatus.FAILED

        result.end_time = datetime.now()
        return result

    def _build_input(self, context: ChainContext) -> Dict[str, Any]:
        """Build input data for the skill.

        Args:
            context: Chain execution context.

        Returns:
            Input data dictionary.
        """
        input_data = {}

        for key, value in self.parameters.items():
            if isinstance(value, str) and value.startswith("$"):
                var_name = value[1:]
                input_data[key] = context.get(var_name)
            else:
                input_data[key] = value

        return input_data

    def _resolve_skill(self, context: ChainContext) -> Optional[Any]:
        """Resolve the skill handler from context.

        Args:
            context: Chain execution context.

        Returns:
            Skill handler if found, None otherwise.
        """
        skills_registry = context.get("skills_registry", {})
        return skills_registry.get(self.skill_name)

    def _simulate_execution(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate skill execution for testing.

        Args:
            input_data: Input data for the skill.

        Returns:
            Simulated output.
        """
        return {
            "skill": self.skill_name,
            "input": input_data,
            "output": f"Simulated output from {self.skill_name}",
            "timestamp": datetime.now().isoformat(),
        }

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "skill_name": self.skill_name,
            "parameters": self.parameters,
            "output_key": self.output_key,
        }

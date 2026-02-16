# -*- coding: utf-8 -*-
"""Condition Node - Evaluates conditions and branches logic."""

import re
from typing import Any, Dict, Optional
from datetime import datetime

from ..core.base_node import BaseNode, NodeType, NodeResult, NodeStatus
from ..core.chain_context import ChainContext


class ConditionNode(BaseNode):
    """Node that evaluates a condition and stores result.

    Supports:
    - Variable comparisons: $var == value
    - Expressions: $count > 5
    - Pattern matching: $email matches .*@domain.com
    - Existence checks: $var exists
    """

    def __init__(
        self,
        node_id: str,
        name: str,
        condition: str = "",
        output_key: str = None,
    ):
        super().__init__(node_id, NodeType.CONDITION, name)
        self.condition = condition
        self.output_key = output_key

    async def execute(self, context: ChainContext) -> NodeResult:
        """Execute the condition node.

        Args:
            context: Chain execution context.

        Returns:
            NodeResult with evaluation outcome.
        """
        result = NodeResult(
            node_id=self.node_id,
            node_name=self.name,
            status=NodeStatus.RUNNING,
            start_time=datetime.now(),
        )

        try:
            condition_met = self._evaluate_condition(context)

            result.success = True
            result.data = {"condition_met": condition_met, "condition": self.condition}
            result.status = NodeStatus.COMPLETED

            if self.output_key:
                context.set(self.output_key, condition_met)

        except Exception as e:
            result.success = False
            result.error = str(e)
            result.status = NodeStatus.FAILED

        result.end_time = datetime.now()
        return result

    def _evaluate_condition(self, context: ChainContext) -> bool:
        """Evaluate the condition against context.

        Args:
            context: Chain execution context.

        Returns:
            True if condition is met, False otherwise.
        """
        if not self.condition:
            return True

        condition = self.condition.strip()

        pattern_matching = re.match(r"\$(\w+)\s+matches\s+(.+)", condition)
        if pattern_matching:
            var_name = pattern_matching.group(1)
            pattern = pattern_matching.group(2).strip("'\"")
            value = context.get(var_name, "")
            return bool(re.match(pattern, str(value)))

        existence_check = re.match(r"\$(\w+)\s+(exists|not_exists)", condition)
        if existence_check:
            var_name = existence_check.group(1)
            check_type = existence_check.group(2)
            has_var = context.has(var_name)
            return has_var if check_type == "exists" else not has_var

        comparison = re.match(r"\$(\w+)\s*(==|!=|<=|>=|<|>)\s*(.+)", condition)
        if comparison:
            var_name = comparison.group(1)
            operator = comparison.group(2)
            raw_value = comparison.group(3).strip()

            left = context.get(var_name)
            right = self._parse_value(raw_value, context)

            return self._compare(left, operator, right)

        return bool(condition)

    def _parse_value(self, value: str, context: ChainContext) -> Any:
        """Parse a value string, resolving variables if needed.

        Args:
            value: String value to parse.
            context: Chain execution context.

        Returns:
            Parsed value.
        """
        if value.startswith("$"):
            return context.get(value[1:])

        if value in ("true", "True"):
            return True
        if value in ("false", "False"):
            return False
        if value in ("null", "None"):
            return None

        try:
            if "." in value:
                return float(value)
            return int(value)
        except ValueError:
            return value.strip("'\"")

    def _compare(self, left: Any, operator: str, right: Any) -> bool:
        """Perform comparison with given operator.

        Args:
            left: Left operand.
            operator: Comparison operator.
            right: Right operand.

        Returns:
            Comparison result.
        """
        operators = {
            "==": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
            "<": lambda a, b: a < b,
            "<=": lambda a, b: a <= b,
            ">": lambda a, b: a > b,
            ">=": lambda a, b: a >= b,
        }
        func = operators.get(operator)
        return func(left, right) if func else False

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "condition": self.condition,
            "output_key": self.output_key,
        }


class IfElseNode(BaseNode):
    """Node that implements IF/ELSE branching logic.

    Takes a condition node result and routes to true/false branches.
    """

    def __init__(
        self,
        node_id: str,
        name: str,
        condition_node_id: str = None,
    ):
        super().__init__(node_id, NodeType.IF_ELSE, name)
        self.condition_node_id = condition_node_id

    async def execute(self, context: ChainContext) -> NodeResult:
        """Execute the IF/ELSE node.

        Args:
            context: Chain execution context.

        Returns:
            NodeResult with branch decision.
        """
        result = NodeResult(
            node_id=self.node_id,
            node_name=self.name,
            status=NodeStatus.RUNNING,
            start_time=datetime.now(),
        )

        try:
            condition_result = self._get_condition_result(context)
            branch_taken = "true" if condition_result else "false"

            result.success = True
            result.data = {
                "condition_met": condition_result,
                "branch_taken": branch_taken,
            }
            result.status = NodeStatus.COMPLETED
            result.metadata = {"branch": branch_taken}

        except Exception as e:
            result.success = False
            result.error = str(e)
            result.status = NodeStatus.FAILED

        result.end_time = datetime.now()
        return result

    def _get_condition_result(self, context: ChainContext) -> bool:
        """Get the condition evaluation result.

        Args:
            context: Chain execution context.

        Returns:
            True if condition was met, False otherwise.
        """
        if self.condition_node_id:
            cond_result = context.get_node_result(self.condition_node_id)
            if cond_result and isinstance(cond_result, dict):
                return cond_result.get("data", {}).get("condition_met", False)

        for key, value in context.variables.items():
            if isinstance(value, bool):
                return value

        return False

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "condition_node_id": self.condition_node_id,
        }

# -*- coding: utf-8 -*-
"""Database Node - Execute database queries as part of a chain."""

from typing import Any, Dict, Optional
from datetime import datetime

from ..core.base_node import BaseNode, NodeType, NodeResult, NodeStatus
from ..core.chain_context import ChainContext


class DatabaseNode(BaseNode):
    """Node that executes a database query.

    Supports Supabase database operations.
    """

    def __init__(
        self,
        node_id: str,
        name: str,
        table: str = "",
        operation: str = "select",
        columns: str = "*",
        where: Dict[str, Any] = None,
        order_by: str = None,
        limit: int = None,
        output_key: str = None,
    ):
        super().__init__(node_id, NodeType.SKILL, name)
        self.table = table
        self.operation = operation
        self.columns = columns
        self.where = where or {}
        self.order_by = order_by
        self.limit = limit
        self.output_key = output_key

    async def execute(self, context: ChainContext) -> NodeResult:
        """Execute the database node.

        Args:
            context: Chain execution context.

        Returns:
            NodeResult containing query outcome.
        """
        result = NodeResult(
            node_id=self.node_id,
            node_name=self.name,
            status=NodeStatus.RUNNING,
            start_time=datetime.now(),
        )

        try:
            from skills.utils import get_supabase_client, log_execution

            log_execution(self.name, "START", f"Operation: {self.operation} on {self.table}")

            client = get_supabase_client()
            if not client:
                result.success = False
                result.error = "Supabase client not configured (SUPABASE_URL/SUPABASE_KEY missing)"
                result.status = NodeStatus.FAILED
                return result

            query = client.table(self.table).select(self.columns)

            for key, value in self.where.items():
                resolved_value = self._resolve_value(value, context)
                query = query.eq(key, resolved_value)

            if self.order_by:
                descending = self.order_by.startswith("-")
                order_column = self.order_by.lstrip("-")
                query = query.order(order_column, desc=descending)

            if self.limit:
                query = query.limit(self.limit)

            response = query.execute()

            if hasattr(response, 'data') and response.data:
                data = response.data
            else:
                data = []

            result.success = True
            result.data = {
                "operation": self.operation,
                "table": self.table,
                "row_count": len(data),
                "records": data,
            }
            result.status = NodeStatus.COMPLETED

            log_execution(self.name, "SUCCESS", f"Retrieved {len(data)} records")

            if self.output_key:
                context.set(self.output_key, data)

        except Exception as e:
            result.success = False
            result.error = str(e)
            result.status = NodeStatus.FAILED
            log_execution(self.name, "ERROR", str(e))

        result.end_time = datetime.now()
        return result

    def _resolve_value(self, value: Any, context: ChainContext) -> Any:
        """Resolve a value, replacing $variable references.

        Args:
            value: Value which may contain variable references.
            context: Chain execution context.

        Returns:
            Resolved value.
        """
        if isinstance(value, str) and value.startswith("$"):
            return context.get(value[1:], value)
        return value

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "table": self.table,
            "operation": self.operation,
            "columns": self.columns,
            "where": self.where,
            "order_by": self.order_by,
            "limit": self.limit,
            "output_key": self.output_key,
        }

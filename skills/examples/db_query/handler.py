# -*- coding: utf-8 -*-
"""Database Query Skill - Query records from Supabase.

This skill demonstrates interaction with Supabase database.
"""

from typing import Any, Dict
from skills.utils import validate_input, format_response, get_supabase_client


def handle(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a database query.

    Args:
        input_data: Query parameters.
            - table: Table name to query (required)
            - columns: Columns to select (default: "*")
            - where: Dictionary of filters (optional)
            - limit: Maximum rows to return (optional)

    Returns:
        dict: Query results or error.
    """
    print(f"[db_query] Input: {input_data}")

    is_valid, error = validate_input(input_data, ["table"])
    if not is_valid:
        return format_response(False, error=error)

    table = input_data["table"]
    columns = input_data.get("columns", "*")
    where = input_data.get("where", {})
    limit = input_data.get("limit", 10)

    try:
        client = get_supabase_client()
        if not client:
            return format_response(
                False,
                error="SUPABASE_URL and SUPABASE_KEY environment variables not set"
            )

        query = client.table(table).select(columns)

        for key, value in where.items():
            query = query.eq(key, value)

        if limit:
            query = query.limit(limit)

        response = query.execute()

        records = getattr(response, 'data', []) or []

        print(f"[db_query] Retrieved {len(records)} records from {table}")

        return format_response(
            True,
            data={
                "table": table,
                "row_count": len(records),
                "records": records
            }
        )

    except Exception as e:
        print(f"[db_query] Error: {e}")
        return format_response(False, error=str(e))


if __name__ == "__main__":
    test_input = {
        "table": "users",
        "columns": "id,email,created_at",
        "limit": 5
    }
    result = handle(test_input)
    print(f"\nTest Result:\n{result}")

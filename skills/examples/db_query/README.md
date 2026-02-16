# Database Query Skill

A skill that queries records from Supabase database.

## Usage

```python
from skills.examples.db_query.handler import handle

result = handle({
    "table": "users",
    "columns": "id,email,created_at",
    "where": {"status": "active"},
    "limit": 10
})
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `table` | string | Yes | Table name to query |
| `columns` | string | No | Columns to select (default: "*") |
| `where` | object | No | Filter conditions |
| `limit` | number | No | Maximum rows (default: 10) |

## Returns

```json
{
  "success": true,
  "data": {
    "table": "users",
    "row_count": 5,
    "records": [...]
  },
  "error": null
}
```

## Environment Variables

- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_KEY`: Supabase API key

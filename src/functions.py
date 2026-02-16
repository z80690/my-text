# -*- coding: utf-8 -*-
"""
Agent Functions

Example functions for AI agent function calling
Includes knowledge base queries, user management, and database operations
"""

import json
import logging
from typing import Dict, Any

# Handle both relative and absolute imports
try:
    from .skill_handler import FunctionRegistry, FunctionParameter
except ImportError:
    from skill_handler import FunctionRegistry, FunctionParameter

# Supabase client - handle missing import gracefully
try:
    from .ai_api import get_supabase_client
except ImportError:
    try:
        from ai_api import get_supabase_client
    except ImportError:
        def get_supabase_client():
            raise ImportError("Supabase client not available")


# Knowledge Base Functions

@FunctionRegistry.register(
    name="query_knowledge_base",
    description="Query the knowledge base for information using semantic search",
    parameters=[
        FunctionParameter(
            "query",
            "string",
            "Search query text",
            required=True,
            max_length=1000
        ),
        FunctionParameter(
            "limit",
            "integer",
            "Maximum number of results to return",
            required=False,
            default_value=5,
            minimum=1,
            maximum=20
        ),
        FunctionParameter(
            "category",
            "string",
            "Filter by category (optional)",
            required=False
        )
    ],
    required_params=["query"]
)
def query_knowledge_base(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Query knowledge base for relevant information"""
    query = arguments.get("query", "")
    limit = arguments.get("limit", 5)
    category = arguments.get("category")
    
    try:
        client = get_supabase_client()
    except ImportError:
        return {
            "success": False,
            "error": "Database connection not available",
            "query": query,
            "note": "Please configure SUPABASE_URL and SUPABASE_KEY"
        }
    
    try:
        # Build query
        query_builder = client.table("knowledge_base").select("*")
        
        if category:
            query_builder = query_builder.eq("category", category)
        
        # Use text search if available, otherwise return recent items
        response = query_builder.limit(limit).execute()
        
        if hasattr(response, 'data') and response.data:
            results = []
            for item in response.data:
                results.append({
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "content": item.get("content", "")[:500],  # Truncate long content
                    "category": item.get("category"),
                    "relevance_score": item.get("similarity", 0.9)
                })
            
            return {
                "success": True,
                "query": query,
                "results_count": len(results),
                "results": results
            }
        
        return {
            "success": True,
            "query": query,
            "results_count": 0,
            "results": [],
            "message": "No results found"
        }
    
    except Exception as e:
        logging.error("[ERROR] Knowledge base query failed: %s", e)
        return {
            "success": False,
            "error": str(e),
            "query": query
        }


@FunctionRegistry.register(
    name="search_documents",
    description="Search through stored documents with full-text search",
    parameters=[
        FunctionParameter(
            "search_term",
            "string",
            "Term or phrase to search for",
            required=True,
            max_length=500
        ),
        FunctionParameter(
            "document_type",
            "string",
            "Filter by document type (pdf, doc, txt, etc.)",
            required=False
        ),
        FunctionParameter(
            "include_content",
            "boolean",
            "Include document content in results",
            required=False,
            default_value=True
        )
    ],
    required_params=["search_term"]
)
def search_documents(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Search through stored documents"""
    search_term = arguments.get("search_term", "")
    document_type = arguments.get("document_type")
    include_content = arguments.get("include_content", True)
    
    try:
        client = get_supabase_client()
    except ImportError:
        return {
            "success": False,
            "error": "Database connection not available"
        }
    
    try:
        # Build search query
        query = client.table("documents").select("*")
        
        if document_type:
            query = query.eq("document_type", document_type)
        
        # Simple search - in production, use Supabase text search
        response = query.limit(10).execute()
        
        if hasattr(response, 'data') and response.data:
            # Filter by search term
            filtered = []
            for doc in response.data:
                content = doc.get("content", "") or ""
                title = doc.get("title", "") or ""
                
                if search_term.lower() in content.lower() or search_term.lower() in title.lower():
                    result = {
                        "id": doc.get("id"),
                        "title": doc.get("title"),
                        "document_type": doc.get("document_type"),
                        "created_at": doc.get("created_at")
                    }
                    if include_content:
                        result["content_preview"] = content[:200]
                    filtered.append(result)
            
            return {
                "success": True,
                "search_term": search_term,
                "results_count": len(filtered),
                "results": filtered
            }
        
        return {
            "success": True,
            "search_term": search_term,
            "results_count": 0,
            "results": []
        }
    
    except Exception as e:
        logging.error("[ERROR] Document search failed: %s", e)
        return {
            "success": False,
            "error": str(e)
        }


# User Management Functions

@FunctionRegistry.register(
    name="get_user_profile",
    description="Get user profile information by user ID",
    parameters=[
        FunctionParameter(
            "user_id",
            "string",
            "User ID to retrieve",
            required=True
        )
    ],
    required_params=["user_id"]
)
def get_user_profile(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Get user profile by ID"""
    user_id = arguments.get("user_id", "")
    
    try:
        client = get_supabase_client()
    except ImportError:
        return {
            "success": False,
            "error": "Database connection not available"
        }
    
    try:
        response = client.table("users").select("*").eq("id", user_id).execute()
        
        if hasattr(response, 'data') and response.data:
            user = response.data[0]
            return {
                "success": True,
                "user": {
                    "id": user.get("id"),
                    "email": user.get("email"),
                    "display_name": user.get("display_name"),
                    "created_at": user.get("created_at")
                }
            }
        
        return {
            "success": False,
            "error": "User not found",
            "user_id": user_id
        }
    
    except Exception as e:
        logging.error("[ERROR] Get user profile failed: %s", e)
        return {
            "success": False,
            "error": str(e)
        }


@FunctionRegistry.register(
    name="list_users",
    description="List users with optional filtering and pagination",
    parameters=[
        FunctionParameter(
            "limit",
            "integer",
            "Maximum number of users to return",
            required=False,
            default_value=10,
            minimum=1,
            maximum=100
        ),
        FunctionParameter(
            "offset",
            "integer",
            "Number of users to skip (pagination)",
            required=False,
            default_value=0,
            minimum=0
        ),
        FunctionParameter(
            "role",
            "string",
            "Filter by user role",
            required=False,
            enum_values=["user", "moderator", "admin"]
        )
    ],
    required_params=[]
)
def list_users(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """List users with optional filtering"""
    limit = arguments.get("limit", 10)
    offset = arguments.get("offset", 0)
    role = arguments.get("role")
    
    try:
        client = get_supabase_client()
    except ImportError:
        return {
            "success": False,
            "error": "Database connection not available"
        }
    
    try:
        query = client.table("users").select("id,email,display_name,role,created_at")
        
        if role:
            query = query.eq("role", role)
        
        response = query.limit(limit).offset(offset).execute()
        
        users = []
        if hasattr(response, 'data') and response.data:
            for user in response.data:
                users.append({
                    "id": user.get("id"),
                    "email": user.get("email"),
                    "display_name": user.get("display_name"),
                    "role": user.get("role"),
                    "created_at": user.get("created_at")
                })
        
        return {
            "success": True,
            "count": len(users),
            "limit": limit,
            "offset": offset,
            "users": users
        }
    
    except Exception as e:
        logging.error("[ERROR] List users failed: %s", e)
        return {
            "success": False,
            "error": str(e)
        }


# Database Query Functions

@FunctionRegistry.register(
    name="execute_safe_query",
    description="Execute a read-only database query with safety checks",
    parameters=[
        FunctionParameter(
            "table_name",
            "string",
            "Name of the table to query",
            required=True
        ),
        FunctionParameter(
            "columns",
            "string",
            "Comma-separated list of columns to select",
            required=False,
            default_value="*"
        ),
        FunctionParameter(
            "filters",
            "object",
            "Filter conditions as JSON object",
            required=False
        ),
        FunctionParameter(
            "limit",
            "integer",
            "Maximum rows to return",
            required=False,
            default_value=100,
            maximum=1000
        )
    ],
    required_params=["table_name"]
)
def execute_safe_query(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a read-only database query with safety checks"""
    table_name = arguments.get("table_name", "")
    columns = arguments.get("columns", "*")
    filters = arguments.get("filters", {})
    limit = arguments.get("limit", 100)
    
    # Safety: Block dangerous tables
    blocked_tables = ["users", "passwords", "api_keys", "sessions"]
    if table_name.lower() in blocked_tables:
        return {
            "success": False,
            "error": "Access to this table is blocked for security reasons"
        }
    
    try:
        client = get_supabase_client()
    except ImportError:
        return {
            "success": False,
            "error": "Database connection not available"
        }
    
    try:
        # Safety: Only allow SELECT operations (enforced by query builder)
        query = client.table(table_name).select(columns)
        
        # Apply filters
        for key, value in filters.items():
            query = query.eq(key, value)
        
        response = query.limit(limit).execute()
        
        return {
            "success": True,
            "table": table_name,
            "rows_returned": len(response.data) if hasattr(response, 'data') else 0,
            "data": response.data if hasattr(response, 'data') else []
        }
    
    except Exception as e:
        logging.error("[ERROR] Database query failed: %s", e)
        return {
            "success": False,
            "error": str(e),
            "table": table_name
        }


@FunctionRegistry.register(
    name="count_records",
    description="Count records in a table with optional filtering",
    parameters=[
        FunctionParameter(
            "table_name",
            "string",
            "Name of the table to count",
            required=True
        ),
        FunctionParameter(
            "filter_column",
            "string",
            "Column to filter by (optional)",
            required=False
        ),
        FunctionParameter(
            "filter_value",
            "string",
            "Value to filter by (optional)",
            required=False
        )
    ],
    required_params=["table_name"]
)
def count_records(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Count records in a table"""
    table_name = arguments.get("table_name", "")
    filter_column = arguments.get("filter_column")
    filter_value = arguments.get("filter_value")
    
    try:
        client = get_supabase_client()
    except ImportError:
        return {
            "success": False,
            "error": "Database connection not available"
        }
    
    try:
        query = client.table(table_name).select("*", count="exact")
        
        if filter_column and filter_value:
            query = query.eq(filter_column, filter_value)
        
        response = query.execute()
        
        count = response.count if hasattr(response, 'count') else 0
        
        return {
            "success": True,
            "table": table_name,
            "count": count,
            "filter": {filter_column: filter_value} if filter_column else None
        }
    
    except Exception as e:
        logging.error("[ERROR] Count records failed: %s", e)
        return {
            "success": False,
            "error": str(e)
        }


# Utility Functions

@FunctionRegistry.register(
    name="format_data",
    description="Format data into a readable structure",
    parameters=[
        FunctionParameter(
            "data",
            "object",
            "Data to format",
            required=True
        ),
        FunctionParameter(
            "format_type",
            "string",
            "Output format type",
            required=False,
            default_value="json",
            enum_values=["json", "text", "table"]
        ),
        FunctionParameter(
            "include_summary",
            "boolean",
            "Include data summary",
            required=False,
            default_value=True
        )
    ],
    required_params=["data"]
)
def format_data(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Format data for display"""
    data = arguments.get("data", {})
    format_type = arguments.get("format_type", "json")
    include_summary = arguments.get("include_summary", True)
    
    result = {
        "format": format_type,
        "data": data
    }
    
    if include_summary:
        result["summary"] = {
            "keys_count": len(data) if isinstance(data, dict) else 0,
            "type": type(data).__name__
        }
    
    if format_type == "json":
        result["formatted"] = json.dumps(data, ensure_ascii=False, indent=2)
    elif format_type == "text":
        if isinstance(data, dict):
            lines = [f"{k}: {v}" for k, v in data.items()]
            result["formatted"] = "\n".join(lines)
        else:
            result["formatted"] = str(data)
    
    return {
        "success": True,
        "result": result
    }


# Function to register all functions
def register_all_functions() -> None:
    """
    Explicitly register all functions in this module
    
    Note: Functions decorated with @FunctionRegistry.register are
    automatically registered when the module is imported.
    This function is for manual registration or verification.
    """
    logging.info("[INFO] Agent functions registered:")
    for func_name in FunctionRegistry.list_functions():
        logging.info(f"  - {func_name}")

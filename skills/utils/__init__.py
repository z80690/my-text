# -*- coding: utf-8 -*-
"""Shared utility functions for AI Agent Skills."""


def validate_input(data: dict, required_fields: list) -> tuple:
    """Validate that required fields are present in input data.

    Args:
        data: Input data dictionary.
        required_fields: List of field names that are required.

    Returns:
        tuple: (is_valid, error_message)
    """
    missing = [f for f in required_fields if f not in data]
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"
    return True, None


def format_response(success: bool, data: any = None, error: str | None = None) -> dict:
    """Standard response format for skills.

    Args:
        success: Whether the operation was successful.
        data: Response data.
        error: Error message if any.

    Returns:
        dict: Standardized response structure.
    """
    return {
        "success": success,
        "data": data,
        "error": error
    }


def sanitize_input(data: dict, allowed_fields: list | None = None) -> dict:
    """Remove unknown fields from input data.

    Args:
        data: Input data dictionary.
        allowed_fields: List of allowed field names. If None, returns copy of data.

    Returns:
        dict: Sanitized input data.
    """
    if allowed_fields is None:
        return data.copy()
    return {k: v for k, v in data.items() if k in allowed_fields}


def load_skill_config(skill_path: str) -> dict:
    """Load skill configuration from JSON file.

    Args:
        skill_path: Path to the skill directory.

    Returns:
        dict: Skill configuration.
    """
    import json
    import os

    config_path = os.path.join(skill_path, "skill.json")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_supabase_client():
    """Get a Supabase client instance.

    Returns:
        Client: Supabase client or None if not configured.
    """
    import os
    from supabase import create_client, Client

    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")

    if not url or not key:
        return None

    return create_client(url, key)


def log_execution(step: str, status: str, message: str = "") -> None:
    """Log skill execution step.

    Args:
        step: Name of the execution step.
        status: Status (START, SUCCESS, ERROR, END).
        message: Optional message.
    """
    print(f"[{status}] {step}: {message}")

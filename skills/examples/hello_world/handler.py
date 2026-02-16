def handle(input_data: dict) -> dict:
    """Execute the hello world skill."""
    return {
        "success": True,
        "message": f"Hello, {input_data.get('name', 'World')}!"
    }

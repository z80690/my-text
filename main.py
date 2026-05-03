# -*- coding: utf-8 -*-
"""
Main Application Entry Point

Local development server entry point for the Agent Team Dispatcher application.
Provides a lightweight HTTP server with request handling capabilities.
"""

import json
import os
from typing import Dict, Any, Optional

# Environment configuration
DEFAULT_PORT = 9000


def main_handler(event: Dict[str, Any], context: Optional[Any] = None) -> Dict[str, Any]:
    """
    Main request handler for processing incoming events.

    Args:
        event: Dictionary containing request data
        context: Optional context object for runtime information

    Returns:
        Dictionary with statusCode and response body
    """
    try:
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "OK", "status": "success"})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": str(e), "status": "error"})
        }


def get_port() -> int:
    """
    Retrieve the port number from environment variable or use default.

    Returns:
        Port number as integer
    """
    try:
        return int(os.environ.get("PORT", str(DEFAULT_PORT)))
    except (ValueError, TypeError):
        return DEFAULT_PORT


def start_server() -> None:
    """Start the development server."""
    port = get_port()
    print(f"Starting Agent Team Dispatcher server on port {port}")
    
    # Placeholder for actual server implementation
    # For production, consider using a proper ASGI server like Uvicorn
    try:
        import http.server
        import socketserver
        
        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                response = main_handler({"path": self.path, "method": "GET"})
                self.send_response(response["statusCode"])
                for key, value in response.get("headers", {}).items():
                    self.send_header(key, value)
                self.end_headers()
                self.wfile.write(response["body"].encode("utf-8"))
        
        with socketserver.TCPServer(("", port), Handler) as httpd:
            print(f"Server running at http://localhost:{port}")
            httpd.serve_forever()
    except ImportError:
        print(f"Server module not available. Port {port} configured.")


if __name__ == "__main__":
    start_server()
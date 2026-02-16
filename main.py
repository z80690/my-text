# -*- coding: utf-8 -*-
"""
Main Application Entry Point

Local development server entry point
"""

import os
import json
from typing import Dict, Any


def main_handler(event: Dict[str, Any], context=None) -> Dict[str, Any]:
    """Main request handler"""
    return {"statusCode": 200, "body": json.dumps({"message": "OK"})}


if __name__ == "__main__":
    port = int(os.getenv("PORT", "9000"))
    print(f"Starting server on port {port}")

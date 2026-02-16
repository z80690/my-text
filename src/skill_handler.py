# -*- coding: utf-8 -*-
"""
Skill Handler

Manages function registration and execution for AI agent function calling

This module provides:
- FunctionRegistry: Central registry for all available functions
- Function schemas with type validation
- Decorator-based function registration
- Integration with ZhipuAI function calling
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from functools import wraps


# Type aliases
FunctionExecutor = Callable[[Dict[str, Any]], Dict[str, Any]]
FunctionValidator = Callable[[Dict[str, Any]], tuple[bool, Optional[str]]]


@dataclass
class FunctionParameter:
    """Function parameter definition for schema generation"""
    name: str
    param_type: str = "string"
    description: str = ""
    required: bool = False
    enum_values: Optional[List[str]] = None
    default_value: Any = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    minimum: Optional[Union[int, float]] = None
    maximum: Optional[Union[int, float]] = None


@dataclass
class FunctionSchema:
    """Complete function schema for AI model"""
    name: str
    description: str
    parameters: List[FunctionParameter] = field(default_factory=list)
    required_params: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to ZhipuAI/OpenAI function calling format"""
        properties = {}
        for param in self.parameters:
            prop_dict: Dict[str, Any] = {
                "type": param.param_type,
                "description": param.description
            }
            if param.enum_values:
                prop_dict["enum"] = param.enum_values
            if param.default_value is not None:
                prop_dict["default"] = param.default_value
            if param.min_length is not None:
                prop_dict["minLength"] = param.min_length
            if param.max_length is not None:
                prop_dict["maxLength"] = param.max_length
            if param.minimum is not None:
                prop_dict["minimum"] = param.minimum
            if param.maximum is not None:
                prop_dict["maximum"] = param.maximum
            properties[param.name] = prop_dict
        
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": self.required_params
                }
            }
        }


class FunctionRegistry:
    """
    Central registry for all available functions
    
    Provides:
    - Function registration and management
    - Schema generation for AI models
    - Type validation for function arguments
    - Execution with error handling
    """
    
    # Class-level registry storage
    _functions: Dict[str, Dict[str, Any]] = {}
    _executors: Dict[str, FunctionExecutor] = {}
    _schemas: Dict[str, FunctionSchema] = {}
    
    @classmethod
    def register(
        cls,
        name: str,
        description: str,
        parameters: List[FunctionParameter],
        required_params: Optional[List[str]] = None
    ) -> Callable[[FunctionExecutor], FunctionExecutor]:
        """
        Decorator to register a function with the AI agent
        
        Args:
            name: Function name (should be snake_case)
            description: Description of what the function does
            parameters: List of FunctionParameter definitions
            required_params: List of required parameter names
            
        Returns:
            Decorator function
            
        Example:
            @FunctionRegistry.register(
                name="query_knowledge_base",
                description="Query the knowledge base for information",
                parameters=[
                    FunctionParameter("query", "string", "Search query", required=True)
                ],
                required_params=["query"]
            )
            def query_kb(args):
                # Implementation
                pass
        """
        def decorator(func: FunctionExecutor) -> FunctionExecutor:
            # Store function metadata
            cls._functions[name] = {
                "name": name,
                "description": description,
                "parameters": parameters,
                "required_params": required_params or [p.name for p in parameters if p.required]
            }
            
            # Store executor
            cls._executors[name] = func
            
            # Create and store schema
            schema = FunctionSchema(
                name=name,
                description=description,
                parameters=parameters,
                required_params=cls._functions[name]["required_params"]
            )
            cls._schemas[name] = schema
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            
            return wrapper
        return decorator
    
    @classmethod
    def register_function(
        cls,
        name: str,
        executor: FunctionExecutor,
        description: str,
        parameters: List[FunctionParameter],
        required_params: Optional[List[str]] = None
    ) -> None:
        """
        Register a function programmatically (without decorator)
        
        Args:
            name: Function name
            executor: Function to execute
            description: Function description
            parameters: Parameter definitions
            required_params: Required parameter names
        """
        cls._functions[name] = {
            "name": name,
            "description": description,
            "parameters": parameters,
            "required_params": required_params or [p.name for p in parameters if p.required]
        }
        cls._executors[name] = executor
        cls._schemas[name] = FunctionSchema(
            name=name,
            description=description,
            parameters=parameters,
            required_params=cls._functions[name]["required_params"]
        )
    
    @classmethod
    def get_executor(cls, name: str) -> Optional[FunctionExecutor]:
        """Get function executor by name"""
        return cls._executors.get(name)
    
    @classmethod
    def get_schema(cls, name: str) -> Optional[Dict[str, Any]]:
        """Get function schema by name"""
        schema = cls._schemas.get(name)
        if schema:
            return schema.to_dict()
        return None
    
    @classmethod
    def get_all_schemas(cls) -> List[Dict[str, Any]]:
        """Get all registered function schemas"""
        return [schema.to_dict() for schema in cls._schemas.values()]
    
    @classmethod
    def get_function_info(cls, name: str) -> Optional[Dict[str, Any]]:
        """Get function metadata by name"""
        return cls._functions.get(name)
    
    @classmethod
    def list_functions(cls) -> List[str]:
        """List all registered function names"""
        return list(cls._executors.keys())
    
    @classmethod
    def execute(
        cls,
        name: str,
        arguments: Dict[str, Any],
        validate: bool = True
    ) -> Dict[str, Any]:
        """
        Execute a registered function with type validation
        
        Args:
            name: Function name
            arguments: Function arguments as dict
            validate: Whether to validate arguments before execution
            
        Returns:
            Dict with 'success', 'result', and optionally 'error'
        """
        # Check if function exists
        executor = cls.get_executor(name)
        if not executor:
            return {
                "success": False,
                "error": f"Function not found: {name}",
                "function": name
            }
        
        # Get function info for validation
        func_info = cls.get_function_info(name)
        if not func_info:
            return {
                "success": False,
                "error": f"Function info not found: {name}",
                "function": name
            }
        
        # Validate arguments if requested
        if validate:
            is_valid, error_msg = cls._validate_arguments(func_info, arguments)
            if not is_valid:
                return {
                    "success": False,
                    "error": error_msg,
                    "function": name,
                    "arguments": arguments
                }
        
        # Execute function
        try:
            result = executor(arguments)
            return {
                "success": True,
                "result": result,
                "function": name
            }
        except Exception as e:
            logging.error("[ERROR] Function execution failed: %s - %s", name, str(e))
            return {
                "success": False,
                "error": f"Execution error: {str(e)}",
                "function": name
            }
    
    @classmethod
    def _validate_arguments(
        cls,
        func_info: Dict[str, Any],
        arguments: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """Validate function arguments against schema"""
        params = func_info.get("parameters", [])
        required_params = func_info.get("required_params", [])
        
        # Check required parameters
        for param_name in required_params:
            if param_name not in arguments:
                return False, f"Missing required parameter: {param_name}"
        
        # Type validation
        for param in params:
            param_name = param.name
            if param_name in arguments:
                value = arguments[param_name]
                
                # Type checking
                expected_type = param.param_type
                if expected_type == "string" and not isinstance(value, str):
                    return False, f"Parameter '{param_name}' must be a string"
                elif expected_type == "integer" and not isinstance(value, int):
                    return False, f"Parameter '{param_name}' must be an integer"
                elif expected_type == "number" and not isinstance(value, (int, float)):
                    return False, f"Parameter '{param_name}' must be a number"
                elif expected_type == "boolean" and not isinstance(value, bool):
                    return False, f"Parameter '{param_name}' must be a boolean"
                elif expected_type == "array" and not isinstance(value, list):
                    return False, f"Parameter '{param_name}' must be an array"
                elif expected_type == "object" and not isinstance(value, dict):
                    return False, f"Parameter '{param_name}' must be an object"
                
                # Enum validation
                if param.enum_values and value not in param.enum_values:
                    return False, f"Parameter '{param_name}' must be one of: {param.enum_values}"
                
                # Range validation
                if param.minimum is not None and isinstance(value, (int, float)) and value < param.minimum:
                    return False, f"Parameter '{param_name}' must be >= {param.minimum}"
                if param.maximum is not None and isinstance(value, (int, float)) and value > param.maximum:
                    return False, f"Parameter '{param_name}' must be <= {param.maximum}"
                if param.min_length is not None and isinstance(value, str) and len(value) < param.min_length:
                    return False, f"Parameter '{param_name}' must have length >= {param.min_length}"
        
        return True, None
    
    @classmethod
    def clear(cls) -> None:
        """Clear all registered functions (useful for testing)"""
        cls._functions.clear()
        cls._executors.clear()
        cls._schemas.clear()


# Convenience function for getting all tools for AI models
def get_all_tools() -> List[Dict[str, Any]]:
    """Get all registered functions in AI tool format"""
    return FunctionRegistry.get_all_schemas()


def execute_tool(tool_call: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a tool call from AI model
    
    Args:
        tool_call: Dict with 'function' key containing 'name' and 'arguments'
        
    Returns:
        Tool execution result
    """
    function_name = tool_call.get("function", {}).get("name", "")
    arguments_str = tool_call.get("function", {}).get("arguments", "{}")
    
    try:
        arguments = json.loads(arguments_str)
    except json.JSONDecodeError:
        return {
            "success": False,
            "error": f"Invalid JSON arguments: {arguments_str}",
            "function": function_name
        }
    
    return FunctionRegistry.execute(function_name, arguments)


# Built-in functions for the agent system
# These provide core functionality that can be extended

@FunctionRegistry.register(
    name="get_system_info",
    description="Get system information and status",
    parameters=[
        FunctionParameter(
            "info_type",
            "string",
            "Type of information to retrieve (version, status, config)",
            required=False,
            enum_values=["version", "status", "config"]
        )
    ],
    required_params=[]
)
def get_system_info(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Get system information"""
    info_type = arguments.get("info_type", "status")
    
    if info_type == "version":
        return {
            "version": "1.0.0",
            "model": os.getenv("ZHIPU_MODEL", "glm-4.7"),
            "environment": os.getenv("ENVIRONMENT", "development")
        }
    
    if info_type == "config":
        return {
            "supabase_url": "***" if os.getenv("SUPABASE_URL") else None,
            "zhipu_api_configured": bool(os.getenv("ZHIPU_API_KEY")),
            "log_level": os.getenv("LOG_LEVEL", "INFO")
        }
    
    return {
        "status": "operational",
        "functions_registered": len(FunctionRegistry.list_functions()),
        "memory_usage": "normal"
    }


@FunctionRegistry.register(
    name="validate_input",
    description="Validate user input for safety and format",
    parameters=[
        FunctionParameter(
            "text",
            "string",
            "Text to validate",
            required=True
        ),
        FunctionParameter(
            "max_length",
            "integer",
            "Maximum allowed length",
            required=False,
            default_value=10000
        ),
        FunctionParameter(
            "check_sql_injection",
            "boolean",
            "Check for SQL injection patterns",
            required=False,
            default_value=True
        )
    ],
    required_params=["text"]
)
def validate_input(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Validate input for safety"""
    text = arguments.get("text", "")
    max_length = arguments.get("max_length", 10000)
    check_sql = arguments.get("check_sql_injection", True)
    
    errors = []
    
    # Length check
    if len(text) > max_length:
        errors.append(f"Input exceeds maximum length of {max_length} characters")
    
    # SQL injection check
    if check_sql:
        dangerous_patterns = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE"]
        text_upper = text.upper()
        for pattern in dangerous_patterns:
            if pattern in text_upper:
                errors.append("Input contains potentially dangerous SQL patterns")
                break
    
    # XSS check
    dangerous_chars = ["<script", "javascript:", "onload=", "onerror="]
    text_lower = text.lower()
    for pattern in dangerous_chars:
        if pattern in text_lower:
            errors.append("Input contains potentially dangerous script patterns")
            break
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "length": len(text),
        "max_length": max_length
    }


# Import hook for auto-registering functions from other modules
def auto_register_module(module) -> None:
    """Auto-register functions from a module"""
    import inspect
    
    for _obj in inspect.getmembers(module, inspect.isfunction):
        # Check if function was registered via our decorator
        if hasattr(_obj, "__name__") and _obj.__name__.startswith("_"):
            continue
        
        # Functions registered via decorator are already in the registry
        # This is just for discovery/documentation
        pass

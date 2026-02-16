# -*- coding: utf-8 -*-
"""
Test script for function calling implementation
"""

import sys
sys.path.insert(0, '.')

# Test imports
print('Testing imports...')
try:
    from skill_handler import FunctionRegistry, FunctionParameter, FunctionSchema
    from functions import query_knowledge_base, get_user_profile, list_users
    print('  [OK] All imports successful')
except Exception as e:
    print(f'  [FAIL] Import failed: {e}')
    sys.exit(1)

# Test function registration
print('\nTesting function registration...')
try:
    functions = FunctionRegistry.list_functions()
    print(f'  [OK] Registered functions: {functions}')
except Exception as e:
    print(f'  [FAIL] Function listing failed: {e}')
    sys.exit(1)

# Test schema generation
print('\nTesting schema generation...')
try:
    tools = FunctionRegistry.get_all_schemas()
    print(f'  [OK] Generated {len(tools)} tool schemas')
    if tools:
        print(f'  [OK] First tool: {tools[0]["function"]["name"]}')
except Exception as e:
    print(f'  [FAIL] Schema generation failed: {e}')
    sys.exit(1)

# Test function execution
print('\nTesting function execution...')
try:
    result = FunctionRegistry.execute('get_system_info', {'info_type': 'version'})
    print(f'  [OK] System info result: {result}')
except Exception as e:
    print(f'  [FAIL] System info execution failed: {e}')
    sys.exit(1)

try:
    result = FunctionRegistry.execute('validate_input', {'text': 'Hello world', 'max_length': 100})
    print(f'  [OK] Input validation result: {result}')
except Exception as e:
    print(f'  [FAIL] Input validation failed: {e}')
    sys.exit(1)

# Test ZhipuAI client (will use mock if not configured)
print('\nTesting ZhipuAI client...')
try:
    from zhipu_service import get_zhipu_client
    client = get_zhipu_client()
    available = client.is_available()
    print(f'  [OK] ZhipuAI client available: {available}')
    
    # Test mock response
    if not available:
        result = client.chat([{'role': 'user', 'content': 'What time is it?'}])
        print(f'  [OK] Mock response: {result.get("content")}')
except Exception as e:
    print(f'  [FAIL] ZhipuAI client test failed: {e}')
    sys.exit(1)

print('\n' + '='*50)
print('[PASS] All tests passed!')
print('='*50)

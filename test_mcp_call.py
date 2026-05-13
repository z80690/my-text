# -*- coding: utf-8 -*-
"""
auto-memory-mcp 调用测试
使用 stdin/stdout 与 MCP 通信
"""

import subprocess
import json
import sys

def call_mcp():
    """调用 auto-memory-mcp"""
    mcp_path = r"C:\Users\Administrator\Desktop\my-text\auto-memory-mcp\dist\index.js"
    
    print("="*70)
    print("🚀 测试 auto-memory-mcp 调用")
    print("="*70)
    
    # 启动 MCP 进程
    process = subprocess.Popen(
        ['node', mcp_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # 1. 发送 initialize 请求
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "0.1.0",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    print("\n📤 发送 initialize 请求...")
    stdout, stderr = process.communicate(input=json.dumps(init_request) + '\n', timeout=5)
    
    if stdout:
        print(f"📥 响应: {stdout.strip()}")
    
    # 2. 发送 listTools 请求
    list_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    
    print("\n📤 发送 listTools 请求...")
    stdout, stderr = process.communicate(input=json.dumps(list_request) + '\n', timeout=5)
    
    if stdout:
        print(f"📥 响应: {stdout.strip()}")
    
    # 3. 发送 callTool 请求 - 测试自动记忆功能
    call_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "process_message",
            "arguments": {
                "message": "我习惯用4空格缩进，这是我的个人偏好"
            }
        }
    }
    
    print("\n📤 发送 callTool 请求 (测试自动记忆)...")
    stdout, stderr = process.communicate(input=json.dumps(call_request) + '\n', timeout=5)
    
    if stdout:
        print(f"📥 响应: {stdout.strip()}")
        
        # 解析响应
        try:
            response = json.loads(stdout.strip())
            if 'result' in response:
                content = response['result'].get('content', [])
                if content and content[0].get('type') == 'text':
                    result = json.loads(content[0]['text'])
                    print(f"\n✅ MCP 调用成功!")
                    print(f"   auto_saved: {result.get('auto_saved')}")
                    print(f"   type: {result.get('type')}")
                    print(f"   reason: {result.get('reason')}")
        except:
            pass
    
    process.terminate()
    print("\n✅ 测试完成")

if __name__ == "__main__":
    try:
        call_mcp()
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
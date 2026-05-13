# -*- coding: utf-8 -*-
"""
MCP 服务简单测试脚本
"""

import subprocess
import json
import time

def test_auto_memory():
    print("测试 auto-memory MCP...")
    process = subprocess.Popen(
        ['python', '.trae/auto_memory_mcp_stdio.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        init_req = json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': 'initialize'})
        stdout, stderr = process.communicate(input=init_req + '\n', timeout=5)
        
        if stdout:
            try:
                response = json.loads(stdout.strip())
                if 'result' in response and 'serverInfo' in response['result']:
                    print(f"✅ auto-memory 初始化成功: {response['result']['serverInfo']}")
                    return True
            except:
                print(f"⚠️ auto-memory 响应: {stdout[:100]}")
        return False
    except Exception as e:
        print(f"❌ auto-memory 异常: {e}")
        return False

def test_knowledge_graph():
    print("测试 knowledge-graph MCP...")
    try:
        result = subprocess.run(
            ['npx', '-y', '@itseasy21/mcp-knowledge-graph', '--help'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print("✅ knowledge-graph 安装成功")
            return True
        else:
            print(f"⚠️ knowledge-graph: {result.stderr[:100]}")
            return False
    except Exception as e:
        print(f"❌ knowledge-graph 异常: {e}")
        return False

def main():
    print("="*60)
    print("🚀 MCP 服务测试")
    print("="*60)
    
    results = []
    results.append(("auto-memory", test_auto_memory()))
    results.append(("knowledge-graph", test_knowledge_graph()))
    
    print("\n" + "="*60)
    print("📊 测试结果")
    print("="*60)
    
    success_count = sum(1 for _, success in results if success)
    total_count = len(results)
    
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")
    
    print(f"\n成功率: {success_count}/{total_count}")

if __name__ == "__main__":
    main()
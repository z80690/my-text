#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的MCP脚本
"""

import sys
import subprocess
import time
import json
import urllib.request

def test_script_syntax():
    """测试脚本语法"""
    print("🔍 测试脚本语法...")
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", ".trae/auto_memory_mcp.py"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print("✅ 脚本语法正确")
        return True
    else:
        print(f"❌ 语法错误: {result.stderr}")
        return False

def test_server_start():
    """测试服务器启动"""
    print("\n🔍 测试服务器启动...")
    
    # 启动服务器
    process = subprocess.Popen(
        [sys.executable, ".trae/auto_memory_mcp.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # 等待启动
    time.sleep(2)
    
    # 检查是否还在运行
    if process.poll() is not None:
        stdout, stderr = process.communicate()
        print(f"❌ 服务器启动失败: {stderr}")
        return False
    
    # 测试健康检查
    try:
        response = urllib.request.urlopen("http://127.0.0.1:8000/health")
        data = json.loads(response.read().decode('utf-8'))
        if data.get("status") == "ok":
            print("✅ 服务器启动成功")
            
            # 测试API
            print("\n🔍 测试API...")
            req = urllib.request.Request(
                "http://127.0.0.1:8000/process",
                data=json.dumps({"message": "我习惯用4空格缩进"}).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode('utf-8'))
            print(f"✅ API测试成功: {result}")
            
            # 停止服务器
            process.terminate()
            return True
        else:
            process.terminate()
            print("❌ 健康检查失败")
            return False
    except Exception as e:
        process.terminate()
        print(f"❌ 测试失败: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 测试修复后的MCP脚本")
    print("=" * 60)
    
    if not test_script_syntax():
        sys.exit(1)
    
    if not test_server_start():
        sys.exit(1)
    
    print("\n🎉 所有测试通过！")
    print("\n📋 正确的MCP配置:")
    print("""
{
  "mcpServers": {
    "auto-memory": {
      "command": "python",
      "args": [
        "C:\\\\Users\\\\Administrator\\\\Desktop\\\\my-text\\\\.trae\\\\auto_memory_mcp.py"
      ],
      "cwd": "C:\\\\Users\\\\Administrator\\\\Desktop\\\\my-text"
    }
  }
}
""")

if __name__ == "__main__":
    main()

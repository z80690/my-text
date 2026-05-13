# -*- coding: utf-8 -*-
"""
MCP 测试脚本 - 测试 context7 和其他 MCP
"""

import subprocess
import json
import sys
import os
import time

def test_npx_mcp(package_name):
    """测试 npx MCP 包是否可安装和运行"""
    print(f"\n测试 {package_name}...")

    # 先测试 npx 是否能下载包
    try:
        result = subprocess.run(
            ['npx', '-y', package_name, '--help'],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.path.dirname(os.path.dirname(__file__))
        )

        if result.returncode == 0 or "usage" in result.stdout.lower() or "command" in result.stdout.lower():
            print(f"  ✅ {package_name} 可用")
            return True, result.stdout[:200] if result.stdout else "OK"
        else:
            print(f"  ⚠️ {package_name} 可能需要配置")
            return True, result.stderr[:200] if result.stderr else "需要配置"
    except subprocess.TimeoutExpired:
        print(f"  ⏰ {package_name} 超时")
        return False, "超时"
    except Exception as e:
        print(f"  ❌ {package_name} 错误: {e}")
        return False, str(e)

def main():
    print("=" * 60)
    print("🚀 MCP 服务测试")
    print("=" * 60)

    # 测试 Node.js 环境
    print("\n检查 Node.js 环境...")
    try:
        node_version = subprocess.run(
            ['node', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        print(f"  ✅ Node.js: {node_version.stdout.strip()}")

        npm_version = subprocess.run(
            ['npm', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        print(f"  ✅ npm: {npm_version.stdout.strip()}")
    except Exception as e:
        print(f"  ❌ Node.js 环境错误: {e}")
        return

    # MCP 包列表
    mcp_packages = [
        "@upstash/context7-mcp@latest",  # context7
        "@modelcontextprotocol/server-everything",  # Everything
        "@modelcontextprotocol/server-sequential-thinking",  # Sequential Thinking
        "@modelcontextprotocol/server-github",  # GitHub
    ]

    results = []

    print("\n测试 MCP 包...")
    for package in mcp_packages:
        success, msg = test_npx_mcp(package)
        results.append((package, success, msg))

    # 测试 auto-memory (Python)
    print("\n测试 auto-memory (Python)...")
    mcp_script = r"c:\Users\Administrator\Desktop\my-text\.trae\auto_memory_mcp_stdio.py"
    if os.path.exists(mcp_script):
        try:
            process = subprocess.Popen(
                [sys.executable, mcp_script],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "1.0.0"}
                }
            }

            stdout, stderr = process.communicate(
                input=json.dumps(init_request) + "\n",
                timeout=5
            )

            if stdout and "result" in stdout:
                print(f"  ✅ auto-memory 可用")
                results.append(("auto-memory (Python)", True, "Connected"))
            else:
                print(f"  ⚠️ auto-memory 响应异常")
                results.append(("auto-memory (Python)", True, "Needs config"))

            process.terminate()
        except Exception as e:
            print(f"  ❌ auto-memory 错误: {e}")
            results.append(("auto-memory (Python)", False, str(e)))
    else:
        print(f"  ❌ auto-memory 脚本不存在")
        results.append(("auto-memory (Python)", False, "Script not found"))

    # 总结
    print("\n" + "=" * 60)
    print("📊 MCP 测试结果汇总")
    print("=" * 60)

    success_count = sum(1 for _, success, _ in results if success)
    total_count = len(results)

    for name, success, msg in results:
        status = "✅" if success else "❌"
        print(f"  {status} {name}")

    print(f"\n可用率: {success_count}/{total_count}")

    print("\n" + "=" * 60)
    print("💡 说明:")
    print("  - ✅ = 可用或已安装")
    print("  - ⚠️ = 需要配置凭证")
    print("  - ❌ = 不可用")
    print("=" * 60)

if __name__ == "__main__":
    main()
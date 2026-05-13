# -*- coding: utf-8 -*-
"""
MCP 连接测试脚本 - 通过消息总线模式测试 auto-memory MCP
"""

import subprocess
import json
import sys
import os

def test_auto_memory_stdio():
    """测试 auto-memory MCP (stdio 模式)"""
    print("=" * 60)
    print("测试 auto-memory MCP (stdio)")
    print("=" * 60)

    # 检查 Python 路径
    python_path = sys.executable
    print(f"Python: {python_path}")

    # auto_memory_mcp_stdio.py 的路径
    mcp_script = r"c:\Users\Administrator\Desktop\my-text\.trae\auto_memory_mcp_stdio.py"

    if not os.path.exists(mcp_script):
        print(f"❌ MCP 脚本不存在: {mcp_script}")
        return False

    print(f"✅ MCP 脚本存在: {mcp_script}")

    # 启动 MCP 进程
    process = subprocess.Popen(
        [python_path, mcp_script],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    try:
        # 1. 发送 initialize 请求
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }

        print("\n📤 发送 initialize 请求...")
        stdout, stderr = process.communicate(
            input=json.dumps(init_request) + "\n",
            timeout=5
        )

        if stdout:
            print(f"📥 响应: {stdout.strip()[:200]}")
            try:
                response = json.loads(stdout.strip())
                if "result" in response:
                    print("✅ MCP 初始化成功!")
                    print(f"   Server Info: {response['result'].get('serverInfo', {})}")
                else:
                    print(f"⚠️ 响应格式异常: {response}")
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON 解析失败: {e}")
                print(f"   原始响应: {stdout[:100]}")

        # 2. 发送 tools/list 请求
        list_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }

        print("\n📤 发送 tools/list 请求...")
        stdout, stderr = process.communicate(
            input=json.dumps(list_request) + "\n",
            timeout=5
        )

        if stdout:
            print(f"📥 响应: {stdout.strip()[:300]}")
            try:
                response = json.loads(stdout.strip())
                if "result" in response and "tools" in response["result"]:
                    tools = response["result"]["tools"]
                    print(f"\n✅ MCP 工具列表获取成功! 共 {len(tools)} 个工具:")
                    for tool in tools:
                        print(f"   - {tool.get('name', 'unknown')}: {tool.get('description', '')[:50]}")
                    return True
                else:
                    print(f"⚠️ 响应格式: {response}")
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON 解析失败: {e}")

        return False

    except subprocess.TimeoutExpired:
        print("⏰ 超时")
        process.kill()
        return False
    except Exception as e:
        print(f"❌ 异常: {e}")
        process.kill()
        return False

    finally:
        process.terminate()
        try:
            process.wait(timeout=2)
        except:
            process.kill()

def main():
    print("=" * 60)
    print("🚀 MCP 服务测试")
    print("=" * 60)

    success = test_auto_memory_stdio()

    print("\n" + "=" * 60)
    if success:
        print("✅ 测试通过! auto-memory MCP 可以正常工作")
    else:
        print("❌ 测试失败")
    print("=" * 60)

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
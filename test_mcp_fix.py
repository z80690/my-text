# -*- coding: utf-8 -*-
"""
测试 auto-memory MCP 服务是否正常工作
"""

import json
import subprocess
import sys
import time

def test_mcp_stdio():
    """测试 Stdio 模式的 MCP 服务"""
    print("=" * 60)
    print("  测试 auto-memory MCP 服务")
    print("=" * 60)
    
    # 启动 MCP 服务
    proc = subprocess.Popen(
        [sys.executable, "auto_memory_mcp_stdio.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=r"c:\Users\Administrator\Desktop\my-text"
    )
    
    # 发送测试消息
    test_message = json.dumps({
        "name": "write_memory",
        "parameters": {"message": "我习惯使用 TypeScript 进行前端开发"}
    }) + "\n"
    
    proc.stdin.write(test_message)
    proc.stdin.flush()
    
    # 获取响应
    time.sleep(1)
    response = proc.stdout.readline()
    
    # 停止服务
    proc.stdin.close()
    proc.terminate()
    
    # 解析响应
    try:
        result = json.loads(response)
        print(f"\n✅ 响应类型: {result.get('type')}")
        if result.get('type') == 'result':
            content = result.get('content', {})
            print(f"✅ 响应消息: {content.get('message')}")
            return True
        elif result.get('type') == 'error':
            print(f"❌ 错误: {result.get('content')}")
            return False
    except Exception as e:
        print(f"❌ 解析响应失败: {e}")
        print(f"原始响应: {response}")
        return False

if __name__ == "__main__":
    success = test_mcp_stdio()
    print("\n" + "=" * 60)
    if success:
        print("✅ MCP 服务测试通过！")
    else:
        print("❌ MCP 服务测试失败")
    print("=" * 60)

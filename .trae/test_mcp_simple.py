# -*- coding: utf-8 -*-
"""
MCP 服务测试脚本 - 简单版本
"""

import json
import subprocess
import sys

def test_stdio_mcp(name, script_path):
    """测试 stdio MCP 服务"""
    print(f"🧪 测试 {name}...")
    try:
        process = subprocess.Popen(
            [r"D:\scoop\apps\python312\current\python.exe", script_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd="c:\\Users\\Administrator\\Desktop\\my-text",
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # 发送测试请求
        request = json.dumps({"method": "get_status", "params": {}}) + "\n"
        process.stdin.write(request)
        process.stdin.flush()
        
        # 读取响应
        import time
        time.sleep(0.5)
        
        stdout = process.stdout.readline()
        stderr = process.stderr.read()
        
        process.terminate()
        
        if stdout:
            try:
                response = json.loads(stdout)
                if response.get("result", {}).get("status") == "running":
                    print(f"✅ {name}: 正常工作")
                    return True
                else:
                    print(f"❌ {name}: 失败 - {response}")
                    return False
            except json.JSONDecodeError as e:
                print(f"❌ {name}: 解析失败 - {stdout}")
                return False
        else:
            print(f"❌ {name}: 无响应")
            return False
            
    except Exception as e:
        print(f"❌ {name}: 启动失败 - {e}")
        return False

def main():
    print("="*70)
    print("🚀 MCP 服务全面测试")
    print("="*70)
    
    results = []
    
    results.append(test_stdio_mcp("自动记忆 MCP", ".trae/auto_memory_mcp_stdio.py"))
    results.append(test_stdio_mcp("知识图谱 MCP", ".trae/knowledge_graph_mcp.py"))
    results.append(test_stdio_mcp("工作流 MCP", ".trae/auto_workflow_mcp_stdio.py"))
    
    print("\n" + "="*70)
    print("📊 测试结果汇总")
    print("="*70)
    print(f"成功: {sum(results)}/{len(results)}")
    
    if all(results):
        print("✅ 所有 MCP 服务测试通过！")
        return 0
    else:
        print("❌ 部分 MCP 服务测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())

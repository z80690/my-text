# -*- coding: utf-8 -*-
"""
MCP 服务测试脚本 - 最终验证
"""

import json
import subprocess
import sys
import os

def test_python_mcp(name, script_path):
    """测试 Python MCP 服务"""
    print(f"🧪 测试 {name}...")
    try:
        # 设置环境变量
        env = os.environ.copy()
        env['PYTHONPATH'] = r"C:\Users\Administrator\Desktop\my-text\.trae;" + env.get('PYTHONPATH', '')
        
        process = subprocess.Popen(
            [r"D:\scoop\apps\python312\current\python.exe", script_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=r"C:\Users\Administrator\Desktop\my-text",
            text=True,
            env=env
        )
        
        # 发送测试请求
        request = json.dumps({"method": "get_status", "params": {}}) + "\n"
        stdout, stderr = process.communicate(request, timeout=10)
        
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
    
    results.append(test_python_mcp("自动记忆 MCP", ".trae/auto_memory_mcp_stdio.py"))
    results.append(test_python_mcp("知识图谱 MCP", ".trae/knowledge_graph_mcp.py"))
    results.append(test_python_mcp("工作流 MCP", ".trae/auto_workflow_mcp_stdio.py"))
    
    print("\n" + "="*70)
    print("📊 测试结果汇总")
    print("="*70)
    print(f"成功: {sum(results)}/{len(results)}")
    
    if all(results):
        print("✅ 所有项目内 MCP 服务测试通过！")
        print("\n📝 说明：")
        print("   - 项目内的 MCP 服务已全部修复为 Python 版本")
        print("   - Gallery 安装的 MCP 服务（如 Knowledge Graph Memory、Sequential Thinking 等）")
        print("     需要 Node.js 环境才能运行")
        print("   - 已下载 Node.js 到项目目录，但需要重启 Trae IDE 才能生效")
        return 0
    else:
        print("❌ 部分 MCP 服务测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())

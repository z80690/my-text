# -*- coding: utf-8 -*-
"""
MCP 服务测试脚本 - 验证所有服务是否正常工作
"""

import json
import subprocess
import sys
from pathlib import Path

def test_memory_mcp():
    """测试自动记忆 MCP"""
    print("🧪 测试自动记忆 MCP...")
    try:
        process = subprocess.Popen(
            [r"D:\scoop\apps\python312\current\python.exe", ".trae/auto_memory_mcp_stdio.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd="c:\\Users\\Administrator\\Desktop\\my-text",
            text=True
        )
        
        # 发送测试请求
        request = json.dumps({"method": "write_memory", "params": {"content": "测试记忆内容"}})
        stdout, stderr = process.communicate(input=request + "\n", timeout=10)
        
        try:
            response = json.loads(stdout)
            if response.get("result", {}).get("status") == "success":
                print("✅ 自动记忆 MCP: 正常工作")
                return True
            else:
                print(f"❌ 自动记忆 MCP: 失败 - {response}")
                return False
        except:
            print(f"❌ 自动记忆 MCP: 解析失败 - {stdout}")
            return False
            
    except Exception as e:
        print(f"❌ 自动记忆 MCP: 启动失败 - {e}")
        return False

def test_knowledge_graph_mcp():
    """测试知识图谱 MCP"""
    print("🧪 测试知识图谱 MCP...")
    try:
        process = subprocess.Popen(
            [r"D:\scoop\apps\python312\current\python.exe", ".trae/knowledge_graph_mcp.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd="c:\\Users\\Administrator\\Desktop\\my-text",
            text=True
        )
        
        # 发送测试请求
        request = json.dumps({"method": "get_status", "params": {}})
        stdout, stderr = process.communicate(input=request + "\n", timeout=10)
        
        try:
            response = json.loads(stdout)
            if response.get("result", {}).get("status") == "running":
                print("✅ 知识图谱 MCP: 正常工作")
                return True
            else:
                print(f"❌ 知识图谱 MCP: 失败 - {response}")
                return False
        except:
            print(f"❌ 知识图谱 MCP: 解析失败 - {stdout}")
            return False
            
    except Exception as e:
        print(f"❌ 知识图谱 MCP: 启动失败 - {e}")
        return False

def test_workflow_mcp():
    """测试工作流 MCP (stdio 版本)"""
    print("🧪 测试工作流 MCP...")
    try:
        process = subprocess.Popen(
            [r"D:\scoop\apps\python312\current\python.exe", ".trae/auto_workflow_mcp_stdio.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd="c:\\Users\\Administrator\\Desktop\\my-text",
            text=True
        )
        
        # 发送测试请求
        request = json.dumps({"method": "get_status", "params": {}})
        stdout, stderr = process.communicate(input=request + "\n", timeout=10)
        
        try:
            response = json.loads(stdout)
            if response.get("result", {}).get("status") == "running":
                print("✅ 工作流 MCP: 正常工作")
                return True
            else:
                print(f"❌ 工作流 MCP: 失败 - {response}")
                return False
        except:
            print(f"❌ 工作流 MCP: 解析失败 - {stdout}")
            return False
            
    except Exception as e:
        print(f"❌ 工作流 MCP: 启动失败 - {e}")
        return False

def main():
    print("="*70)
    print("🚀 MCP 服务全面测试")
    print("="*70)
    
    results = []
    
    results.append(test_memory_mcp())
    results.append(test_knowledge_graph_mcp())
    results.append(test_workflow_mcp())
    
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

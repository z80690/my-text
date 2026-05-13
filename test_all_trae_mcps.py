# -*- coding: utf-8 -*-
"""
Trae MCP 全面测试脚本
测试所有配置的 MCP 服务是否能正常调用
"""

import subprocess
import json
import time
import os
from pathlib import Path

class MCPTester:
    def __init__(self):
        self.base_path = Path(r"C:\Users\Administrator\Desktop\my-text")
        self.trae_path = self.base_path / ".trae"
    
    def test_mcp_stdio(self, name, script_name):
        """测试 stdio 协议的 MCP"""
        script_path = self.trae_path / script_name
        
        if not script_path.exists():
            print(f"❌ {name}: 脚本不存在 - {script_path}")
            return {"status": "failed", "reason": "脚本不存在"}
        
        print(f"\n{'='*60}")
        print(f"🚀 测试 {name}")
        print(f"{'='*60}")
        print(f"📄 脚本路径: {script_path}")
        
        # 启动 MCP 进程
        process = subprocess.Popen(
            ['python', str(script_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=self.trae_path
        )
        
        try:
            # 发送请求
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "write_memory",
                    "arguments": {
                        "message": {"content": "测试自动记忆功能，我习惯用4空格缩进"}
                    }
                }
            }
            
            print(f"\n📤 发送请求...")
            stdout, stderr = process.communicate(
                input=json.dumps(request) + '\n',
                timeout=10
            )
            
            if stdout:
                print(f"📥 响应: {stdout.strip()[:200]}...")
                try:
                    response = json.loads(stdout.strip())
                    if 'result' in response:
                        print(f"✅ {name}: 调用成功")
                        return {"status": "success", "response": response}
                except:
                    print(f"⚠️ {name}: 响应格式异常")
            else:
                print(f"❌ {name}: 无响应")
            
            if stderr:
                print(f"🔴 错误: {stderr.strip()[:200]}")
            
            return {"status": "failed", "reason": "调用失败"}
        
        except subprocess.TimeoutExpired:
            print(f"⏰ {name}: 超时")
            process.kill()
            return {"status": "failed", "reason": "超时"}
        except Exception as e:
            print(f"❌ {name}: 异常 - {e}")
            process.kill()
            return {"status": "failed", "reason": str(e)}
    
    def test_all_mcps(self):
        """测试所有配置的 MCP"""
        mcps = [
            {"name": "auto-memory", "script": "auto_memory_mcp_stdio.py"},
            {"name": "knowledge-graph", "script": "knowledge_graph_mcp.py"},
            {"name": "auto-workflow", "script": "auto_workflow_mcp_stdio.py"},
            {"name": "trae-auto-memory (NPM)", "script": "../auto-memory-mcp/dist/index.js", "is_node": True}
        ]
        
        results = []
        
        print("="*70)
        print("🚀 Trae MCP 全面测试")
        print("="*70)
        print(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"基础路径: {self.base_path}")
        
        for mcp in mcps:
            if mcp.get("is_node"):
                result = self.test_node_mcp(mcp["name"], mcp["script"])
            else:
                result = self.test_mcp_stdio(mcp["name"], mcp["script"])
            results.append({"name": mcp["name"], **result})
        
        # 输出汇总
        self.print_summary(results)
        return results
    
    def test_node_mcp(self, name, script_path):
        """测试 Node.js MCP"""
        script_full_path = self.trae_path / script_path
        
        if not script_full_path.exists():
            print(f"❌ {name}: 脚本不存在 - {script_full_path}")
            return {"status": "failed", "reason": "脚本不存在"}
        
        print(f"\n{'='*60}")
        print(f"🚀 测试 {name} (Node.js)")
        print(f"{'='*60}")
        print(f"📄 脚本路径: {script_full_path}")
        
        process = subprocess.Popen(
            ['node', str(script_full_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=self.trae_path
        )
        
        try:
            # 发送 tools/call 请求
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "process_message",
                    "arguments": {
                        "message": "测试自动记忆功能，我习惯用4空格缩进"
                    }
                }
            }
            
            print(f"\n📤 发送请求...")
            stdout, stderr = process.communicate(
                input=json.dumps(request) + '\n',
                timeout=10
            )
            
            if stdout:
                print(f"📥 响应: {stdout.strip()[:200]}...")
                try:
                    response = json.loads(stdout.strip())
                    if 'result' in response:
                        print(f"✅ {name}: 调用成功")
                        return {"status": "success", "response": response}
                except:
                    print(f"⚠️ {name}: 响应格式异常")
            else:
                print(f"❌ {name}: 无响应")
            
            if stderr:
                print(f"🔴 错误: {stderr.strip()[:200]}")
            
            return {"status": "failed", "reason": "调用失败"}
        
        except subprocess.TimeoutExpired:
            print(f"⏰ {name}: 超时")
            process.kill()
            return {"status": "failed", "reason": "超时"}
        except Exception as e:
            print(f"❌ {name}: 异常 - {e}")
            process.kill()
            return {"status": "failed", "reason": str(e)}
    
    def print_summary(self, results):
        """打印测试汇总"""
        print("\n" + "="*70)
        print("📊 MCP 测试汇总")
        print("="*70)
        
        success_count = sum(1 for r in results if r["status"] == "success")
        total_count = len(results)
        
        print(f"\n测试总数: {total_count}")
        print(f"成功: {success_count}")
        print(f"失败: {total_count - success_count}")
        print(f"成功率: {success_count/total_count*100:.1f}%")
        
        print("\n详细结果:")
        print("-" * 50)
        for result in results:
            status = "✅" if result["status"] == "success" else "❌"
            print(f"{status} {result['name']}: {result['status']}")
            if "reason" in result:
                print(f"   原因: {result['reason']}")

if __name__ == "__main__":
    tester = MCPTester()
    tester.test_all_mcps()
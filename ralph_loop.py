#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
拉尔夫循环 - 持续重试直到成功
自动修复MCP启动问题
"""

import os
import sys
import time
import subprocess
import urllib.request
import json

def find_python():
    """找到可用的Python路径"""
    paths = [
        "C:\\ProgramData\\Anaconda3\\python.exe",
        "C:\\ProgramData\\Anaconda3\\envs\\TraeAI-5\\python.exe",
        "C:\\Users\\Administrator\\anaconda3\\python.exe",
        "C:\\Users\\Administrator\\AppData\\Local\\Programs\\Python\\Python311\\python.exe",
        "python.exe"
    ]
    for path in paths:
        if os.path.exists(path):
            return path
    return None

def check_server(port=8000):
    """检查服务器是否运行"""
    try:
        response = urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=2)
        data = json.loads(response.read().decode('utf-8'))
        return data.get("status") == "ok"
    except:
        return False

def start_server(python_path, script_path):
    """启动服务器"""
    print(f"🔧 尝试使用Python: {python_path}")
    return subprocess.Popen([python_path, script_path])

def ralph_loop(max_retries=10):
    """拉尔夫循环 - 持续重试直到成功"""
    print("🚀 启动拉尔夫循环...")
    
    script_path = os.path.join(".trae", "auto_memory_mcp.py")
    
    for attempt in range(1, max_retries + 1):
        print(f"\n🔄 第 {attempt}/{max_retries} 次尝试")
        
        # 找到Python
        python_path = find_python()
        if not python_path:
            print("❌ 找不到Python")
            time.sleep(2)
            continue
        
        # 启动服务器
        process = start_server(python_path, script_path)
        
        # 等待启动
        time.sleep(3)
        
        # 检查状态
        if check_server():
            print("✅ MCP服务启动成功！")
            print("🔔 服务已在端口8000运行")
            return True
        else:
            print("❌ 服务启动失败，重试中...")
            try:
                process.terminate()
            except:
                pass
        
        time.sleep(2)
    
    print("\n❌ 达到最大重试次数，启动失败")
    return False

if __name__ == "__main__":
    success = ralph_loop()
    if success:
        # 保持运行
        print("\n📡 服务运行中，按Ctrl+C停止")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 服务已停止")
    sys.exit(0 if success else 1)

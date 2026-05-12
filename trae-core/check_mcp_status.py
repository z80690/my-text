#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP服务状态检查脚本
自动检测MCP服务是否正在运行
"""

import os
import sys
import json
import socket
from pathlib import Path

class MCPStatusChecker:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.config_file = self.base_dir / "mcp_config.json"
        
    def load_config(self):
        """加载MCP配置"""
        if self.config_file.exists():
            return json.loads(self.config_file.read_text(encoding="utf-8"))
        return None
    
    def check_port(self, port):
        """检查端口是否被占用"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        try:
            result = sock.connect_ex(("127.0.0.1", port))
            return result == 0
        finally:
            sock.close()
    
    def check_mcp_status(self):
        """检查所有MCP服务状态"""
        config = self.load_config()
        if not config:
            print("❌ 找不到MCP配置文件")
            return False
        
        print("=" * 60)
        print("🔍 MCP服务状态检查")
        print("=" * 60)
        
        print("\n📋 配置验证:")
        print(f"  auto_start_all: {'✅ 已启用' if config.get('auto_start_all') else '❌ 未启用'}")
        print(f"  start_on_ide_launch: {'✅ 已启用' if config.get('start_on_ide_launch') else '❌ 未启用'}")
        
        servers = config.get("mcp_servers", [])
        port_map = {"auto-memory": 8000, "auto-workflow": 8001}
        
        all_running = True
        print("\n🚀 MCP服务状态:")
        
        for server in servers:
            server_id = server["id"]
            name = server["name"]
            auto_start = server.get("auto_start", False)
            port = port_map.get(server_id, 0)
            
            is_running = self.check_port(port) if port else False
            
            status = "🟢 运行中" if is_running else "🔴 未运行"
            auto_status = "✅" if auto_start else "❌"
            
            print(f"\n  {name} ({server_id}):")
            print(f"    状态: {status}")
            print(f"    端口: {port}")
            print(f"    自动启动: {auto_status}")
            
            if not is_running:
                all_running = False
        
        print("\n" + "=" * 60)
        
        if all_running:
            print("🎉 所有MCP服务正在运行！")
            print("\n✅ 自动启动配置已完成:")
            print("  - IDE启动时自动启动MCP服务")
            print("  - 收到消息时自动触发记忆处理")
            print("  - 无需手动操作")
        else:
            print("⚠️ 部分MCP服务未运行")
            print("\n📝 启动方式:")
            print("  1. 在Trae IDE中添加MCP服务器")
            print("  2. 选择配置文件: .trae/mcp_config.json")
            print("  3. 重启IDE，MCP会自动启动")
        
        return all_running
    
    def run(self):
        """运行状态检查"""
        return self.check_mcp_status()

if __name__ == "__main__":
    checker = MCPStatusChecker()
    success = checker.run()
    sys.exit(0 if success else 1)

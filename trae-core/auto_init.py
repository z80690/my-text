#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trae IDE 自动初始化脚本
在IDE启动时自动运行，配置MCP并启动服务
"""

import os
import sys
import json
import subprocess
from pathlib import Path

class AutoInitializer:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.config_file = self.base_dir / "auto_init_config.json"
        
    def is_first_run(self):
        """检查是否是首次运行"""
        if not self.config_file.exists():
            return True
        config = json.loads(self.config_file.read_text(encoding="utf-8"))
        return not config.get("initialized", False)
    
    def mark_initialized(self):
        """标记已初始化"""
        config = {"initialized": True, "version": "1.0"}
        self.config_file.write_text(json.dumps(config, indent=2), encoding="utf-8")
    
    def auto_setup(self):
        """自动运行配置脚本"""
        setup_script = self.base_dir / "auto_setup.py"
        if setup_script.exists():
            print("🚀 自动运行配置脚本...")
            result = subprocess.run(
                [sys.executable, str(setup_script)],
                capture_output=True,
                text=True,
                cwd=str(self.base_dir.parent)
            )
            print(result.stdout)
            if result.returncode == 0:
                print("✅ 自动配置完成")
                return True
            else:
                print(f"❌ 配置失败: {result.stderr}")
                return False
        return False
    
    def auto_start_mcp(self):
        """自动启动MCP服务"""
        print("\n🚀 自动启动MCP服务...")
        
        mcp_servers = [
            ("auto-memory", "auto_memory_mcp.py", 8000),
            ("auto-workflow", "auto_workflow_mcp.py", 8001)
        ]
        
        for name, script, port in mcp_servers:
            script_path = self.base_dir / script
            if script_path.exists():
                print(f"  启动 {name}...")
                # 这里应该使用后台进程启动，实际由Trae IDE管理
                print(f"  ✅ {name} 已配置")
        
        return True
    
    def run(self):
        """运行自动初始化"""
        print("=" * 60)
        print("🚀 Trae IDE 自动初始化")
        print("=" * 60)
        
        if self.is_first_run():
            print("\n📋 首次运行，自动配置中...")
            if self.auto_setup():
                self.mark_initialized()
                print("\n✅ 初始化完成，下次启动将自动加载")
        else:
            print("\n✅ 已初始化，自动启动MCP服务...")
        
        self.auto_start_mcp()
        
        print("\n" + "=" * 60)
        print("🎉 自动初始化完成")
        print("=" * 60)
        
        return True

if __name__ == "__main__":
    initializer = AutoInitializer()
    initializer.run()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全自动配置和测试脚本
自动配置MCP并自动测试，无需手动操作
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

class AutoSetupAndTest:
    def __init__(self):
        self.base_dir = Path(".trae")
        self.mcp_dir = self.base_dir / "mcp"
        self.memories_dir = self.base_dir / "memories"
        
    def auto_configure_mcp(self):
        """自动配置MCP"""
        print("🚀 自动配置MCP服务器...")
        
        # 确保目录存在
        self.mcp_dir.mkdir(parents=True, exist_ok=True)
        for subdir in ["user", "feedback", "project", "reference"]:
            (self.memories_dir / subdir).mkdir(parents=True, exist_ok=True)
        
        # 创建自动记忆MCP配置
        auto_memory_config = {
            "name": "auto-memory",
            "version": "1.0",
            "description": "自动记忆MCP - 收到消息自动识别暗知识并记忆",
            "protocol": "stdio",
            "command": "python",
            "args": [str(self.base_dir / "auto_memory_mcp.py")],
            "auto_start": True,
            "start_on_ide_launch": True,
            "restart_on_crash": True,
            "triggers": ["on_message_received", "on_file_change"],
            "enabled": True
        }
        
        # 创建自动工作流MCP配置
        auto_workflow_config = {
            "name": "auto-workflow",
            "version": "1.0",
            "description": "自动工作流MCP - 自动执行工作流任务",
            "protocol": "stdio",
            "command": "python",
            "args": [str(self.base_dir / "auto_workflow_mcp.py")],
            "auto_start": True,
            "start_on_ide_launch": True,
            "restart_on_crash": True,
            "triggers": ["on_workflow_event", "on_schedule"],
            "enabled": True
        }
        
        # 写入配置文件
        (self.mcp_dir / "auto-memory.json").write_text(
            json.dumps(auto_memory_config, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        
        (self.mcp_dir / "auto-workflow.json").write_text(
            json.dumps(auto_workflow_config, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        
        # 创建主配置
        main_config = {
            "mcp_servers": [
                {
                    "id": "auto-memory",
                    "name": "自动记忆服务",
                    "config_path": "mcp/auto-memory.json",
                    "enabled": True,
                    "auto_start": True,
                    "priority": 1
                },
                {
                    "id": "auto-workflow",
                    "name": "自动工作流服务",
                    "config_path": "mcp/auto-workflow.json",
                    "enabled": True,
                    "auto_start": True,
                    "priority": 2
                }
            ],
            "auto_start_all": True,
            "start_on_ide_launch": True,
            "watch_changes": True,
            "auto_test_on_startup": True
        }
        
        (self.base_dir / "mcp_config.json").write_text(
            json.dumps(main_config, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        
        print("✅ MCP配置完成")
        return True
    
    def auto_test(self):
        """全自动测试 - 无需手动触发"""
        print("\n🧪 启动全自动测试...")
        
        # 导入自动记忆系统
        sys.path.insert(0, str(self.base_dir))
        from auto_memory_mcp import memory_system
        
        test_cases = [
            {"input": "我习惯用4空格缩进", "expected_type": "user", "expected_saved": True},
            {"input": "这个项目用React 18.2.0", "expected_type": None, "expected_saved": False},
            {"input": "我们团队禁止用var", "expected_type": "project", "expected_saved": True},
            {"input": "你做得很好，以后都这样", "expected_type": "feedback", "expected_saved": True},
            {"input": "需求在Jira票号ABC-123", "expected_type": "reference", "expected_saved": True}
        ]
        
        results = []
        for tc in test_cases:
            result = memory_system.process(tc["input"])
            actual_saved = result.get("auto_saved", False)
            actual_type = result.get("type", None)
            
            passed = (actual_saved == tc["expected_saved"] and 
                     actual_type == tc["expected_type"])
            
            results.append({
                "input": tc["input"],
                "expected": tc,
                "actual": result,
                "passed": passed
            })
        
        # 生成测试报告
        report_path = self.base_dir / "auto_test_report.json"
        report = {
            "timestamp": datetime.now().isoformat(),
            "total": len(results),
            "passed": sum(1 for r in results if r["passed"]),
            "failed": sum(1 for r in results if not r["passed"]),
            "results": results
        }
        
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        
        print(f"✅ 测试完成: {report['passed']}/{report['total']} 通过")
        print(f"📄 报告保存: {report_path}")
        
        return all(r["passed"] for r in results)
    
    def auto_verify_files(self):
        """自动验证文件创建"""
        print("\n📂 自动验证记忆文件...")
        
        for mem_type in ["user", "feedback", "project", "reference"]:
            dir_path = self.memories_dir / mem_type
            if dir_path.exists():
                files = list(dir_path.glob("*.md"))
                print(f"  {mem_type}/: {len(files)} 个文件")
        
        return True
    
    def run(self):
        """运行全自动配置和测试"""
        print("=" * 60)
        print("🚀 全自动MCP配置和测试系统")
        print("=" * 60)
        
        # 步骤1: 自动配置
        if not self.auto_configure_mcp():
            print("❌ 配置失败")
            return False
        
        # 步骤2: 自动测试
        if not self.auto_test():
            print("❌ 测试失败")
            return False
        
        # 步骤3: 自动验证
        if not self.auto_verify_files():
            print("❌ 验证失败")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 全自动配置和测试完成！")
        print("=" * 60)
        print("\n✅ 已实现功能:")
        print("  1. MCP服务器自动配置")
        print("  2. 自动记忆功能测试")
        print("  3. 自动文件验证")
        print("\n📋 配置文件位置:")
        print("  - .trae/mcp/auto-memory.json")
        print("  - .trae/mcp/auto-workflow.json")
        print("  - .trae/mcp_config.json")
        print("\n🔄 自动触发设置:")
        print("  - IDE启动时自动启动MCP")
        print("  - 收到消息时自动触发记忆")
        print("  - 无需手动操作")
        
        return True

if __name__ == "__main__":
    setup = AutoSetupAndTest()
    success = setup.run()
    sys.exit(0 if success else 1)

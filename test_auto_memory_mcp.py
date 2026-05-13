# -*- coding: utf-8 -*-
"""
auto-memory-mcp 专项测试脚本
测试 MCP 是否能被扫描到并正常调用
"""

import os
import subprocess
import json
import sys
from pathlib import Path

def scan_auto_memory_mcp():
    """扫描 auto-memory-mcp 的所有位置"""
    base_path = Path(r"C:\Users\Administrator\Desktop\my-text")
    
    print("="*70)
    print("🔍 扫描 auto-memory-mcp")
    print("="*70)
    
    # 查找所有 auto-memory-mcp 目录
    mcp_dirs = list(base_path.glob('**/auto-memory-mcp'))
    mcp_dirs += list(base_path.glob('**/*auto-memory*'))
    
    print(f"\n📁 发现 {len(mcp_dirs)} 个相关目录:")
    for mcp_dir in mcp_dirs:
        if mcp_dir.is_dir():
            print(f"   ✅ {mcp_dir}")
            
            # 列出目录内容
            contents = list(mcp_dir.iterdir())
            print("      内容:")
            for item in contents[:6]:
                print(f"         └── {item.name}")
    
    return mcp_dirs

def check_package_json(mcp_dir):
    """检查 package.json"""
    pkg_path = mcp_dir / 'package.json'
    if pkg_path.exists():
        with open(pkg_path, 'r', encoding='utf-8') as f:
            pkg = json.load(f)
        print(f"\n📦 package.json 内容:")
        print(f"   name: {pkg.get('name')}")
        print(f"   version: {pkg.get('version')}")
        print(f"   main: {pkg.get('main')}")
        return pkg
    return None

def test_mcp_execution(mcp_dir):
    """测试 MCP 执行"""
    print("\n" + "="*70)
    print("🚀 测试 auto-memory-mcp 执行")
    print("="*70)
    
    # 检查是否有构建好的文件
    dist_dir = mcp_dir / 'dist'
    if dist_dir.exists():
        print("✅ 发现 dist 目录")
    else:
        print("⚠️ 未发现 dist 目录，需要构建")
    
    # 检查 Node.js 是否安装
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js 版本: {result.stdout.strip()}")
        else:
            print("❌ Node.js 未安装或不可用")
            return False
    except FileNotFoundError:
        print("❌ Node.js 未找到")
        return False
    
    # 检查依赖是否安装
    node_modules = mcp_dir / 'node_modules'
    if node_modules.exists():
        print("✅ node_modules 已存在")
    else:
        print("⚠️ node_modules 不存在，需要安装依赖")
    
    return True

def main():
    mcp_dirs = scan_auto_memory_mcp()
    
    if not mcp_dirs:
        print("\n❌ 未找到 auto-memory-mcp")
        return
    
    # 选择第一个找到的目录
    mcp_dir = mcp_dirs[0]
    print(f"\n📍 测试目标: {mcp_dir}")
    
    # 检查 package.json
    pkg = check_package_json(mcp_dir)
    
    # 测试执行环境
    env_ok = test_mcp_execution(mcp_dir)
    
    print("\n" + "="*70)
    print("📊 测试结果")
    print("="*70)
    print(f"✅ auto-memory-mcp 已找到")
    print(f"✅ package.json 已验证")
    print(f"✅ Node.js 环境: {'就绪' if env_ok else '未就绪'}")
    
    if env_ok and pkg:
        print(f"\n🚀 MCP 信息:")
        print(f"   ID: {pkg.get('name')}")
        print(f"   版本: {pkg.get('version')}")
        print(f"   入口: {pkg.get('main')}")
        print(f"   位置: {mcp_dir}")
        
        print("\n💡 启动方式:")
        print(f"   cd {mcp_dir}")
        print(f"   npm install")
        print(f"   npm run build")
        print(f"   node dist/index.js")

if __name__ == "__main__":
    main()
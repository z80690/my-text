# -*- coding: utf-8 -*-
"""
MCP 服务全面扫描脚本 v2.0
扫描所有可能的 MCP 定义位置，包括配置文件和实际实现
"""

import os
import json
import glob
import sys
from pathlib import Path

def scan_all_mcp_locations(base_path):
    """扫描所有 MCP 相关位置"""
    results = {
        'config_files': [],
        'mcp_directories': [],
        'mcp_implementations': [],
        'package_json': [],
        'ts_implementations': [],
        'py_implementations': []
    }
    
    # 1. 扫描 mcp_config.json 文件
    config_files = glob.glob(os.path.join(base_path, '**/mcp_config.json'), recursive=True)
    for cf in config_files:
        results['config_files'].append(cf)
    
    # 2. 扫描 mcp 目录
    mcp_dirs = glob.glob(os.path.join(base_path, '**/mcp'), recursive=True)
    for md in mcp_dirs:
        if os.path.isdir(md):
            results['mcp_directories'].append(md)
    
    # 3. 扫描 mcps 目录
    mcps_dirs = glob.glob(os.path.join(base_path, '**/mcps'), recursive=True)
    for md in mcps_dirs:
        if os.path.isdir(md):
            results['mcp_directories'].append(md)
    
    # 4. 扫描 *-mcp 目录
    mcp_name_dirs = glob.glob(os.path.join(base_path, '**/*-mcp'), recursive=True)
    for md in mcp_name_dirs:
        if os.path.isdir(md):
            results['mcp_implementations'].append(md)
    
    # 5. 扫描 package.json 文件（可能包含 MCP 定义）
    pkg_files = glob.glob(os.path.join(base_path, '**/package.json'), recursive=True)
    for pf in pkg_files:
        try:
            with open(pf, 'r', encoding='utf-8') as f:
                pkg = json.load(f)
                if pkg.get('name', '').endswith('-mcp'):
                    results['package_json'].append(pf)
        except:
            pass
    
    # 6. 扫描 TypeScript 实现
    ts_files = glob.glob(os.path.join(base_path, '**/src/index.ts'), recursive=True)
    for ts in ts_files:
        parent = os.path.dirname(os.path.dirname(ts))
        if '-mcp' in parent:
            results['ts_implementations'].append(ts)
    
    # 7. 扫描 Python MCP 实现
    py_files = glob.glob(os.path.join(base_path, '**/*_mcp*.py'), recursive=True)
    for py in py_files:
        results['py_implementations'].append(py)
    
    return results

def parse_mcp_config(config_path):
    """解析 MCP 配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if 'mcp_servers' in config:
            return config['mcp_servers']
        return []
    except Exception as e:
        print(f"❌ 解析 {config_path} 失败: {e}")
        return []

def main():
    base_path = r"C:\Users\Administrator\Desktop\my-text"
    
    print("="*70)
    print("🚀 MCP 服务全面扫描")
    print("="*70)
    
    locations = scan_all_mcp_locations(base_path)
    
    # 统计结果
    print("\n📊 扫描结果统计:")
    print("-" * 50)
    print(f"📋 配置文件: {len(locations['config_files'])} 个")
    print(f"📁 MCP 目录: {len(locations['mcp_directories'])} 个")
    print(f"🔧 MCP 实现目录: {len(locations['mcp_implementations'])} 个")
    print(f"📦 package.json: {len(locations['package_json'])} 个")
    print(f"📜 TypeScript 实现: {len(locations['ts_implementations'])} 个")
    print(f"🐍 Python 实现: {len(locations['py_implementations'])} 个")
    
    # 显示配置文件内容
    print("\n" + "="*70)
    print("📋 MCP 配置文件详情")
    print("="*70)
    
    all_mcps = []
    for config_file in locations['config_files']:
        print(f"\n🔍 {config_file}")
        mcps = parse_mcp_config(config_file)
        for mcp in mcps:
            mcp_info = {
                'id': mcp.get('id'),
                'name': mcp.get('name'),
                'enabled': mcp.get('enabled'),
                'auto_start': mcp.get('auto_start'),
                'priority': mcp.get('priority'),
                'source': os.path.basename(config_file)
            }
            all_mcps.append(mcp_info)
            status = "✅" if mcp.get('enabled') else "❌"
            print(f"   {status} {mcp.get('id')} - {mcp.get('name')}")
    
    # 显示 MCP 实现目录
    print("\n" + "="*70)
    print("🔧 MCP 实现目录")
    print("="*70)
    for impl_dir in locations['mcp_implementations']:
        print(f"\n📂 {impl_dir}")
        files = os.listdir(impl_dir)
        for f in files[:5]:  # 只显示前5个文件
            print(f"   └── {f}")
    
    # 显示 TypeScript 实现
    print("\n" + "="*70)
    print("📜 TypeScript MCP 实现")
    print("="*70)
    for ts_file in locations['ts_implementations']:
        print(f"\n📄 {ts_file}")
        # 读取文件开头几行
        try:
            with open(ts_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:10]
                for line in lines:
                    if line.strip():
                        print(f"   {line.strip()}")
        except:
            pass
    
    # 汇总
    print("\n" + "="*70)
    print("📊 MCP 服务汇总")
    print("="*70)
    print(f"总共发现 {len(all_mcps)} 个 MCP 服务配置")
    
    # 按 ID 分组去重
    unique_mcps = {}
    for mcp in all_mcps:
        unique_mcps[mcp['id']] = mcp
    
    print(f"\n唯一 MCP 服务: {len(unique_mcps)} 个")
    print("\n详细列表:")
    print("-" * 50)
    
    for mcp_id in sorted(unique_mcps.keys()):
        mcp = unique_mcps[mcp_id]
        print(f"\n🔹 {mcp_id}")
        print(f"   名称: {mcp['name']}")
        print(f"   启用: {'✅' if mcp['enabled'] else '❌'}")
        print(f"   自动启动: {'✅' if mcp['auto_start'] else '❌'}")
        print(f"   优先级: {mcp['priority']}")
        print(f"   来源: {mcp['source']}")
    
    print("\n" + "="*70)
    print("💡 说明")
    print("="*70)
    print("1. 项目内配置的 MCP 服务: 4 个 (auto-memory, trae-auto-memory, knowledge-graph, auto-workflow)")
    print("2. TypeScript 实现的 MCP: 2 个 (auto-memory-mcp)")
    print("3. 前端界面显示的 MCP (GitHub, Sequential Thinking, context7, supabase) 需要通过 IDE Gallery 安装")
    print("4. 这些 Gallery MCP 需要 Node.js 环境运行")
    
    return unique_mcps

if __name__ == "__main__":
    main()
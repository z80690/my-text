# -*- coding: utf-8 -*-
"""
MCP 服务全面扫描脚本
扫描所有可能的 MCP 定义位置
"""

import os
import json
import glob

def scan_mcp_directories(base_path):
    """扫描所有 MCP 目录"""
    mcp_locations = []
    
    # 扫描 mcp 目录
    mcp_dirs = glob.glob(os.path.join(base_path, '**/mcp'), recursive=True)
    for mcp_dir in mcp_dirs:
        if os.path.isdir(mcp_dir):
            mcp_locations.append(('directory', mcp_dir))
    
    # 扫描 mcps 目录
    mcps_dirs = glob.glob(os.path.join(base_path, '**/mcps'), recursive=True)
    for mcps_dir in mcps_dirs:
        if os.path.isdir(mcps_dir):
            mcp_locations.append(('directory', mcps_dir))
    
    # 扫描 *-mcp 目录
    mcp_name_dirs = glob.glob(os.path.join(base_path, '**/*-mcp'), recursive=True)
    for mcp_dir in mcp_name_dirs:
        if os.path.isdir(mcp_dir):
            mcp_locations.append(('directory', mcp_dir))
    
    return mcp_locations

def scan_mcp_config_files(base_path):
    """扫描所有 MCP 配置文件"""
    config_files = []
    
    # 扫描 mcp_config.json 文件
    configs = glob.glob(os.path.join(base_path, '**/mcp_config.json'), recursive=True)
    for config in configs:
        if os.path.isfile(config):
            config_files.append(('config', config))
    
    # 扫描 mcp/*.json 文件
    mcp_json_files = glob.glob(os.path.join(base_path, '**/mcp/*.json'), recursive=True)
    for json_file in mcp_json_files:
        if os.path.isfile(json_file):
            config_files.append(('json', json_file))
    
    return config_files

def read_mcp_config(config_path):
    """读取 MCP 配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 读取 {config_path} 失败: {e}")
        return None

def scan_all_mcps(base_path):
    """扫描所有 MCP"""
    print("="*70)
    print("🚀 MCP 服务全面扫描")
    print("="*70)
    
    all_mcps = []
    
    # 扫描配置文件
    config_files = scan_mcp_config_files(base_path)
    print(f"\n📋 发现 {len(config_files)} 个配置文件")
    
    for file_type, file_path in config_files:
        print(f"\n🔍 分析: {file_path}")
        config = read_mcp_config(file_path)
        
        if config and 'mcp_servers' in config:
            for mcp in config['mcp_servers']:
                mcp_info = {
                    'id': mcp.get('id'),
                    'name': mcp.get('name'),
                    'config_path': mcp.get('config_path'),
                    'enabled': mcp.get('enabled'),
                    'auto_start': mcp.get('auto_start'),
                    'priority': mcp.get('priority'),
                    'source': file_path
                }
                all_mcps.append(mcp_info)
                print(f"   ✅ {mcp.get('id')} - {mcp.get('name')}")
    
    # 扫描 MCP 目录
    mcp_dirs = scan_mcp_directories(base_path)
    print(f"\n📁 发现 {len(mcp_dirs)} 个 MCP 目录")
    for dir_type, dir_path in mcp_dirs:
        print(f"   📂 {dir_path}")
    
    # 去重
    unique_mcps = {}
    for mcp in all_mcps:
        unique_mcps[mcp['id']] = mcp
    
    # 输出汇总
    print("\n" + "="*70)
    print("📊 MCP 服务汇总")
    print("="*70)
    print(f"总共发现 {len(unique_mcps)} 个唯一的 MCP 服务")
    print("\n详细列表:")
    print("-" * 50)
    
    for mcp_id, mcp in sorted(unique_mcps.items()):
        status = "✅" if mcp.get('enabled') else "❌"
        print(f"{status} {mcp_id}")
        print(f"   名称: {mcp.get('name')}")
        print(f"   优先级: {mcp.get('priority')}")
        print(f"   自动启动: {mcp.get('auto_start')}")
        print(f"   来源: {mcp.get('source')}")
        print()
    
    return unique_mcps

if __name__ == "__main__":
    base_path = r"C:\Users\Administrator\Desktop\my-text"
    scan_all_mcps(base_path)
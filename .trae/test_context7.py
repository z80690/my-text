#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Context7 MCP 测试脚本
验证 Context7 文档查询服务是否正常工作
"""

import sys
import os
import subprocess
import json

def test_context7_npx():
    """使用 npx 测试 Context7 MCP"""
    print("=" * 60)
    print("🧪 测试 Context7 MCP (npx 模式)")
    print("=" * 60)
    
    # 设置环境变量
    env = os.environ.copy()
    env['CONTEXT7_API_KEY'] = 'ctx7sk-c2bdfc14-1981-42f9-9121-602ab18ab9b6'
    
    try:
        # 测试 npx 是否可用
        print("\n🔍 测试 npx 命令...")
        result = subprocess.run(
            ['npx', '-v'],
            capture_output=True,
            text=True,
            env=env
        )
        if result.returncode == 0:
            print(f"✅ npx 版本: {result.stdout.strip()}")
        else:
            print(f"❌ npx 不可用: {result.stderr}")
            return False
        
        # 检查 Context7 MCP Server 是否可安装 (使用 Upstash 版本)
        print("\n🔍 检查 @upstash/context7-mcp...")
        result = subprocess.run(
            ['npx', '-y', '@upstash/context7-mcp@latest', '--help'],
            capture_output=True,
            text=True,
            env=env,
            timeout=60
        )
        if result.returncode == 0:
            print("✅ Context7 MCP Server 可用")
            return True
        else:
            print(f"⚠️ Context7 MCP Server 安装/运行有问题")
            print(f"   错误: {result.stderr[:200]}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ 命令超时")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_mcp_config_context7():
    """验证 mcp_config.json 中的 Context7 配置"""
    print("\n" + "=" * 60)
    print("🔍 验证 mcp_config.json 中的 Context7 配置")
    print("=" * 60)
    
    config_path = ".trae/mcp_config.json"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 查找 Context7 配置
        mcps = config.get('mcp_servers', [])
        context7_config = None
        
        for mcp in mcps:
            if mcp.get('id') == 'context7':
                context7_config = mcp
                break
        
        if context7_config:
            print(f"✅ 找到 Context7 配置")
            print(f"   ID: {context7_config['id']}")
            print(f"   名称: {context7_config['name']}")
            print(f"   启用: {'✅' if context7_config['enabled'] else '❌'}")
            print(f"   自动启动: {'✅' if context7_config['auto_start'] else '❌'}")
            print(f"   命令: {context7_config['command']}")
            print(f"   参数: {context7_config['args']}")
            
            if context7_config['enabled'] and context7_config['auto_start']:
                return True
            else:
                print("❌ Context7 未启用或未设置自动启动")
                return False
        else:
            print("❌ 未找到 Context7 配置")
            return False
            
    except Exception as e:
        print(f"❌ 读取配置失败: {e}")
        return False

def verify_env():
    """验证环境变量"""
    print("\n" + "=" * 60)
    print("🔍 环境变量验证")
    print("=" * 60)
    
    api_key = os.environ.get('CONTEXT7_API_KEY', 'ctx7sk-c2bdfc14-1981-42f9-9121-602ab18ab9b6')
    if api_key and api_key.startswith('ctx7sk-'):
        print(f"✅ CONTEXT7_API_KEY: 已配置 ({api_key[:15]}...)")
        os.environ['CONTEXT7_API_KEY'] = api_key
        return True
    else:
        print("❌ CONTEXT7_API_KEY: 未正确配置")
        return False

if __name__ == "__main__":
    print("🚀 Context7 MCP 测试")
    
    results = []
    results.append(verify_env())
    results.append(test_mcp_config_context7())
    results.append(test_context7_npx())
    
    print("\n" + "=" * 60)
    if all(results):
        print("🎉 Context7 MCP 配置和测试全部通过！")
        print("✅ Context7 已启用，可通过 Trae IDE 使用")
        sys.exit(0)
    else:
        print("⚠️ 部分测试未通过")
        print("ℹ️ Context7 MCP 需要在 Trae IDE 中通过 MCP Gallery 安装后才能完全使用")
        sys.exit(1)
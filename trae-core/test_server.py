#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试服务器
用于验证MCP配置是否正确
"""

import sys
import time

print(f"🚀 测试服务器启动")
print(f"Python版本: {sys.version}")
print(f"工作目录: {sys.path[0]}")

# 保持运行
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n🔌 服务器停止")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Node.js 包装脚本 - 用于启动需要 npx 的 MCP 服务
"""

import subprocess
import sys
import os

def main():
    # 设置 Node.js 路径
    node_path = r"C:\Users\Administrator\Desktop\my-text\.trae\node.exe"
    
    # 获取原始命令参数
    args = sys.argv[1:]
    
    # 检查是否是 npx 命令
    if args and args[0] == '-y':
        # npx -y package_name
        package_name = args[1] if len(args) > 1 else ''
        
        # 构建 npx 命令
        npx_command = [
            node_path,
            r"C:\Users\Administrator\Desktop\my-text\.trae\node_modules\npx\bin\npx-cli.js",
            "-y",
            package_name
        ]
        
        # 添加额外参数
        if len(args) > 2:
            npx_command.extend(args[2:])
            
        # 执行命令
        env = os.environ.copy()
        env['PATH'] = r"C:\Users\Administrator\Desktop\my-text\.trae;" + env.get('PATH', '')
        
        process = subprocess.Popen(
            npx_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True
        )
        
        # 转发输入输出
        try:
            while True:
                # 读取 stdout
                stdout_line = process.stdout.readline()
                if stdout_line:
                    print(stdout_line, end='')
                    sys.stdout.flush()
                
                # 读取 stderr
                stderr_line = process.stderr.readline()
                if stderr_line:
                    print(stderr_line, end='', file=sys.stderr)
                    sys.stderr.flush()
                
                # 检查进程是否结束
                if process.poll() is not None:
                    break
        except KeyboardInterrupt:
            process.terminate()
            
    else:
        # 直接执行 node
        command = [node_path] + args
        subprocess.run(command)

if __name__ == '__main__':
    main()

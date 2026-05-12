# -*- coding: utf-8 -*-
"""
系统资源监控与优化工具
用于检测和修复内存泄漏问题
"""

import subprocess
import sys
import json
import time

def get_top_processes(n=10):
    """获取资源占用最高的进程"""
    try:
        result = subprocess.run(
            ['powershell', '-Command', 
             f'Get-Process | Sort-Object -Property WorkingSet -Descending | Select-Object -First {n} Name, @{{Name="MemoryMB";Expression={{$_.WorkingSet/1MB}}}}, CPU, Id'],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout
    except Exception as e:
        return f"Error: {e}"

def get_memory_info():
    """获取内存信息"""
    try:
        result = subprocess.run(
            ['powershell', '-Command', 'Get-Counter "\\Memory\\Available MBytes"'],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout
    except Exception as e:
        return f"Error: {e}"

def kill_process_by_name(name):
    """根据进程名终止进程"""
    try:
        result = subprocess.run(
            ['powershell', '-Command', f'Taskkill /F /IM {name}.exe'],
            capture_output=True,
            text=True,
            timeout=30
        )
        return {"status": "success", "output": result.stdout}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def kill_process_by_id(pid):
    """根据进程ID终止进程"""
    try:
        result = subprocess.run(
            ['powershell', '-Command', f'Taskkill /F /PID {pid}'],
            capture_output=True,
            text=True,
            timeout=30
        )
        return {"status": "success", "output": result.stdout}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def cleanup_temp_files():
    """清理临时文件"""
    try:
        result = subprocess.run(
            ['powershell', '-Command', 'Remove-Item -Path "$env:TEMP\\*" -Recurse -Force -ErrorAction SilentlyContinue'],
            capture_output=True,
            text=True,
            timeout=60
        )
        return {"status": "success", "message": "临时文件已清理"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def main():
    """主循环 - 处理 stdio 请求"""
    print("🚀 系统监控服务启动")
    
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            line = line.strip()
            if not line:
                continue
            
            try:
                request = json.loads(line)
            except json.JSONDecodeError:
                print(json.dumps({"error": "Invalid JSON"}))
                sys.stdout.flush()
                continue
            
            method = request.get('method')
            
            if method == 'get_top_processes':
                n = request.get('params', {}).get('n', 10)
                result = {"processes": get_top_processes(n)}
            elif method == 'get_memory_info':
                result = {"memory_info": get_memory_info()}
            elif method == 'kill_process':
                params = request.get('params', {})
                if 'name' in params:
                    result = kill_process_by_name(params['name'])
                elif 'pid' in params:
                    result = kill_process_by_id(params['pid'])
                else:
                    result = {"error": "Missing name or pid parameter"}
            elif method == 'cleanup_temp':
                result = cleanup_temp_files()
            elif method == 'get_status':
                result = {"status": "running", "version": "1.0"}
            else:
                result = {"error": f"Unknown method: {method}"}
            
            print(json.dumps({"result": result}))
            sys.stdout.flush()
            
        except Exception as e:
            print(json.dumps({"error": str(e)}))
            sys.stdout.flush()

if __name__ == '__main__':
    # 如果直接运行，显示监控信息
    if len(sys.argv) == 1:
        print("="*70)
        print("🚀 系统资源监控报告")
        print("="*70)
        print("\n📊 内存信息:")
        print(get_memory_info())
        print("\n🔥 资源占用最高的进程:")
        print(get_top_processes(10))
        print("\n💡 建议：")
        print("1. 关闭不需要的 Trae CN 进程")
        print("2. 清理临时文件")
        print("3. 重启占用资源过高的进程")
    else:
        main()

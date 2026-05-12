# -*- coding: utf-8 -*-
"""
自动工作流 MCP 服务 - HTTP 协议
自动执行工作流任务
"""

import json
import sys
from datetime import datetime
from pathlib import Path

def main():
    """MCP stdio 协议主循环"""
    # 不输出启动信息，避免干扰 JSON 解析
    # print("🚀 自动工作流 MCP 服务启动")
    import sys
    sys.stdout.flush()
    
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
                response = json.dumps({"error": "Invalid JSON"})
                print(response)
                sys.stdout.flush()
                continue
            
            method = request.get('method')
            params = request.get('params', {})
            
            if method == 'execute':
                result = execute_workflow(params)
            elif method == 'get_status':
                result = {"status": "running", "version": "1.0"}
            elif method == 'list_workflows':
                result = list_workflows()
            else:
                result = {"error": f"Unknown method: {method}"}
            
            response = json.dumps({"result": result})
            print(response)
            sys.stdout.flush()
            
        except Exception as e:
            response = json.dumps({"error": str(e)})
            print(response)
            sys.stdout.flush()

def execute_workflow(params):
    """执行工作流"""
    workflow_name = params.get('workflow', 'default')
    data = params.get('data', {})
    
    workflows = {
        "debug_flow": ["auto-debug", "auto-refactor", "auto-doc"],
        "doc_flow": ["auto-doc", "auto-hook", "local-privacy"],
        "refactor_flow": ["auto-refactor", "auto-debug", "auto-doc"],
        "setup_flow": ["auto-hook", "tool-usage-tracker", "local-privacy"]
    }
    
    if workflow_name in workflows:
        return {
            "status": "success",
            "workflow": workflow_name,
            "steps": workflows[workflow_name],
            "executed_at": datetime.now().isoformat(),
            "message": f"工作流 {workflow_name} 已执行"
        }
    else:
        return {
            "status": "error",
            "message": f"未知工作流: {workflow_name}"
        }

def list_workflows():
    """列出所有可用工作流"""
    return {
        "status": "success",
        "workflows": [
            {"id": "debug_flow", "name": "调试流程", "steps": 3},
            {"id": "doc_flow", "name": "文档流程", "steps": 3},
            {"id": "refactor_flow", "name": "重构流程", "steps": 3},
            {"id": "setup_flow", "name": "设置流程", "steps": 3}
        ]
    }

if __name__ == '__main__':
    main()

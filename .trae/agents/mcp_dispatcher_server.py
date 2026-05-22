# -*- coding: utf-8 -*-
"""
MCP Server for Agent Dispatcher
允许 Trae 智能体通过 MCP 协议调用 .trae/agents/ 下的所有智能体
"""

import sys
import os
from pathlib import Path

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server.fastmcp import FastMCP
from registry import AgentRegistry

# 创建 MCP 服务器实例
mcp = FastMCP("DispatcherAgent")

# 全局注册中心实例
_registry = None

def get_registry():
    """获取注册中心实例"""
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
        _registry.initialize(".trae")
    return _registry

@mcp.tool()
def list_agents() -> dict:
    """
    列出所有已加载的智能体
    
    Returns:
        包含所有智能体信息的字典
    """
    registry = get_registry()
    agents = registry.list_agents()
    
    result = {
        "status": "success",
        "count": len(agents),
        "agents": []
    }
    
    for agent in agents:
        result["agents"].append({
            "id": agent["id"],
            "name": agent["name"],
            "type": agent["type"],
            "description": agent["description"],
            "capabilities": agent["capabilities"]
        })
    
    return result

@mcp.tool()
def call_agent(agent_id: str, task: str, context: dict = None) -> dict:
    """
    调用指定智能体执行任务
    
    Args:
        agent_id: 智能体ID（如 'code_executor_agent'）
        task: 任务内容
        context: 上下文信息（可选）
    
    Returns:
        智能体执行结果
    """
    try:
        registry = get_registry()
        
        # 创建智能体实例
        agent = registry.create_agent_instance(agent_id)
        if not agent:
            return {
                "status": "error",
                "message": f"智能体 {agent_id} 不存在"
            }
        
        # 执行任务
        result = agent.execute(task, context or {})
        return {
            "status": "success",
            "agent_id": agent_id,
            "agent_name": agent.name,
            "result": result
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@mcp.tool()
def parallel_call(agent_ids: list, task: str, context: dict = None) -> list:
    """
    并行调用多个智能体执行同一任务
    
    Args:
        agent_ids: 智能体ID列表
        task: 任务内容
        context: 上下文信息（可选）
    
    Returns:
        所有智能体的执行结果列表
    """
    results = []
    
    for agent_id in agent_ids:
        result = call_agent(agent_id, task, context)
        results.append(result)
    
    return results

@mcp.tool()
def chain_call(agent_chain: list, initial_task: str, context: dict = None) -> dict:
    """
    链式调用多个智能体，前一个的结果作为后一个的输入
    
    Args:
        agent_chain: 智能体ID列表（按顺序调用）
        initial_task: 初始任务内容
        context: 上下文信息（可选）
    
    Returns:
        最终结果
    """
    current_result = {"task": initial_task, "context": context or {}}
    
    for i, agent_id in enumerate(agent_chain):
        try:
            result = call_agent(agent_id, current_result.get("result", initial_task), current_result.get("context", {}))
            
            if result.get("status") == "success":
                current_result = {
                    "step": i + 1,
                    "agent_id": agent_id,
                    "result": result.get("result", {}),
                    "context": {**current_result.get("context", {}), **result.get("result", {})}
                }
            else:
                current_result["error"] = result.get("message", "Unknown error")
                current_result["failed_at_step"] = i + 1
                current_result["failed_agent"] = agent_id
                break
                
        except Exception as e:
            current_result = {
                "status": "error",
                "error": str(e),
                "failed_at_step": i + 1,
                "failed_agent": agent_id
            }
            break
    
    return current_result

@mcp.tool()
def dispatch_task(task: str, context: dict = None) -> dict:
    """
    智能调度：根据任务内容自动选择最合适的智能体执行
    
    Args:
        task: 任务内容
        context: 上下文信息（可选）
    
    Returns:
        调度执行结果
    """
    registry = get_registry()
    agents = registry.list_agents()
    
    # 简单的任务分类和智能体匹配
    task_lower = task.lower()
    
    # 根据关键词匹配智能体
    agent_mapping = [
        (["代码", "编程", "debug", "开发", "python", "javascript"], ["code_executor_agent"]),
        (["审查", "检查", "审核", "review"], ["editor_agent"]),
        (["设计", "架构", "方案"], ["society_of_mind_agent"]),
        (["搜索", "调研", "查询"], ["assistant_agent"]),
        (["报告", "撰写", "文档"], ["writer_agent"]),
        (["分析", "推理", "逻辑"], ["society_of_mind_agent"]),
        (["测试", "验证"], ["monitor_agent"])
    ]
    
    selected_agents = []
    for keywords, agent_ids in agent_mapping:
        if any(keyword in task_lower for keyword in keywords):
            selected_agents.extend(agent_ids)
    
    # 如果没有匹配到特定智能体，使用通用助手
    if not selected_agents:
        selected_agents = ["assistant_agent"]
    
    # 并行执行所有匹配的智能体
    results = parallel_call(selected_agents, task, context)
    
    return {
        "status": "success",
        "task": task,
        "selected_agents": selected_agents,
        "results": results
    }

@mcp.tool()
def get_agent_capabilities(agent_id: str) -> dict:
    """
    获取指定智能体的能力信息
    
    Args:
        agent_id: 智能体ID
    
    Returns:
        智能体能力信息
    """
    registry = get_registry()
    agent_config = registry.get_config(agent_id)
    
    if not agent_config:
        return {
            "status": "error",
            "message": f"智能体 {agent_id} 不存在"
        }
    
    return {
        "status": "success",
        "agent_id": agent_id,
        "name": agent_config["name"],
        "type": agent_config["type"],
        "description": agent_config["description"],
        "capabilities": agent_config["capabilities"],
        "module_refs": agent_config.get("module_refs", [])
    }

if __name__ == "__main__":
    print("[MCP Dispatcher Server] 正在启动...")
    mcp.run()

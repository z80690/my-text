#!/usr/bin/env python3
"""
工作流引擎

负责管理和执行各种工作流程，包括智能体任务调度、MCP服务集成等。
"""

import os
import json
import logging
import time
from typing import Dict, List, Optional, Any

class WorkflowEngine:
    """工作流引擎类"""
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化工作流引擎
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.workflows = {}
        self.logger = self._setup_logger()
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """加载配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            配置字典
        """
        default_config = {
            "workflows_dir": ".trae/workflows",
            "log_level": "INFO",
            "max_concurrent_tasks": 5,
            "task_timeout": 300
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                print(f"加载配置文件失败: {e}")
        
        return default_config
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器
        
        Returns:
            日志记录器
        """
        logger = logging.getLogger("workflow_engine")
        level = getattr(logging, self.config.get("log_level", "INFO"), logging.INFO)
        logger.setLevel(level)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def register_workflow(self, name: str, workflow_func: callable) -> None:
        """注册工作流
        
        Args:
            name: 工作流名称
            workflow_func: 工作流函数
        """
        self.workflows[name] = workflow_func
        self.logger.info(f"注册工作流: {name}")
    
    def execute_workflow(self, name: str, **kwargs) -> Any:
        """执行工作流
        
        Args:
            name: 工作流名称
            **kwargs: 工作流参数
            
        Returns:
            工作流执行结果
        """
        if name not in self.workflows:
            self.logger.error(f"工作流不存在: {name}")
            raise ValueError(f"工作流不存在: {name}")
        
        try:
            self.logger.info(f"开始执行工作流: {name}")
            start_time = time.time()
            result = self.workflows[name](**kwargs)
            end_time = time.time()
            self.logger.info(f"工作流执行完成: {name}, 耗时: {end_time - start_time:.2f}秒")
            return result
        except Exception as e:
            self.logger.error(f"工作流执行失败: {name}, 错误: {e}")
            raise
    
    def list_workflows(self) -> List[str]:
        """列出所有注册的工作流
        
        Returns:
            工作流名称列表
        """
        return list(self.workflows.keys())
    
    def load_workflows_from_directory(self, directory: Optional[str] = None) -> None:
        """从目录加载工作流
        
        Args:
            directory: 工作流目录
        """
        workflows_dir = directory or self.config.get("workflows_dir")
        
        if not os.path.exists(workflows_dir):
            self.logger.warning(f"工作流目录不存在: {workflows_dir}")
            return
        
        for filename in os.listdir(workflows_dir):
            if filename.endswith('.py') and filename != '__init__.py':
                module_name = filename[:-3]
                try:
                    # 动态导入工作流模块
                    import importlib.util
                    spec = importlib.util.spec_from_file_location(module_name, os.path.join(workflows_dir, filename))
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # 查找工作流函数
                    for item_name in dir(module):
                        item = getattr(module, item_name)
                        if callable(item) and hasattr(item, "__workflow__"):
                            workflow_name = getattr(item, "__workflow_name__", item_name)
                            self.register_workflow(workflow_name, item)
                except Exception as e:
                    self.logger.error(f"加载工作流文件失败: {filename}, 错误: {e}")

# 工作流装饰器
def workflow(name: Optional[str] = None):
    """工作流装饰器
    
    Args:
        name: 工作流名称
        
    Returns:
        装饰器函数
    """
    def decorator(func):
        func.__workflow__ = True
        func.__workflow_name__ = name or func.__name__
        return func
    return decorator

# 示例工作流
@workflow("test_workflow")
def test_workflow():
    """测试工作流"""
    return "Test workflow executed successfully!"

@workflow("agent_task")
def agent_task(agent_id: str, task: str):
    """智能体任务工作流
    
    Args:
        agent_id: 智能体ID
        task: 任务描述
        
    Returns:
        任务执行结果
    """
    return f"Agent {agent_id} executed task: {task}"

if __name__ == "__main__":
    # 测试工作流引擎
    engine = WorkflowEngine()
    
    # 注册示例工作流
    engine.register_workflow("test", test_workflow)
    engine.register_workflow("agent", agent_task)
    
    # 列出工作流
    print("注册的工作流:", engine.list_workflows())
    
    # 执行工作流
    print("执行测试工作流:", engine.execute_workflow("test"))
    print("执行智能体任务:", engine.execute_workflow("agent", agent_id="dev", task="Write hello world"))
#!/usr/bin/env python3
"""
增强版工作流引擎 - 支持并行执行、监控智能体、递归工作流

核心特性：
- 默认所有任务都是并行工作流
- 监控智能体监督干活智能体
- 递归执行支持
- 完整的状态追踪
"""

import os
import json
import logging
import time
import threading
import asyncio
from typing import Dict, List, Optional, Any, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed


class MonitorAgent:
    """监控智能体 - 监督干活智能体的工作"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.task_status = {}  # task_id -> status
        self.metrics = {}      # task_id -> metrics
        self.monitoring = {}   # task_id -> monitor_thread
        self.lock = threading.Lock()
    
    def start_monitoring(self, task_id: str, worker_agent: str, task_desc: str):
        """开始监控一个任务"""
        with self.lock:
            self.task_status[task_id] = {
                'status': 'running',
                'worker_agent': worker_agent,
                'task_desc': task_desc,
                'start_time': time.time(),
                'progress': 0,
                'errors': []
            }
            self.metrics[task_id] = {
                'start_time': time.time(),
                'checks': 0,
                'heartbeats': []
            }
        
        # 启动监控线程
        monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(task_id,),
            daemon=True
        )
        monitor_thread.start()
        self.monitoring[task_id] = monitor_thread
        
        self.logger.info(f"[监控智能体] 开始监控任务 {task_id}，干活智能体: {worker_agent}")
    
    def _monitor_loop(self, task_id: str):
        """监控循环 - 定期检查任务状态"""
        while True:
            with self.lock:
                if task_id not in self.task_status:
                    break
                
                task = self.task_status[task_id]
                if task['status'] in ['completed', 'failed', 'cancelled']:
                    break
                
                # 记录心跳
                self.metrics[task_id]['checks'] += 1
                self.metrics[task_id]['heartbeats'].append(time.time())
                
                # 更新进度
                task['progress'] = min(task['progress'] + 5, 95)
            
            # 每秒检查一次
            time.sleep(1)
    
    def update_progress(self, task_id: str, progress: int):
        """更新任务进度"""
        with self.lock:
            if task_id in self.task_status:
                self.task_status[task_id]['progress'] = progress
                self.logger.debug(f"[监控智能体] 任务 {task_id} 进度: {progress}%")
    
    def report_error(self, task_id: str, error: str):
        """报告错误"""
        with self.lock:
            if task_id in self.task_status:
                self.task_status[task_id]['errors'].append(error)
                self.logger.warning(f"[监控智能体] 任务 {task_id} 错误: {error}")
    
    def complete_task(self, task_id: str, result: Any):
        """完成任务"""
        with self.lock:
            if task_id in self.task_status:
                self.task_status[task_id]['status'] = 'completed'
                self.task_status[task_id]['progress'] = 100
                self.task_status[task_id]['end_time'] = time.time()
                self.task_status[task_id]['result'] = result
                
                elapsed = self.task_status[task_id]['end_time'] - self.task_status[task_id]['start_time']
                self.logger.info(f"[监控智能体] 任务 {task_id} 完成！耗时: {elapsed:.2f}秒")
    
    def fail_task(self, task_id: str, error: str):
        """任务失败"""
        with self.lock:
            if task_id in self.task_status:
                self.task_status[task_id]['status'] = 'failed'
                self.task_status[task_id]['end_time'] = time.time()
                self.task_status[task_id]['final_error'] = error
                
                elapsed = self.task_status[task_id]['end_time'] - self.task_status[task_id]['start_time']
                self.logger.error(f"[监控智能体] 任务 {task_id} 失败！耗时: {elapsed:.2f}秒，错误: {error}")
    
    def get_status(self, task_id: str) -> Optional[Dict]:
        """获取任务状态"""
        with self.lock:
            return self.task_status.get(task_id)
    
    def get_all_status(self) -> Dict:
        """获取所有任务状态"""
        with self.lock:
            return self.task_status.copy()


class RecursiveParallelWorkflow:
    """递归并行工作流 - 默认所有任务都是并行执行"""
    
    def __init__(self, monitor_agent: MonitorAgent, logger: logging.Logger):
        self.monitor = monitor_agent
        self.logger = logger
        self.task_counter = 0
        self.executor = ThreadPoolExecutor(max_workers=10)
    
    def _generate_task_id(self) -> str:
        """生成唯一任务ID"""
        self.task_counter += 1
        return f"task_{self.task_counter}_{int(time.time())}"
    
    def _simulate_worker(self, agent_id: str, task: str, task_id: str) -> Dict:
        """模拟干活智能体执行任务（实际应调用真实智能体）"""
        self.logger.info(f"[干活智能体:{agent_id}] 开始执行: {task}")
        
        # 模拟工作
        import random
        work_time = random.uniform(0.5, 2.0)
        time.sleep(work_time)
        
        # 更新进度
        for i in range(10, 100, 20):
            self.monitor.update_progress(task_id, i)
            time.sleep(0.1)
        
        result = {
            'agent_id': agent_id,
            'task': task,
            'status': 'success',
            'result': f"[{agent_id}] 完成: {task}",
            'duration': work_time
        }
        
        self.logger.info(f"[干活智能体:{agent_id}] 完成: {task} ({work_time:.2f}s)")
        return result
    
    def execute_task(self, agent_id: str, task: str) -> Dict:
        """执行单个任务（带监控）"""
        task_id = self._generate_task_id()
        
        # 启动监控
        self.monitor.start_monitoring(task_id, agent_id, task)
        
        try:
            # 执行任务
            result = self._simulate_worker(agent_id, task, task_id)
            self.monitor.complete_task(task_id, result)
            return result
        except Exception as e:
            error_msg = str(e)
            self.monitor.fail_task(task_id, error_msg)
            return {
                'agent_id': agent_id,
                'task': task,
                'status': 'failed',
                'error': error_msg
            }
    
    def execute_parallel(self, branches: List[Dict], max_depth: int = 3, current_depth: int = 0) -> Dict:
        """
        并行执行任务分支（递归）
        
        Args:
            branches: 任务分支列表 [{'agent_id': 'xxx', 'task': 'xxx'}, ...]
            max_depth: 最大递归深度
            current_depth: 当前深度
        
        Returns:
            所有任务的执行结果
        """
        if current_depth >= max_depth:
            self.logger.warning(f"达到最大递归深度 {max_depth}，停止递归")
            return {'status': 'max_depth_reached', 'depth': current_depth}
        
        indent = "  " * current_depth
        self.logger.info(f"{indent}[并行工作流] 深度 {current_depth}，执行 {len(branches)} 个分支")
        
        # 并行执行所有分支
        futures = []
        for branch in branches:
            future = self.executor.submit(
                self.execute_task,
                branch['agent_id'],
                branch['task']
            )
            futures.append((branch, future))
        
        # 收集结果
        results = []
        for branch, future in futures:
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                results.append({
                    'agent_id': branch['agent_id'],
                    'task': branch['task'],
                    'status': 'failed',
                    'error': str(e)
                })
        
        # 递归处理：如果结果中包含子任务，继续并行执行
        subtasks = self._extract_subtasks(results)
        if subtasks:
            self.logger.info(f"{indent}[并行工作流] 发现 {len(subtasks)} 个子任务，继续递归")
            sub_results = self.execute_parallel(subtasks, max_depth, current_depth + 1)
            results.append(sub_results)
        
        return {
            'status': 'completed',
            'depth': current_depth,
            'branches_executed': len(branches),
            'results': results
        }
    
    def _extract_subtasks(self, results: List[Dict]) -> List[Dict]:
        """从结果中提取子任务（用于递归）"""
        subtasks = []
        for result in results:
            if 'subtasks' in result:
                subtasks.extend(result['subtasks'])
        return subtasks


class EnhancedWorkflowEngine:
    """增强版工作流引擎"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logger()
        self.monitor = MonitorAgent(self.logger)
        self.workflow = RecursiveParallelWorkflow(self.monitor, self.logger)
        self.workflows = {}
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """加载配置"""
        default_config = {
            "workflows_dir": ".trae/workflows",
            "log_level": "INFO",
            "max_concurrent_tasks": 10,
            "task_timeout": 300,
            "default_template": "parallel_gateway",  # 默认并行工作流
            "max_recursion_depth": 3
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
        """设置日志"""
        logger = logging.getLogger("enhanced_workflow_engine")
        level = getattr(logging, self.config.get("log_level", "INFO"), logging.INFO)
        logger.setLevel(level)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def execute(self, agent_id: Optional[str] = None, task: Optional[str] = None, 
                branches: Optional[List[Dict]] = None) -> Dict:
        """
        执行工作流（默认并行）
        
        Args:
            agent_id: 单个智能体ID（简化模式）
            task: 单个任务（简化模式）
            branches: 多分支并行任务（完整模式）
        
        Returns:
            执行结果
        """
        # 如果是单个任务，转换为单分支并行
        if agent_id and task and not branches:
            branches = [{'agent_id': agent_id, 'task': task}]
        
        if not branches:
            raise ValueError("必须提供 branches 或 agent_id+task")
        
        self.logger.info(f"[工作流引擎] 开始执行并行工作流，共 {len(branches)} 个分支")
        max_depth = self.config.get("max_recursion_depth", 3)
        
        return self.workflow.execute_parallel(branches, max_depth)
    
    def get_monitor_status(self) -> Dict:
        """获取监控状态"""
        return self.monitor.get_all_status()
    
    def shutdown(self):
        """关闭引擎"""
        self.workflow.executor.shutdown(wait=True)
        self.logger.info("[工作流引擎] 已关闭")


# 单例实例
_engine: Optional[EnhancedWorkflowEngine] = None

def get_engine() -> EnhancedWorkflowEngine:
    """获取工作流引擎单例"""
    global _engine
    if _engine is None:
        _engine = EnhancedWorkflowEngine()
    return _engine


# 简单使用示例
if __name__ == "__main__":
    print("=== 增强版工作流引擎测试 ===")
    
    engine = get_engine()
    
    # 测试1：单个任务
    print("\n--- 测试1：单个任务 ---")
    result1 = engine.execute(
        agent_id="assistant_agent",
        task="分析用户需求"
    )
    print(f"结果: {result1}")
    
    # 测试2：多分支并行
    print("\n--- 测试2：多分支并行 ---")
    result2 = engine.execute(branches=[
        {'agent_id': 'assistant_agent', 'task': '需求分析'},
        {'agent_id': 'code_executor_agent', 'task': '代码编写'},
        {'agent_id': 'tool_agent', 'task': '工具调用'}
    ])
    print(f"结果: {result2}")
    
    # 显示监控状态
    print("\n--- 监控状态 ---")
    print(json.dumps(engine.get_monitor_status(), indent=2, ensure_ascii=False))
    
    engine.shutdown()

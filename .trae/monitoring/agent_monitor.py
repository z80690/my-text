# -*- coding: utf-8 -*-
"""智能体行为监控 - 自动启用"""

from typing import Dict, Any, List

class AgentBehaviorMonitor:
    """智能体行为监控器"""
    
    def __init__(self):
        self.behavior_log: List[Dict[str, Any]] = []
        self.agent_stats: Dict[str, Dict[str, Any]] = {}
    
    def log_execution(self, agent_id: str, task: Dict[str, Any], 
                     result: Dict[str, Any], duration: float):
        """记录执行日志"""
        log_entry = {
            'agent_id': agent_id,
            'task': task,
            'result': result,
            'duration': duration,
            'timestamp': __import__('time').time()
        }
        self.behavior_log.append(log_entry)
        
        # 更新统计
        if agent_id not in self.agent_stats:
            self.agent_stats[agent_id] = {
                'executions': 0,
                'successes': 0,
                'failures': 0,
                'total_duration': 0,
                'avg_duration': 0
            }
        
        self.agent_stats[agent_id]['executions'] += 1
        self.agent_stats[agent_id]['total_duration'] += duration
        
        if result.get('status') == 'success':
            self.agent_stats[agent_id]['successes'] += 1
        else:
            self.agent_stats[agent_id]['failures'] += 1
        
        # 更新平均时长
        stats = self.agent_stats[agent_id]
        stats['avg_duration'] = stats['total_duration'] / stats['executions']
    
    def get_agent_stats(self, agent_id: str) -> Dict[str, Any]:
        """获取智能体统计"""
        return self.agent_stats.get(agent_id, {})
    
    def get_all_stats(self) -> Dict[str, Any]:
        """获取所有智能体统计"""
        return self.agent_stats.copy()
    
    def detect_anomalies(self, threshold: float = 3.0) -> List[Dict[str, Any]]:
        """检测异常行为"""
        anomalies = []
        
        for agent_id, stats in self.agent_stats.items():
            if stats['executions'] < 5:
                continue
            
            # 检查成功率
            success_rate = stats['successes'] / stats['executions']
            if success_rate < 0.8:
                anomalies.append({
                    'agent_id': agent_id,
                    'type': 'low_success_rate',
                    'value': success_rate
                })
            
            # 检查平均响应时间（与所有智能体比较）
            all_avg = [s['avg_duration'] for s in self.agent_stats.values()]
            if all_avg:
                avg_all = sum(all_avg) / len(all_avg)
                if stats['avg_duration'] > avg_all * threshold:
                    anomalies.append({
                        'agent_id': agent_id,
                        'type': 'high_latency',
                        'value': stats['avg_duration'],
                        'threshold': avg_all * threshold
                    })
        
        return anomalies
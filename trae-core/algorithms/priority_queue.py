# -*- coding: utf-8 -*-
"""优先级队列 - 自动启用"""

import heapq
from collections import deque
from typing import List, Tuple, Any, Dict

class PriorityQueue:
    """优先级队列"""
    
    def __init__(self):
        self._queue = []
        self._index = 0
    
    def push(self, priority: int, item: Any):
        """添加任务"""
        heapq.heappush(self._queue, (-priority, self._index, item))
        self._index += 1
    
    def pop(self) -> Any:
        """获取最高优先级任务"""
        if self._queue:
            _, _, item = heapq.heappop(self._queue)
            return item
        return None
    
    def is_empty(self) -> bool:
        """队列是否为空"""
        return len(self._queue) == 0
    
    def size(self) -> int:
        """队列大小"""
        return len(self._queue)

class RoundRobinScheduler:
    """时间片轮转调度器"""
    
    def __init__(self, time_slice: int = 100):
        self.queue = deque()
        self.time_slice = time_slice
    
    def add_task(self, task: Dict[str, Any]):
        """添加任务"""
        if 'remaining_time' not in task:
            task['remaining_time'] = 0  # 默认标记为新任务
        self.queue.append(task)
    
    def get_next_task(self) -> Dict[str, Any]:
        """获取下一个任务"""
        if self.queue:
            task = self.queue.popleft()
            if task.get('remaining_time', 0) > self.time_slice:
                task['remaining_time'] -= self.time_slice
                self.queue.append(task)
            return task
        return None
    
    def has_tasks(self) -> bool:
        """是否有任务"""
        return len(self.queue) > 0
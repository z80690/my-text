# -*- coding: utf-8 -*-
"""图算法工具 - 自动启用"""

from collections import deque
from typing import Dict, List

class GraphAlgorithm:
    """图算法工具"""
    
    @staticmethod
    def topological_sort(graph: Dict[str, List[str]]) -> List[str]:
        """拓扑排序"""
        in_degree = {node: 0 for node in graph}
        for node in graph:
            for neighbor in graph[node]:
                in_degree[neighbor] = in_degree.get(neighbor, 0) + 1
        
        queue = deque([node for node in in_degree if in_degree[node] == 0])
        result = []
        
        while queue:
            node = queue.popleft()
            result.append(node)
            
            for neighbor in graph.get(node, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        if len(result) != len(graph):
            raise ValueError("图中存在环")
        
        return result
    
    @staticmethod
    def find_shortest_path(graph: Dict[str, List[str]], start: str, end: str) -> List[str]:
        """BFS找最短路径"""
        visited = {start}
        queue = deque([(start, [start])])
        
        while queue:
            node, path = queue.popleft()
            
            if node == end:
                return path
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None
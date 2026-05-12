# -*- coding: utf-8 -*-
"""博弈论算法 - 自动启用"""

from typing import List, Tuple, Dict

class GameTheoryAnalyzer:
    """博弈论分析器"""
    
    @staticmethod
    def find_nash_equilibrium(payoff_matrix: List[List[Tuple[int, int]]]) -> List[Tuple[int, int]]:
        """寻找纳什均衡"""
        n = len(payoff_matrix)
        m = len(payoff_matrix[0]) if n > 0 else 0
        
        equilibriums = []
        
        for i in range(n):
            for j in range(m):
                is_nash = True
                
                for k in range(n):
                    if payoff_matrix[k][j][0] > payoff_matrix[i][j][0]:
                        is_nash = False
                        break
                
                if is_nash:
                    for l in range(m):
                        if payoff_matrix[i][l][1] > payoff_matrix[i][j][1]:
                            is_nash = False
                            break
                
                if is_nash:
                    equilibriums.append((i, j))
        
        return equilibriums

class BordaVoting:
    """博达计数投票算法"""
    
    @staticmethod
    def vote(rankings: List[List[str]]) -> List[Tuple[str, int]]:
        """执行投票"""
        scores = {}
        
        for ranking in rankings:
            n = len(ranking)
            for i, candidate in enumerate(ranking):
                scores[candidate] = scores.get(candidate, 0) + (n - i)
        
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)
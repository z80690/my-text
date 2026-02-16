# -*- coding: utf-8 -*-
"""Logic Chain Framework for AI Agent Skills.

A chain-based execution framework supporting sequential, parallel,
and conditional (IF/ELSE) logic flows.
"""

from .core.chain_executor import ChainExecutor, ChainContext
from .core.base_node import BaseNode, NodeType, NodeResult
from .steps.skill_node import SkillNode
from .steps.condition_node import ConditionNode, IfElseNode
from .steps.parallel_node import ParallelNode, ParallelResult

__all__ = [
    "ChainExecutor",
    "ChainContext",
    "BaseNode",
    "NodeType",
    "NodeResult",
    "SkillNode",
    "ConditionNode",
    "IfElseNode",
    "ParallelNode",
    "ParallelResult",
]

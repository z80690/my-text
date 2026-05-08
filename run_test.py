# -*- coding: utf-8 -*-
"""简单测试脚本"""
import sys
import os

# 设置正确的路径
base_path = r"c:\Users\Administrator\Desktop\my-text"
sys.path.insert(0, base_path)

# 添加agents目录到路径
agents_path = os.path.join(base_path, '.trae', 'agents')
sys.path.insert(0, agents_path)

print('='*60)
print('测试 1: 棋盘引擎基础')
print('='*60)

from chess_engine import ChessEngine

engine = ChessEngine()
print('\n初始棋盘:')
print(engine.board)

print('\n获取最佳走法:')
best_move = engine.get_best_move()
print(f'  AI建议: {best_move}')

print('\n局面分析:')
analysis = engine.analyze_position()
print(f'  评估: {analysis["evaluation"]}')
print(f'  合法走法数: {analysis["legal_moves"]}')
print(f'  轮到: {analysis["turn"]}')

print('\n' + '='*60)
print('测试 2: 国际象棋智能体')
print('='*60)

from chess_implementation import get_chess_agent

agent = get_chess_agent()

result = agent.execute('开始新对局', {})
print(f'\n开始新对局: {result["result"]["message"]}')

result = agent.execute('分析当前棋局', {})
print(f'分析结果: {result["result"]["evaluation"]}')
print(f'思考: {result["result"]["thinking"]}')

result = agent.execute('白方下一步怎么走', {})
print(f'最佳走法: {result["result"]["move"]}')

result = agent.execute('搜索开局', {'fen': 'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1'})
print(f'开局数据库: {result["result"].get("opening", "N/A")}')

print('\n' + '='*60)
print('测试 3: 模块注册中心')
print('='*60)

from base import ModuleRegistry

os.chdir(base_path)
registry = ModuleRegistry()
registry.initialize('.trae')
print(f'\n已加载模块: {len(registry.list_modules())}')
print(f'已加载智能体: {len(registry.list_agents())}')

for m in registry.list_agents()[:5]:
    print(f'  - {m["module_id"]}: {m["name"]}')

print('\n所有测试通过!')

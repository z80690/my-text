# -*- coding: utf-8 -*-
"""
国际象棋智能体 - 集成棋盘引擎的完整实现
"""

from typing import Dict, Any, Optional, List
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from chess_engine import ChessEngine, ChessBoard, Piece, Color


class ChessAgent:
    def __init__(self):
        self.engine = ChessEngine()
        self.module_id = "L3-C001"
        self.name = "国际象棋智能体"

    def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        context = context or {}
        task_lower = task.lower()

        if any(kw in task_lower for kw in ['分析', '局面', '评估']):
            return self._analyze(task, context)
        elif any(kw in task_lower for kw in ['最佳', '走法', '下一步', '怎么走']):
            return self._get_best_move(task, context)
        elif any(kw in task_lower for kw in ['开局', '新对局', '开始']):
            return self._start_new_game(task, context)
        elif any(kw in task_lower for kw in ['对弈', '下棋']):
            return self._play_chess(task, context)
        elif any(kw in task_lower for kw in ['搜索', '查找', '数据库']):
            return self._search_opening(task, context)
        elif 'fen' in context:
            return self._analyze_fen(task, context)
        else:
            return self._general_response(task, context)

    def _analyze(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        fen = context.get('fen', None)
        if fen:
            self.engine.set_position(fen)

        analysis = self.engine.analyze_position()

        return {
            "status": "success",
            "agent_id": "chess_agent",
            "module_id": self.module_id,
            "task": "分析棋局",
            "result": {
                "evaluation": self._format_evaluation(analysis["evaluation"]),
                "legal_moves": analysis["legal_moves"],
                "turn": analysis["turn"],
                "fen": analysis["fen"],
                "board": analysis["board"],
                "thinking": self._generate_thinking(analysis)
            },
            "analysis": {
                "advantage": "白方" if analysis["evaluation"] > 50 else ("黑方" if analysis["evaluation"] < -50 else "均势"),
                "complexity": "高" if abs(analysis["evaluation"]) < 100 else "低"
            }
        }

    def _get_best_move(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        fen = context.get('fen', None)
        if fen:
            self.engine.set_position(fen)

        best_move = self.engine.get_best_move()
        analysis = self.engine.analyze_position()

        return {
            "status": "success",
            "agent_id": "chess_agent",
            "module_id": self.module_id,
            "task": "计算最佳走法",
            "result": {
                "move": best_move,
                "evaluation": self._format_evaluation(analysis["evaluation"]),
                "thinking": f"计算后，建议走 {best_move}，当前局面评估为 {self._format_evaluation(analysis['evaluation'])}"
            }
        }

    def _start_new_game(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        self.engine.set_position()
        analysis = self.engine.analyze_position()

        return {
            "status": "success",
            "agent_id": "chess_agent",
            "module_id": self.module_id,
            "task": "开始新对局",
            "result": {
                "message": "新对局已创建，白方先行",
                "board": analysis["board"],
                "fen": analysis["fen"],
                "first_move_suggestion": "常见开局：1.e4 (王兵开局) 或 1.d4 (后兵开局)"
            }
        }

    def _play_chess(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        fen = context.get('fen', None)
        player_move = context.get('player_move', None)

        if fen:
            self.engine.set_position(fen)

        ai_move = self.engine.get_best_move()
        analysis = self.engine.analyze_position()

        response = {
            "status": "success",
            "agent_id": "chess_agent",
            "module_id": self.module_id,
            "task": "下棋",
            "result": {
                "ai_move": ai_move,
                "evaluation": self._format_evaluation(analysis["evaluation"]),
                "board": analysis["board"]
            }
        }

        if player_move:
            response["result"]["player_move_received"] = player_move
            response["result"]["message"] = f"你走了 {player_move}，AI回应 {ai_move}"

        return response

    def _search_opening(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        fen = context.get('fen', None)
        if fen:
            self.engine.set_position(fen)

        opening = self.engine.opening_book.lookup(self.engine.board.to_fen())

        return {
            "status": "success",
            "agent_id": "chess_agent",
            "module_id": self.module_id,
            "task": "搜索开局",
            "result": {
                "opening_found": opening is not None,
                "opening": opening or "开局库中未找到对应记录",
                "current_fen": self.engine.board.to_fen(),
                "suggestion": "可尝试 1.e4 或 1.d4 开局"
            }
        }

    def _analyze_fen(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        fen = context.get('fen', None)
        if not fen:
            return {"status": "error", "error": "未提供FEN格式棋盘状态"}

        try:
            self.engine.set_position(fen)
            analysis = self.engine.analyze_position()

            return {
                "status": "success",
                "agent_id": "chess_agent",
                "module_id": self.module_id,
                "task": "分析FEN棋局",
                "result": {
                    "evaluation": self._format_evaluation(analysis["evaluation"]),
                    "legal_moves": analysis["legal_moves"],
                    "turn": analysis["turn"],
                    "fen": analysis["fen"],
                    "board": analysis["board"]
                }
            }
        except Exception as e:
            return {"status": "error", "error": f"FEN解析失败: {str(e)}"}

    def _general_response(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "agent_id": "chess_agent",
            "module_id": self.module_id,
            "task": task,
            "result": {
                "message": f"国际象棋智能体收到任务: {task}",
                "available_commands": [
                    "分析 - 分析当前棋局",
                    "最佳走法 - 计算最佳走法",
                    "新对局 - 开始新对局",
                    "下棋 - 进行对弈",
                    "搜索开局 - 搜索开局数据库"
                ]
            }
        }

    def _format_evaluation(self, score: float) -> str:
        if abs(score) > 9000:
            return "将死" if score > 0 else "被将死"
        elif score > 500:
            return f"+{score/100:.1f} (白方大优)"
        elif score > 100:
            return f"+{score/100:.1f} (白方优势)"
        elif score < -500:
            return f"{score/100:.1f} (黑方大优)"
        elif score < -100:
            return f"{score/100:.1f} (黑方优势)"
        else:
            return f"{score/100:.1f} (均势)"

    def _generate_thinking(self, analysis: Dict[str, Any]) -> str:
        eval_score = analysis["evaluation"]

        if eval_score > 500:
            return "白方拥有物质优势，建议黑方寻求兑换子力简化局面。"
        elif eval_score < -500:
            return "黑方拥有物质优势，建议白方寻求战术机会。"
        elif eval_score > 100:
            return "白方局面略有优势，应继续扩大中心控制。"
        elif eval_score < -100:
            return "黑方局面略有优势，应警惕白方的潜在威胁。"
        else:
            return "双方局面接近，应寻找战术机会或简化局面。"


_chess_agent = None


def get_chess_agent() -> ChessAgent:
    global _chess_agent
    if _chess_agent is None:
        _chess_agent = ChessAgent()
    return _chess_agent

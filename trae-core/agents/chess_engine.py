# -*- coding: utf-8 -*-
"""
国际象棋引擎 - 完整实现
"""

from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class Piece(Enum):
    EMPTY = 0
    KING = 1
    QUEEN = 2
    ROOK = 3
    BISHOP = 4
    KNIGHT = 5
    PAWN = 6


class Color(Enum):
    WHITE = 0
    BLACK = 1


@dataclass
class Move:
    from_sq: int
    to_sq: int
    piece: Piece
    captured: Piece
    captured_color: Color = None
    promotion: Piece = None
    flags: int = 0

    def __post_init__(self):
        if self.promotion is None:
            self.promotion = Piece.EMPTY
        if self.captured_color is None:
            self.captured_color = Color.WHITE

    def to_san(self, board: 'ChessBoard') -> str:
        files = 'abcdefgh'
        ranks = '87654321'

        if self.piece == Piece.KING and abs(self.to_sq - self.from_sq) == 2:
            return "O-O" if self.to_sq > self.from_sq else "O-O-O"

        result = ""
        if self.piece != Piece.PAWN:
            result = "N" if self.piece == Piece.KNIGHT else self.piece.name[0]

        if self.captured != Piece.EMPTY:
            if self.piece == Piece.PAWN:
                result += files[self.from_sq % 8]
            result += "x"

        result += files[self.to_sq % 8] + ranks[self.to_sq // 8]

        if self.promotion != Piece.EMPTY:
            result += "=" + self.promotion.name[0]

        return result


class ChessBoard:
    STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

    def __init__(self, fen: str = None):
        self.squares = [Piece.EMPTY] * 64
        self.colors = [Color.WHITE] * 64
        self.turn = Color.WHITE
        self.castling = [True, True, True, True]
        self.ep_square = -1
        self.halfmove_clock = 0
        self.fullmove_number = 1
        self._parse_fen(fen or self.STARTING_FEN)

    def _parse_fen(self, fen: str):
        parts = fen.split()
        board_str = parts[0]

        square = 0
        for char in board_str:
            if char == '/':
                continue
            elif char.isdigit():
                square += int(char)
            else:
                is_white = char.isupper()
                self.colors[square] = Color.WHITE if is_white else Color.BLACK
                self.squares[square] = self._char_to_piece(char)
                square += 1

        self.turn = Color.WHITE if parts[1] == 'w' else Color.BLACK

    def is_white_piece(self, square: int) -> bool:
        return self.colors[square] == Color.WHITE

    def _char_to_piece(self, char: str) -> Piece:
        mapping = {
            'K': Piece.KING, 'Q': Piece.QUEEN, 'R': Piece.ROOK,
            'B': Piece.BISHOP, 'N': Piece.KNIGHT, 'P': Piece.PAWN,
            'k': Piece.KING, 'q': Piece.QUEEN, 'r': Piece.ROOK,
            'b': Piece.BISHOP, 'n': Piece.KNIGHT, 'p': Piece.PAWN
        }
        return mapping.get(char, Piece.EMPTY)

    def _piece_to_char(self, piece: Piece, is_white: bool) -> str:
        if piece == Piece.KNIGHT:
            char = 'N'
        elif piece == Piece.KING:
            char = 'K'
        elif piece == Piece.QUEEN:
            char = 'Q'
        elif piece == Piece.ROOK:
            char = 'R'
        elif piece == Piece.BISHOP:
            char = 'B'
        elif piece == Piece.PAWN:
            char = 'P'
        else:
            char = '.'
        return char.upper() if is_white else char.lower()

    def is_white_piece(self, square: int) -> bool:
        return self.colors[square] == Color.WHITE

    def generate_moves(self, square: int) -> List[Move]:
        piece = self.squares[square]
        if piece == Piece.EMPTY:
            return []

        is_white = self.is_white_piece(square)

        if piece == Piece.PAWN:
            return self._generate_pawn_moves(square, is_white)
        elif piece == Piece.KNIGHT:
            return self._generate_knight_moves(square, is_white)
        elif piece == Piece.KING:
            return self._generate_king_moves(square, is_white)
        elif piece == Piece.BISHOP:
            return self._generate_sliding_moves(square, is_white, [(-1, -1), (-1, 1), (1, -1), (1, 1)])
        elif piece == Piece.ROOK:
            return self._generate_sliding_moves(square, is_white, [(-1, 0), (1, 0), (0, -1), (0, 1)])
        elif piece == Piece.QUEEN:
            return self._generate_sliding_moves(square, is_white, [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)])

        return []

    def _generate_pawn_moves(self, square: int, is_white: bool) -> List[Move]:
        moves = []
        rank = square // 8
        file_pos = square % 8
        direction = -1 if is_white else 1
        start_rank = 6 if is_white else 1

        new_rank = rank + direction
        if 0 <= new_rank < 8:
            new_square = new_rank * 8 + file_pos
            if self.squares[new_square] == Piece.EMPTY:
                promotion = Piece.QUEEN if new_rank in (0, 7) else Piece.EMPTY
                moves.append(Move(square, new_square, Piece.PAWN, Piece.EMPTY, captured_color=Color.WHITE if is_white else Color.BLACK, promotion=promotion))

                if rank == start_rank:
                    new_square2 = (rank + 2 * direction) * 8 + file_pos
                    if self.squares[new_square2] == Piece.EMPTY:
                        moves.append(Move(square, new_square2, Piece.PAWN, Piece.EMPTY, captured_color=Color.WHITE if is_white else Color.BLACK))

        for df in (-1, 1):
            new_file = file_pos + df
            if 0 <= new_file < 8:
                new_square = new_rank * 8 + new_file
                if 0 <= new_square < 64:
                    target = self.squares[new_square]
                    if target != Piece.EMPTY and self.is_white_piece(new_square) != is_white:
                        promotion = Piece.QUEEN if new_rank in (0, 7) else Piece.EMPTY
                        cap_color = self.colors[new_square]
                        moves.append(Move(square, new_square, Piece.PAWN, target, captured_color=cap_color, promotion=promotion))

        return moves

    def _generate_knight_moves(self, square: int, is_white: bool) -> List[Move]:
        moves = []
        offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        rank = square // 8
        file_pos = square % 8

        for dr, df in offsets:
            new_rank, new_file = rank + dr, file_pos + df
            if 0 <= new_rank < 8 and 0 <= new_file < 8:
                new_square = new_rank * 8 + new_file
                target = self.squares[new_square]
                if target == Piece.EMPTY or self.is_white_piece(new_square) != is_white:
                    cap_color = self.colors[new_square]
                    moves.append(Move(square, new_square, Piece.KNIGHT, target, captured_color=cap_color))

        return moves

    def _generate_king_moves(self, square: int, is_white: bool) -> List[Move]:
        moves = []
        rank = square // 8
        file_pos = square % 8

        for dr in (-1, 0, 1):
            for df in (-1, 0, 1):
                if dr == 0 and df == 0:
                    continue
                new_rank, new_file = rank + dr, file_pos + df
                if 0 <= new_rank < 8 and 0 <= new_file < 8:
                    new_square = new_rank * 8 + new_file
                    target = self.squares[new_square]
                    if target == Piece.EMPTY or self.is_white_piece(new_square) != is_white:
                        cap_color = self.colors[new_square]
                        moves.append(Move(square, new_square, Piece.KING, target, captured_color=cap_color))

        return moves

    def _generate_sliding_moves(self, square: int, is_white: bool, directions: List[Tuple[int, int]]) -> List[Move]:
        moves = []
        rank = square // 8
        file_pos = square % 8
        piece = self.squares[square]

        for dr, df in directions:
            new_rank, new_file = rank + dr, file_pos + df
            while 0 <= new_rank < 8 and 0 <= new_file < 8:
                new_square = new_rank * 8 + new_file
                target = self.squares[new_square]
                if target == Piece.EMPTY:
                    moves.append(Move(square, new_square, piece, Piece.EMPTY, captured_color=Color.WHITE if is_white else Color.BLACK))
                elif self.is_white_piece(new_square) != is_white:
                    cap_color = self.colors[new_square]
                    moves.append(Move(square, new_square, piece, target, captured_color=cap_color))
                    break
                else:
                    break
                new_rank += dr
                new_file += df

        return moves

    def make_move(self, move: Move):
        self.colors[move.to_sq] = self.colors[move.from_sq]
        self.squares[move.to_sq] = move.piece if move.promotion == Piece.EMPTY else move.promotion
        self.squares[move.from_sq] = Piece.EMPTY
        self.colors[move.from_sq] = Color.WHITE

    def unmake_move(self, move: Move, captured: Piece):
        self.colors[move.from_sq] = self.colors[move.to_sq]
        self.squares[move.from_sq] = move.piece
        self.squares[move.to_sq] = captured
        if captured != Piece.EMPTY:
            self.colors[move.to_sq] = move.captured_color

    def to_fen(self) -> str:
        result = []
        for rank in range(7, -1, -1):
            empty = 0
            for file_pos in range(8):
                piece = self.squares[rank * 8 + file_pos]
                if piece == Piece.EMPTY:
                    empty += 1
                else:
                    if empty > 0:
                        result.append(str(empty))
                        empty = 0
                    result.append(self._piece_to_char(piece, self.is_white_piece(rank * 8 + file_pos)))
            if empty > 0:
                result.append(str(empty))
            result.append('/')
        result.pop()
        result.append(' w' if self.turn == Color.WHITE else ' b')
        castling = ''
        if self.castling[0]: castling += 'K'
        if self.castling[1]: castling += 'Q'
        if self.castling[2]: castling += 'k'
        if self.castling[3]: castling += 'q'
        result.append(' ' + (castling if castling else '-'))
        result.append(f' {-1 if self.ep_square == -1 else self.ep_square}')
        result.append(f' {self.halfmove_clock}')
        result.append(f' {self.fullmove_number}')
        return ''.join(result)

    def __str__(self) -> str:
        lines = []
        ranks = '87654321'
        lines.append('  +-----------------+')
        for rank in range(7, -1, -1):
            line = ranks[rank] + ' |'
            for file_pos in range(8):
                square = rank * 8 + file_pos
                piece = self.squares[square]
                char = '.' if piece == Piece.EMPTY else self._piece_to_char(piece, self.is_white_piece(square))
                line += ' ' + char
            line += ' |'
            lines.append(line)
        lines.append('  +-----------------+')
        lines.append('    a b c d e f g h')
        return '\n'.join(lines)


class EvaluationFunction:
    PIECE_VALUES = {
        Piece.PAWN: 100,
        Piece.KNIGHT: 320,
        Piece.BISHOP: 330,
        Piece.ROOK: 500,
        Piece.QUEEN: 900,
        Piece.KING: 20000,
    }

    def evaluate(self, board: ChessBoard) -> float:
        white_score = 0
        black_score = 0
        for square in range(64):
            piece = board.squares[square]
            if piece != Piece.EMPTY and piece != Piece.KING:
                is_white = board.is_white_piece(square)
                value = self.PIECE_VALUES.get(piece, 0)
                if is_white:
                    white_score += value
                else:
                    black_score += value
        return white_score - black_score


class ChessSearch:
    def __init__(self, depth: int = 3):
        self.depth = depth
        self.nodes_searched = 0

    def search_best_move(self, board: ChessBoard) -> Optional[Move]:
        self.nodes_searched = 0
        moves = self._get_all_moves(board)
        if not moves:
            return None

        best_move = moves[0]
        best_score = float('-inf')

        for move in moves[:10]:
            captured = board.squares[move.to_sq]
            board.make_move(move)
            score = -self._negamax(board, self.depth - 1)
            board.unmake_move(move, captured)
            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def _get_all_moves(self, board: ChessBoard) -> List[Move]:
        moves = []
        for square in range(64):
            if board.squares[square] != Piece.EMPTY:
                if board.turn == Color.WHITE and board.is_white_piece(square):
                    moves.extend(board.generate_moves(square))
                elif board.turn == Color.BLACK and not board.is_white_piece(square):
                    moves.extend(board.generate_moves(square))
        return moves

    def _negamax(self, board: ChessBoard, depth: int) -> float:
        self.nodes_searched += 1
        if depth == 0:
            return EvaluationFunction().evaluate(board)

        moves = self._get_all_moves(board)
        if not moves:
            return -99999

        best_score = float('-inf')
        for move in moves[:10]:
            captured = board.squares[move.to_sq]
            board.make_move(move)
            score = -self._negamax(board, depth - 1)
            board.unmake_move(move, captured)
            best_score = max(best_score, score)

        return best_score


class OpeningBook:
    def __init__(self):
        self.book = {
            "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1": "1...e5",
            "rnbqkbnr/pppppppp/8/8/3P4/8/PPP2PPP/RNBQKBNR b KQkq - 0 1": "1...d5",
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1": "1.e4",
        }

    def lookup(self, fen: str) -> Optional[str]:
        parts = fen.split()
        board_part = parts[0]
        for key, move in self.book.items():
            if key.startswith(board_part):
                return move
        return None


class ChessEngine:
    def __init__(self):
        self.board = ChessBoard()
        self.search = ChessSearch(depth=3)
        self.opening_book = OpeningBook()
        self.move_history = []

    def set_position(self, fen: str = None):
        if fen:
            self.board = ChessBoard(fen)
        else:
            self.board = ChessBoard()
        self.move_history = []

    def get_best_move(self) -> str:
        opening_move = self.opening_book.lookup(self.board.to_fen())
        if opening_move:
            return opening_move

        move = self.search.search_best_move(self.board)
        if move:
            san = move.to_san(self.board)
            self.board.make_move(move)
            self.move_history.append((move, san))
            return san

        return "无合法走法"

    def analyze_position(self) -> Dict[str, Any]:
        evaluation = EvaluationFunction().evaluate(self.board)
        moves = self._get_all_moves()

        return {
            "evaluation": evaluation,
            "legal_moves": len(moves),
            "turn": "white" if self.board.turn == Color.WHITE else "black",
            "fen": self.board.to_fen(),
            "board": str(self.board)
        }

    def _get_all_moves(self) -> List[Move]:
        moves = []
        for square in range(64):
            if self.board.squares[square] != Piece.EMPTY:
                if self.board.turn == Color.WHITE and self.board.is_white_piece(square):
                    moves.extend(self.board.generate_moves(square))
                elif self.board.turn == Color.BLACK and not self.board.is_white_piece(square):
                    moves.extend(self.board.generate_moves(square))
        return moves


_engine = None


def get_engine() -> ChessEngine:
    global _engine
    if _engine is None:
        _engine = ChessEngine()
    return _engine

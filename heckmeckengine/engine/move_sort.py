import chess

from typing import List


class MoveSort:
    def __init__(self):
        self._promotion_table = {
            chess.BISHOP: 6,
            chess.KNIGHT: 6,
            chess.ROOK: 10,
            chess.QUEEN: 20,
        }

        self._piece_table = {
            chess.PAWN: 2,
            chess.BISHOP: 3,
            chess.KNIGHT: 3,
            chess.ROOK: 4,
            chess.QUEEN: 5,
            chess.KING: 1,
        }

        self._piece_values = {
            chess.PAWN: 1,
            chess.BISHOP: 3,
            chess.KNIGHT: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 1,
        }

    def sort_moves(self, legal_moves, board: chess.Board) -> List[chess.Move]:
        scored_moves = {}
        for move in legal_moves:
            score = 0.0
            if move.promotion is not None:
                promotion_value = self._promotion_table[move.promotion]
                score += promotion_value

            piece_type = board.piece_type_at(move.from_square)
            piece_type_capture = board.piece_type_at(move.to_square)
            if piece_type_capture is not None:
                piece_difference = (
                    self._piece_values[piece_type_capture]
                    - self._piece_values[piece_type]
                )
                capture_score = 3 * piece_difference
                score += capture_score

            board.push(move)

            piece_value = self._piece_table[piece_type]
            score += 0.2 * piece_value

            attack_value = len(board.attacks(move.to_square))
            score += attack_value

            check_value = 20 if board.is_check() else 0
            score += check_value

            board.pop()
            scored_moves[move] = score

        sorted_moves = sorted(scored_moves, key=scored_moves.get, reverse=True)
        return sorted_moves

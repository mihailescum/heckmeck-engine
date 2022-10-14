import chess
import numpy as np
from enum import Enum

from typing import Optional

from .score import Score


class EvaluationTarget(Enum):
    COMPLETE = 1
    FAST = 2


class Evaluation:
    def __init__(self):
        self.piece_worth = {
            chess.KING: 0,
            chess.PAWN: 1,
            chess.BISHOP: 3,
            chess.KNIGHT: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
        }
        self._mate_value = 100000

        self._pawn_map = 0.3 * np.array(
            [
                [10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0],
                [3.5, 3.5, 4.0, 4.0, 4.0, 3.5, 3.5, 3.8],
                [2.5, 2.7, 3.0, 3.5, 3.5, 2.8, 1.5, 2.7],
                [2.0, 2.3, 2.5, 3.0, 3.0, 2.0, 2.0, 2.2],
                [1.7, 1.6, 1.8, 2.0, 2.0, 1.2, 1.5, 1.7],
                [1.3, 1.4, 1.0, 1.0, 1.0, 1.0, 1.4, 1.3],
                [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            ]
        )

        self._knight_map = 0.3 * np.array(
            [
                [3.0, 4.0, 5.0, 5.0, 5.0, 5.0, 4.0, 3.0],
                [5.0, 6.0, 7.0, 7.0, 7.0, 7.0, 6.0, 5.0],
                [6.0, 7.0, 8.0, 8.0, 8.0, 8.0, 7.0, 6.0],
                [5.0, 6.0, 7.0, 7.0, 7.0, 7.0, 6.0, 5.0],
                [4.0, 5.0, 6.0, 6.0, 6.0, 6.0, 5.0, 4.0],
                [3.0, 4.0, 5.0, 5.0, 5.0, 5.0, 4.0, 3.0],
                [2.0, 3.0, 4.0, 4.0, 4.0, 4.0, 3.0, 2.0],
                [1.0, 2.0, 3.0, 3.0, 1.0, 1.0, 1.0, 1.0],
            ]
        )

        self._bishop_map = 0.3 * np.array(
            [
                [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
                [1.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 1.0],
                [1.0, 3.0, 2.0, 2.0, 2.0, 2.0, 3.0, 1.0],
                [3.0, 5.0, 4.0, 4.0, 4.0, 4.0, 5.0, 3.0],
                [1.0, 4.0, 4.0, 3.0, 3.0, 4.0, 4.0, 1.0],
                [2.0, 4.0, 5.0, 4.0, 4.0, 5.0, 4.0, 2.0],
                [3.0, 6.0, 4.0, 3.0, 3.0, 4.0, 6.0, 3.0],
                [4.0, 3.0, 2.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            ]
        )

        self._rook_map = 0.3 * np.array(
            [
                [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0],
                [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0],
                [3.0, 4.0, 5.0, 5.0, 5.0, 5.0, 4.0, 4.0],
                [1.0, 2.0, 3.0, 3.0, 3.0, 3.0, 2.0, 1.0],
                [1.0, 2.0, 3.0, 3.0, 3.0, 3.0, 2.0, 1.0],
                [1.0, 2.0, 3.0, 3.0, 3.0, 3.0, 2.0, 1.0],
                [6.0, 7.0, 9.0, 9.0, 9.0, 9.0, 7.0, 6.0],
                [7.0, 8.0, 10.0, 10.0, 10.0, 10.0, 8.0, 7.0],
            ]
        )

        self._queen_map = 0.3 * np.array(
            [
                [4.0, 5.0, 7.0, 7.0, 7.0, 7.0, 4.0, 5.0],
                [4.0, 5.0, 7.0, 7.0, 7.0, 7.0, 4.0, 5.0],
                [6.0, 8.0, 10.0, 10.0, 10.0, 10.0, 8.0, 6.0],
                [6.0, 7.0, 9.0, 9.0, 9.0, 9.0, 7.0, 6.0],
                [5.0, 6.0, 8.0, 8.0, 8.0, 8.0, 6.0, 5.0],
                [2.0, 3.0, 5.0, 6.0, 6.0, 5.0, 3.0, 2.0],
                [2.0, 2.0, 3.0, 5.0, 5.0, 3.0, 2.0, 2.0],
                [1.0, 2.0, 3.0, 4.0, 4.0, 5.0, 2.0, 1.0],
            ]
        )

        self._king_map = 0.4 * np.array(
            [
                [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
                [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
                [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
                [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
                [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
                [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
                [3.0, 4.0, 1.0, 1.0, 1.0, 1.0, 4.0, 9.0],
                [4.0, 7.0, 7.0, 5.0, 1.0, 6.0, 10.0, 9.0],
            ]
        )

        self._maps_white = {
            chess.PAWN: self._pawn_map[::-1].flatten(),
            chess.BISHOP: self._bishop_map[::-1].flatten(),
            chess.KNIGHT: self._knight_map[::-1].flatten(),
            chess.ROOK: self._rook_map[::-1].flatten(),
            chess.QUEEN: self._queen_map[::-1].flatten(),
            chess.KING: self._king_map[::-1].flatten(),
        }

        self._maps_black = {
            chess.PAWN: self._pawn_map.flatten(),
            chess.BISHOP: self._bishop_map.flatten(),
            chess.KNIGHT: self._knight_map.flatten(),
            chess.ROOK: self._rook_map.flatten(),
            chess.QUEEN: self._queen_map.flatten(),
            chess.KING: self._king_map.flatten(),
        }

    def get_eval(
        self,
        board: chess.Board,
        target: EvaluationTarget,
    ) -> Score:
        outcome = board.outcome()
        if outcome is not None:  # Game finished
            if outcome.termination == chess.Termination.CHECKMATE:
                if outcome.winner == chess.WHITE:
                    return Score(np.inf, outcome.termination)
                else:
                    return Score(-np.inf, outcome.termination)
            else:
                return Score(0.0, outcome.termination)

        evaluation = 0
        piece_evaluation = self._piece_evaluation(board)
        evaluation += piece_evaluation

        if target == EvaluationTarget.COMPLETE:
            position_evaluation = self._position_evaluation(board)
            evaluation += position_evaluation

        score = Score(evaluation)
        return score

    def _position_evaluation(
        self,
        board: chess.Board,
        color: Optional[chess.Color] = None,
    ):
        if color is None:
            white_eval = self._position_evaluation(board, chess.WHITE)
            black_eval = self._position_evaluation(board, chess.BLACK)
            eval = white_eval - black_eval
            return eval
        else:
            eval = 0
            for piece_type in chess.PIECE_TYPES:
                piece_count = len(board.pieces(piece_type, color))
                eval += piece_count * self.piece_worth[piece_type]

            return eval

    def _piece_evaluation(
        self,
        board: chess.Board,
        color: Optional[chess.Color] = None,
    ) -> float:
        if color is None:
            white_eval = self._piece_evaluation(board, chess.WHITE)
            black_eval = self._piece_evaluation(board, chess.BLACK)
            eval = white_eval - black_eval
            return eval
        else:
            position_map = (
                self._maps_white if color == chess.WHITE else self._maps_black
            )
            eval = 0
            for piece_type in chess.PIECE_TYPES:
                positions = board.pieces(piece_type, color)
                eval += 0.1 * position_map[piece_type][list(positions)].sum()

            return eval

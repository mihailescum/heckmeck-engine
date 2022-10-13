import chess
import numpy as np

from typing import Generator, List


class MoveGenerator:
    def __init__(self, board: chess.Board):
        self.board = board

        # fmt: off
        self.LVA_MVV = np.array(
            [
                #NOPIECE PAWN    KNIGHT  BISHOP  ROOK    QUEEN   KING
                [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan], # NOPIECE captures
                [np.nan, 60,     61,     62,     63,     64,     np.nan], # PAWN captures
                [np.nan, 50,     51,     52,     53,     54,     np.nan], # KNIGHT captures
                [np.nan, 40,     41,     42,     43,     44,     np.nan], # BISHOP captures
                [np.nan, 30,     31,     32,     33,     34,     np.nan], # ROOK captures
                [np.nan, 20,     21,     22,     23,     24,     np.nan], # QUEEN captures
                [np.nan, 10,     11,     12,     13,     14,     np.nan], # KING captures
            ]
        )
        self.LVA_MVV = self.LVA_MVV.flatten()
        self.LVA_MVV_OFFSET_PAWN = 2 ** 29
        self.LVA_MVV_OFFSET = 2 ** 28

        self.PROMOTION_TARGET = np.array([np.nan, np.nan, 1, 2, 3, 4, np.nan])
        self.PROMOTION_OFFSET_QUEEN = 2 ** 30        
        self.PROMOTION_OFFSET = 2 ** 26

        self.CHECK_OFFSET = 2 ** 27

        self.KILLER_OFFSET = 2 ** 29 - 10
        # fmt: on

    def generate_moves(self) -> List[chess.Move]:
        scored_moves = {}
        for move in self.board.legal_moves:
            score = 0
            if self.board.is_capture(move):
                attacker = self.board.piece_type_at(move.from_square)
                defender = self.board.piece_type_at(move.to_square)
                if defender is None:  # en passent
                    defender = chess.PAWN

                if attacker == chess.PAWN:
                    score += (
                        self.LVA_MVV_OFFSET_PAWN + self.LVA_MVV[attacker * 7 + defender]
                    )
                else:
                    score += self.LVA_MVV_OFFSET + self.LVA_MVV[attacker * 7 + defender]

            promotion = move.promotion
            if promotion == chess.QUEEN:
                score += self.PROMOTION_OFFSET_QUEEN + self.PROMOTION_TARGET[promotion]
            elif promotion is not None:
                score += self.PROMOTION_OFFSET + self.PROMOTION_TARGET[promotion]

            if self.board.gives_check(move):
                score += self.CHECK_OFFSET

            scored_moves[move] = score

        sorted_moves = sorted(scored_moves, key=scored_moves.get, reverse=True)
        return sorted_moves

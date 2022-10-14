import chess
import numpy as np

from typing import Generator, List
from .annotated_move import AnnotatedMove


class MoveGenerator:
    def __init__(self, board: chess.Board):
        self.board = board
        self.killer_moves = {}

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
        self.LVA_MVV_OFFSET_PAWN = 2 ** 24
        self.LVA_MVV_OFFSET = 2 ** 23

        self.PROMOTION_TARGET = np.array([np.nan, np.nan, 1, 2, 3, 4, np.nan])
        self.PROMOTION_OFFSET_QUEEN = 2 ** 25        
        self.PROMOTION_OFFSET = 2 ** 21

        self.CHECK_OFFSET = 2 ** 22

        self.KILLER_OFFSET = 2 ** 24 - 10

        self.PV_OFFSET = 2 ** 30
        # fmt: on

    def generate_moves(self, pv_move: AnnotatedMove = None) -> List[AnnotatedMove]:
        scored_moves = {}
        if pv_move is not None:
            scored_moves[pv_move] = self.PV_OFFSET

        killer_moves_ply = self.killer_moves.get(self.board.ply(), None)
        killer_move_first = None
        killer_move_second = None
        if killer_moves_ply is not None:
            killer_move_first = killer_moves_ply[0]
            if self.board.is_legal(killer_move_first):
                scored_moves[killer_move_first] = self.KILLER_OFFSET

            killer_move_second = killer_moves_ply[1]
            if killer_move_second is not None and self.board.is_legal(
                killer_move_second
            ):
                scored_moves[killer_move_second] = self.KILLER_OFFSET - 1

        for move in self.board.legal_moves:
            move.__class__ = AnnotatedMove

            if (
                move == pv_move
                or move == killer_move_first
                or move == killer_move_second
            ):
                continue

            score = 0
            if self.board.is_capture(move):
                move.is_capture = True

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
                move.is_check = False
                score += self.CHECK_OFFSET

            scored_moves[move] = score

        sorted_moves = sorted(scored_moves, key=scored_moves.get, reverse=True)
        return sorted_moves

    def add_killer_move(self, move: AnnotatedMove):
        ply = self.board.ply()
        if ply not in self.killer_moves:
            self.killer_moves[ply] = (None, None)

        new_killer_moves = (move, self.killer_moves[ply][0])
        self.killer_moves[ply] = new_killer_moves

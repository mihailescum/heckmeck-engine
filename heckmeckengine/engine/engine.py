import chess
from typing import Optional

from abc import ABC, abstractmethod


class Engine(ABC):
    def __init__(self):
        self.board = None
        self.game_started = None

    @abstractmethod
    def play(self, iteration_callback=None) -> chess.Move:
        pass

    @property
    @abstractmethod
    def name(self):
        pass

    @property
    @abstractmethod
    def author(self):
        pass

    def ucinewgame(self):
        self.board = chess.Board()
        self.game_started = False

    def set_position(self, fen: Optional[str], moves: Optional[chess.Move]):
        if fen is None:
            fen = chess.STARTING_BOARD_FEN

        self.board.set_board_fen(fen)

        for move in moves:
            self.board.push(move)

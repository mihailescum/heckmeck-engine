import chess

from abc import ABC, abstractmethod


class Engine(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def play(self, board: chess.Board) -> chess.Move:
        pass

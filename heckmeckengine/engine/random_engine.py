import chess
import random

from heckmeckengine.engine.engine import Engine


class RandomEngine(Engine):
    def __init__(self):
        pass

    def play(self, board: chess.Board) -> chess.Move:
        legal_moves = list(board.legal_moves)
        move_index = random.randrange(len(legal_moves))
        move = legal_moves[move_index]
        return move

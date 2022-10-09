import chess
import logging

from .engine import Engine
from .search_tree import SearchTree
from .evaluation import Evaluation
from .move_sort import MoveSort

LOGGER = logging.getLogger("basic_engine")


class BasicEngine(Engine):
    def __init__(self, color: chess.Color):
        self.color = color

        self.evaluation = Evaluation()
        self.move_sort = MoveSort()
        self.num_evaluations = 0

    def play(self, board: chess.Board) -> chess.Move:
        tree = SearchTree(max_depth=4, color=self.color)
        self.num_evaluations = 0

        def get_child_values():
            sorted_moves = self.move_sort.sort_moves(board.legal_moves, board)
            return sorted_moves

        def feedback_up(move: chess.Move):
            board.pop()

        def feedback_down(move: chess.Move):
            board.push(move)

        def evaluation(depth):
            self.num_evaluations += 1
            evaluation = self.evaluation.get_eval(board, depth)
            return evaluation

        result = tree.traverse_tree(
            evaluation,
            get_child_values,
            feedback_up,
            feedback_down,
        )
        LOGGER.debug(f"Number of evaluations: {self.num_evaluations}")
        return result

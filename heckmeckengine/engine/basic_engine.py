import chess
import logging

from heckmeckengine.engine.annotated_move import AnnotatedMove
from heckmeckengine.engine.engine import Engine
from heckmeckengine.engine.search_tree import SearchTree
from heckmeckengine.engine.evaluation import Evaluation, EvaluationTarget
from heckmeckengine.engine.heckmeck_board import HeckmeckBoard

LOGGER = logging.getLogger("basic_engine")


class BasicEngine(Engine):
    @property
    def name(self):
        return "Heckmeck Basic"

    @property
    def author(self):
        return "Max Mihailescu"

    def play(self, iteration_callback=None) -> chess.Move:
        self.game_started = True
        color = self.board.turn

        self.evaluation.reset_counter()
        tree = SearchTree(
            max_depth=4,
            color=color,
            board=self.board,
            evaluation=self.evaluation,
        )
        self.num_evaluations = 0

        result = tree.traverse_tree(iteration_callback)
        LOGGER.debug(f"Number of evaluations: {self.evaluation.counter}")
        self.board.push(result)
        return result

    def ucinewgame(self):
        super().ucinewgame()

        self.board = HeckmeckBoard()
        self.evaluation = Evaluation(self.board)
        self.num_evaluations = 0

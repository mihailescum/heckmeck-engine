import chess
import logging

from heckmeckengine.engine.annotated_move import AnnotatedMove
from heckmeckengine.engine.engine import Engine
from heckmeckengine.engine.search_tree import SearchTree
from heckmeckengine.engine.evaluation import Evaluation, EvaluationTarget
from heckmeckengine.engine.heckmeck_board import HeckmeckBoard

LOGGER = logging.getLogger("basic_engine")


class BasicEngine(Engine):
    def ucinewgame(self):
        super().ucinewgame()

        self.evaluation = Evaluation()
        self.num_evaluations = 0

    @property
    def name(self):
        return "Heckmeck Basic"

    @property
    def author(self):
        return "Max Mihailescu"

    def play(self, iteration_callback=None) -> chess.Move:
        self.game_started = True
        color = self.board.turn
        tree = SearchTree(
            max_depth=4,
            color=color,
            move_generator=self.move_generator,
        )
        self.num_evaluations = 0

        def feedback_up(move: AnnotatedMove):
            self.board.pop()

        def feedback_down(move: AnnotatedMove):
            self.board.push(move)

        def evaluation(target: EvaluationTarget):
            self.num_evaluations += 1
            evaluation = self.evaluation.get_eval(self.board, target)
            return evaluation

        result = tree.traverse_tree(
            evaluation,
            feedback_up,
            feedback_down,
            iteration_callback,
        )
        LOGGER.debug(f"Number of evaluations: {self.num_evaluations}")
        self.board.push(result)
        return result

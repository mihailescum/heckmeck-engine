from __future__ import annotations

import chess
import numpy as np
import logging
from typing import Iterable, Union


from .evaluation import EvaluationTarget
from .search_node import SearchNode
from .move_generator import MoveGenerator
from .score import Score
from .annotated_move import AnnotatedMove

LOGGER = logging.getLogger("search_tree")


class SearchTree:
    def __init__(
        self,
        color: chess.Color,
        move_generator: MoveGenerator,
        max_depth: int,
        start_depth: int = 2,
    ):
        self.move_generator = move_generator
        self._current_depth = start_depth
        self.max_depth = max_depth

        self.root = SearchNode(
            move_generator=self.move_generator,
            max_depth=0,
            iteration=-1,
            alpha=Score(-np.inf),
            beta=Score(np.inf),
            sign=1 if color == chess.WHITE else -1,
        )

    def _alpha_beta_search(
        self,
        current_node: SearchNode,
        eval_function,
        feedback_up,
        feedback_down,
    ) -> float:
        if current_node.max_depth == 0:
            evaluation = current_node.sign * eval_function(EvaluationTarget.COMPLETE)
            current_node.score = evaluation
            return evaluation

        value = None
        for child_node in current_node:
            feedback_down(child_node.value)
            child_score = -self._alpha_beta_search(
                child_node,
                eval_function,
                feedback_up,
                feedback_down,
            )
            child_node.score = child_score
            feedback_up(child_node.value)

            if value is None or child_score > value:
                current_node.optimizing_node = child_node
                value = child_score

                if value > current_node.alpha:
                    current_node.alpha = value

                    if current_node.alpha >= current_node.beta:  # beta cutoff
                        move = child_node.value
                        if move.is_quiet:  # Found a new killer move
                            self.move_generator.add_killer_move(move)
                        break

        if value is None:  # Terminal node
            evaluation = current_node.sign * eval_function(EvaluationTarget.COMPLETE)
            current_node.score = evaluation
            return evaluation

        current_node.score = value
        return value

    def _mtdf(self, f, eval_function, feedback_up, feedback_down):
        g = f
        upperbound = np.inf
        lowerbound = -np.inf
        while lowerbound < upperbound:
            if g == lowerbound:
                beta = g + 1
            else:
                beta = g

            self.root.alpha = beta - 1
            self.root.beta = beta
            g = self._alpha_beta_search(
                self.root,
                eval_function,
                feedback_up,
                feedback_down,
            )  # TODO: Add memory to alpha beta

            if g < beta:
                upperbound = g
            else:
                lowerbound = g
        return g

    def _start_deepening_iteration(self):
        self.root.max_depth = self._current_depth
        self.root.alpha = Score(-np.inf)
        self.root.beta = Score(np.inf)

    def _iterative_deepening(
        self, eval_function, feedback_up, feedback_down, iteration_callback
    ):
        evaluation = None
        while self._current_depth <= self.max_depth:
            # self._start_deepening_iteration()
            self.root.max_depth = self._current_depth
            evaluation = self._alpha_beta_search(
                self.root,
                eval_function,
                feedback_up,
                feedback_down,
            )
            if iteration_callback is not None:
                stop_iteration = iteration_callback(self._current_depth)
                if stop_iteration:
                    break

            self._current_depth += 1
        return evaluation

    def traverse_tree(
        self,
        eval_function,
        feedback_up,
        feedback_down,
        iteration_callback=None,
    ) -> AnnotatedMove:
        evaluation = self._iterative_deepening(
            eval_function,
            feedback_up,
            feedback_down,
            iteration_callback,
        )

        LOGGER.debug(f"Evaluation: {evaluation}")
        node = self.root
        while node.optimizing_node is not None:
            LOGGER.debug(node.optimizing_node.value)
            node = node.optimizing_node
        return self.root.optimizing_node.value

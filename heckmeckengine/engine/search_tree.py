from __future__ import annotations

import chess
import numpy as np
import logging
from typing import Iterable, Union


from .evaluation import EvaluationTarget
from .search_node import SearchNode
from .move_generator import MoveGenerator

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
        self.current_depth = start_depth
        self.max_depth = max_depth

        self.root = SearchNode(
            parent=None,
            value=None,
            move_generator=self.move_generator,
            max_depth=0,
            iteration=-1,
            alpha=-np.inf,
            beta=np.inf,
            sign=1 if color == chess.WHITE else -1,
        )

    def _alpha_beta_search(
        self,
        current_node: SearchNode,
        eval_function,
        feedback_up,
        feedback_down,
    ) -> float:
        # if current_node.max_depth == self.max_depth - 1:
        #    evaluation = current_node.color * eval_function(
        #        depth, EvaluationTarget.FAST
        #    )
        #    current_node.quiescence_score = evaluation

        if current_node.max_depth == 0:
            evaluation = current_node.sign * eval_function(EvaluationTarget.COMPLETE)
            current_node.score = evaluation
            # current_node.quiescence_score = evaluation
            # parent_quiescence_score = current_node.parent.quiescence_score

            # if abs(evaluation - parent_quiescence_score) < self._quiescence_threshold:
            return evaluation

        value = -np.inf
        for child_node in current_node:
            feedback_down(child_node.value)
            child_score = -self._alpha_beta_search(
                child_node,
                eval_function,
                feedback_up,
                feedback_down,
            )
            feedback_up(child_node.value)

            if child_score > value:
                current_node.optimizing_node = child_node
                value = child_score

            current_node.alpha = max(current_node.alpha, value)
            if current_node.alpha >= current_node.beta:  # beta cutoff
                break

        if value == -np.inf:  # Terminal node
            evaluation = current_node.sign * eval_function(EvaluationTarget.COMPLETE)
            current_node.score = evaluation
            return evaluation

        current_node.score = value
        return value

    def start_iteration(self):
        self.root.max_depth = self.current_depth

    def traverse_tree(
        self,
        eval_function,
        feedback_up,
        feedback_down,
    ) -> chess.Move:
        evaluation = None
        while self.current_depth < self.max_depth:
            self.start_iteration()
            evaluation = self._alpha_beta_search(
                self.root,
                eval_function,
                feedback_up,
                feedback_down,
            )
            self.current_depth += 1
        LOGGER.debug(f"Evaluation: {evaluation}")
        return self.root.optimizing_node.value

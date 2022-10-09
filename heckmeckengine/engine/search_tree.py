from __future__ import annotations

import chess
import math
import logging
from typing import Iterable, Union

from .search_flag import SearchFlag
from .search_node import SearchNode

LOGGER = logging.getLogger("search_tree")


class SearchTree:
    def __init__(self, max_depth: int, color: chess.Color):
        self.root = SearchNode(
            parent=None,
            value=None,
            alpha=-math.inf,
            beta=math.inf,
            maximizing=color == chess.WHITE,
        )
        self.max_depth = max_depth

        self._quiescence_threshold = 1.7

    def fromNode(node: SearchNode) -> SearchTree:
        root = node.copy()
        root.parent = None

        tree = SearchTree()
        tree.root = root

        return tree

    def _alpha_beta_search(
        self,
        depth: int,
        current_node: SearchNode,
        eval_function,
        get_child_values,
        feedback_up,
        feedback_down,
    ) -> float:
        if depth == self.max_depth - 1:
            evaluation = eval_function(depth)
            current_node.quiescence_score = evaluation

        if depth >= self.max_depth:
            evaluation = eval_function(depth)
            current_node.score = evaluation
            current_node.quiescence_score = evaluation
            parent_quiescence_score = current_node.parent.quiescence_score

            if abs(evaluation - parent_quiescence_score) < self._quiescence_threshold:
                return evaluation

        child_values = get_child_values()
        if len(child_values) == 0:  # Terminal node
            evaluation = eval_function(depth)
            current_node.score = evaluation
            return evaluation

        if current_node.maximizing:
            value = -math.inf
            for child_value in child_values:
                child_node = SearchNode(
                    current_node,
                    child_value,
                    current_node.alpha,
                    current_node.beta,
                    not current_node.maximizing,
                )
                current_node.children.append(child_node)

                feedback_down(child_value)
                child_score = self._alpha_beta_search(
                    depth + 1,
                    child_node,
                    eval_function,
                    get_child_values,
                    feedback_up,
                    feedback_down,
                )
                feedback_up(child_value)

                if child_score > value:
                    current_node.optimizing_node = child_node
                    value = child_score

                if value >= current_node.beta:  # beta cutoff
                    break

                current_node.alpha = max(current_node.alpha, value)

            current_node.score = value
            return value
        else:
            value = math.inf
            for child_value in child_values:
                child_node = SearchNode(
                    current_node,
                    child_value,
                    current_node.alpha,
                    current_node.beta,
                    not current_node.maximizing,
                )
                current_node.children.append(child_node)

                feedback_down(child_value)
                child_score = self._alpha_beta_search(
                    depth + 1,
                    child_node,
                    eval_function,
                    get_child_values,
                    feedback_up,
                    feedback_down,
                )
                feedback_up(child_value)

                if child_score < value:
                    current_node.optimizing_node = child_node
                    value = child_score

                if value <= current_node.alpha:  # alpha cutoff
                    break
                current_node.beta = min(current_node.beta, value)

            current_node.score = value
            return value

    def traverse_tree(
        self,
        eval_function,
        get_child_values,
        feedback_up,
        feedback_down,
    ) -> chess.Move:
        eval = self._alpha_beta_search(
            0,
            self.root,
            eval_function,
            get_child_values,
            feedback_up,
            feedback_down,
        )
        LOGGER.debug(f"Evaluation: {eval}")
        return self.root.optimizing_node.value

        """move_down = True
        while True:
            if move_down:
                result = self.move_down(leaf_generator)

                if (
                    SearchFlag.REACHED_MAX_DEPTH in result
                    or SearchFlag.HAS_NO_CHILDREN in result
                ):
                    move_down = False
                    evaluation = eval_function()
                    self.current_node.score = evaluation

                if SearchFlag.VISITED_ALL_CHILDREN not in result:
                    feedback_down(self.current_node.value)
            else:
                result = self.move_up()
                if SearchFlag.REACHED_ROOT_NODE in result:
                    break

                move_down = True
                feedback_up(self.current_node.value)"""

    def move_up(self) -> SearchFlag:
        if self.current_node.parent is None:  # Reached root node
            return SearchFlag.REACHED_ROOT_NODE
        else:
            self.current_node = self.current_node.parent
            self.current_depth -= 1
            return SearchFlag.EMPTY

    def move_down(self, leaf_generator) -> SearchFlag:
        if self.current_node.children_generator is None:
            self.current_node.add_children_generator(leaf_generator)

        result = self.current_node.move_down()
        next_node = self.current_node.get_current_child()

        if next_node is not None:
            self.current_node = next_node
            self.current_depth += 1
            if self.current_depth == self.max_depth:
                result |= SearchFlag.REACHED_MAX_DEPTH

        return result

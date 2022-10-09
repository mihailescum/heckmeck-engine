from __future__ import annotations

import chess
from typing import Generator

from .search_flag import SearchFlag


class SearchNode:
    def __init__(
        self,
        parent: SearchNode,
        value: chess.Move,
        alpha: float,
        beta: float,
        maximizing: bool,
    ):
        self.parent = parent
        self.value = value
        self.alpha = alpha
        self.beta = beta
        self.maximizing = maximizing

        self.score = None
        self.quiescence_score = None
        self.optimizing_node = None
        self.children = []
        self.values_generator = None
        self.current_child_idx = -1

    def copy(self) -> SearchNode:
        raise NotImplementedError()

    def move_down(self) -> SearchFlag:
        try:
            next_value = next(self.values_generator)
            next_child = SearchNode(
                parent=self,
                value=next_value,
                alpha=self.alpha,
                beta=self.beta,
                maximizing=not self.maximizing,
            )

            self.children.append(next_child)
            return SearchFlag.EMPTY
        except StopIteration:
            if len(self.children) == 0:
                return SearchFlag.HAS_NO_CHILDREN
            else:
                return SearchFlag.VISITED_ALL_CHILDREN

    def get_current_child(self) -> SearchNode:
        if self.current_child_idx == -1:
            return None
        else:
            return self.children[self.current_child_idx]

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self)

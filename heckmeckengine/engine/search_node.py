from __future__ import annotations

import chess
from typing import Generator

from .move_generator import MoveGenerator
from .search_flag import SearchFlag


class SearchNode:
    def __init__(
        self,
        parent: SearchNode,
        value: chess.Move,
        move_generator: MoveGenerator,
        sign: int,
        iteration: int,
        max_depth: int,
        alpha: float,
        beta: float,
    ):
        self.parent = parent
        self.move_generator = move_generator
        self.value = value
        self.sign = sign

        self.iteration = iteration
        self.max_depth = max_depth

        self.alpha = alpha
        self.beta = beta

        self.score = None
        self.optimizing_node = None

        self.current_child = 0
        self.legal_moves = None
        self.children = {}

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self)

    def __iter__(self):
        if self.legal_moves is None:
            self.legal_moves = self.move_generator.generate_moves()

        if self.parent is None or self.iteration < self.parent.iteration:
            self.current_child = 0
            self.iteration += 1

        return self

    def __next__(self):
        if self.current_child < len(self.legal_moves):
            move = self.legal_moves[self.current_child]
            if move in self.children:
                child = self.children[move]
                child.max_depth = self.max_depth - 1
                child.alpha = -self.beta
                child.beta = -self.alpha
            else:
                child = SearchNode(
                    parent=self,
                    value=move,
                    move_generator=self.move_generator,
                    iteration=self.iteration,
                    max_depth=self.max_depth - 1,
                    alpha=-self.beta,
                    beta=-self.alpha,
                    sign=-self.sign,
                )
                self.children[move] = child

            self.current_child += 1
            return child
        else:
            raise StopIteration

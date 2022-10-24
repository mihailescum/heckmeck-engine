from __future__ import annotations
from dataclasses import dataclass, field

import chess
from typing import Optional, Dict

from heckmeckengine.engine.heckmeck_board import HeckmeckBoard
from heckmeckengine.engine.score import Score
from heckmeckengine.engine.annotated_move import AnnotatedMove


@dataclass()
class SearchNode:
    board: HeckmeckBoard
    sign: int
    iteration: int
    max_depth: int
    alpha: Score
    beta: Score
    parent: Optional[SearchNode] = None
    value: Optional[AnnotatedMove] = None

    optimizing_node: SearchNode = field(default=None, init=False)
    children: Dict[AnnotatedMove, SearchNode] = field(default_factory=dict, init=False)
    current_move: int = field(default=0, init=False)

    score: Score = field(default=None, init=False)

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self)

    def __iter__(self):
        pv_move = None
        if self.optimizing_node is not None:
            pv_move = self.optimizing_node.value
        self.sorted_moves = self.board.generate_sorted_legal_moves(pv_move=pv_move)

        if self.parent is None or self.iteration < self.parent.iteration:
            self.current_move = 0
            self.iteration += 1

        return self

    def __next__(self):
        for move in self.sorted_moves:
            if move in self.children:
                child = self.children[move]
                child.max_depth = self.max_depth - 1
                child.alpha = -self.beta
                child.beta = -self.alpha
            else:
                child = SearchNode(
                    parent=self,
                    value=move,
                    board=self.board,
                    iteration=self.iteration,
                    max_depth=self.max_depth - 1,
                    alpha=-self.beta,
                    beta=-self.alpha,
                    sign=-self.sign,
                )
                self.children[move] = child

            self.current_move += 1
            return child
        else:
            raise StopIteration

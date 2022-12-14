from dataclasses import dataclass
import chess
import math

from typing import Optional

import logging


@dataclass
class Score:
    value: float
    termination: Optional[chess.Termination] = None

    def __rmul__(self, other):
        return Score(other * self.value, self.termination)

    def __neg__(self):
        return Score(-self.value, self.termination)

    def __eq__(self, other):
        return (
            math.isclose(self.value, other.value)
            and self.termination == other.termination
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if self.termination is None:
            if isinstance(other, (float, int)):
                return self.value < other
            elif other.termination is None:
                return self.value < other.value
            elif other.termination is chess.Termination.CHECKMATE:
                return other.value > 0  # If other.value > 0, opponent has checkmate
            else:  # other is draw
                return self.value < 0
        elif self.termination is chess.Termination.CHECKMATE:
            if isinstance(other, (float, int)) or other.termination is None:
                return self.value < 0  # If self.value is < 0, opponent has checkmate
            elif other.termination is chess.Termination.CHECKMATE:
                if (self.value == other.value) or (self.value > other.value):
                    return False
                else:
                    return True
            else:  # other is draw
                return self.value < 0
        else:  # We say it's a draw
            if isinstance(other, (float, int)) or other.termination is None:
                return other.value > 0
            elif other.termination is chess.Termination.CHECKMATE:
                return other.value > 0  # If other.value > 0, opponent has checkmate
            else:  # other is draw
                return False

    def __gt__(self, other):
        return not self.__lt__(other)

    def __le__(self, other):
        return self.__eq__(other) or self.__lt__(other)

    def __ge__(self, other):
        return self.__eq__(other) or self.__gt__(other)

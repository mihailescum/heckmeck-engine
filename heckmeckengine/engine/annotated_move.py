import chess
from dataclasses import dataclass, field


@dataclass(unsafe_hash=True)
class AnnotatedMove(chess.Move):
    """Note: Annotations do not enter comparisons!"""

    is_check: bool = field(default=False, compare=False, hash=False)
    is_capture: bool = field(default=False, compare=False, hash=False)

    @property
    def is_quiet(self):
        return not (self.is_check or self.is_capture or self.promotion is not None)

    def __repr__(self):
        return self.__str__()

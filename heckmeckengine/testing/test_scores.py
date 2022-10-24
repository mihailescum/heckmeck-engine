import pytest

import chess
from heckmeckengine.engine.score import Score

test_cases = [  # We wil test "<"
    (
        Score(1, None),
        Score(2, None),
        True,
    ),
    (
        Score(1, None),
        Score(-2, None),
        False,
    ),
    (
        Score(-1, None),
        Score(-2, None),
        False,
    ),
    (
        Score(0.0, chess.Termination.FIFTY_MOVES),
        Score(2, None),
        True,
    ),
    (
        Score(0.0, chess.Termination.FIFTY_MOVES),
        Score(-2, None),
        False,
    ),
    (
        Score(1, chess.Termination.FIFTY_MOVES),
        Score(2, chess.Termination.FIFTY_MOVES),
        False,
    ),
    (
        Score(1, chess.Termination.CHECKMATE),
        Score(2, chess.Termination.FIFTY_MOVES),
        False,
    ),
    (
        Score(-1, chess.Termination.CHECKMATE),
        Score(2, chess.Termination.FIFTY_MOVES),
        True,
    ),
    (
        Score(1, chess.Termination.FIFTY_MOVES),
        Score(2, chess.Termination.CHECKMATE),
        True,
    ),
    (
        Score(1, chess.Termination.FIFTY_MOVES),
        Score(-2, chess.Termination.CHECKMATE),
        False,
    ),
    (
        Score(1, None),
        Score(2, chess.Termination.CHECKMATE),
        True,
    ),
    (
        Score(-1, None),
        Score(2, chess.Termination.CHECKMATE),
        True,
    ),
    (
        Score(1, chess.Termination.CHECKMATE),
        Score(2, None),
        False,
    ),
    (
        Score(1, chess.Termination.CHECKMATE),
        Score(-2, None),
        False,
    ),
]


@pytest.mark.parametrize("score1, score2, expected_output", test_cases)
def test_lt(score1, score2, expected_output):
    output = score1 < score2
    assert output == expected_output

import pytest

import chess
from heckmeckengine.engine.evaluation import Evaluation, EvaluationTarget

test_cases = [
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq -",
    "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - -",
    "r2q1rk1/pP1p2pp/Q4n2/bbp1p3/Np6/1B3NBn/pPPP1PPP/R3K2R b KQ - 0 1",
    "rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8",
    "r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10",
]


@pytest.mark.parametrize("fen", test_cases)
@pytest.mark.parametrize(
    "eval_target", [EvaluationTarget.COMPLETE, EvaluationTarget.FAST]
)
def test_get_evaluation(fen, eval_target):
    board = chess.Board(fen=fen)
    evaluation = Evaluation(board).get(eval_target)

    mirrored = board.mirror()
    evaluation_mirrored = Evaluation(mirrored).get(eval_target)

    assert evaluation == evaluation_mirrored


@pytest.mark.parametrize(
    "fen, sign",
    [
        ("8/8/4k3/8/4K3/8/8/QQQQ4 w - - 0 1", 1),
        ("8/8/4k3/8/4K3/8/8/QQQQ4 b - - 0 1", -1),
        ("4qqqq/8/4k3/8/4K3/8/8/8 b - - 0 1", 1),
        ("4qqqq/8/4k3/8/4K3/8/8/8 w - - 0 1", -1),
    ],
)
@pytest.mark.parametrize(
    "eval_target", [EvaluationTarget.COMPLETE, EvaluationTarget.FAST]
)
def test_evaluation_sign(fen, sign, eval_target):
    board = chess.Board(fen=fen)
    evaluation = Evaluation(board).get(eval_target)

    assert sign * evaluation > 1

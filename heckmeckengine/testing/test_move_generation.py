import pytest

import chess
from heckmeckengine.engine.move_generator import MoveGenerator

import time
import logging

logging.basicConfig(level="info")

perft_positions = [
    {
        "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "skip": False,
        "depth": 4,
        "nodes": [20, 400, 8902, 197281, 4865609, 119060324],
        "captures": [0, 0, 34, 1576, 82719, 2812008],
        "ep": [0, 0, 0, 0, 258, 319617],
        "castles": [0, 0, 0, 0, 0, 0],
        "promotions": [0, 0, 0, 0, 0, 0],
        "checks": [0, 0, 12, 469, 27351, 809099],
        "checkmates": [0, 0, 0, 8, 347, 10828],
    },
    {
        "fen": "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq -",
        "skip": False,
        "depth": 3,
        "nodes": [48, 2039, 97862, 4085603, 193690690, 8031647685],
        "captures": [8, 351, 17102, 757163, 35043416, 1558445089],
        "ep": [0, 1, 45, 1929, 73365, 3577504],
        "castles": [2, 91, 3162, 128013, 4993637, 184513607],
        "promotions": [0, 0, 0, 15172, 8392, 56627920],
        "checks": [0, 3, 993, 25523, 3309887, 92238050],
        "checkmates": [0, 0, 1, 43, 30171, 360003],
    },
    {
        "fen": "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - -",
        "skip": True,
        "depth": 1,
        "nodes": [14, 191, 2812, 43238, 674624, 11030083],
        "captures": [1, 14, 209, 3348, 52051, 940350],
        "ep": [0, 0, 2, 123, 1165, 33325],
        "castles": [0, 0, 0, 0, 0, 0],
        "promotions": [0, 0, 0, 0, 0, 7552],
        "checks": [2, 10, 267, 1680, 52950, 452473],
        "checkmates": [0, 0, 0, 17, 0, 2733],
    },
    {
        "fen": "r2q1rk1/pP1p2pp/Q4n2/bbp1p3/Np6/1B3NBn/pPPP1PPP/R3K2R b KQ - 0 1",
        "skip": True,
        "depth": 1,
        "nodes": [6, 264, 9467, 422333, 15833292],
        "captures": [0, 87, 1021, 131393, 2046173],
        "ep": [0, 0, 4, 0, 6521],
        "castles": [0, 6, 0, 7795, 0],
        "promotions": [0, 48, 120, 60032, 329464],
        "checks": [0, 10, 38, 15492, 200568],
        "checkmates": [0, 0, 22, 5, 50562],
    },
    {
        "fen": "rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8",
        "skip": False,
        "depth": 3,
        "nodes": [44, 1468, 62379, 2103487],
    },
    {
        "fen": "r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10",
        "skip": True,
        "depth": 1,
        "nodes": [46, 2079, 89890, 3894594, 164075551],
    },
]


def perft(move_generator, depth, fast=True):
    if fast:
        moves = move_generator.generate_moves(pv_move=None)
        if depth == 1:
            return len(moves)

        nodes = 0
        for move in moves:
            move_generator.board.push(move)
            nodes += perft(move_generator, depth - 1, fast=fast)
            move_generator.board.pop()

        return nodes


@pytest.mark.parametrize("position", perft_positions)
@pytest.mark.parametrize("fast", [True])
def test_generate_move(position, fast):
    if position["skip"]:
        return

    fen = position["fen"]
    depth = position["depth"]

    board = chess.Board(fen=fen)
    move_generator = MoveGenerator(board)

    start = time.time()
    result = perft(move_generator, depth=depth, fast=fast)
    duration = time.time() - start

    nodes = result["nodes"] if isinstance(result, dict) else result

    nodes_per_second = nodes / duration
    logging.info(
        f"FEN: {position['fen']} searched with {(nodes_per_second/1000):.1f}kn/s"
    )

    if fast:
        assert nodes == position["nodes"][depth - 1]
    else:
        raise NotImplementedError

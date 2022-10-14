from optparse import Option
import chess
from typing import Optional

from heckmeckengine.engine import Engine
from heckmeckengine.engine.basic_engine import BasicEngine


class Game:
    def __init__(self, fen: Optional[str] = chess.STARTING_FEN):
        self.board = chess.Board(fen)

        self.engine = None
        self.white_halfmove = None
        self.black_halfmove = None

        self.started = False

    def start(self, usercolor) -> None:
        self.engine = BasicEngine(not usercolor, self.board.copy())

        if usercolor == chess.WHITE:
            self.white_halfmove = self._user_halfmove
            self.black_halfmove = self._engine_halfmove
        else:
            self.white_halfmove = self._engine_halfmove
            self.black_halfmove = self._user_halfmove

        self.started = True
        return usercolor

    def _user_halfmove(self):
        while True:
            inp = input("Chose your move (fen for current FEN): ")
            if inp == "h":
                print("\n".join((str(x) for x in self.board.legal_moves)))
                continue
            elif inp == "fen":
                print(self.board.fen())
                continue
            try:
                move = chess.Move.from_uci(inp)
            except ValueError as ex:
                print("Invalid move!")
                continue
            else:
                self.board.push(move)
                self.engine.board.push(move)
                break

    def _engine_halfmove(self):
        result = self.engine.play()
        print(f"Engine played the move {self.board.san(result)}.")
        self.board.push(result)

    def do_move(self) -> None:
        if not self.started:
            raise Exception("You have to start the game first!")

        self.white_halfmove()
        if not self.is_game_over():
            self.black_halfmove()

    def is_game_over(self):
        return self.board.is_game_over()

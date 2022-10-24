import chess
import random
import logging

from heckmeckengine.game import Game
from heckmeckengine.engine import HeckmeckEngine

logging.basicConfig(level=logging.DEBUG)


def main() -> None:
    usercolor = chess.BLACK
    if usercolor is None:
        usercolor = chess.Color(bool(random.randrange(2)))

    game = Game(
        fen="r1bqk1nr/pppp1ppp/2n5/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4",
    )

    usercolor = game.start(usercolor)
    print(f"User is playing as {'white' if usercolor else 'black'}")

    while not game.is_game_over():
        game.do_move()


if __name__ == "__main__":
    import cProfile

    # cProfile.run("main()")
    main()

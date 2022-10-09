import chess
import random
import logging

from heckmeckengine.game import Game
from heckmeckengine.engine import BasicEngine

logging.basicConfig(level=logging.DEBUG)


def main() -> None:
    usercolor = chess.BLACK
    if usercolor is None:
        usercolor = chess.Color(bool(random.randrange(2)))

    engine = BasicEngine(not usercolor)
    # game = Game(engine=engine)
    game = Game(
        engine=engine,
        fen="1q2b1k1/1r3ppp/8/1n6/8/N7/1R2BPPP/1Q4K1 w - - 0 1",
    )

    usercolor = game.start(usercolor)
    print(f"User is playing as {'white' if usercolor else 'black'}")

    while not game.is_game_over():
        game.do_move()


if __name__ == "__main__":
    import cProfile

    # cProfile.run("main()")
    main()

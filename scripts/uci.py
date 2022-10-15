#!/usr/bin/env python

import chess
import sys
import logging
import multiprocessing

from heckmeckengine.engine import BasicEngine, Engine

logging.basicConfig(level=logging.DEBUG)


class Unbuffered(object):
    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()
        sys.stderr.write(data)
        sys.stderr.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)


out = Unbuffered(sys.stdout)


def output(*values: object):
    print(*values, file=out)


def register_engine(engine: Engine):
    name = engine.name
    author = engine.author
    output("id", name)
    output("id", author)
    output("uciok")


def ucinewgame(engine: Engine):
    engine.ucinewgame()


def setup_position(engine: Engine, *arguments):
    fen = arguments[0]
    if fen == "startpos":
        fen = None
    moves = [chess.Move.from_uci(arg) for arg in arguments[2:]]
    engine.set_position(fen, moves)


def parse_go(*arguments):
    return None


def search_next_move(engine: Engine, connection, *arguments):
    parsed_arguments = parse_go(*arguments)

    def iteration_callback(search_depth):
        stop = False
        while connection.poll():
            command = connection.recv()

            if command.startswith("debug"):
                pass
            elif command.startswith("stop"):
                stop = True
            elif command.startswith("isready"):
                output("readyok")
            else:
                raise ValueError(command)
        return stop

    bestmove = engine.play(iteration_callback=iteration_callback)
    output("bestmove", bestmove)


def run_engine(connection):
    engine = BasicEngine()

    quit = False
    newgame = True
    while not quit:
        command = connection.recv()
        logging.debug("recieved: " + command)

        if command.startswith("debug"):
            pass
        elif command.startswith("ucinewgame"):
            newgame = True
            ucinewgame(engine)
            newgame = False
        elif command.startswith("uci"):
            register_engine(engine)
        elif command.startswith("isready"):
            logging.warning("Recieved an isready command")
            output("readyok")
        elif command.startswith("setoption"):
            pass
        elif command.startswith("register"):
            pass
        elif command.startswith("position"):
            if newgame:
                ucinewgame(engine)

            arguments = command.split(" ")[1:]
            setup_position(engine, *arguments)
        elif command.startswith("go"):
            arguments = command.split(" ")[1:]
            connection.send(True)
            search_next_move(engine, connection, *arguments)
            connection.send(False)
        elif command.startswith("stop"):
            pass  # Not in a calculation at the moment
        elif command.startswith("ponderhit"):
            pass


def main() -> None:
    connection_to_engine, connection_to_main = multiprocessing.Pipe(duplex=True)
    engine_process = multiprocessing.Process(
        target=run_engine, args=(connection_to_main,)
    )
    engine_process.start()

    quit = False
    is_computing = False
    while not quit:
        command = input()

        while connection_to_engine.poll():
            is_computing = connection_to_engine.recv()

        if command.startswith("debug"):
            connection_to_engine.send(command)
        elif command.startswith("quit"):
            engine_process.terminate()
            quit = True
        elif command.startswith("isready") and is_computing:
            output("readyok")
        else:
            connection_to_engine.send(command)


if __name__ == "__main__":
    main()

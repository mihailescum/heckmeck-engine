from enum import Flag, auto


class SearchFlag(Flag):
    EMPTY = 0
    VISITED_ALL_CHILDREN = auto()
    HAS_NO_CHILDREN = auto()
    REACHED_MAX_DEPTH = auto()
    REACHED_ROOT_NODE = auto()

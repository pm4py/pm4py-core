from enum import Enum, auto


class State(Enum):
    CLOSED = auto()
    ENABLED = auto()
    OPEN = auto()
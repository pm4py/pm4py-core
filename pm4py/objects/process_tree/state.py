from enum import Enum, auto


class State(Enum):
    # closed state
    CLOSED = auto()
    # enabled state
    ENABLED = auto()
    # open state
    OPEN = auto()

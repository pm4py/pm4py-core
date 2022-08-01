from typing import Dict, Tuple


class SNA(object):
    connections : Dict[Tuple[str, str], float]
    is_directed : bool

    def __init__(self, connections: Dict[Tuple[str, str], int], is_directed: bool):
        self.connections = connections
        self.is_directed = is_directed

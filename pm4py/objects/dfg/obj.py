from collections import Counter
from typing import Tuple, Any, Counter as TCounter


class DirectlyFollowsGraph:

    def __init__(self):
        self._graph = Counter()
        self._start_activities = Counter()
        self._end_activities = Counter()

    @property
    def graph(self) -> TCounter[Tuple[Any, Any]]:
        return self._graph

    @property
    def start_activities(self) -> TCounter[Any]:
        return self._start_activities

    @property
    def end_activities(self) -> TCounter[Any]:
        return self._end_activities

    def __repr__(self):
        return repr(self._graph)

    def __str__(self):
        return str(self._graph)


DFG = DirectlyFollowsGraph

from collections import Counter
from typing import Tuple, Any, Counter as TCounter


class DirectlyFollowsGraph:

    def __init__(self, graph=None, start_activities=None, end_activities=None):
        if graph is None:
            graph = {}
        if start_activities is None:
            start_activities = {}
        if end_activities is None:
            end_activities = {}
        self._graph = Counter(graph)
        self._start_activities = Counter(start_activities)
        self._end_activities = Counter(end_activities)

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

    def __iter__(self):
        yield dict(self.graph)
        yield dict(self.start_activities)
        yield dict(self.end_activities)


DFG = DirectlyFollowsGraph

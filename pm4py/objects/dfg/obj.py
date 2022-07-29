from typing import Tuple, List, Any


class DirectlyFollowsGraph:

    def __init__(self):
        self._graph = list()
        self._start_activities = list()
        self._end_activities = list()

    @property
    def graph(self) -> List[Tuple[Any, Any, int]]:
        return self._graph

    @property
    def start_activities(self) -> List[Tuple[Any, int]]:
        return self._start_activities

    @property
    def end_activities(self) -> List[Tuple[Any, int]]:
        return self._end_activities


DFG = DirectlyFollowsGraph

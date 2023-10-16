import heapq
from pm4py.objects.dcr.obj import DCRGraph, Marking
from pm4py.objects.dcr import semantics
from typing import List, Tuple, Set, Dict
from collections import namedtuple
from enum import Enum

SKIP = '>>'
STD_MODEL_LOG_MOVE_COST = 10000
STD_TAU_COST = 1
STD_SYNC_COST = 0


class Outputs(Enum):
    ALIGNMENT = "alignment"
    COST = "cost"
    VISITED = "visited_states"
    CLOSED = "closed"


SearchTuple = namedtuple('SearchTuple', ['cost', 'marking', 'path'])


def search_path_dcr(dcr_graph: DCRGraph, ini: Marking, fin: Marking,
                    activated_events: Set[str], skip=SKIP) -> Tuple[List[str], bool, int]:
    """
    Searches a firing sequence among the DCR graph that leads from an initial to a final marking.
    """

    open_set = []
    heapq.heappush(open_set, SearchTuple(0, ini, []))

    visited_markings = set()
    best_tuple = None

    while open_set:
        current = heapq.heappop(open_set)
        cost, marking, path = current

        if marking == fin:
            return path, True, cost

        if marking in visited_markings:
            continue

        visited_markings.add(marking)

        for event in activated_events:
            if dcr_graph.is_enabled(event, marking):
                new_marking = dcr_graph.execute(event, marking)
                new_cost = dcr_graph.get_cost(event, marking) + cost
                new_path = path + [event]
                heapq.heappush(open_set, SearchTuple(new_cost, new_marking, new_path))

    return [], False, 0


def cost_function_dcr(dcr) -> Dict[str, int]:
    costs = {}
    for e in dcr.events:
        if e == SKIP:
            costs[e] = STD_TAU_COST
        else:
            costs[e] = STD_SYNC_COST  # Assign costs based on DCR model
    return costs


def apply_dcr(log: 'EventLog', dcr: DCRGraph, parameters=None, variant="classic") -> Dict:
    if parameters is None:
        parameters = {}
    activated_events = set()
    costs = cost_function_dcr(dcr, SKIP)
    alignment, cost, visited, closed = search_path_dcr(dcr, dcr.ini_marking, dcr.fin_marking, activated_events)
    return {Outputs.ALIGNMENT.value: alignment, Outputs.COST.value: cost, Outputs.VISITED.value: visited, Outputs.CLOSED.value: closed}




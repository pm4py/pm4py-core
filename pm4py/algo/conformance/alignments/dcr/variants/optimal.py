import pandas as pd
import copy
from typing import Optional, Dict, Any, Union, List
from heapq import heappop, heappush
from enum import Enum

from pm4py.objects.dcr.obj import DCR_Graph
from pm4py.objects.dcr.semantics import DCRSemantics
from pm4py.util import constants, xes_constants, exec_utils
from pm4py.objects.log.obj import EventLog, Trace
from pm4py.objects.conversion.log import converter as log_converter


class Parameters(Enum):
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY


class Outputs(Enum):
    ALIGNMENT = "alignment"
    COST = "cost"
    VISITED = "visited_states"
    CLOSED = "closed"


class TraceHandler:
    def __init__(self, trace: Union[List[Dict[str, Any]], pd.DataFrame, EventLog, Trace],
                 parameters: Optional[Dict] = None):
        if parameters is None or not isinstance(parameters, dict):
            parameters = {}

        self.activity_key = parameters.get(Parameters.ACTIVITY_KEY.value, xes_constants.DEFAULT_NAME_KEY)
        if isinstance(trace, pd.DataFrame):
            self.trace = trace.to_dict('records')
        elif isinstance(trace, (EventLog, Trace)):
            self.trace = log_converter.apply(trace, variant=log_converter.Variants.TO_DATA_FRAME).to_dict('records')
        else:
            self.trace = trace

    def is_empty(self) -> bool:
        return not bool(self.trace)

    def get_first_activity(self) -> Any:
        return self.trace[0][self.activity_key] if self.trace else None


class DCRGraphHandler:
    def __init__(self, graph: DCR_Graph):
        if not isinstance(graph, DCR_Graph):
            raise TypeError(f"Expected a DCR_Graph object, got {type(graph)} instead")
        self.graph = graph

    def is_enabled(self, event: Any) -> bool:
        return DCRSemantics.is_enabled(event, self.graph)

    def is_accepting(self) -> bool:
        return DCRSemantics.is_accepting(self.graph)

    def execute(self, event: Any, curr_graph) -> Any:
        new_graph = DCRSemantics.execute(self.graph, event)
        if not new_graph:
            return curr_graph
        return new_graph

    def reset(self):
        self.graph.reset()


class ComparableObject:
    def __init__(self, obj):
        self.obj = obj
        self.type = type(obj)

    def __lt__(self, other):
        return str(self.obj) < str(other.obj)


class Alignment:
    """
    This class contains the object oriented implementation of the Optimal Alignments algorithm,
    based on the paper by:
    Author: Axel Kjeld Fjelrad Christfort and Tijs Slaats
    Title: Efficient Optimal Alignment Between Dynamic Condition Response Graphs and Traces
    Publisher: Springer
    Year: 2023
    DOI: 10.1007/978-3-031-41620-0_1
    Book: Business Process Management (pp.3-19)
    """
    def __init__(self, graph_handler: DCRGraphHandler, trace_handler: TraceHandler, parameters: Optional[Dict] = None):
        self.graph_handler = graph_handler

        if parameters is None:
            parameters = {}
        activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
        parameters[Parameters.ACTIVITY_KEY.value] = activity_key

        self.trace_handler = TraceHandler(trace_handler.trace, parameters)

        self.open_set = []
        self.global_min = float('inf')
        self.closed_set = {}
        self.visited_states = set()
        self.moves = []
        self.new_moves = []
        self.final_alignment = []
        self.closed_markings = set()

    def handle_state(self, curr_cost, curr_graph, curr_trace, current, moves, move_type=None):
        if moves is None:
            moves = []

        new_cost, new_graph, new_trace, new_move = self.get_new_state(curr_cost, curr_graph, curr_trace, moves,
                                                                      move_type)

        is_equivalent = any(
            DCRSemantics.is_execution_equivalent(new_graph.marking, closed_marking)
            for closed_marking in self.closed_markings
        )

        if is_equivalent:
            return

        self.closed_markings.add(new_graph.marking)
        state_representation = (str(new_graph), tuple(map(str, new_trace)))

        if state_representation not in self.visited_states:
            self.visited_states.add(state_representation)
            self.new_moves = moves + [new_move]
            heappush(self.open_set,
                     (new_cost, ComparableObject(new_graph), ComparableObject(new_trace), current, self.new_moves))

    def get_new_state(self, curr_cost, curr_graph, curr_trace, moves, move_type):
        new_cost = curr_cost
        new_graph = curr_graph
        new_trace = curr_trace
        new_move = None

        first_activity = self.trace_handler.get_first_activity()

        if move_type == "sync":
            new_cost += 0
            new_move = ('sync', first_activity)
            new_trace = curr_trace[1:]
            if self.graph_handler.is_enabled(first_activity):
                new_graph = self.graph_handler.execute(first_activity, new_graph)

        elif move_type == "model":
            new_cost += 1
            new_move = ('model', first_activity)
            if self.graph_handler.is_enabled(first_activity):
                new_graph = self.graph_handler.execute(first_activity, new_graph)

        elif move_type == "log":
            new_cost += 1
            new_move = ('log', first_activity)
            new_trace = curr_trace[1:]

        return new_cost, new_graph, new_trace, new_move

    def process_current_state(self, current):
        curr_cost, curr_graph, curr_trace, _, moves = current

        if isinstance(curr_graph, ComparableObject):
            curr_graph = curr_graph.obj

        if isinstance(curr_trace, ComparableObject):
            curr_trace = curr_trace.obj

        if not isinstance(curr_graph, DCR_Graph):
            return None

        if isinstance(curr_trace, ComparableObject):
            trace_to_check = curr_trace.obj
        else:
            trace_to_check = curr_trace

        self.graph_handler.graph = copy.deepcopy(curr_graph)
        state_repr = (str(self.graph_handler.graph), tuple(map(str, trace_to_check)))

        return curr_cost, curr_graph, curr_trace, state_repr, moves

    def update_closed_and_visited_sets(self, curr_cost, state_repr):
        self.closed_set[state_repr] = True
        if curr_cost <= self.global_min:
            self.global_min = curr_cost

    def check_accepting_conditions(self, curr_cost, is_accepting):
        final_cost = float('inf')
        if is_accepting:
            if curr_cost <= self.global_min:
                self.global_min = curr_cost
                self.final_alignment = self.new_moves
                final_cost = curr_cost

            if final_cost < self.global_min:
                self.global_min = final_cost
        return final_cost

    def apply_trace(self, parameters=None):
        if parameters is None:
            parameters = {}

        activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
        if isinstance(self.trace_handler.trace, pd.DataFrame):
            case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
            self.trace_handler.trace = list(self.trace_handler.trace.groupby(case_id_key)[activity_key].apply(tuple))
        else:
            converted_trace = log_converter.apply(self.trace_handler.trace, variant=log_converter.Variants.TO_EVENT_LOG,
                                                  parameters=parameters)
            if isinstance(converted_trace, list) and all(isinstance(x, dict) for x in converted_trace):
                self.trace_handler.trace = converted_trace
        visited = 0
        closed = 0
        cost = 0
        self.open_set.append((cost, self.graph_handler.graph, self.trace_handler.trace, None, []))

        self.final_alignment = None
        final_cost = float('inf')

        while self.open_set:
            current = heappop(self.open_set)
            visited += 1

            result = self.process_current_state(current)
            if result is None:
                continue

            curr_cost, curr_graph, curr_trace, state_repr, moves = result

            if state_repr in self.closed_set:
                continue
            elif curr_cost > self.global_min:
                continue

            closed += 1
            self.update_closed_and_visited_sets(curr_cost, state_repr)

            self.trace_handler.trace = curr_trace
            is_accepting = self.graph_handler.is_accepting()
            final_cost = self.check_accepting_conditions(curr_cost, is_accepting)

            if is_accepting and self.trace_handler.is_empty():
                break

            first_activity = self.trace_handler.get_first_activity()
            is_enabled = self.graph_handler.is_enabled(first_activity)
            # Synchronous Moves
            if first_activity and is_enabled:
                self.handle_state(curr_cost, curr_graph, curr_trace, current, moves, "sync")
            # Model Moves
            if is_enabled:
                self.handle_state(curr_cost, curr_graph, curr_trace, current, moves, "model")
            # Log Moves
            if first_activity:
                self.handle_state(curr_cost, curr_graph, curr_trace, current, moves, "log")
            if self.trace_handler.get_first_activity() and self.graph_handler.is_enabled(
                    self.trace_handler.get_first_activity()):
                self.handle_state(curr_cost, curr_graph, curr_trace, current, moves)

        return {
            'alignment': self.final_alignment,
            'cost': final_cost,
            'visited': visited,
            'closed': closed,
            'global_min': self.global_min
        }



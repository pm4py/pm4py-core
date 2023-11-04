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


class Facade:
    """
    The Facade class provides a simplified interface to perform optimal alignment for DCR graphs,
    abstracting the complexity of direct interactions with the DCRGraphHandler, TraceHandler, and Alignment classes.

    Users should initialize the facade with a DCR_Graph object and a trace object, which can be a list of events, a Pandas DataFrame,
    an EventLog, or a Trace. Optional parameters can also be passed to customize the processing, such as specifying custom activity
    and case ID keys.

    After initializing the facade, users can call perform_alignment() to execute the alignment process, which returns the result of
    the alignment procedure. Once alignment is done, get_performance_metrics() can be used to calculate and retrieve performance
    metrics such as fitness and precision for the alignment.

    Example usage:
        Define your instances of DCR graph and trace representation as 'graph' and 'trace'
        facade = Facade(graph, trace)
        alignment_result = facade.perform_alignment()
        performance_metrics = facade.get_performance_metrics()
        print(f"Alignment Result: {alignment_result}")
        print(f"Performance Metrics: {performance_metrics}")

    Note:
    - perform_alignment() must be called before get_performance_metrics(), as the metrics calculation depends on the alignment results.
    - The user is expected to have a basic understanding of DCR graphs and trace alignment in the context of process mining.

    Attributes:
        graph_handler (DCRGraphHandler): Handler for DCR graph operations.
        trace_handler (TraceHandler): Handler for trace operations.
        alignment (Alignment): Instance that holds the result of the alignment process, initialized to None.

    Methods:
        perform_alignment(): Performs trace alignment against the DCR graph and returns the alignment result.
        get_performance_metrics(): Calculates and returns the fitness and precision performance metrics.
    """

    def __init__(self, graph: DCR_Graph, trace: Union[List[Dict[str, Any]], pd.DataFrame, EventLog, Trace],
                 parameters: Optional[Dict] = None):
        self.graph_handler = DCRGraphHandler(graph)
        self.trace_handler = TraceHandler(trace, parameters)
        self.alignment = None  # This will hold an instance of Alignment class after perform_alignment is called

    def perform_alignment(self):
        # Perform the alignment process and store the result in the self.alignment attribute
        self.alignment = Alignment(self.graph_handler, self.trace_handler)
        return self.alignment.apply_trace()

    def get_performance_metrics(self):
        # Ensure that alignment has been performed before calculating performance metrics
        if not self.alignment:
            raise ValueError("Alignment has not been performed yet.")
        # Calculate and return fitness and precision based on the alignment result
        performance = Performance(self.alignment, self.trace_handler)
        fitness = performance.calculate_fitness()
        precision = performance.calculate_precision()
        return {
            'fitness': fitness,
            'precision': precision
        }


class Parameters(Enum):
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    SYNC_COST = 0
    MODEL_COST = 1
    LOG_COST = 1


class Outputs(Enum):
    ALIGNMENT = "alignment"
    COST = "cost"
    VISITED = "visited_states"
    CLOSED = "closed"
    GLOBAL_MIN = "global_min"


class TraceHandler:
    """
        TraceHandler is responsible for managing and converting traces into a format suitable
        for the alignment algorithm. This class provides functionalities to check if the trace is
        empty, retrieve the first activity from the trace, and convert the trace format as needed.

        A trace can be provided as a list of dictionaries, a pandas DataFrame, an EventLog, or a Trace object.
        The TraceHandler takes care of converting these into a uniform internal representation.

        Attributes
        ----------
        trace : Union[List[Dict[str, Any]], pd.DataFrame, EventLog, Trace]
            The trace to be managed and converted. It's stored internally in a list of dictionaries
            regardless of the input format.
        activity_key : str
            The key to identify activities within the trace data.

        Methods
        -------
        is_empty() -> bool:
            Checks if the trace is empty (contains no events).

        get_first_activity() -> Any:
            Retrieves the first activity from the trace, if available.

        convert_trace(activity_key, case_id_key, parameters):
            Converts the trace into a tuple-based format required for processing by the alignment algorithm.
            This conversion handles both DataFrame and Event Log traces and can be configured via parameters.

        Parameters
        ----------
        trace : Union[List[Dict[str, Any]], pd.DataFrame, EventLog, Trace]
            The initial trace data provided in one of the acceptable formats.
        parameters : Optional[Dict]
            Optional parameters for trace conversion. These can define the keys for activity and case ID within
            the trace data and can include other conversion-related parameters.
        """
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

    def convert_trace(self, activity_key, case_id_key, parameters):
        """
        Convert the trace to the required format.
        """
        if isinstance(self.trace, pd.DataFrame):
            # Conversion for DataFrame traces
            self.trace = list(self.trace.groupby(case_id_key)[activity_key].apply(tuple))
        else:
            # Conversion for Event Log traces
            converted_trace = log_converter.apply(self.trace, variant=log_converter.Variants.TO_EVENT_LOG,
                                                  parameters=parameters)
            if isinstance(converted_trace, list) and all(isinstance(x, dict) for x in converted_trace):
                self.trace = converted_trace


class DCRGraphHandler:
    """
        DCRGraphHandler manages operations on a DCR graph within the context of an alignment algorithm.
        It provides methods to check if an event is enabled, if the graph is in an accepting state,
        and to execute an event on the graph.

        The DCR graph follows the semantics defined in the DCR semantics module, and this class
        acts as an interface to apply these semantics for the purpose of alignment computation.

        Attributes
        ----------
        graph : DCR_Graph
            The DCR graph on which the operations are to be performed.

        Methods
        -------
        is_enabled(event: Any) -> bool:
            Determines if an event is enabled in the current state of the DCR graph.

        is_accepting() -> bool:
            Checks if the current state of the DCR graph is an accepting state.

        execute(event: Any, curr_graph) -> Any:
            Executes an event on the DCR graph, which may result in a transition to a new state.
            If the execution is not possible, it returns the current graph state.

        Parameters
        ----------
        graph : DCR_Graph
            An instance of a DCR_Graph object which the handler will manage and manipulate.

        Raises
        ------
        TypeError
            If the provided graph is not an instance of DCR_Graph.
        """
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


class Performance:
    def __init__(self, alignment, trace_handler):
        self.alignment = alignment
        self.trace_handler = trace_handler

    def calculate_fitness(self):
        # Use the stored cost values from the Alignment object to compute the fitness
        fitness = 1 - (self.alignment.optimal_alignment_cost / self.alignment.worst_case_alignment_cost) \
            if self.alignment.worst_case_alignment_cost > 0 else 0
        return fitness

    @staticmethod
    def calculate_precision():
        # Implement if we have the time
        precision = 1.0
        return precision


class Alignment:
    """
    This class contains the object-oriented implementation of the Optimal Alignments algorithm,
    based on the paper by:
    Author: Axel Kjeld Fjelrad Christfort and Tijs Slaats
    Title: Efficient Optimal Alignment Between Dynamic Condition Response Graphs and Traces
    Publisher: Springer International Publishing
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
        self.optimal_alignment_cost = 0
        self.worst_case_alignment_cost = 0

    def handle_state(self, curr_cost, curr_graph, curr_trace, current, moves, move_type=None):
        """
        Manages the transition to a new state in the alignment algorithm based on the specified move type.
        It computes the new state, checks for execution equivalency to avoid re-processing, and if unique,
        updates the visited states and the priority queue for further processing.

        Parameters
        ----------
        curr_cost : int
            The current cost of the alignment.
        curr_graph : DCR_Graph
            The current state of the DCR graph.
        curr_trace : list
            The current state of the trace.
        current : tuple
            The current state representation in the algorithm.
        moves : list
            The list of moves made so far.
        move_type : str, optional
            The type of move to make. This should be one of "sync", "model", or "log". Default is None.

        Returns
        -------
        None

        Raises
        ------
        None

        Notes
        -----
        - This method interfaces with the `get_new_state` method to compute the new state.
        - It employs a heap-based priority queue to manage the processing order of states based on their costs.
        - Execution equivalency check is performed to reduce redundant processing of similar states.
        """
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

            heappush(self.open_set, (new_cost, new_graph, new_trace, current, self.new_moves))

    def get_new_state(self, curr_cost, curr_graph, curr_trace, moves, move_type):
        """
        Computes the new state of the alignment algorithm based on the current state and
        the specified move type. The new state includes the updated cost, graph, trace,
        and move. This method handles three types of moves: synchronous, model, and log.

        Parameters
        ----------
        curr_cost : int
            The current cost of the alignment.
        curr_graph : DCR_Graph
            The current state of the DCR graph.
        curr_trace : list
            The current state of the trace.
        moves : list
            The list of moves made so far.
        move_type : str
            The type of move to make. This should be one of "sync", "model", or "log".

        Returns
        -------
        tuple
            A tuple containing four elements:
            - new_cost : int, the updated cost of the alignment.
            - new_graph : DCR_Graph, the updated state of the DCR graph.
            - new_trace : list, the updated state of the trace.
            - new_move : tuple, a tuple representing the move made, formatted as (move_type, first_activity).

        Example
        -------
        new_cost, new_graph, new_trace, new_move = get_new_state(curr_cost, curr_graph, curr_trace, moves, "sync")

        """
        new_cost = curr_cost
        new_graph = curr_graph
        new_trace = curr_trace
        new_move = None

        first_activity = self.trace_handler.get_first_activity()

        if move_type == "sync":
            new_cost += Parameters.SYNC_COST.value
            new_move = ('sync', first_activity)
            new_trace = curr_trace[1:]
            if self.graph_handler.is_enabled(first_activity):
                new_graph = self.graph_handler.execute(first_activity, new_graph)

        elif move_type == "model":
            new_cost += Parameters.MODEL_COST.value
            new_move = ('model', first_activity)
            if self.graph_handler.is_enabled(first_activity):
                new_graph = self.graph_handler.execute(first_activity, new_graph)

        elif move_type == "log":
            new_cost += Parameters.LOG_COST.value
            new_move = ('log', first_activity)
            new_trace = curr_trace[1:]

        self.optimal_alignment_cost = min(self.optimal_alignment_cost, new_cost)
        self.worst_case_alignment_cost = len(self.trace_handler.trace) + len(self.graph_handler.graph.events)

        return new_cost, new_graph, new_trace, new_move

    def process_current_state(self, current):
        curr_cost, curr_graph, curr_trace, _, moves = current
        self.graph_handler.graph = copy.deepcopy(curr_graph)
        state_repr = (str(self.graph_handler.graph), tuple(map(str, curr_trace)))

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
        """
        Applies the alignment algorithm to a trace in order to find an optimal alignment
        between the DCR graph and the trace based on the algorithm outlined in the paper
        by Axel Kjeld Fjelrad Christfort and Tijs Slaats.

        Parameters
        ----------
        parameters : dict, optional
            A dictionary of parameters to configure the alignment algorithm.
            Possible keys include:
            - Parameters.ACTIVITY_KEY: Specifies the key to use for activity names in the trace data.
            - Parameters.CASE_ID_KEY: Specifies the key to use for case IDs in the trace data.
            If not provided or None, default values are used.

        Returns
        -------
        dict
            A dictionary containing the results of the alignment algorithm, with the following keys:
            - 'alignment': List of tuples representing the optimal alignment found.
            - 'cost': The cost of the optimal alignment.
            - 'visited': The number of states visited during the alignment algorithm.
            - 'closed': The number of closed states during the alignment algorithm.
            - 'global_min': The global minimum cost found during the alignment algorithm.

        Example
        -------
        result = alignment_obj.apply_trace()
        optimal_alignment = result['alignment']
        alignment_cost = result['cost']

        """

        parameters = {} if parameters is None else parameters

        activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
        case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)

        self.trace_handler.convert_trace(activity_key, case_id_key, parameters)
        visited, closed, cost, self.final_alignment, final_cost = 0, 0, 0, None, float('inf')
        self.open_set.append((cost, self.graph_handler.graph, self.trace_handler.trace, None, []))

        while self.open_set:
            current = heappop(self.open_set)
            visited += 1

            result = self.process_current_state(current)
            if result is None or self.skip_current(result):
                continue

            curr_cost, curr_trace, state_repr, moves = result[0], result[2], result[3], result[4]
            closed += 1

            self.update_closed_and_visited_sets(curr_cost, state_repr)
            self.trace_handler.trace = curr_trace
            final_cost = self.check_accepting_conditions(curr_cost, self.graph_handler.is_accepting())

            if self.graph_handler.is_accepting() and self.trace_handler.is_empty():
                break

            self.perform_moves(curr_cost, current, moves)

        return self.construct_results(visited, closed, final_cost)

    def skip_current(self, result):
        curr_cost, state_repr = result[0], result[3]
        return state_repr in self.closed_set or curr_cost > self.global_min

    def perform_moves(self, curr_cost, current, moves):
        first_activity = self.trace_handler.get_first_activity()
        is_enabled = self.graph_handler.is_enabled(first_activity)

        if first_activity and is_enabled:
            self.handle_state(curr_cost, current[1], current[2], current[3], moves, "sync")
        if is_enabled:
            self.handle_state(curr_cost, current[1], current[2], current[3], moves, "model")
        if first_activity:
            self.handle_state(curr_cost, current[1], current[2], current[3], moves, "log")

    def construct_results(self, visited, closed, final_cost):
        """
        Constructs a dictionary of results from the alignment process containing various metrics
        and outcomes, such as the final alignment, its cost, and statistics about the search process.

        Parameters
        ----------
        visited : int
            The number of states visited during the alignment process.
        closed : int
            The number of states that were closed (i.e., fully processed and will not be revisited).
        final_cost : float
            The cost associated with the final alignment obtained.

        Returns
        -------
        dict
            A dictionary with keys corresponding to various outputs of the alignment process:
            - 'alignment': The final alignment between the process model and the trace.
            - 'cost': The cost of the final alignment.
            - 'visited': The total number of visited states.
            - 'closed': The total number of closed states.
            - 'global_min': The global minimum cost across all explored alignments.
        """
        return {
            Outputs.ALIGNMENT.value: self.final_alignment,
            Outputs.COST.value: final_cost,
            Outputs.VISITED.value: visited,
            Outputs.CLOSED.value: closed,
            Outputs.GLOBAL_MIN.value: self.global_min
        }
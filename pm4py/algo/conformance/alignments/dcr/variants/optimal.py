"""
This module contains the object-oriented implementation of the Optimal Alignments algorithm,
based on the paper by Axel Kjeld Fjelrad Christfort and Tijs Slaats [1].

Overview:
The implementation encapsulates the core components of the algorithm and provides performance calculations
in terms of fitness and precision as described in [2].

The calculation of the alignments, graph-trace handling, and algorithm performance are encapsulated in separate,
dedicated classes, thereby facilitating modularity and reuse.
Central to the module are the following classes:

- `Facade`: Serves as the primary interface for interacting with the algorithm,
  orchestrating the alignment process and providing access to performance metrics.
- `TraceHandler`: Manages the conversion and handling of event traces, preparing them for alignment.
- `DCRGraphHandler`: Encapsulates operations and checks on DCR graphs relevant for the alignment.
- `Performance`: Computes fitness and precision based on the alignment results.
- `Alignment`: Implements the actual algorithm, managing the search space, and constructing optimal alignments.

The module's classes interact to process an input DCR graph and a trace, execute the alignment algorithm,
and compute performance metrics. This process helps in understanding how closely the behavior described by
the trace matches the behavior allowed by the DCR graph, which is essential in the analysis and optimization of business processes.

References
----------
.. [1]
    A. K. F. Christfort, T. Slaats, "Efficient Optimal Alignment Between Dynamic Condition Response Graphs and Traces",
    in Business Process Management, Springer International Publishing, 2023, pp. 3-19.
    DOI <https://doi.org/10.1007/978-3-031-41620-0_1>_.

.. [2]
    J. Carmona, B. van Dongen, A. Solti, M. Weidlich, "Conformance Checking", Springer International Publishing, 2018.
    ISBN 9783319994147.


"""

import pandas as pd
import copy
from typing import Optional, Dict, Any, Union, List
from heapq import heappop, heappush
from enum import Enum
import time

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
        """
        Initializes the facade with a DCR graph and a trace to be processed.

        The facade serves as a simplified interface to perform alignment between
        the provided DCR graph and the trace, handling the creation and coordination
        of the necessary handler objects.

        Parameters
        ----------
        graph : DCR_Graph
            The DCR graph against which the trace will be aligned. The graph should
            encapsulate the behavior model.
        trace : Union[List[Dict[str, Any]], pd.DataFrame, EventLog, Trace]
            The trace to be aligned with the DCR graph. The trace can be in various
            forms, such as a list of dictionaries representing events, a pandas
            DataFrame, an EventLog object, or a Trace object.
        parameters : Optional[Dict], optional
            A dictionary of parameters that can be used to fine-tune the handling
            of the graph and trace. The exact parameters that can be provided will
            depend on the implementation of the DCRGraphHandler and TraceHandler.

        Attributes
        ----------
        self.graph_handler : DCRGraphHandler
            An instance of DCRGraphHandler to manage operations related to the DCR graph.
        self.trace_handler : TraceHandler
            An instance of TraceHandler to manage the conversion and processing of the trace.
        self.alignment : Alignment or None
            An instance of the Alignment class that will be initialized after
            perform_alignment is called. This will hold the result of the trace
            alignment against the DCR graph.
        """
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
    """
    Enumeration that defines keys and constants for various parameters used in the alignment process.

    Attributes:
        CASE_ID_KEY: The key used to identify the case ID in the event log.
        ACTIVITY_KEY: The key used to identify the activity in the event log.
        SYNC_COST: The cost of a synchronous move during the alignment.
        MODEL_COST: The cost of a model move during the alignment.
        LOG_COST: The cost of a log move during the alignment.
    """
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    SYNC_COST = 0
    MODEL_COST = 1
    LOG_COST = 1


class Outputs(Enum):
    """
    Enumeration that defines constants for various outputs of the alignment process.

    Attributes:
        ALIGNMENT: The key for accessing the final alignment from the result.
        COST: The key for accessing the total cost of the alignment.
        VISITED: The key for accessing the number of visited states during the alignment process.
        CLOSED: The key for accessing the number of closed states during the alignment process.
        GLOBAL_MIN: The key for accessing the global minimum cost encountered during the alignment.
    """
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
        """
        Initializes the TraceHandler object, converting the input trace into a standard format
        and storing the specified parameters.

        The conversion process varies depending on the type of trace input provided. The trace is
        converted to a list of dictionary records for consistent internal processing.

        Parameters
        ----------
        trace : Union[List[Dict[str, Any]], pd.DataFrame, EventLog, Trace]
            The initial trace data provided in one of: Pandas DataFrame, an EventLog, or a single Trace.
        parameters : Optional[Dict]
            Optional parameters for trace conversion. These can define the keys for activity and case ID within
            the trace data and can include other conversion-related parameters. If None or not a dictionary,
            defaults will be used.

        The activity key used in the trace is determined by the provided parameters or defaults to
        a standard key from the xes_constants if not specified.
        """
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
        """
        From the Conformance Checking book.
        Calculate the fitness of the alignment based on the optimal and worst-case costs.

        The fitness is calculated as one minus the ratio of the optimal alignment cost to
        the worst-case alignment cost. If the worst-case alignment cost is zero,
        fitness is set to zero to avoid division by zero.

        Returns
        -------
        float
            The calculated fitness value, where higher values indicate a better fit.
        """
        fitness = 1 - (self.alignment.optimal_alignment_cost / self.alignment.worst_case_alignment_cost) \
            if self.alignment.worst_case_alignment_cost > 0 else 0
        return fitness

        def calculate_precision(self):
            # Initialize counters for the numerator and denominator of the precision formula
            matching_behavior = 0
            total_behavior = 0

            # Get all activities in the log
            all_activities_in_log = set(event[self.trace_handler.activity_key] for event in self.trace_handler.trace)

            # Iterate through each event in the log
            for event in self.trace_handler.trace:
                activity = event[self.trace_handler.activity_key]

                # Check if the event is enabled in the model
                if self.alignment.graph_handler.is_enabled(activity):
                    total_behavior += 1

                    # Check if the event is also present in the log
                    if activity in all_activities_in_log:
                        matching_behavior += 1

            precision = matching_behavior / total_behavior if total_behavior > 0 else 0.0
            return precision

    def get_model_behavior(self):
        # Initialize an empty set to store the model behavior
        model_behavior = set()

        # Iterate through all events in the model
        for event in self.alignment.graph_handler.graph.events:
            # Check if the event is enabled
            if self.alignment.graph_handler.is_enabled(event):
                # If the event is enabled, add it to the model behavior set
                model_behavior.add(event)

        return model_behavior


class Alignment:
    def __init__(self, graph_handler: DCRGraphHandler, trace_handler: TraceHandler, parameters: Optional[Dict] = None):
        """
        Initialize the Alignment instance.
        This constructor initializes the alignment with the provided DCR graph and trace handlers. It sets up
        all necessary data structures for computing the alignment and its costs.

        Parameters
        ----------
        graph_handler : DCRGraphHandler
            An instance of DCRGraphHandler to manage the DCR graph.
        trace_handler : TraceHandler
            An instance of TraceHandler to manage the event log trace.
        parameters : Optional[Dict]
            A dictionary of parameters to configure the alignment process. Defaults are used if None.
        """
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
        """
        Process the current state in the alignment process.
        This method processes the current state of the alignment, updates the graph handler
        with the current graph, and prepares the state representation for further processing.

        Parameters
        ----------
        current : Tuple
            The current state, which is a tuple containing the current cost, current graph,
            current trace, and the moves made up to this point.
        """
        curr_cost, curr_graph, curr_trace, _, moves = current
        self.graph_handler.graph = copy.deepcopy(curr_graph)
        state_repr = (str(self.graph_handler.graph), tuple(map(str, curr_trace)))

        return curr_cost, curr_graph, curr_trace, state_repr, moves

    def update_closed_and_visited_sets(self, curr_cost, state_repr):
        self.closed_set[state_repr] = True
        if curr_cost <= self.global_min:
            self.global_min = curr_cost

    def check_accepting_conditions(self, curr_cost, is_accepting):
        """
        Check if the current state meets the accepting conditions and update the global minimum cost and final alignment.

        Parameters
        ----------
        curr_cost : float
            The cost associated with the current state.
        is_accepting : bool
            Flag indicating whether the current state is an accepting state.

        Returns
        -------
        float
            The final cost if the accepting conditions are met; `float('inf')` otherwise.
        """
        final_cost = float('inf')
        if is_accepting:
            if curr_cost <= self.global_min:
                self.global_min = curr_cost
                self.final_alignment = self.new_moves
                final_cost = curr_cost

            if final_cost < self.global_min:
                self.global_min = final_cost
        return final_cost

    def apply(self, trace_or_log, parameters=None):
        if isinstance(trace_or_log, Trace):
            return self.apply_trace(trace_or_log, parameters)
        elif isinstance(trace_or_log, EventLog):
            return self.apply_log(trace_or_log, parameters)
        else:
            raise ValueError("Input must be of type Trace or EventLog")

    def apply_log(self, log: Union[pd.DataFrame, EventLog], parameters: Optional[Dict] = None) -> Dict[str, Any]:

        activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
        results = {}

        if isinstance(log, pd.DataFrame):
            case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
            traces = list(log.groupby(case_id_key)[activity_key].apply(tuple))
            for index, trace in enumerate(traces):
                trace_id = f'trace_{index}'
                trace_df = log[log[case_id_key] == trace_id]
                results[trace_id] = self.apply_trace(trace_df, parameters)
        else:
            log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)
            for trace in log:
                trace_id = trace.attributes.get(constants.CASE_CONCEPT_NAME, str(id(trace)))
                results[trace_id] = self.apply_trace(trace, parameters)

        return results

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
        """
        Defines available moves based on the trace and model state.

        This method determines which moves are possible (synchronous, model, or log moves)
        so that they can be processed accordingly. Each move type is defined as:
        - Synchronous (sync): The activity is both in the trace and the model, and is currently enabled.
        - Model move: The activity is enabled in the model but not in the trace.
        - Log move: The activity is in the trace but not enabled in the model.

        Parameters
        ----------
        curr_cost : float
            The cost associated with the current state before performing any moves.
        current : tuple
            The current state represented as a tuple containing the following:
            - current[0]: The current cumulative cost associated with the trace.
            - current[1]: The current state of the graph representing the model.
            - current[2]: The current position in the trace.
            - current[3]: A placeholder for additional information (if any).
            - current[4]: The list of moves performed to reach this state.
        moves : list
            The list of moves performed so far to reach the current state. This will be updated with new moves
            as they are performed.

        """
        first_activity = self.trace_handler.get_first_activity()
        is_enabled = self.graph_handler.is_enabled(first_activity)

        if first_activity and is_enabled:
            self.handle_state(curr_cost, current[1], current[2], current[3], moves, "sync")
        elif is_enabled:
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

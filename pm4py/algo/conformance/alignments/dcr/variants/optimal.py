'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''

from heapq import heappop, heappush
from enum import Enum

from pm4py.objects.dcr.obj import DCR_Graph
from pm4py.objects.dcr.semantics import DCRSemantics
from pm4py.util import constants, xes_constants, exec_utils
from pm4py.objects.dcr.utils import align_utils
from pm4py.objects.log.obj import EventLog, Trace
from typing import Optional, Dict, Any, Union, List
from pm4py.objects.conversion.log import converter as log_converter
import pandas as pd


class Parameters(Enum):
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    SYNC_COST_FUNCTION = "sync_cost_function"
    MODEL_MOVE_COST_FUNCTION = "model_move_cost_function"
    LOG_MOVE_COST_FUNCTION = "log_move_cost_function"


class Outputs(Enum):
    ALIGNMENT = "alignment"
    COST = "cost"
    VISITED = "visited_states"
    CLOSED = "closed"


POSITION_G = 0
POSITION_MODEL = 1
POSITION_NUM_VISITED = 2
POSITION_F = 3
POSITION_PREV = 4


def apply(obj: Union[EventLog, Trace], G: DCR_Graph, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Union[Dict, List[Dict]]:
    if isinstance(obj[0], list):
        return apply_log(obj, G, parameters=parameters)
    else:
        return apply_trace(obj, G, parameters=parameters)


def enabled(G, e):
    """Check if an event is enabled in the DCR graph"""
    return DCRSemantics.is_enabled(e, G)


def accepting(G):
    """Check if the DCR graph is in an accepting state"""
    return DCRSemantics.is_accepting(G)


def execute(G, e):
    """Execute an event in the DCR graph"""
    new_G = DCRSemantics.execute(G, e)

    if not new_G:
        # Handle error: event couldn't be executed
        pass
    return G


def apply_log(log, G: DCR_Graph, parameters=None):
    aligned_traces = []
    for trace in log:
        al_tr = apply_trace(trace, G, parameters=parameters)
        aligned_traces.append(al_tr)
    return aligned_traces


def handle_state(open_set, curr_cost, curr_G, curr_trace, current, moves, cost_function, global_min, execute_fn=None, update_trace=True):
    new_cost = curr_cost + cost_function.get(curr_trace[0], 0)
    if new_cost >= global_min:
        return global_min
    new_G = execute_fn(curr_G, curr_trace[0]) if execute_fn else curr_G
    new_trace = curr_trace[1:] if update_trace else curr_trace
    heappush(open_set, (new_cost, new_G, new_trace, current, moves + [(new_G, "type", curr_trace[0])]))
    return global_min


def is_empty_trace(curr_trace):
    if hasattr(curr_trace, 'empty'):  # DataFrame
        return curr_trace.empty
    elif isinstance(curr_trace, list):  # List
        return not bool(curr_trace)
    elif isinstance(curr_trace, Trace):  # Trace object
        return not bool(curr_trace)
    else:
        print(f"Unknown type for curr_trace: {type(curr_trace)}")
        return True


def get_first_activity(curr_trace, activity_key):
    if hasattr(curr_trace, 'empty'):  # DataFrame
        return curr_trace.iloc[0, 0] if not curr_trace.empty else None
    elif isinstance(curr_trace, list):  # List
        return curr_trace[0] if curr_trace else None
    elif isinstance(curr_trace, Trace):  # Trace object
        return curr_trace[0][activity_key] if curr_trace else None
    else:
        print(f"Unknown type for curr_trace: {type(curr_trace)}")
        return None


def apply_trace(trace, G, parameters=None):
    """
    Applies the alignment algorithm provided a trace of a log and a DCR Graph.

    Parameters
    ----------
    trace : list
        List of activities in the trace.
    G : DCR_Graph
        DCR Graph.
    parameters : dict, optional
        Parameters for the alignment.

    Returns
    -------
    ali : dict
        Dictionary containing alignment, cost, visited states, and closed states.
    """

    # internal_log_move_cost_function = exec_utils.get_param_value(Parameters.INTERNAL_LOG_MOVE_COST_FUNCTION, parameters,None)
    global_min = float('inf')
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)

    if type(trace) is pd.DataFrame:
        case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
        trace = list(trace.groupby(case_id_key)[activity_key].apply(tuple))
    else:
        converted_trace = log_converter.apply(trace, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

        # Check the type of converted_trace before proceeding
        if isinstance(converted_trace, list) and all(isinstance(x, dict) for x in converted_trace):
            trace = [tuple(x[activity_key] for x in single_trace) for single_trace in converted_trace]
        else:
            print(
                f"Warning: Unexpected format for converted_trace. Type: {type(converted_trace)}, Content: {converted_trace}")

    curr_trace = trace
    # print(f"Applying alignment on trace: {trace}")

    sync_cost_function = parameters.get(Parameters.SYNC_COST_FUNCTION.value, {})
    model_move_cost_function = parameters.get(Parameters.MODEL_MOVE_COST_FUNCTION.value, {})
    log_move_cost_function = parameters.get(Parameters.LOG_MOVE_COST_FUNCTION.value, {})

    visited = 0
    closed = 0
    cost = 0

    open_set = [(cost, G, trace, None, [])]
    closed_set = {}

    while open_set:
        current = heappop(open_set)
        visited += 1

        curr_cost, curr_G, curr_trace, _, moves = current

        if curr_cost >= global_min:
            continue

        state_repr = (curr_G.__repr__(), tuple(curr_trace))
        curr_index = len(curr_trace)

        is_empty = is_empty_trace(curr_trace)
        first_activity = get_first_activity(curr_trace, activity_key)

        if state_repr in closed_set and closed_set[state_repr] >= curr_index:
            continue

        closed += 1
        closed_set[state_repr] = curr_index

        is_accepting = accepting(curr_G)

        if is_accepting and is_empty:
            if curr_cost < global_min:
                global_min = curr_cost
            return {
                'alignment': moves,
                'cost': curr_cost,
                'visited': visited,
                'closed': closed,
                'global_min': global_min
            }

        # Synchronous Moves
        if curr_trace and enabled(curr_G, curr_trace[0]):
            global_min = handle_state(open_set, curr_cost, curr_G, curr_trace, current, moves, sync_cost_function, global_min,
                         execute_fn=execute, update_trace=True)

        # Model Moves
        if enabled(curr_G, curr_trace[0]):
            global_min = handle_state(open_set, curr_cost, curr_G, curr_trace, current, moves, model_move_cost_function, global_min,
                         execute_fn=execute, update_trace=False)

        # Log Moves
        if curr_trace:
            global_min = handle_state(open_set, curr_cost, curr_G, curr_trace, current, moves, log_move_cost_function, global_min,
                         execute_fn=None, update_trace=True)

import datetime

import pm4py.objects.log.log as log_instance
from pm4py.objects.petri import semantics
from pm4py.util import exec_utils
from pm4py.util import xes_constants
from enum import Enum
from pm4py.util import constants


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    MAX_TRACE_LENGTH = "maxTraceLength"

POSITION_MARKING = 0
POSITION_TRACE = 1


def apply(net, initial_marking, final_marking=None, parameters=None):
    """
    Do the playout of a Petrinet generating a log (extensive search; stop at the maximum
    trace length specified

    Parameters
    -----------
    net
        Petri net to play-out
    initial_marking
        Initial marking of the Petri net
    final_marking
        If provided, the final marking of the Petri net
    parameters
        Parameters of the algorithm:
            Parameters.MAX_TRACE_LENGTH -> Maximum trace length
    """
    if parameters is None:
        parameters = {}

    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, xes_constants.DEFAULT_TRACEID_KEY)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    max_trace_length = exec_utils.get_param_value(Parameters.MAX_TRACE_LENGTH, parameters, 10)

    # assigns to each event an increased timestamp from 1970
    curr_timestamp = 10000000

    log = log_instance.EventLog()

    to_visit = [(initial_marking, ())]
    visited = set()

    while len(to_visit) > 0:
        state = to_visit.pop(0)
        if state in visited:
            continue
        visited.add(state)

        m = state[POSITION_MARKING]
        trace = state[POSITION_TRACE]
        en_t = semantics.enabled_transitions(net, m)

        if (final_marking is not None and m == final_marking) or len(en_t) == 0:
            if len(trace) <= max_trace_length:
                log_trace = log_instance.Trace()
                log_trace.attributes[case_id_key] = str(len(log))
                for act in trace:
                    curr_timestamp = curr_timestamp + 1
                    log_trace.append(log_instance.Event({activity_key: act, timestamp_key: datetime.datetime.fromtimestamp(curr_timestamp)}))
                log.append(log_trace)

        for t in en_t:
            new_m = semantics.weak_execute(t, m)
            if t.label is not None:
                new_trace = trace + (t.label,)
            else:
                new_trace = trace
            new_state = (new_m, new_trace)
            if new_state in visited or len(new_trace) > max_trace_length:
                continue
            to_visit.append(new_state)

    return log

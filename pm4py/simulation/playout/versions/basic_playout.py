from copy import copy
from random import shuffle

import pm4py.objects.log.log as log_instance
from pm4py.objects.petri import semantics
from pm4py.simulation.playout.parameters import Parameters
from pm4py.util import exec_utils
from pm4py.util import xes_constants

import time
import datetime


def apply_playout(net, initial_marking, no_traces=100, max_trace_length=100,
                  case_id_key=xes_constants.DEFAULT_TRACEID_KEY,
                  activity_key=xes_constants.DEFAULT_NAME_KEY, timestamp_key=xes_constants.DEFAULT_TIMESTAMP_KEY):
    """
    Do the playout of a Petrinet generating a log

    Parameters
    ----------
    net
        Petri net to play-out
    initial_marking
        Initial marking of the Petri net
    no_traces
        Number of traces to generate
    max_trace_length
        Maximum number of events per trace (do break)
    case_id_key
        Trace attribute that is the case ID
    activity_key
        Event attribute that corresponds to the activity
    timestamp_key
        Event attribute that corresponds to the timestamp
    """
    # assigns to each event an increased timestamp from 1970
    curr_timestamp = 10000000
    log = log_instance.EventLog()
    for i in range(no_traces):
        trace = log_instance.Trace()
        trace.attributes[case_id_key] = str(i)
        marking = copy(initial_marking)
        while True:
            if not semantics.enabled_transitions(net, marking):
                break
            all_enabled_trans = semantics.enabled_transitions(net, marking)
            all_enabled_trans = list(all_enabled_trans)
            shuffle(all_enabled_trans)
            trans = all_enabled_trans[0]
            if trans.label is not None:
                event = log_instance.Event()
                event[activity_key] = trans.label
                event[timestamp_key] = datetime.datetime.fromtimestamp(curr_timestamp)
                trace.append(event)
                # increases by 1 second
                curr_timestamp = curr_timestamp + 1
            marking = semantics.execute(trans, net, marking)
            if len(trace) > max_trace_length:
                break
        if len(trace) > 0:
            log.append(trace)
    return log


def apply(net, initial_marking, parameters=None):
    """
    Do the playout of a Petrinet generating a log

    Parameters
    -----------
    net
        Petri net to play-out
    initial_marking
        Initial marking of the Petri net
    parameters
        Parameters of the algorithm:
            Parameters.NO_TRACES -> Number of traces of the log to generate
            Parameters.MAX_TRACE_LENGTH -> Maximum trace length
    """
    if parameters is None:
        parameters = {}
    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, xes_constants.DEFAULT_TRACEID_KEY)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    no_traces = exec_utils.get_param_value(Parameters.NO_TRACES, parameters, 100)
    max_trace_length = exec_utils.get_param_value(Parameters.MAX_TRACE_LENGTH, parameters, 100)

    return apply_playout(net, initial_marking, max_trace_length=max_trace_length, no_traces=no_traces,
                         case_id_key=case_id_key, activity_key=activity_key, timestamp_key=timestamp_key)

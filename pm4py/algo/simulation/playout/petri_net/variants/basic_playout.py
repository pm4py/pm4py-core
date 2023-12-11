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
import datetime
from copy import copy
from enum import Enum
from random import choice
from typing import Optional, Dict, Any, Union

from pm4py.objects import petri_net
from pm4py.objects.log import obj as log_instance
from pm4py.objects.log.obj import EventLog
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.util import constants
from pm4py.util import exec_utils
from pm4py.util import xes_constants
from pm4py.util.dt_parsing.variants import strpfromiso


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    RETURN_VISITED_ELEMENTS = "return_visited_elements"
    NO_TRACES = "noTraces"
    MAX_TRACE_LENGTH = "maxTraceLength"
    PETRI_SEMANTICS = "petri_semantics"
    ADD_ONLY_IF_FM_IS_REACHED = "add_only_if_fm_is_reached"
    FM_LEQ_ACCEPTED = "fm_leq_accepted"
    INITIAL_TIMESTAMP = "initial_timestamp"
    INITIAL_CASE_ID = "initial_case_id"


def apply_playout(net, initial_marking, no_traces=100, max_trace_length=100,
                  initial_timestamp=10000000, initial_case_id=0,
                  case_id_key=xes_constants.DEFAULT_TRACEID_KEY,
                  activity_key=xes_constants.DEFAULT_NAME_KEY, timestamp_key=xes_constants.DEFAULT_TIMESTAMP_KEY,
                  final_marking=None, return_visited_elements=False, semantics=petri_net.semantics.ClassicSemantics(),
                  add_only_if_fm_is_reached=False, fm_leq_accepted=False):
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
    initial_timestamp
        Increased timestamp from 1970 for the first event
    initial_case_id
        Case id of the first event
    case_id_key
        Trace attribute that is the case ID
    activity_key
        Event attribute that corresponds to the activity
    timestamp_key
        Event attribute that corresponds to the timestamp
    final_marking
        If provided, the final marking of the Petri net
    semantics
        Semantics of the Petri net to be used (default: petri_net.semantics.ClassicSemantics())
    add_only_if_fm_is_reached
        Adds the case only if the final marking is reached
    fm_leq_accepted
        Accepts traces ending in a marking that is a superset of the final marking
    """
    # assigns to each event an increased timestamp from 1970
    curr_timestamp = initial_timestamp
    all_visited_elements = []

    i = 0
    while True:
        if len(all_visited_elements) >= no_traces:
            break

        if i >= no_traces:
            if not add_only_if_fm_is_reached:
                break

            if len(all_visited_elements) == 0:
                # likely, the final marking is not reachable, therefore terminate here the playout
                break

        visited_elements = []
        visible_transitions_visited = []

        marking = copy(initial_marking)
        while len(visible_transitions_visited) < max_trace_length:
            visited_elements.append(marking)

            if not semantics.enabled_transitions(net, marking):  # supports nets with possible deadlocks
                break
            all_enabled_trans = semantics.enabled_transitions(net, marking)
            if final_marking is not None and final_marking <= marking and (final_marking == marking or fm_leq_accepted):
                trans = choice(list(all_enabled_trans.union({None})))
            else:
                trans = choice(list(all_enabled_trans))
            if trans is None:
                break

            visited_elements.append(trans)
            if trans.label is not None:
                visible_transitions_visited.append(trans)

            marking = semantics.execute(trans, net, marking)

        if not add_only_if_fm_is_reached:
            all_visited_elements.append(tuple(visited_elements))
        elif final_marking == marking:
            all_visited_elements.append(tuple(visited_elements))
        elif final_marking <= marking and fm_leq_accepted:
            all_visited_elements.append(tuple(visited_elements))

        i = i + 1

    if return_visited_elements:
        return all_visited_elements

    log = log_instance.EventLog()

    for index, visited_elements in enumerate(all_visited_elements):
        trace = log_instance.Trace()
        trace.attributes[case_id_key] = str(index+initial_case_id)
        for element in visited_elements:
            if type(element) is PetriNet.Transition and element.label is not None:
                event = log_instance.Event()
                event[activity_key] = element.label
                event[timestamp_key] = strpfromiso.fix_naivety(datetime.datetime.fromtimestamp(curr_timestamp))
                trace.append(event)
                # increases by 1 second
                curr_timestamp += 1
        log.append(trace)

    return log


def apply(net: PetriNet, initial_marking: Marking, final_marking: Marking = None,
          parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> EventLog:
    """
    Do the playout of a Petrinet generating a log

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
            Parameters.NO_TRACES -> Number of traces of the log to generate
            Parameters.MAX_TRACE_LENGTH -> Maximum trace length
            Parameters.INITIAL_TIMESTAMP -> The first event is set with INITIAL_TIMESTAMP increased from 1970
            Parameters.INITIAL_CASE_ID -> Numeric case id for the first trace
            Parameters.PETRI_SEMANTICS -> Petri net semantics to be used (default: petri_nets.semantics.ClassicSemantics())
            Parameters.ADD_ONLY_IF_FM_IS_REACHED -> adds the case only if the final marking is reached
            Parameters.FM_LEQ_ACCEPTED -> Accepts traces ending in a marking that is a superset of the final marking
    """
    if parameters is None:
        parameters = {}
    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, xes_constants.DEFAULT_TRACEID_KEY)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    no_traces = exec_utils.get_param_value(Parameters.NO_TRACES, parameters, 1000)
    max_trace_length = exec_utils.get_param_value(Parameters.MAX_TRACE_LENGTH, parameters, 1000)
    initial_timestamp = exec_utils.get_param_value(Parameters.INITIAL_TIMESTAMP, parameters, 10000000)
    initial_case_id = exec_utils.get_param_value(Parameters.INITIAL_CASE_ID, parameters, 0)
    return_visited_elements = exec_utils.get_param_value(Parameters.RETURN_VISITED_ELEMENTS, parameters, False)
    semantics = exec_utils.get_param_value(Parameters.PETRI_SEMANTICS, parameters, petri_net.semantics.ClassicSemantics())
    add_only_if_fm_is_reached = exec_utils.get_param_value(Parameters.ADD_ONLY_IF_FM_IS_REACHED, parameters, False)
    fm_leq_accepted = exec_utils.get_param_value(Parameters.FM_LEQ_ACCEPTED, parameters, False)

    return apply_playout(net, initial_marking, max_trace_length=max_trace_length,
                         initial_timestamp=initial_timestamp,
                         initial_case_id=initial_case_id,
                         no_traces=no_traces,
                         case_id_key=case_id_key, activity_key=activity_key, timestamp_key=timestamp_key,
                         final_marking=final_marking, return_visited_elements=return_visited_elements,
                         semantics=semantics, add_only_if_fm_is_reached=add_only_if_fm_is_reached,
                         fm_leq_accepted=fm_leq_accepted)

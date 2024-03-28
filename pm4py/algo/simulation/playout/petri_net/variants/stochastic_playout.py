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
from typing import Optional, Dict, Any, Union

from pm4py.objects import petri_net
from pm4py.objects.log import obj as log_instance
from pm4py.objects.log.obj import EventLog
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.petri_net.utils import final_marking as final_marking_discovery
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
    LOG = "log"
    STOCHASTIC_MAP = "smap"
    PETRI_SEMANTICS = "petri_semantics"


def apply_playout(net, initial_marking, no_traces=100, max_trace_length=100,
                  case_id_key=xes_constants.DEFAULT_TRACEID_KEY,
                  activity_key=xes_constants.DEFAULT_NAME_KEY, timestamp_key=xes_constants.DEFAULT_TIMESTAMP_KEY,
                  final_marking=None, smap=None, log=None, return_visited_elements=False,
                  semantics=petri_net.semantics.ClassicSemantics(), parameters=None):
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
    final_marking
        If provided, the final marking of the Petri net
    smap
        Stochastic map
    log
        Log
    semantics
        Semantics of the Petri net to be used (default: petri_net.semantics.ClassicSemantics())
    """
    from pm4py.algo.simulation.montecarlo.utils import replay
    from pm4py.objects.stochastic_petri import utils as stochastic_utils

    if final_marking is None:
        # infer the final marking from the net
        final_marking = final_marking_discovery.discover_final_marking(net)
    if smap is None:
        if log is None:
            raise Exception("please provide at least one between stochastic map and log")
        if parameters is None:
            parameters = {}
        parameters_rep = copy(parameters)
        parameters_rep[Parameters.ACTIVITY_KEY] = activity_key
        parameters_rep[Parameters.TIMESTAMP_KEY] = timestamp_key
        smap = replay.get_map_from_log_and_net(log, net, initial_marking, final_marking,
                                               parameters=parameters_rep)

    # assigns to each event an increased timestamp from 1970
    curr_timestamp = 10000000
    all_visited_elements = []

    for i in range(no_traces):
        visited_elements = []
        visible_transitions_visited = []
        marking = copy(initial_marking)

        while len(visible_transitions_visited) < max_trace_length:
            visited_elements.append(marking)

            if not semantics.enabled_transitions(net, marking):  # supports nets with possible deadlocks
                break
            all_enabled_trans = semantics.enabled_transitions(net, marking)
            if final_marking is not None and marking == final_marking:
                en_t_list = list(all_enabled_trans.union({None}))
            else:
                en_t_list = list(all_enabled_trans)

            trans = stochastic_utils.pick_transition(en_t_list, smap)

            if trans is None:
                break

            visited_elements.append(trans)
            if trans.label is not None:
                visible_transitions_visited.append(trans)

            marking = semantics.execute(trans, net, marking)

        all_visited_elements.append(tuple(visited_elements))

    if return_visited_elements:
        return all_visited_elements

    log = log_instance.EventLog()

    for index, visited_elements in enumerate(all_visited_elements):
        trace = log_instance.Trace()
        trace.attributes[case_id_key] = str(index)
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
            Parameters.PETRI_SEMANTICS -> Petri net semantics to be used (default: petri_nets.semantics.ClassicSemantics())
    """
    if parameters is None:
        parameters = {}
    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, xes_constants.DEFAULT_TRACEID_KEY)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    no_traces = exec_utils.get_param_value(Parameters.NO_TRACES, parameters, 1000)
    max_trace_length = exec_utils.get_param_value(Parameters.MAX_TRACE_LENGTH, parameters, 1000)
    smap = exec_utils.get_param_value(Parameters.STOCHASTIC_MAP, parameters, None)
    log = exec_utils.get_param_value(Parameters.LOG, parameters, None)
    return_visited_elements = exec_utils.get_param_value(Parameters.RETURN_VISITED_ELEMENTS, parameters, False)
    semantics = exec_utils.get_param_value(Parameters.PETRI_SEMANTICS, parameters, petri_net.semantics.ClassicSemantics())

    return apply_playout(net, initial_marking, max_trace_length=max_trace_length, no_traces=no_traces,
                         case_id_key=case_id_key, activity_key=activity_key, timestamp_key=timestamp_key,
                         final_marking=final_marking, smap=smap, log=log,
                         return_visited_elements=return_visited_elements,
                         semantics=semantics, parameters=None)

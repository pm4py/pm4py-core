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
import sys
from collections import Counter
from enum import Enum
from typing import Optional, Dict, Any, Union

from pm4py.objects import petri_net
from pm4py.objects.log import obj as log_instance
from pm4py.objects.log.obj import EventLog
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.util.dt_parsing.variants import strpfromiso
from pm4py.util import constants
from pm4py.util import exec_utils
from pm4py.util import xes_constants


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    MAX_TRACE_LENGTH = "maxTraceLength"
    RETURN_ELEMENTS = "return_elements"
    MAX_MARKING_OCC = "max_marking_occ"
    PETRI_SEMANTICS = "petri_semantics"


POSITION_MARKING = 0
POSITION_TRACE = 1
POSITION_ELEMENTS = 2


def apply(net: PetriNet, initial_marking: Marking, final_marking: Marking = None,
          parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> EventLog:
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
            Parameters.PETRI_SEMANTICS -> Petri net semantics
    """
    if parameters is None:
        parameters = {}

    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, xes_constants.DEFAULT_TRACEID_KEY)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    max_trace_length = exec_utils.get_param_value(Parameters.MAX_TRACE_LENGTH, parameters, 10)
    return_elements = exec_utils.get_param_value(Parameters.RETURN_ELEMENTS, parameters, False)
    max_marking_occ = exec_utils.get_param_value(Parameters.MAX_MARKING_OCC, parameters, sys.maxsize)
    semantics = exec_utils.get_param_value(Parameters.PETRI_SEMANTICS, parameters, petri_net.semantics.ClassicSemantics())

    # assigns to each event an increased timestamp from 1970
    curr_timestamp = 10000000

    feasible_elements = []

    to_visit = [(initial_marking, (), ())]
    visited = set()

    while len(to_visit) > 0:
        state = to_visit.pop(0)

        m = state[POSITION_MARKING]
        trace = state[POSITION_TRACE]
        elements = state[POSITION_ELEMENTS]

        if (m, trace) in visited:
            continue
        visited.add((m, trace))

        en_t = semantics.enabled_transitions(net, m)

        if (final_marking is not None and m == final_marking) or (final_marking is None and len(en_t) == 0):
            if len(trace) <= max_trace_length:
                feasible_elements.append(elements)

        for t in en_t:
            new_elements = elements + (m,)
            new_elements = new_elements + (t,)

            counter_elements = Counter(new_elements)

            if counter_elements[m] > max_marking_occ:
                continue

            new_m = semantics.weak_execute(t, net, m)
            if t.label is not None:
                new_trace = trace + (t.label,)
            else:
                new_trace = trace

            new_state = (new_m, new_trace, new_elements)

            if new_state in visited or len(new_trace) > max_trace_length:
                continue
            to_visit.append(new_state)

    if return_elements:
        return feasible_elements

    log = log_instance.EventLog()
    for elements in feasible_elements:
        log_trace = log_instance.Trace()
        log_trace.attributes[case_id_key] = str(len(log))
        activities = [x.label for x in elements if type(x) is PetriNet.Transition and x.label is not None]
        for act in activities:
            curr_timestamp = curr_timestamp + 1
            log_trace.append(
                log_instance.Event({activity_key: act, timestamp_key: strpfromiso.fix_naivety(datetime.datetime.fromtimestamp(curr_timestamp))}))
        log.append(log_trace)

    return log

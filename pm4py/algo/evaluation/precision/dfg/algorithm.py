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
from collections import Counter
from enum import Enum
from typing import Optional, Dict, Any, Union, Tuple

from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.obj import EventLog, EventStream
from pm4py.util import exec_utils, xes_constants, constants


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY


def __is_allowed_prefix(exiting_activities, sa, prefix):
    if not prefix:
        return True
    if prefix[0] not in sa:
        return False
    prev_act = prefix[0]
    for i in range(1, len(prefix)):
        curr_act = prefix[i]
        if prev_act not in exiting_activities or curr_act not in exiting_activities[prev_act]:
            return False
        prev_act = curr_act
    if not prefix[-1] in exiting_activities:
        return False
    return True


def apply(log: Union[EventLog, EventStream], dfg: Dict[Tuple[str, str], int],
                            start_activities: Dict[str, int], end_activities: Dict[str, int],
                            parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> float:
    """
    Computes the precision of a directly-follows graph using the ETConformance approach

    Parameters
    ---------------
    log
        Event log
    dfg
        Directly-follows graph
    start_activities
        Start activities
    end_activities
        End activities
    parameters
        Parameters of the algorithm:
        - Parameters.ACTIVITY_KEY: the key to use

    Returns
    ----------------
    precision
        Precision value
    """
    if parameters is None:
        parameters = {}
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    precision = 1.0
    sum_ee = 0
    sum_at = 0
    exiting_activities = {}
    for act_couple in dfg:
        if not act_couple[0] in exiting_activities:
            exiting_activities[act_couple[0]] = set()
        exiting_activities[act_couple[0]].add(act_couple[1])
    prefixes = {}
    prefixes_count = Counter()
    for trace in log:
        prefix_act = []
        for i in range(len(trace)):
            prefix_act_tuple = tuple(prefix_act)
            if prefix_act_tuple not in prefixes:
                prefixes[prefix_act_tuple] = set()
            prefixes_count[prefix_act_tuple] += 1
            prefixes[prefix_act_tuple].add(trace[i][activity_key])
            prefix_act.append(trace[i][activity_key])
    for prefix in prefixes:
        if __is_allowed_prefix(exiting_activities, start_activities, prefix):
            log_transitions = prefixes[prefix]
            activated_transitions = set(start_activities.keys()) if not prefix else exiting_activities[prefix[-1]]
            escaping_edges = activated_transitions.difference(log_transitions)
            sum_ee += len(escaping_edges) * prefixes_count[prefix]
            sum_at += len(activated_transitions) * prefixes_count[prefix]

    if sum_at > 0:
        precision = 1 - float(sum_ee) / float(sum_at)

    return precision

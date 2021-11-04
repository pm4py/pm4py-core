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
import collections

from pm4py.util import exec_utils
from pm4py.objects.log import util as log_util
from pm4py.util.xes_constants import DEFAULT_NAME_KEY
from pm4py.objects.transition_system import obj as ts, constants as ts_constants
from enum import Enum
from pm4py.util import constants
from pm4py.objects.transition_system.obj import TransitionSystem
from typing import Optional, Dict, Any, Union, Tuple
from pm4py.objects.log.obj import EventLog, EventStream
import pandas as pd


class Parameters(Enum):
    VIEW_MULTI_SET = 'multiset'
    VIEW_SET = 'set'
    VIEW_SEQUENCE = 'sequence'

    VIEWS = {VIEW_MULTI_SET, VIEW_SET, VIEW_SEQUENCE}

    DIRECTION_FORWARD = 'forward'
    DIRECTION_BACKWARD = 'backward'
    DIRECTIONS = {DIRECTION_FORWARD, DIRECTION_BACKWARD}

    PARAM_KEY_VIEW = 'view'
    PARAM_KEY_WINDOW = 'window'
    PARAM_KEY_DIRECTION = 'direction'

    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY

    INCLUDE_DATA = 'include_data'


def apply(log: Union[EventLog, EventStream, pd.DataFrame], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> TransitionSystem:
    if parameters is None:
        parameters = {}
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, DEFAULT_NAME_KEY)
    include_data = exec_utils.get_param_value(Parameters.INCLUDE_DATA, parameters, False)

    transition_system = ts.TransitionSystem()
    control_flow_log = log_util.log.project_traces(log, activity_key)
    view_sequence = []
    for i in range(len(log)):
        view_sequence.append(__compute_view_sequence(control_flow_log[i], log[i], parameters=parameters))
    for vs in view_sequence:
        __construct_state_path(vs, transition_system, include_data=include_data)
    return transition_system


def __construct_state_path(view_sequence, transition_system, include_data=False):
    for i in range(0, len(view_sequence) - 1):
        sf = {'state': s for s in transition_system.states if s.name == view_sequence[i][0]}
        sf = sf['state'] if len(sf) > 0 else ts.TransitionSystem.State(view_sequence[i][0])
        st = {'state': s for s in transition_system.states if s.name == view_sequence[i + 1][0]}
        st = st['state'] if len(st) > 0 else ts.TransitionSystem.State(view_sequence[i + 1][0])
        t = {'t': t for t in sf.outgoing if t.name == view_sequence[i][1] and t.from_state == sf and t.to_state == st}
        if len(t) == 0:
            t = ts.TransitionSystem.Transition(view_sequence[i][1], sf, st)
            sf.outgoing.add(t)
            st.incoming.add(t)
        else:
            t = t['t']
        if include_data:
            # add the event to the data in both the source state,
            # the sink state and the transition
            sf.data[ts_constants.OUTGOING_EVENTS].append(view_sequence[i][2])
            st.data[ts_constants.INGOING_EVENTS].append(view_sequence[i][2])
            t.data[ts_constants.EVENTS].append(view_sequence[i][2])
        transition_system.states.add(sf)
        transition_system.states.add(st)
        transition_system.transitions.add(t)


def __compute_view_sequence(trace, full_case, parameters):
    view_sequences = list()
    direction = exec_utils.get_param_value(Parameters.PARAM_KEY_DIRECTION, parameters,
                                           Parameters.DIRECTION_FORWARD.value)
    window = exec_utils.get_param_value(Parameters.PARAM_KEY_WINDOW, parameters, 2)
    for i in range(0, len(trace) + 1):
        if direction == Parameters.DIRECTION_FORWARD.value:
            view_sequences.append((__apply_abstr(trace[i:i + window], parameters),
                                   trace[i] if i < len(trace) else None, (full_case, i) if i < len(full_case) else None))
        else:
            view_sequences.append((__apply_abstr(trace[max(0, i - window):i], parameters),
                                   trace[i] if i < len(trace) else None, (full_case, i) if i < len(full_case) else None))
    return view_sequences


def __apply_abstr(seq, parameters):
    key_view = exec_utils.get_param_value(Parameters.PARAM_KEY_VIEW, parameters, Parameters.VIEW_SEQUENCE.value)

    if key_view == Parameters.VIEW_SEQUENCE.value:
        return list(seq)
    elif key_view == Parameters.VIEW_MULTI_SET.value:
        return collections.Counter(seq)
    elif key_view == Parameters.VIEW_SET.value:
        return set(seq)

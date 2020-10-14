import collections

from pm4py.algo.discovery.transition_system.parameters import Parameters
from pm4py.util import exec_utils
from pm4py.objects.log import util as log_util
from pm4py.util.xes_constants import DEFAULT_NAME_KEY
from pm4py.objects.transition_system import transition_system as ts, constants as ts_constants


def apply(log, parameters=None):
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

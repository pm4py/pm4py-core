import collections

from pm4py.algo.discovery.transition_system.parameters import *
from pm4py.objects.log import util as log_util
from pm4py.objects.log.util.xes import DEFAULT_NAME_KEY
from pm4py.objects.transition_system import transition_system as ts
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY


def apply(log, parameters=None):
    if parameters is None:
        parameters = {}
    for parameter in DEFAULT_PARAMETERS:
        if parameter not in parameters:
            parameters[parameter] = DEFAULT_PARAMETERS[parameter]
    activity_key = parameters[
        PARAMETER_CONSTANT_ACTIVITY_KEY] if PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else DEFAULT_NAME_KEY
    transition_system = ts.TransitionSystem()
    control_flow_log = log_util.log.project_traces(log, activity_key)
    view_sequence = (list(map(lambda t: __compute_view_sequence(t, parameters), control_flow_log)))
    for vs in view_sequence:
        __construct_state_path(vs, transition_system)
    return transition_system


def __construct_state_path(view_sequence, transition_system):
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
        transition_system.states.add(sf)
        transition_system.states.add(st)
        transition_system.transitions.add(t)


def __compute_view_sequence(trace, parameters):
    view_sequences = list()
    for i in range(0, len(trace) + 1):
        if parameters[PARAM_KEY_DIRECTION] == DIRECTION_FORWARD:
            view_sequences.append((__apply_abstr(trace[i:i + parameters[PARAM_KEY_WINDOW]], parameters),
                                   trace[i] if i < len(trace) else None))
        else:
            view_sequences.append((__apply_abstr(trace[max(0, i - parameters[PARAM_KEY_WINDOW]):i], parameters),
                                   trace[i] if i < len(trace) else None))
    return view_sequences


def __apply_abstr(seq, parameters):
    case = {
        VIEW_SEQUENCE: list,
        VIEW_MULTI_SET: collections.Counter,
        VIEW_SET: set
    }
    return case[parameters[PARAM_KEY_VIEW]](seq) if len(seq) > 0 else case[parameters[PARAM_KEY_VIEW]]()

import re

from pm4py.objects import petri
from pm4py.objects.transition_system import transition_system as ts
from pm4py.objects.transition_system import utils
from pm4py.util import exec_utils
from enum import Enum
import time


class Parameters(Enum):
    MAX_ELAB_TIME = "max_elab_time"


def staterep(name):
    """
    Creates a string representation for a state of a transition system.
    Necessary because graphviz does not support symbols simulation than alphanimerics and '_'.
    TODO: find a better representation.

    Parameters
    ----------
    name: the name of a state

    Returns
    -------
    Version of the name filtered of non-alphanumerical characters (except '_').
    """
    return re.sub(r'\W+', '', name)


def marking_flow_petri(net, im, return_eventually_enabled=False, parameters=None):
    """
    Construct the marking flow of a Petri net

    Parameters
    -----------------
    net
        Petri net
    im
        Initial marking
    return_eventually_enabled
        Return the eventually enabled (visible) transitions
    """
    if parameters is None:
        parameters = {}

    # set a maximum execution time of 1 day (it can be changed by providing the parameter)
    max_exec_time = exec_utils.get_param_value(Parameters.MAX_ELAB_TIME, parameters, 86400)

    start_time = time.time()

    incoming_transitions = {im: set()}
    outgoing_transitions = {}
    eventually_enabled = {}

    active = [im]
    while active:
        if (time.time() - start_time) >= max_exec_time:
            # interrupt the execution
            return incoming_transitions, outgoing_transitions, eventually_enabled
        m = active.pop()
        enabled_transitions = petri.semantics.enabled_transitions(net, m)
        if return_eventually_enabled:
            eventually_enabled[m] = petri.align_utils.get_visible_transitions_eventually_enabled_by_marking(net, m)
        outgoing_transitions[m] = {}
        for t in enabled_transitions:
            nm = petri.semantics.weak_execute(t, m)
            outgoing_transitions[m][t] = nm
            if nm not in incoming_transitions:
                incoming_transitions[nm] = set()
                if nm not in active:
                    active.append(nm)
            incoming_transitions[nm].add(t)

    return incoming_transitions, outgoing_transitions, eventually_enabled


def construct_reachability_graph_from_flow(incoming_transitions, outgoing_transitions,
                                           use_trans_name=False, parameters=None):
    """
    Construct the reachability graph from the marking flow

    Parameters
    ----------------
    incoming_transitions
        Incoming transitions
    outgoing_transitions
        Outgoing transitions
    use_trans_name
        Use the transition name

    Returns
    ----------------
    re_gr
        Transition system that represents the reachability graph of the input Petri net.
    """
    if parameters is None:
        parameters = {}

    re_gr = ts.TransitionSystem()

    map_states = {}
    for s in incoming_transitions:
        map_states[s] = ts.TransitionSystem.State(staterep(repr(s)))
        re_gr.states.add(map_states[s])

    for s1 in outgoing_transitions:
        for t in outgoing_transitions[s1]:
            s2 = outgoing_transitions[s1][t]
            if use_trans_name:
                utils.add_arc_from_to(t.name, map_states[s1], map_states[s2], re_gr)
            else:
                utils.add_arc_from_to(repr(t), map_states[s1], map_states[s2], re_gr)

    return re_gr


def construct_reachability_graph(net, initial_marking, use_trans_name=False, parameters=None):
    """
    Creates a reachability graph of a certain Petri net.
    DO NOT ATTEMPT WITH AN UNBOUNDED PETRI NET, EVER.

    Parameters
    ----------
    net: Petri net
    initial_marking: initial marking of the Petri net.

    Returns
    -------
    re_gr: Transition system that represents the reachability graph of the input Petri net.
    """
    incoming_transitions, outgoing_transitions, eventually_enabled = marking_flow_petri(net, initial_marking,
                                                                                        parameters=parameters)

    return construct_reachability_graph_from_flow(incoming_transitions, outgoing_transitions,
                                                  use_trans_name=use_trans_name, parameters=parameters)

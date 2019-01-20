import re

from pm4py.objects import petri
from pm4py.objects.transition_system import transition_system as ts
from pm4py.objects.transition_system import utils


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


def construct_reachability_graph(net, initial_marking):
    """
    Creates a reachability graph of a certain Petri net.
    DO NOT ATTEMPT WITH AN UNBOUNDED PETRI NET, EVER.
    TODO: graphviz do not show labeling for the arcs. Add the labeling.

    Parameters
    ----------
    net: Petri net
    initial_marking: initial marking of the Petri net.

    Returns
    -------
    re_gr: Transition system that represents the reachability graph of the input Petri net.
    """
    active = [initial_marking]
    visited = []
    re_gr = ts.TransitionSystem()
    re_gr.states.add(ts.TransitionSystem.State(staterep(repr(initial_marking))))
    for i in range(10000000):
        if not active:
            break
        curr_mark = active.pop(0)
        curr_state = next((state for state in re_gr.states if state.name == staterep(repr(curr_mark))), None)
        en_tr = petri.semantics.enabled_transitions(net, curr_mark)
        for t in en_tr:
            next_mark = petri.semantics.execute(t, net, curr_mark)
            next_state = next((state for state in re_gr.states if state.name == staterep(repr(next_mark))), None)
            if next_state is None:
                next_state = ts.TransitionSystem.State(staterep(repr(next_mark)))
                re_gr.states.add(next_state)
            utils.add_arc_from_to(repr(t), curr_state, next_state, re_gr)
            # If the next marking hash is not in visited, if the next marking itself is not already in active
            # and if the next marking is different from the current one
            if hash(next_mark) not in visited and next((mark for mark in active if hash(mark) == hash(next_mark)),
                                                       None) is None and hash(curr_mark) != hash(next_mark):
                active.append(next_mark)
        visited.append(hash(curr_mark))
    return re_gr

from pm4py.models.transition_system import transition_system


def add_arc_from_to(name, fr, to, ts, data=None):
    '''
    Adds a transition from a state to another state in some transition system.
    Assumes from and to are in the transition system!

    Parameters
    ----------
    name: name of the transition
    fr: state from
    to:  state to
    ts: transition system to use

    Returns
    -------
    None
    '''
    tran = transition_system.TransitionSystem.Transition(name, fr, to, data)
    ts.transitions.add(tran)
    fr.outgoing.add(tran)
    to.incoming.add(tran)


def remove_arc_from_to(name, fr, to, ts):
    '''
    Removes a transition with a specific name from a state to another state in some transition system.
    Assumes from and to are in the transition system!

    Parameters
    ----------
    name: name of the transition
    fr: state from
    to:  state to
    ts: transition system to use

    Returns
    -------
    None
    '''
    ts.transitions[:] = [t for t in ts.transitions if t.name != name]
    fr.outgoing[:] = [t for t in fr.outgoing if t.name != name]
    to.incoming[:] = [t for t in fr.incoming if t.name != name]


# def transitive_reduction(ts):
#     for vertex0 in vertices:
#         done = set()
#         for child in vertex0.children:
#             df(edges, vertex0, child, done)
#
#     df = function(edges, vertex0, child0, done)
#     if child0 in done:
#         return
#     for child in child0.children:
#         edge.discard((vertex0, child))
#         df(edges, vertex0, child, done)
#     done.add(child0)

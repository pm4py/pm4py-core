from pm4py.entities.transition_system import transition_system


def add_arc_from_to(name, fr, to, ts, data=None):
    '''
    Adds a transition from a state to another state in some transition system.
    Assumes from and to are in the transition system!

    Parameters
    ----------
    name:
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

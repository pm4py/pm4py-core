from pm4py.objects import petri
from pm4py.objects.log.util import xes as xes_util


def remove_transition(net, trans):
    """
    Remove a transition from a Petri net

    Parameters
    ----------
    net
        Petri net
    trans
        Transition to remove

    Returns
    ----------
    net
        Petri net
    """
    if trans in net.transitions:
        in_arcs = trans.in_arcs
        for arc in in_arcs:
            place = arc.source
            place.out_arcs.remove(arc)
            net.arcs.remove(arc)
        out_arcs = trans.out_arcs
        for arc in out_arcs:
            place = arc.target
            place.in_arcs.remove(arc)
            net.arcs.remove(arc)
        net.transitions.remove(trans)
    return net


def add_arc_from_to(fr, to, net, weight=1):
    """
    Adds an arc from a specific element to another element in some net. Assumes from and to are in the net!

    Parameters
    ----------
    fr: transition/place from
    to:  transition/place to
    net: net to use
    weight: weight associated to the arc

    Returns
    -------
    None
    """
    a = petri.petrinet.PetriNet.Arc(fr, to, weight)
    net.arcs.add(a)
    fr.out_arcs.add(a)
    to.in_arcs.add(a)


def construct_trace_net(trace, trace_name_key=xes_util.DEFAULT_NAME_KEY, activity_key=xes_util.DEFAULT_NAME_KEY):
    """
    Creates a trace net, i.e. a trace in Petri net form.

    Parameters
    ----------
    trace: :class:`list` input trace, assumed to be a list of events
    trace_name_key: :class:`str` key of the attribute that defines the name of the trace
    activity_key: :class:`str` key of the attribute of the events that defines the activity name

    Returns
    -------
    tuple: :class:`tuple` of the net, initial marking and the final marking

    """
    net = petri.petrinet.PetriNet(
        'trace net of %s' % trace.attributes[trace_name_key] if trace_name_key in trace.attributes else ' ')
    place_map = {0: petri.petrinet.PetriNet.Place('p_0')}
    net.places.add(place_map[0])
    for i in range(0, len(trace)):
        t = petri.petrinet.PetriNet.Transition('t' + str(i), trace[i][activity_key])
        net.transitions.add(t)
        place_map[i + 1] = petri.petrinet.PetriNet.Place('p_' + str(i + 1))
        net.places.add(place_map[i + 1])
        petri.utils.add_arc_from_to(place_map[i], t, net)
        petri.utils.add_arc_from_to(t, place_map[i + 1], net)
    return net, petri.petrinet.Marking({place_map[0]: 1}), petri.petrinet.Marking({place_map[len(trace)]: 1})


def construct_trace_net_cost_aware(trace, costs, trace_name_key=xes_util.DEFAULT_NAME_KEY,
                                   activity_key=xes_util.DEFAULT_NAME_KEY):
    """
    Creates a trace net, i.e. a trace in Petri net form.

    Parameters
    ----------
    trace: :class:`list` input trace, assumed to be a list of events
    costs: :class:`list` list of costs, length should be equal to the length of the input trace
    trace_name_key: :class:`str` key of the attribute that defines the name of the trace
    activity_key: :class:`str` key of the attribute of the events that defines the activity name

    Returns
    -------
    tuple: :class:`tuple` of the net, initial marking and the final marking

    """
    net = petri.petrinet.PetriNet(
        'trace net of %s' % trace.attributes[trace_name_key] if trace_name_key in trace.attributes else ' ')
    place_map = {0: petri.petrinet.PetriNet.Place('p_0')}
    net.places.add(place_map[0])
    cost_map = dict()
    for i in range(0, len(trace)):
        t = petri.petrinet.PetriNet.Transition('t' + str(i), trace[i][activity_key])
        cost_map[t] = costs[i]
        net.transitions.add(t)
        place_map[i + 1] = petri.petrinet.PetriNet.Place('p_' + str(i + 1))
        net.places.add(place_map[i + 1])
        petri.utils.add_arc_from_to(place_map[i], t, net)
        petri.utils.add_arc_from_to(t, place_map[i + 1], net)
    return net, petri.petrinet.Marking({place_map[0]: 1}), petri.petrinet.Marking({place_map[len(trace)]: 1}), cost_map


def variants(net, initial_marking, final_marking):
    """
    Given an acyclic workflow net, initial and final marking extracts a set of variants (list of event)
    replayable on the net.

    Parameters
    ----------
    net: An acyclic workflow net
    initial_marking: The initial marking of the net.
    final_marking: The final marking of the net.

    Returns
    -------
    variants: :class:`list` List of variants replayable in the net.

    """
    active = [(initial_marking, [])]
    visited = []
    this_variants = []
    for i in range(10000000):
        if not active:
            break
        curr_couple = active.pop(0)
        en_tr = petri.semantics.enabled_transitions(net, curr_couple[0])
        for t in en_tr:
            next_activitylist = list(curr_couple[1])
            next_activitylist.append(repr(t))
            next_couple = (petri.semantics.execute(t, net, curr_couple[0]), next_activitylist)
            if hash(next_couple[0]) == hash(final_marking):
                this_variants.append(next_couple[1])
            else:
                # If the next marking hash is not in visited, if the next marking+partial trace itself is
                # not already in active and if the next marking+partial trace is different from the
                # current one+partial trace
                if hash(next_couple[0]) not in visited and next((mark for mark in active if hash(mark[0]) == hash(
                        next_couple[0] and mark[1] == next_couple[1])), None) is None and (
                        hash(curr_couple[0]) != hash(next_couple[0]) or curr_couple[1] != next_couple[1]):
                    active.append(next_couple)
        visited.append(hash(curr_couple[0]))
    return this_variants


def get_transition_by_name(net, transition_name):
    for t in net.transitions:
        if t.name == transition_name:
            return t
    return None

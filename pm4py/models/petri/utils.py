from pm4py.models import petri
from pm4py.log.util import xes as xes_util


def add_arc_from_to(fr, to, net, weight=1):
    '''
    Adds an arc from a specific element to another element in some net. Assumes from and to are in the net!

    Parameters
    ----------
    fr: transition/place from
    to:  transition/place to
    net: net to use

    Returns
    -------
    None
    '''
    a = petri.petrinet.PetriNet.Arc(fr, to, weight)
    net.arcs.add(a)
    fr.out_arcs.add(a)
    to.in_arcs.add(a)


def construct_trace_net(trace, trace_name_key=xes_util.DEFAULT_NAME_KEY, activity_key=xes_util.DEFAULT_NAME_KEY):
    '''
    Creates a trace net, i.e. a trace in Petri net form.

    Parameters
    ----------
    trace: :class:`list` input trace, assumed to be a list of events
    trace_name_key: :class:`str` key of the attribute that defines the name of the trace.
    activity_key: :class:`str` key of the attribute of the events that defines the activity name

    Returns
    -------
    tuple: :class:`tuple` of the net, initial marking and the final marking

    '''
    net = petri.petrinet.PetriNet('trace net of %s' % trace.attributes[trace_name_key] if trace_name_key in trace.attributes else ' ')
    place_map = {0: petri.petrinet.PetriNet.Place('p_0')}
    net.places.add(place_map[0])
    for i in range(0, len(trace)):
        t = petri.petrinet.PetriNet.Transition('t' + str(i), trace[i][activity_key])
        net.transitions.add(t)
        place_map[i+1] = petri.petrinet.PetriNet.Place('p_' + str(i+1))
        net.places.add(place_map[i+1])
        petri.utils.add_arc_from_to(place_map[i], t, net)
        petri.utils.add_arc_from_to(t, place_map[i+1], net)
    return net, petri.petrinet.Marking({place_map[0]: 1}), petri.petrinet.Marking({place_map[len(trace)]: 1})


def construct_trace_net_cost_aware(trace, costs, trace_name_key=xes_util.DEFAULT_NAME_KEY, activity_key=xes_util.DEFAULT_NAME_KEY):
    '''
    Creates a trace net, i.e. a trace in Petri net form.

    Parameters
    ----------
    trace: :class:`list` input trace, assumed to be a list of events
    costs: :class:`list` list of costs, length should be equal to the length of the input trace
    trace_name_key: :class:`str` key of the attribute that defines the name of the trace.
    activity_key: :class:`str` key of the attribute of the events that defines the activity name

    Returns
    -------
    tuple: :class:`tuple` of the net, initial marking and the final marking

    '''
    net = petri.petrinet.PetriNet('trace net of %s' % trace.attributes[trace_name_key] if trace_name_key in trace.attributes else ' ')
    place_map = {0: petri.petrinet.PetriNet.Place('p_0')}
    net.places.add(place_map[0])
    cost_map = dict()
    for i in range(0, len(trace)):
        t = petri.petrinet.PetriNet.Transition('t' + str(i), trace[i][activity_key])
        cost_map[t] = costs[i]
        net.transitions.add(t)
        place_map[i+1] = petri.petrinet.PetriNet.Place('p_' + str(i+1))
        net.places.add(place_map[i+1])
        petri.utils.add_arc_from_to(place_map[i], t, net)
        petri.utils.add_arc_from_to(t, place_map[i+1], net)
    return net, petri.petrinet.Marking({place_map[0]: 1}), petri.petrinet.Marking({place_map[len(trace)]: 1}), cost_map

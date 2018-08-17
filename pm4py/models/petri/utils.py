from pm4py.models import petri
from pm4py.log.util import xes as xes_util

def add_arc_from_to(fr, to, net, weight=1):
    '''
    Adds an arc from a specific element to another element in some net. Assumes from and to are in the net!

    :param fr: transition/place from
    :param to:  transition/place to
    :param net: net to use
    :return: pass
    '''
    a = petri.net.PetriNet.Arc(fr, to, weight)
    net.arcs.add(a)
    fr.out_arcs.add(a)
    to.in_arcs.add(a)


def construct_trace_net(trace, trace_name_key=xes_util.DEFAULT_NAME_KEY, activity_key=xes_util.DEFAULT_NAME_KEY):
    net = petri.net.PetriNet('trace net of %s' % trace.attributes[trace_name_key] if trace_name_key in trace.attributes else ' ')
    place_map = {0: petri.net.PetriNet.Place('p_0')}
    net.places.add(place_map[0])
    for i in range(0, len(trace)):
        t = petri.net.PetriNet.Transition('t' + str(i), trace[i][activity_key])
        net.transitions.add(t)
        place_map[i+1] = petri.net.PetriNet.Place('p_' + str(i+1))
        net.places.add(place_map[i+1])
        petri.utils.add_arc_from_to(place_map[i], t, net)
        petri.utils.add_arc_from_to(t, place_map[i+1], net)
    return net, petri.net.Marking({place_map[0]: 1}), petri.net.Marking({place_map[len(trace)]: 1})

from copy import deepcopy

from pm4py.objects.petri import utils
from pm4py.objects.petri.petrinet import PetriNet, Marking


def project(net0, im0, fm0, allowed_transitions):
    """
    Project a Petri Net on a set of transitions provided by the user

    Parameters
    -------------
    net0
        Petri net
    im0
        Initial marking
    fm0
        Final marking
    allowed_transitions
        Sets of allowed transitions

    Returns
    -------------
    net
        Projected net
    im
        Projected initial marking
    fm
        Projected final marking
    """
    [net, im1, fm1] = deepcopy([net0, im0, fm0])

    # keep only visible transitions that have a label in allowed_transitions
    trans_list = list(net.transitions)
    for trans in trans_list:
        if trans.label is not None and trans.name not in allowed_transitions:
            net = utils.remove_transition(net, trans)

    # create a fictious Petri net
    old_net = PetriNet("")
    # remove unconnected elements until a 'stable' platform is reached
    n_it = 0
    while not (len(old_net.places) == len(net.places) and len(old_net.transitions) == len(net.transitions) and len(
            old_net.arcs) == len(net.arcs)):
        n_it = n_it + 1
        old_net = deepcopy(net)
        trans_list = list(net.transitions)
        for trans in trans_list:
            # remove invisible transitions that have no input or output arcs
            if trans.label is None and (
                    len(trans.in_arcs) == 0 or len(trans.out_arcs) == 0) and trans.name not in allowed_transitions:
                net = utils.remove_transition(net, trans)
                continue

        places_list = list(net.places)

        for place in places_list:
            # remove places that have no input or output arcs
            if len(place.in_arcs) == 0 and (not place in im1 or len(place.out_arcs) == 0):
                net = utils.remove_place(net, place)
                continue

        # now the goal is to remove further places, but being carefully to not remove something structurally relevant

        for place in places_list:
            all_inputs = [arc.source for arc in place.in_arcs]
            hid_input = [trans for trans in all_inputs if trans.label is None and trans.name not in allowed_transitions]
            all_outputs = [arc.target for arc in place.out_arcs]
            hid_output = [trans for trans in all_outputs if
                          trans.label is None and trans.name not in allowed_transitions]

            if len(hid_input) == len(all_inputs) and len(hid_output) == len(all_outputs):
                net = utils.remove_place(net, place)
                continue

    im = Marking()
    fm = Marking()

    for place in im1:
        if place in net.places:
            im[place] = im1[place]

    for place in fm1:
        if place in net.places:
            fm[place] = fm1[place]

    return net, im, fm

from pm4py.objects.petri.petrinet import PetriNet, Marking
from pm4py.objects.petri.utils import add_arc_from_to


def project_net_on_place(place):
    """
    Project a Petri net on a place

    Parameters
    -------------
    place
        Place

    Returns
    -------------
    net
        (Place) net
    im
        Empty initial marking
    fm
        Empty final marking
    """
    place_net = PetriNet()
    place_net_im = Marking()
    place_net_fm = Marking()

    input_trans = [arc.source for arc in place.in_arcs]
    output_trans = [arc.target for arc in place.out_arcs]

    if len(input_trans) == 0 or len(output_trans) == 0:
        raise Exception("place projection not available on source/sink places")

    input_trans_visible = [trans for trans in input_trans if trans.label]
    output_trans_visible = [trans for trans in output_trans if trans.label]

    if not len(input_trans) == len(input_trans_visible) or not len(output_trans) == len(output_trans_visible):
        raise Exception("place projection not available on places that have invisible transitions as preset/postset")

    new_place = PetriNet.Place(place.name)
    place_net.places.add(new_place)

    for trans in input_trans:
        new_trans = PetriNet.Transition(trans.name, trans.label)
        place_net.transitions.add(new_trans)
        add_arc_from_to(new_trans, new_place, place_net)

    for trans in output_trans:
        new_trans = PetriNet.Transition(trans.name, trans.label)
        place_net.transitions.add(new_trans)
        add_arc_from_to(new_place, new_trans, place_net)

    return place_net, place_net_im, place_net_fm

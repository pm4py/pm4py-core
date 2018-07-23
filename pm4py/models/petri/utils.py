from pm4py.models.petri import instance as pn_instance


def add_arc_from_to(fr, to, net, weight=1):
    '''
    Adds an arc from a specific element to another element in some net. Assumes from and to are in the net!

    :param fr: transition/place from
    :param to:  transition/place to
    :param net: net to use
    :return: pass
    '''
    a = pn_instance.PetriNet.Arc(fr, to, weight)
    net.arcs.add(a)
    fr.out_arcs.add(a)
    to.in_arcs.add(a)
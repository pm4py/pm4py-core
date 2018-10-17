from pm4py.objects.petri.petrinet import Marking


def discover_initial_marking(petri):
    """
    Discovers initial marking from a Petri net

    Parameters
    ------------
    petri
        Petri net

    Returns
    ------------
    initial_marking
        Initial marking of the Petri net
    """
    initial_marking = Marking()

    for place in petri.places:
        if len(place.in_arcs) == 0:
            initial_marking[place] = 1

    return initial_marking

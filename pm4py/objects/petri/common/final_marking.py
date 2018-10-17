from pm4py.objects.petri.petrinet import Marking


def discover_final_marking(petri):
    """
    Discovers final marking from a Petri net

    Parameters
    -----------
    petri
        Petri net

    Returns
    -----------
    final_marking
        Final marking
    """
    final_marking = Marking()

    for place in petri.places:
        if len(place.out_arcs) == 0:
            final_marking[place] = 1

    return final_marking

from statistics import mean

def apply(petri_net, parameters=None):
    """
    Gets simplicity from a Petri net

    The approach is suggested in the paper
    Blum, Fabian Rojas. Metrics in process discovery. Technical Report TR/DCC-2015-6,
    Computer Science Department, University of Chile, 2015.

    Parameters
    -----------
    petri_net
        Petri net
    parameters
        Possible parameters of the algorithm

    Returns
    -----------
    simplicity
        Simplicity measure associated to the Petri net
    """
    if parameters is None:
        parameters = {}
    #str(parameters)
    #arc_degree = 0.0
    #if len(petri_net.transitions) > 0:
    #    arc_degree = float(len(petri_net.places)) / float(len(petri_net.transitions))
    #simplicity = 1.0 / (1.0 + arc_degree)

    # TODO: verify the real provenence of the approach before!

    all_arc_degrees = []
    for place in petri_net.places:
        all_arc_degrees.append(len(place.in_arcs) + len(place.out_arcs))
    for trans in petri_net.transitions:
        all_arc_degrees.append(len(trans.in_arcs) + len(trans.out_arcs))

    # original model: we have plenty of choices there.
    # one choice is about taking a model containing the most frequent variant,
    # along with a short circuit between the final and the initial marking.
    # in that case, the average arc degree of the "original model" is 2

    # or take as original model the one containing only the transitions, in that case
    # the average arc degree of the original model is 0.

    # let's stick with 2

    mean_degree = mean(all_arc_degrees) if all_arc_degrees else 0.0

    simplicity = 1.0 / (1.0 + max(mean_degree - 2, 0))

    return simplicity

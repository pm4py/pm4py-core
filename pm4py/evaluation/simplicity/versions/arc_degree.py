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
    str(parameters)
    arc_degree = 0.0
    if len(petri_net.transitions) > 0:
        arc_degree = float(len(petri_net.places)) / float(len(petri_net.transitions))
    simplicity = 1.0 / (1.0 + arc_degree)
    return simplicity

from pm4py.objects.conversion.heuristics_net.versions import to_petri_net

TO_PETRI_NET = "to_petri_net"

VERSIONS = {TO_PETRI_NET: to_petri_net.apply}


def apply(heu_net, parameters=None, variant=TO_PETRI_NET):
    """
    Converts an Heuristics Net to a different type of object

    Parameters
    --------------
    heu_net
        Heuristics net
    parameters
        Possible parameters of the algorithm
    variant
        Variant of the algorithm: to_petri_net
    """
    return VERSIONS[variant](heu_net, parameters=parameters)

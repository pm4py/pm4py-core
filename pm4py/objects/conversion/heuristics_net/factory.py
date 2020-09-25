from pm4py.objects.conversion.heuristics_net.versions import to_petri_net
import deprecation

TO_PETRI_NET = "to_petri_net"

VERSIONS = {TO_PETRI_NET: to_petri_net.apply}


@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Use algorithm entrypoint instead (conversion/heuristics_net/factory)')
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

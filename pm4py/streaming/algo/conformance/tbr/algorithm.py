from enum import Enum
from pm4py.util import exec_utils
from pm4py.streaming.algo.conformance.tbr.variants import classic


class Variants(Enum):
    CLASSIC = classic


def apply(net, im, fm, variant=Variants.CLASSIC, parameters=None):
    """
    Method that creates the TbrStreamingConformance object

    Parameters
    ----------------
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    variant
        Variant of the algorithm to use, possible:
            - Variants.CLASSIC
    parameters
        Parameters of the algorithm

    Returns
    ----------------
    conf_stream_obj
        Conformance streaming object
    """
    return exec_utils.get_variant(variant).apply(net, im, fm, parameters=parameters)

from enum import Enum
from pm4py.util import exec_utils
from pm4py.streaming.algo.conformance.footprints.variants import classic


class Variants(Enum):
    CLASSIC = classic


def apply(footprints, variant=Variants.CLASSIC, parameters=None):
    """
    Gets a footprints conformance checking object

    Parameters
    --------------
    footprints
        Footprints object (calculated from an entire log, from a process tree ...)
    variant
        Variant of the algorithm. Possible values: Variants.CLASSIC
    parameters
        Parameters of the algorithm

    Returns
    --------------
    fp_check_obj
        Footprints conformance checking object
    """
    return exec_utils.get_variant(variant).apply(footprints, parameters=parameters)

from pm4py.streaming.algo.discovery.dfg.variants import frequency
from enum import Enum
from pm4py.util import exec_utils


class Variants(Enum):
    FREQUENCY = frequency


DEFAULT_VARIANT = Variants.FREQUENCY


def apply(variant=DEFAULT_VARIANT, parameters=None):
    """
    Discovers a DFG from an event stream

    Parameters
    --------------
    variant
        Variant of the algorithm (default: Variants.FREQUENCY)

    Returns
    --------------
    stream_dfg_obj
        Streaming DFG discovery object
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(parameters=parameters)

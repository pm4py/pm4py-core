from pm4py.streaming.util.dictio.versions import classic
from enum import Enum
from pm4py.util import exec_utils


class Variants(Enum):
    CLASSIC = classic


DEFAULT_VARIANT = Variants.CLASSIC


def apply(variant=DEFAULT_VARIANT, parameters=None):
    """
    Generates a Python dictionary object
    (different implementations are possible)

    Parameters
    ----------------
    variant
        Variant to use
    parameters
        Parameters to use in the generation

    Returns
    -----------------
    dictio
        Dictionary
    """
    return exec_utils.get_variant(variant).apply(parameters=parameters)

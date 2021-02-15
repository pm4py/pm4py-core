from enum import Enum

from pm4py.streaming.util.dictio.versions import classic, thread_safe, redis
from pm4py.util import exec_utils


class Variants(Enum):
    CLASSIC = classic
    THREAD_SAFE = thread_safe
    REDIS = redis


DEFAULT_VARIANT = Variants.THREAD_SAFE


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

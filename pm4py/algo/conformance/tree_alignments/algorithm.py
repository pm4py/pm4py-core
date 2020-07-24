from pm4py.algo.conformance.tree_alignments.variants.approximated import algorithm as approximated
from pm4py.util import exec_utils
from enum import Enum


class Variants(Enum):
    APPROXIMATED = approximated


DEFAULT_VARIANT = Variants.APPROXIMATED


def apply(obj, pt, variant=DEFAULT_VARIANT, parameters=None):
    """
    Align an event log or a trace with a process tree

    Parameters
    --------------
    obj
        Log / Trace
    pt
        Process tree
    variant
        Variant
    parameters
        Variant-specific parameters

    Returns
    --------------
    alignments
        Alignments
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(obj, pt, parameters=parameters)

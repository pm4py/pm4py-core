from pm4py.algo.conformance.decomp_alignments.versions import recompos_maximal
from enum import Enum
from pm4py.util import exec_utils


class Variants(Enum):
    RECOMPOS_MAXIMAL = recompos_maximal


VERSIONS = {Variants.RECOMPOS_MAXIMAL}


def apply(log, net, im, fm, variant=Variants.RECOMPOS_MAXIMAL, parameters=None):
    """
    Apply the recomposition alignment approach
    to a log and a Petri net performing decomposition

    Parameters
    --------------
    log
        Event log
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    variant
        Variant of the algorithm, possible values:
            - Variants.RECOMPOS_MAXIMAL
    parameters
        Parameters of the algorithm

    Returns
    --------------
    aligned_traces
        For each trace, return its alignment
    """
    return exec_utils.get_variant(variant).apply(log, net, im, fm, parameters=parameters)

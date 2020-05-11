from pm4py.algo.discovery.causal.versions import alpha, heuristic
from enum import Enum
from pm4py.util import exec_utils


class Variants(Enum):
    CAUSAL_ALPHA = alpha
    CAUSAL_HEURISTIC = heuristic


CAUSAL_ALPHA = Variants.CAUSAL_ALPHA
CAUSAL_HEURISTIC = Variants.CAUSAL_HEURISTIC

VERSIONS = {CAUSAL_ALPHA, CAUSAL_HEURISTIC}


def apply(dfg, variant=CAUSAL_ALPHA):
    """
    Computes the causal relation on the basis of a given directly follows graph.

    Parameters
    -----------
    dfg
        Directly follows graph
    variant
        Variant of the algorithm to use:
            - Variants.CAUSAL_ALPHA
            - Variants.CAUSAL_HEURISTIC

    Returns
    -----------
    causal relations
        dict
    """
    return exec_utils.get_variant(variant).apply(dfg)

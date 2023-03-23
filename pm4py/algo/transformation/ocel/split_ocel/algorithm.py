from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any
from enum import Enum
from pm4py.algo.transformation.ocel.split_ocel.variants import connected_components, ancestors_descendants
from pm4py.util import exec_utils


class Variants(Enum):
    CONNECTED_COMPONENTS = connected_components
    ANCESTORS_DESCENDANTS = ancestors_descendants


def apply(ocel: OCEL, variant=Variants.CONNECTED_COMPONENTS, parameters: Optional[Dict[Any, Any]] = None):
    """
    Splits an OCEL into sub-OCELs using a given criteria (variant).

    Parameters
    ----------------
    ocel
        OCEL
    variant
        Variant of the algorithm to be used, possible values:
        - Variants.CONNECTED_COMPONENTS

    Returns
    ----------------
    splitted_ocel
        List of OCELs found based on the connected components
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(ocel, parameters)

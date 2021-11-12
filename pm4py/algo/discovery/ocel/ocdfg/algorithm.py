from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any
from pm4py.algo.discovery.ocel.ocdfg.variants import classic
from enum import Enum
from pm4py.util import exec_utils


class Variants(Enum):
    CLASSIC = classic


def apply(ocel: OCEL, variant=Variants.CLASSIC, parameters: Optional[Dict[Any, Any]] = None) -> Dict[str, Any]:
    """
    Discovers an OC-DFG model from an object-centric event log
    Reference paper:
    Berti, Alessandro, and Wil van der Aalst. "Extracting multiple viewpoint models from relational databases." Data-Driven Process Discovery and Analysis. Springer, Cham, 2018. 24-51.

    Parameters
    ----------------
    ocel
        Object-centric event log
    variant
        Variant of the algorithm to use:
        - Variants.CLASSIC
    parameters
        Variant-specific parameters

    Returns
    ----------------
    ocdfg
        Object-centric directly-follows graph
    """
    return exec_utils.get_variant(variant).apply(ocel, parameters)

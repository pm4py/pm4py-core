from enum import Enum
from pm4py.algo.discovery.ocel.ocpn.variants import classic
from pm4py.objects.ocel.obj import OCEL
from pm4py.util import exec_utils
from typing import Optional, Dict, Any


class Variants(Enum):
    WO_ANNOTATION = classic
    CLASSIC = classic


def apply(ocel: OCEL, variant=Variants.CLASSIC, parameters: Optional[Dict[Any, Any]] = None) -> Dict[str, Any]:
    """
    Discovers an object-centric Petri net from the provided object-centric event log.

    Reference paper: van der Aalst, Wil MP, and Alessandro Berti. "Discovering object-centric Petri nets." Fundamenta informaticae 175.1-4 (2020): 1-40.

    Parameters
    -----------------
    ocel
        Object-centric event log
    variant
        Variant of the algorithm to be used
    parameters
        Variant-specific parameters

    Returns
    ----------------
    ocpn
        Object-centric Petri net model, as a dictionary of properties.
    """
    return exec_utils.get_variant(variant).apply(ocel, parameters=parameters)

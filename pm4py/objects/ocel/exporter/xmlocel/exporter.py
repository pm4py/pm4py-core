from enum import Enum
from typing import Optional, Dict, Any

from pm4py.objects.ocel.exporter.xmlocel.variants import classic, ocel20
from pm4py.objects.ocel.obj import OCEL
from pm4py.util import exec_utils


class Variants(Enum):
    CLASSIC = classic
    OCEL20 = ocel20


def apply(ocel: OCEL, target_path: str, variant=Variants.CLASSIC, parameters: Optional[Dict[Any, Any]] = None):
    """
    Exports an object-centric event log to a XML-OCEL file.

    Parameters
    -----------------
    ocel
        Object-centric event log
    target_path
        Destination path
    variant
        Variant of the algorithm to use, possible values:
        - Variants.CLASSIC
    parameters
        Variant-specific parameters
    """
    return exec_utils.get_variant(variant).apply(ocel, target_path, parameters)

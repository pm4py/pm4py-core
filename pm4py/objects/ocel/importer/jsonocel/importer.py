from enum import Enum
from typing import Optional, Dict, Any

from pm4py.objects.ocel.importer.jsonocel.variants import classic, ocel20_standard
from pm4py.objects.ocel.obj import OCEL
from pm4py.util import exec_utils


class Variants(Enum):
    CLASSIC = classic
    OCEL20_STANDARD = ocel20_standard


def apply(file_path: str, variant=Variants.CLASSIC, parameters: Optional[Dict[Any, Any]] = None) -> OCEL:
    """
    Imports an object-centric event log from a JSON-OCEL file

    Parameters
    -----------------
    file_path
        Path to the JSON-OCEL file
    variant
        Variant of the algorithm to use, possible values:
        - Variants.CLASSIC
    parameters
        Variant-specific parameters

    Returns
    ------------------
    ocel
        Object-centric event log
    """
    return exec_utils.get_variant(variant).apply(file_path, parameters)

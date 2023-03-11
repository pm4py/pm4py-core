from enum import Enum
from pm4py.util import exec_utils
from pm4py.objects.ocel.exporter.sqlite.variants import pandas_exporter, ocel20
from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any


class Variants(Enum):
    PANDAS_EXPORTER = pandas_exporter
    OCEL20 = ocel20


def apply(ocel: OCEL, target_path: str, variant=Variants.PANDAS_EXPORTER, parameters: Optional[Dict[Any, Any]] = None):
    """
    Exports an OCEL to a SQLite database

    Parameters
    -------------
    ocel
        Object-centric event log
    target_path
        Path to the SQLite database
    variant
        Variant to use. Possible values:
        - Variants.PANDAS_EXPORTER => Pandas exporter
    parameters
        Variant-specific parameters
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(ocel, target_path, parameters=parameters)

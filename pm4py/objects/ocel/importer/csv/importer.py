from enum import Enum
from typing import Optional, Dict, Any

from pm4py.objects.ocel.importer.csv.variants import pandas
from pm4py.objects.ocel.obj import OCEL
from pm4py.util import exec_utils


class Variants(Enum):
    PANDAS = pandas


def apply(file_path: str, objects_path: str = None, variant=Variants.PANDAS,
          parameters: Optional[Dict[Any, Any]] = None) -> OCEL:
    """
    Imports an object-centric event log from a CSV file

    Parameters
    -----------------
    file_path
        Path to the object-centric event log
    objects_path
        Optional path to a CSV file containing the objects dataframe
    variant
        Variant of the algorithm that should be used, possible values:
        - Variants.PANDAS
    parameters
        Parameters of the algorithm

    Returns
    ------------------
    ocel
        Object-centric event log
    """
    return exec_utils.get_variant(variant).apply(file_path, objects_path, parameters)

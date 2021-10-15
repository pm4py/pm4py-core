from enum import Enum
from typing import Optional, Dict, Any

from pm4py.objects.ocel.exporter.csv.variants import pandas
from pm4py.objects.ocel.obj import OCEL
from pm4py.util import exec_utils


class Variants(Enum):
    PANDAS = pandas


def apply(ocel: OCEL, output_path: str, variant=Variants.PANDAS, objects_path=None,
          parameters: Optional[Dict[Any, Any]] = None):
    """
    Exports an object-centric event log in a CSV file

    Parameters
    -----------------
    ocel
        Object-centric event log
    output_path
        Destination file
    variant
        Variant of the algorithm that should be used, possible values:
        - Variants.PANDAS
    objects_path
        Optional path, where the objects dataframe is stored
    parameters
        Parameters of the algorithm
    """
    return exec_utils.get_variant(variant).apply(ocel, output_path, objects_path=objects_path, parameters=parameters)

from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any
from pm4py.objects.ocel.util import ocel_consistency


def apply(ocel: OCEL, output_path: str, objects_path=None, parameters: Optional[Dict[Any, Any]] = None):
    """
    Exports an object-centric event log in a CSV file, using Pandas as backend

    Parameters
    -----------------
    ocel
        Object-centric event log
    output_path
        Destination file
    objects_path
        Optional path, where the objects dataframe is stored
    parameters
        Parameters of the algorithm
    """
    if parameters is None:
        parameters = {}

    ocel = ocel_consistency.apply(ocel, parameters=parameters)

    ocel.get_extended_table().to_csv(output_path, index=False, na_rep="")

    if objects_path is not None:
        ocel.objects.to_csv(objects_path, index=False, na_rep="")

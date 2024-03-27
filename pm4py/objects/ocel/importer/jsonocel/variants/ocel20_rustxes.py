from typing import Optional, Dict, Any
from pm4py.objects.ocel.obj import OCEL


def apply(file_path: str, parameters: Optional[Dict[Any, Any]] = None) -> OCEL:
    """
    Imports an OCEL 2.0 JSON using the RUSTXES parser.

    Parameters
    ---------------
    file_path
        Path to the OCEL 2.0 JSON
    parameters
        Optional parameters.

    Returns
    ---------------
    ocel
        Object-centric event log
    """
    if parameters is None:
        parameters = {}

    import rustxes

    return rustxes.import_ocel_json_pm4py(file_path)

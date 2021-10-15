from typing import Optional, Dict, Any, List

from pm4py.objects.ocel import constants
from pm4py.objects.ocel.obj import OCEL


def get_attribute_names(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None) -> List[str]:
    """
    Gets the list of attributes at the event and the object level of an object-centric event log
    (e.g. ["cost", "amount", "name"])

    Parameters
    -------------------
    ocel
        Object-centric event log
    parameters
        Parameters of the algorithm

    Returns
    -------------------
    attributes_list
        List of attributes at the event and object level (e.g. ["cost", "amount", "name"])
    """
    if parameters is None:
        parameters = {}

    attributes = sorted(set(x for x in ocel.events.columns if not x.startswith(constants.OCEL_PREFIX)).union(
        x for x in ocel.objects.columns if not x.startswith(constants.OCEL_PREFIX)))

    return attributes

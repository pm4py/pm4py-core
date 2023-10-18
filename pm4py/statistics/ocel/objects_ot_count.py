from enum import Enum
from pm4py.util import exec_utils
from pm4py.objects.ocel import constants as ocel_constants
from collections import Counter
from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any


class Parameters(Enum):
    EVENT_ID = ocel_constants.PARAM_EVENT_ID
    OBJECT_ID = ocel_constants.PARAM_OBJECT_ID
    OBJECT_TYPE = ocel_constants.PARAM_OBJECT_TYPE


def get_objects_ot_count(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None) -> Dict[str, Dict[str, int]]:
    """
    Counts for each event the number of related objects per type

    Parameters
    -------------------
    ocel
        Object-centric Event log
    parameters
        Parameters of the algorithm, including:
        - Parameters.EVENT_ID => the event identifier to be used
        - Parameters.OBJECT_ID => the object identifier to be used
        - Parameters.OBJECT_TYPE => the object type to be used

    Returns
    -------------------
    dict_ot
        Dictionary associating to each event identifier a dictionary with the number of related objects
    """
    if parameters is None:
        parameters = {}

    event_id = exec_utils.get_param_value(Parameters.EVENT_ID, parameters, ocel.event_id_column)
    object_id = exec_utils.get_param_value(Parameters.OBJECT_ID, parameters, ocel.object_id_column)
    object_type = exec_utils.get_param_value(Parameters.OBJECT_TYPE, parameters, ocel.object_type_column)

    ref0 = ocel.relations.groupby(event_id)[object_type].agg(list).to_dict()
    ref = {x: Counter(y) for x, y in ref0.items()}

    return ref

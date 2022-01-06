from enum import Enum
from pm4py.util import exec_utils
from pm4py.objects.ocel.obj import OCEL
from pm4py.objects.ocel import constants as ocel_constants
from typing import Optional, Dict, Any


class Parameters(Enum):
    EVENT_ID = ocel_constants.PARAM_EVENT_ID
    OBJECT_TYPE = ocel_constants.PARAM_OBJECT_TYPE


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None):
    """
    Returns for each object type the number of events related to at least one object of the given type.

    Parameters
    ----------------
    ocel
        Object-centric event log
    parameters
        Parameters of the algorithm, including:
        - Parameters.EVENT_ID => the event identifier
        - Parameters.OBJECT_TYPE => the object type column

    Returns
    -----------------
    dictio
        Dictionary associating to each object type the number of events related to at least one object of the given
        type.
    """
    if parameters is None:
        parameters = {}

    event_id = exec_utils.get_param_value(Parameters.EVENT_ID, parameters, ocel.event_id_column)
    object_type = exec_utils.get_param_value(Parameters.OBJECT_TYPE, parameters, ocel.object_type_column)

    object_types = set(ocel.objects[object_type].unique())

    ret = {}

    for ot in object_types:
        ret[ot] = ocel.relations[ocel.relations[object_type] == ot][event_id].nunique()

    return ret

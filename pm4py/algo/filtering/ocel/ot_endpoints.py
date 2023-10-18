from enum import Enum
from pm4py.util import exec_utils
from pm4py.objects.ocel import constants as ocel_constants
from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any
from copy import copy
from pm4py.objects.ocel.util import filtering_utils


class Parameters(Enum):
    EVENT_ID = ocel_constants.PARAM_EVENT_ID
    OBJECT_ID = ocel_constants.PARAM_OBJECT_ID
    OBJECT_TYPE = ocel_constants.PARAM_OBJECT_TYPE


def filter_start_events_per_object_type(ocel: OCEL, object_type: str, parameters: Optional[Dict[Any, Any]] = None) -> OCEL:
    """
    Filters the events in which a new object for the given object type is spawn.
    (E.g. an event with activity "Create Order" might spawn new orders).

    Parameters
    ------------------
    ocel
        Object-centric event log
    object_type
        Object type to consider
    parameters
        Parameters of the algorithm, including:
        - Parameters.EVENT_ID => the attribute working as event identifier
        - Parameters.OBJECT_ID => the attribute working as object identifier
        - Parameters.OBJECT_TYPE => the attribute working as object type

    Returns
    ------------------
    filtered_ocel
        Filtered object-centric event log
    """
    if parameters is None:
        parameters = {}

    event_id = exec_utils.get_param_value(Parameters.EVENT_ID, parameters, ocel.event_id_column)
    object_id = exec_utils.get_param_value(Parameters.OBJECT_ID, parameters, ocel.object_id_column)
    object_type_column = exec_utils.get_param_value(Parameters.OBJECT_TYPE, parameters, ocel.object_type_column)

    evs = set(ocel.relations[ocel.relations[object_type_column] == object_type].groupby(object_id).first()[event_id].unique())

    ocel = copy(ocel)
    ocel.events = ocel.events[ocel.events[event_id].isin(evs)]

    return filtering_utils.propagate_event_filtering(ocel, parameters=parameters)


def filter_end_events_per_object_type(ocel: OCEL, object_type: str, parameters: Optional[Dict[Any, Any]] = None) -> OCEL:
    """
    Filters the events in which an object for the given object type terminates its lifecycle.
    (E.g. an event with activity "Pay Order" might terminate an order).

    Parameters
    ------------------
    ocel
        Object-centric event log
    object_type
        Object type to consider
    parameters
        Parameters of the algorithm, including:
        - Parameters.EVENT_ID => the attribute working as event identifier
        - Parameters.OBJECT_ID => the attribute working as object identifier
        - Parameters.OBJECT_TYPE => the attribute working as object type

    Returns
    ------------------
    filtered_ocel
        Filtered object-centric event log
    """
    if parameters is None:
        parameters = {}

    event_id = exec_utils.get_param_value(Parameters.EVENT_ID, parameters, ocel.event_id_column)
    object_id = exec_utils.get_param_value(Parameters.OBJECT_ID, parameters, ocel.object_id_column)
    object_type_column = exec_utils.get_param_value(Parameters.OBJECT_TYPE, parameters, ocel.object_type_column)

    evs = set(ocel.relations[ocel.relations[object_type_column] == object_type].groupby(object_id).last()[event_id].unique())

    ocel = copy(ocel)
    ocel.events = ocel.events[ocel.events[event_id].isin(evs)]

    return filtering_utils.propagate_event_filtering(ocel, parameters=parameters)

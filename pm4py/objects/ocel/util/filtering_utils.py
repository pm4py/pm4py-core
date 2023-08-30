from pm4py.objects.ocel import constants
from enum import Enum
from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any
from pm4py.util import exec_utils


class Parameters(Enum):
    EVENT_ID = constants.PARAM_EVENT_ID
    OBJECT_ID = constants.PARAM_OBJECT_ID
    OBJECT_TYPE = constants.PARAM_OBJECT_TYPE


def propagate_event_filtering(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None) -> OCEL:
    """
    Propagates the filtering at the event level to the remaining parts of the OCEL structure
    (objects, relations)

    Parameters
    ----------------
    ocel
        Object-centric event log
    parameters
        Parameters of the algorithm, including:
        - Parameters.EVENT_ID => the column to be used as case identifier
        - Parameters.OBJECT_ID => the column to be used as object identifier
        - Parameters.OBJECT_TYPE => the column to be used as object type

    Returns
    ----------------
    ocel
        Object-centric event log with propagated filter
    """
    if parameters is None:
        parameters = {}

    event_id = exec_utils.get_param_value(Parameters.EVENT_ID, parameters, ocel.event_id_column)
    object_id = exec_utils.get_param_value(Parameters.OBJECT_ID, parameters, ocel.object_id_column)

    selected_event_ids = set(ocel.events[event_id].unique())
    ocel.relations = ocel.relations[ocel.relations[event_id].isin(selected_event_ids)]
    selected_object_ids = set(ocel.relations[object_id].unique())
    ocel.objects = ocel.objects[ocel.objects[object_id].isin(selected_object_ids)]

    ocel.e2e = ocel.e2e[(ocel.e2e[event_id].isin(selected_event_ids)) & (ocel.e2e[event_id+"_2"].isin(selected_event_ids))]
    ocel.o2o = ocel.o2o[(ocel.o2o[object_id].isin(selected_object_ids)) & (ocel.o2o[object_id+"_2"].isin(selected_object_ids))]

    ocel.object_changes = ocel.object_changes[ocel.object_changes[object_id].isin(selected_object_ids)]

    return ocel


def propagate_object_filtering(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None) -> OCEL:
    """
    Propagates the filtering at the object level to the remaining parts of the OCEL structure
    (events, relations)

    Parameters
    ----------------
    ocel
        Object-centric event log
    parameters
        Parameters of the algorithm, including:
        - Parameters.EVENT_ID => the column to be used as case identifier
        - Parameters.OBJECT_ID => the column to be used as object identifier
        - Parameters.OBJECT_TYPE => the column to be used as object type

    Returns
    ----------------
    ocel
        Object-centric event log with propagated filter
    """
    if parameters is None:
        parameters = {}

    event_id = exec_utils.get_param_value(Parameters.EVENT_ID, parameters, ocel.event_id_column)
    object_id = exec_utils.get_param_value(Parameters.OBJECT_ID, parameters, ocel.object_id_column)

    selected_object_ids = set(ocel.objects[object_id].unique())
    ocel.relations = ocel.relations[ocel.relations[object_id].isin(selected_object_ids)]
    selected_event_ids = set(ocel.relations[event_id].unique())
    ocel.events = ocel.events[ocel.events[event_id].isin(selected_event_ids)]

    ocel.e2e = ocel.e2e[(ocel.e2e[event_id].isin(selected_event_ids)) & (ocel.e2e[event_id+"_2"].isin(selected_event_ids))]
    ocel.o2o = ocel.o2o[(ocel.o2o[object_id].isin(selected_object_ids)) & (ocel.o2o[object_id+"_2"].isin(selected_object_ids))]

    ocel.object_changes = ocel.object_changes[ocel.object_changes[object_id].isin(selected_object_ids)]

    return ocel


def propagate_relations_filtering(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None) -> OCEL:
    """
    Propagates the filtering at the relations level to the remaining parts of the OCEL structure
    (events, objects)

    Parameters
    ----------------
    ocel
        Object-centric event log
    parameters
        Parameters of the algorithm, including:
        - Parameters.EVENT_ID => the column to be used as case identifier
        - Parameters.OBJECT_ID => the column to be used as object identifier
        - Parameters.OBJECT_TYPE => the column to be used as object type

    Returns
    ----------------
    ocel
        Object-centric event log with propagated filter
    """
    if parameters is None:
        parameters = {}

    event_id = exec_utils.get_param_value(Parameters.EVENT_ID, parameters, ocel.event_id_column)
    object_id = exec_utils.get_param_value(Parameters.OBJECT_ID, parameters, ocel.object_id_column)

    selected_event_ids = set(ocel.relations[event_id].unique()).intersection(set(ocel.events[event_id].unique()))
    selected_object_ids = set(ocel.relations[object_id].unique()).intersection(set(ocel.objects[object_id].unique()))
    ocel.events = ocel.events[ocel.events[event_id].isin(selected_event_ids)]
    ocel.objects = ocel.objects[ocel.objects[object_id].isin(selected_object_ids)]
    ocel.relations = ocel.relations[ocel.relations[event_id].isin(selected_event_ids)]
    ocel.relations = ocel.relations[ocel.relations[object_id].isin(selected_object_ids)]

    ocel.e2e = ocel.e2e[(ocel.e2e[event_id].isin(selected_event_ids)) & (ocel.e2e[event_id+"_2"].isin(selected_event_ids))]
    ocel.o2o = ocel.o2o[(ocel.o2o[object_id].isin(selected_object_ids)) & (ocel.o2o[object_id+"_2"].isin(selected_object_ids))]

    ocel.object_changes = ocel.object_changes[ocel.object_changes[object_id].isin(selected_object_ids)]

    return ocel

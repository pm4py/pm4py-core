from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any
from enum import Enum
from pm4py.util import exec_utils
from pm4py.algo.transformation.ocel.features.events import event_activity, event_num_rel_objs, event_num_rel_objs_type, event_timestamp, event_str_attributes, event_num_attributes, event_start_ot, event_end_ot


class Parameters(Enum):
    ENABLE_ALL = "enable_all"
    ENABLE_EVENT_ACTIVITY = "enable_event_activity"
    ENABLE_EVENT_TIMESTAMP = "enable_event_timestamp"
    ENABLE_EVENT_NUM_REL_OBJS = "enable_event_num_rel_objs"
    ENABLE_EVENT_NUM_REL_OBJS_TYPE = "enable_event_num_rel_objs_type"
    ENABLE_EVENT_STR_ATTRIBUTES = "enable_event_str_attributes"
    ENABLE_EVENT_NUM_ATTRIBUTES = "enable_event_num_attributes"
    ENABLE_EVENT_START_OT = "enable_event_start_ot"
    ENABLE_EVENT_END_OT = "enable_event_end_ot"


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None):
    """
    Extracts a feature table related to the events of an OCEL

    Parameters
    ---------------
    ocel
        Object-centric event log
    parameters
        Parameters for extracting the feature table, including:
        - Parameters.ENABLE_ALL => enables all the belowmentioned features
        - Parameters.ENABLE_EVENT_ACTIVITY => enables the one-hot-encoding of the activities of the event
        - Parameters.ENABLE_EVENT_TIMESTAMP => enables the encoding of the timestamp of the event as feature
        - Parameters.ENABLE_EVENT_NUM_REL_OBJS => enables the "overall number of related objects" feature
        - Parameters.ENABLE_EVENT_NUM_REL_OBJS_TYPE => enables the "number of related objects per type" feature
        - Parameters.ENABLE_EVENT_STR_ATTRIBUTES => enables the one-hot-encoding of a given collection of string event
                                                    attributes (specified inside the "str_ev_attr" parameter)
        - Parameters.ENABLE_EVENT_NUM_ATTRIBUTES => enables the extraction of a given collection of numeric event
                                                    attributes in the feature table
        - Parameters.ENABLE_EVENT_START_OT => calculates some features which establish if the event starts the
                                                lifecycle of some objects of a type.
        - Parameters.ENABLE_EVENT_END_OT => calculates some features which establish if the event completes the
                                                lifecycle of some objects of a type.

    Returns
    ------------------
    data
        Values of the features
    feature_names
        Names of the features
    """
    if parameters is None:
        parameters = {}

    enable_all = exec_utils.get_param_value(Parameters.ENABLE_ALL, parameters, True)
    enable_event_activity = exec_utils.get_param_value(Parameters.ENABLE_EVENT_ACTIVITY, parameters, enable_all)
    enable_event_timestamp = exec_utils.get_param_value(Parameters.ENABLE_EVENT_TIMESTAMP, parameters, enable_all)
    enable_event_num_rel_objs = exec_utils.get_param_value(Parameters.ENABLE_EVENT_NUM_REL_OBJS, parameters, enable_all)
    enable_event_num_rel_objs_type = exec_utils.get_param_value(Parameters.ENABLE_EVENT_NUM_REL_OBJS_TYPE, parameters, enable_all)
    enable_event_str_attributes = exec_utils.get_param_value(Parameters.ENABLE_EVENT_STR_ATTRIBUTES, parameters, enable_all)
    enable_event_num_attributes = exec_utils.get_param_value(Parameters.ENABLE_EVENT_NUM_ATTRIBUTES, parameters, enable_all)
    enable_event_start_ot = exec_utils.get_param_value(Parameters.ENABLE_EVENT_START_OT, parameters, enable_all)
    enable_event_end_ot = exec_utils.get_param_value(Parameters.ENABLE_EVENT_END_OT, parameters, enable_all)

    ordered_events = list(ocel.events[ocel.event_id_column])

    datas = [[] for x in ordered_events]
    feature_namess = []

    if enable_event_activity:
        data, feature_names = event_activity.apply(ocel, parameters=parameters)
        feature_namess = feature_namess + feature_names
        for i in range(len(data)):
            datas[i] = datas[i] + data[i]

    if enable_event_timestamp:
        data, feature_names = event_timestamp.apply(ocel, parameters=parameters)
        feature_namess = feature_namess + feature_names
        for i in range(len(data)):
            datas[i] = datas[i] + data[i]

    if enable_event_num_rel_objs:
        data, feature_names = event_num_rel_objs.apply(ocel, parameters=parameters)
        feature_namess = feature_namess + feature_names
        for i in range(len(data)):
            datas[i] = datas[i] + data[i]

    if enable_event_num_rel_objs_type:
        data, feature_names = event_num_rel_objs_type.apply(ocel, parameters=parameters)
        feature_namess = feature_namess + feature_names
        for i in range(len(data)):
            datas[i] = datas[i] + data[i]

    if enable_event_str_attributes:
        data, feature_names = event_str_attributes.apply(ocel, parameters=parameters)
        feature_namess = feature_namess + feature_names
        for i in range(len(data)):
            datas[i] = datas[i] + data[i]

    if enable_event_num_attributes:
        data, feature_names = event_num_attributes.apply(ocel, parameters=parameters)
        feature_namess = feature_namess + feature_names
        for i in range(len(data)):
            datas[i] = datas[i] + data[i]

    if enable_event_start_ot:
        data, feature_names = event_start_ot.apply(ocel, parameters=parameters)
        feature_namess = feature_namess + feature_names
        for i in range(len(data)):
            datas[i] = datas[i] + data[i]

    if enable_event_end_ot:
        data, feature_names = event_end_ot.apply(ocel, parameters=parameters)
        feature_namess = feature_namess + feature_names
        for i in range(len(data)):
            datas[i] = datas[i] + data[i]

    return datas, feature_namess

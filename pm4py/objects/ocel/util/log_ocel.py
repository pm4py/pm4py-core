'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
from enum import Enum
from pm4py.objects.log.obj import EventLog, EventStream
import pandas as pd
from typing import Optional, Dict, Any, Collection, Union
from pm4py.util import exec_utils, constants, xes_constants
from pm4py.objects.ocel.obj import OCEL
from pm4py.objects.ocel import constants as ocel_constants
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.ocel.util import ocel_consistency
from copy import copy


class Parameters(Enum):
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    CASE_ATTRIBUTE_PREFIX = constants.PARAMETER_KEY_CASE_ATTRIBUTE_PRFIX
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    TARGET_OBJECT_TYPE = "target_object_type"
    TARGET_OBJECT_TYPE_2 = "target_object_type_2"
    LEFT_INDEX = "left_index"
    RIGHT_INDEX = "right_index"
    DIRECTION = "direction"


def from_traditional_log(log: EventLog, parameters: Optional[Dict[Any, Any]] = None) -> OCEL:
    """
    Transforms an EventLog to an OCEL

    Parameters
    -----------------
    log
        Event log
    parameters
        Parameters of the algorithm, including:
        - Parameters.TARGET_OBJECT_TYPE => the name of the object type to which the cases should be mapped
        - Parameters.ACTIVITY_KEY => the attribute to use as activity
        - Parameters.TIMESTAMP_KEY => the attribute to use as timestamp
        - Parameters.CASE_ID_KEY => the attribute to use as case identifier

    Returns
    -----------------
    ocel
        OCEL (equivalent to the provided event log)
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    target_object_type = exec_utils.get_param_value(Parameters.TARGET_OBJECT_TYPE, parameters, "OTYPE")
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, xes_constants.DEFAULT_TRACEID_KEY)

    events = []
    objects = []
    relations = []

    ev_count = 0
    for trace in log:
        case_id = trace.attributes[case_id_key]
        obj = {ocel_constants.DEFAULT_OBJECT_ID: case_id, ocel_constants.DEFAULT_OBJECT_TYPE: target_object_type}
        for attr in trace.attributes:
            if attr != case_id_key:
                obj[attr] = trace.attributes[attr]
        objects.append(obj)
        for ev in trace:
            ev_count = ev_count + 1
            activity = ev[activity_key]
            timestamp = ev[timestamp_key]
            eve = {ocel_constants.DEFAULT_EVENT_ID: str(ev_count), ocel_constants.DEFAULT_EVENT_ACTIVITY: activity,
                   ocel_constants.DEFAULT_EVENT_TIMESTAMP: timestamp}
            for attr in ev:
                if attr not in [activity, timestamp]:
                    eve[attr] = ev[attr]
            events.append(eve)
            relations.append(
                {ocel_constants.DEFAULT_EVENT_ID: str(ev_count), ocel_constants.DEFAULT_EVENT_ACTIVITY: activity,
                 ocel_constants.DEFAULT_EVENT_TIMESTAMP: timestamp, ocel_constants.DEFAULT_OBJECT_ID: case_id,
                 ocel_constants.DEFAULT_OBJECT_TYPE: target_object_type})

    events = pd.DataFrame(events)
    objects = pd.DataFrame(objects)
    relations = pd.DataFrame(relations)

    return OCEL(events=events, objects=objects, relations=relations)


def __get_events_dataframe(df: pd.DataFrame, activity_key: str, timestamp_key: str, case_id_key: str,
                           case_attribute_prefix: str, events_prefix="E") -> pd.DataFrame:
    """
    Internal method to get the events dataframe out of a traditional log stored as Pandas dataframe
    """
    columns = {case_id_key}.union(set(x for x in df.columns if not x.startswith(case_attribute_prefix)))
    df = df[columns]
    df = df.rename(columns={activity_key: ocel_constants.DEFAULT_EVENT_ACTIVITY,
                            timestamp_key: ocel_constants.DEFAULT_EVENT_TIMESTAMP,
                            case_id_key: ocel_constants.DEFAULT_OBJECT_ID})
    df[ocel_constants.DEFAULT_EVENT_ID] = events_prefix + df.index.astype(str)
    return df


def __get_objects_dataframe(df: pd.DataFrame, case_id_key: str, case_attribute_prefix: str,
                            target_object_type: str) -> pd.DataFrame:
    """
    Internal method to get the objects dataframe out of a traditional log stored as Pandas dataframe
    """
    columns = {x for x in df.columns if x.startswith(case_attribute_prefix)}
    df = df[columns]
    df = df.rename(columns={case_id_key: ocel_constants.DEFAULT_OBJECT_ID})
    df = df.groupby(ocel_constants.DEFAULT_OBJECT_ID).first().reset_index()
    df[ocel_constants.DEFAULT_OBJECT_TYPE] = target_object_type
    return df


def __get_relations_from_events(events: pd.DataFrame, target_object_type: str) -> pd.DataFrame:
    """
    Internal method to get the relations dataframe out of a traditional log stored as Pandas dataframe
    """
    relations = events[[ocel_constants.DEFAULT_EVENT_ACTIVITY, ocel_constants.DEFAULT_EVENT_TIMESTAMP,
                        ocel_constants.DEFAULT_OBJECT_ID, ocel_constants.DEFAULT_EVENT_ID]]
    relations[ocel_constants.DEFAULT_OBJECT_TYPE] = target_object_type
    return relations


def from_traditional_pandas(df: pd.DataFrame, parameters: Optional[Dict[Any, Any]] = None) -> OCEL:
    """
    Transforms a dataframe to an OCEL

    Parameters
    -----------------
    df
        Pandas dataframe
    parameters
        Parameters of the algorithm, including:
        - Parameters.TARGET_OBJECT_TYPE => the name of the object type to which the cases should be mapped
        - Parameters.ACTIVITY_KEY => the attribute to use as activity
        - Parameters.TIMESTAMP_KEY => the attribute to use as timestamp
        - Parameters.CASE_ID_KEY => the attribute to use as case identifier
        - Parameters.CASE_ATTRIBUTE_PREFIX => the prefix identifying the attributes at the case level

    Returns
    -----------------
    ocel
        OCEL (equivalent to the provided event log)
    """
    if parameters is None:
        parameters = {}

    target_object_type = exec_utils.get_param_value(Parameters.TARGET_OBJECT_TYPE, parameters, "OTYPE")
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
    case_attribute_prefix = exec_utils.get_param_value(Parameters.CASE_ATTRIBUTE_PREFIX, parameters,
                                                       constants.CASE_ATTRIBUTE_PREFIX)

    events = __get_events_dataframe(df, activity_key, timestamp_key, case_id_key, case_attribute_prefix)
    objects = __get_objects_dataframe(df, case_id_key, case_attribute_prefix, target_object_type)
    relations = __get_relations_from_events(events, target_object_type)
    del events[ocel_constants.DEFAULT_OBJECT_ID]

    events = events.sort_values([ocel_constants.DEFAULT_EVENT_TIMESTAMP, ocel_constants.DEFAULT_EVENT_ID])
    relations = relations.sort_values([ocel_constants.DEFAULT_EVENT_TIMESTAMP, ocel_constants.DEFAULT_EVENT_ID])

    return OCEL(events=events, objects=objects, relations=relations)


def from_interleavings(df1: pd.DataFrame, df2: pd.DataFrame, interleavings: pd.DataFrame,
                       parameters: Optional[Dict[Any, Any]] = None) -> OCEL:
    """
    Transforms a couple of dataframes, along with the interleavings between them, to an OCEL

    Parameters
    -----------------
    df1
        First of the two dataframes
    df2
        Second of the two dataframes
    interleavings
        Interleavings dataframe
    parameters
        Parameters of the algorithm, including:
        - Parameters.ACTIVITY_KEY => the attribute to use as activity
        - Parameters.TIMESTAMP_KEY => the attribute to use as timestamp
        - Parameters.CASE_ID_KEY => the attribute to use as case identifier
        - Parameters.CASE_ATTRIBUTE_PREFIX => the prefix identifying the attributes at the case level
        - Parameters.TARGET_OBJECT_TYPE => the name of the object type to which the cases of the first log should be mapped
        - Parameters.TARGET_OBJECT_TYPE_2 => the name of the object type to which the cases of the second log should be mapped
        - Parameters.LEFT_INDEX => the index column of the events of the first dataframe, in the interleavings dataframe
        - Parameters.RIGHT_INDEX => the index column of the events of the second dataframe, in the interleavings
                                    dataframe.
        - Parameters.DIRECTION => the direction of the interleavings (LR or RL)

    Returns
    -----------------
    ocel
        OCEL (equivalent to the provided event log)
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
    case_attribute_prefix = exec_utils.get_param_value(Parameters.CASE_ATTRIBUTE_PREFIX, parameters,
                                                       constants.CASE_ATTRIBUTE_PREFIX)
    target_object_type = exec_utils.get_param_value(Parameters.TARGET_OBJECT_TYPE, parameters, "OTYPE")
    target_object_type_2 = exec_utils.get_param_value(Parameters.TARGET_OBJECT_TYPE_2, parameters, "OTYPE2")
    left_index = exec_utils.get_param_value(Parameters.LEFT_INDEX, parameters, "@@left_index")
    right_index = exec_utils.get_param_value(Parameters.RIGHT_INDEX, parameters, "@@right_index")
    direction = exec_utils.get_param_value(Parameters.DIRECTION, parameters, "@@direction")

    events1 = __get_events_dataframe(df1, activity_key, timestamp_key, case_id_key, case_attribute_prefix,
                                     events_prefix="E1_")
    objects1 = __get_objects_dataframe(df1, case_id_key, case_attribute_prefix, target_object_type)
    relations1 = __get_relations_from_events(events1, target_object_type)

    relations1_minimal = relations1[
        {ocel_constants.DEFAULT_EVENT_ID, ocel_constants.DEFAULT_OBJECT_ID, ocel_constants.DEFAULT_OBJECT_TYPE}]

    events2 = __get_events_dataframe(df2, activity_key, timestamp_key, case_id_key, case_attribute_prefix,
                                     events_prefix="E2_")
    objects2 = __get_objects_dataframe(df2, case_id_key, case_attribute_prefix, target_object_type_2)
    relations2 = __get_relations_from_events(events2, target_object_type_2)
    relations2_minimal = relations2[
        {ocel_constants.DEFAULT_EVENT_ID, ocel_constants.DEFAULT_OBJECT_ID, ocel_constants.DEFAULT_OBJECT_TYPE}]

    interleavings[left_index] = "E1_" + interleavings[left_index].astype(int).astype(str)
    interleavings[right_index] = "E2_" + interleavings[right_index].astype(int).astype(str)
    interleavings_lr = interleavings[interleavings[direction] == "LR"][[left_index, right_index]]
    interleavings_rl = interleavings[interleavings[direction] == "RL"][[left_index, right_index]]

    relations3 = events1.merge(interleavings_lr, left_on=ocel_constants.DEFAULT_EVENT_ID, right_on=left_index)
    relations3 = relations3.merge(relations2_minimal, left_on=right_index, right_on=ocel_constants.DEFAULT_EVENT_ID,
                                  suffixes=('', '_@#@#RIGHT'))
    relations3[ocel_constants.DEFAULT_OBJECT_ID] = relations3[ocel_constants.DEFAULT_OBJECT_ID + '_@#@#RIGHT']
    relations3[ocel_constants.DEFAULT_OBJECT_TYPE] = target_object_type_2

    relations4 = events2.merge(interleavings_rl, left_on=ocel_constants.DEFAULT_EVENT_ID, right_on=right_index)
    relations4 = relations4.merge(relations1_minimal, left_on=left_index, right_on=ocel_constants.DEFAULT_EVENT_ID,
                                  suffixes=('', '_@#@#LEFT'))
    relations4[ocel_constants.DEFAULT_OBJECT_ID] = relations4[ocel_constants.DEFAULT_OBJECT_ID + '_@#@#LEFT']
    relations4[ocel_constants.DEFAULT_OBJECT_TYPE] = target_object_type

    del events1[ocel_constants.DEFAULT_OBJECT_ID]
    del events2[ocel_constants.DEFAULT_OBJECT_ID]

    events = pd.concat([events1, events2])
    objects = pd.concat([objects1, objects2])
    relations = pd.concat([relations1, relations2, relations3, relations4])

    events = events.sort_values([ocel_constants.DEFAULT_EVENT_TIMESTAMP, ocel_constants.DEFAULT_EVENT_ID])
    relations = relations.sort_values([ocel_constants.DEFAULT_EVENT_TIMESTAMP, ocel_constants.DEFAULT_EVENT_ID])

    return OCEL(events=events, objects=objects, relations=relations)


def log_to_ocel_multiple_obj_types(log_obj: Union[EventLog, EventStream, pd.DataFrame], activity_column: str, timestamp_column: str, obj_types: Collection[str], obj_separator: str = " AND ", additional_event_attributes: Optional[Collection[str]] = None) -> OCEL:
    """
    Converts an event log to an object-centric event log with one or more than one
    object types.

    Parameters
    ---------------
    log_obj
        Log object
    activity_column
        Activity column
    timestamp_column
        Timestamp column
    object_types
        List of columns to consider as object types
    obj_separator
        Separator between different objects in the same column
    additional_event_attributes
        Additional attributes to be considered as event attributes in the OCEL

    Returns
    ----------------
    ocel
        Object-centric event log
    """
    log_obj = log_converter.apply(log_obj, variant=log_converter.Variants.TO_DATA_FRAME)

    if additional_event_attributes is None:
        additional_event_attributes = {}

    events = []
    objects = []
    relations = []

    obj_ids = set()

    stream = log_obj.to_dict("records")

    for index, eve in enumerate(stream):
        ocel_eve = {ocel_constants.DEFAULT_EVENT_ID: str(index), ocel_constants.DEFAULT_EVENT_ACTIVITY: eve[activity_column], ocel_constants.DEFAULT_EVENT_TIMESTAMP: eve[timestamp_column]}
        for attr in additional_event_attributes:
            ocel_eve[attr] = eve[attr]
        events.append(ocel_eve)

        for col in obj_types:
            try:
                objs = eve[col].split(obj_separator)

                for obj in objs:
                    if len(obj.strip()) > 0:
                        if obj not in obj_ids:
                            obj_ids.add(obj)

                            objects.append({ocel_constants.DEFAULT_OBJECT_ID: obj, ocel_constants.DEFAULT_OBJECT_TYPE: col})

                        rel = copy(ocel_eve)
                        rel[ocel_constants.DEFAULT_OBJECT_ID] = obj
                        rel[ocel_constants.DEFAULT_OBJECT_TYPE] = col

                        relations.append(rel)
            except:
                pass

    events = pd.DataFrame(events)
    objects = pd.DataFrame(objects)
    relations = pd.DataFrame(relations)
    relations.drop_duplicates(subset=[ocel_constants.DEFAULT_EVENT_ID, ocel_constants.DEFAULT_OBJECT_ID], inplace=True)

    ocel = OCEL(events=events, objects=objects, relations=relations)
    ocel = ocel_consistency.apply(ocel)

    return ocel

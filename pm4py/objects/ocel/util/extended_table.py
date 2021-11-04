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
from typing import Optional, Dict, Any

import pandas as pd

from pm4py.objects.ocel import constants
from pm4py.objects.ocel.obj import OCEL
from pm4py.util import exec_utils


class Parameters(Enum):
    OBJECT_TYPE_PREFIX = constants.PARAM_OBJECT_TYPE_PREFIX_EXTENDED
    EVENT_ID = constants.PARAM_EVENT_ID
    EVENT_ACTIVITY = constants.PARAM_EVENT_ACTIVITY
    EVENT_TIMESTAMP = constants.PARAM_EVENT_TIMESTAMP
    OBJECT_ID = constants.PARAM_OBJECT_ID
    OBJECT_TYPE = constants.PARAM_OBJECT_TYPE
    INTERNAL_INDEX = constants.PARAM_INTERNAL_INDEX


def parse_list(value):
    if type(value) is str:
        if value[0] == "[":
            return eval(value)
    return []


def get_ocel_from_extended_table(df: pd.DataFrame, objects_df: Optional[Dict[Any, Any]] = None,
                                 parameters: Optional[Dict[Any, Any]] = None) -> OCEL:
    if parameters is None:
        parameters = {}

    object_type_prefix = exec_utils.get_param_value(Parameters.OBJECT_TYPE_PREFIX, parameters,
                                                    constants.DEFAULT_OBJECT_TYPE_PREFIX_EXTENDED)
    event_activity = exec_utils.get_param_value(Parameters.EVENT_ACTIVITY, parameters,
                                                constants.DEFAULT_EVENT_ACTIVITY)
    event_id = exec_utils.get_param_value(Parameters.EVENT_ID, parameters, constants.DEFAULT_EVENT_ID)
    event_timestamp = exec_utils.get_param_value(Parameters.EVENT_TIMESTAMP, parameters,
                                                 constants.DEFAULT_EVENT_TIMESTAMP)
    object_id_column = exec_utils.get_param_value(Parameters.OBJECT_ID, parameters, constants.DEFAULT_OBJECT_ID)
    object_type_column = exec_utils.get_param_value(Parameters.OBJECT_TYPE, parameters, constants.DEFAULT_OBJECT_TYPE)

    non_object_type_columns = set(x for x in df.columns if not x.startswith(object_type_prefix))
    object_type_columns = set(x for x in df.columns if x.startswith(object_type_prefix))
    meaningful_columns = object_type_columns.union({event_activity, event_id, event_timestamp})
    internal_index = exec_utils.get_param_value(Parameters.INTERNAL_INDEX, parameters, constants.DEFAULT_INTERNAL_INDEX)

    df_red = df[meaningful_columns]

    stream = df_red.to_dict("records")
    relations = []
    objects = {x: set() for x in object_type_columns}

    for ev in stream:
        for ot in object_type_columns:
            ot_stri = ot.split(object_type_prefix)[1]
            ev[ot] = parse_list(ev[ot])
            oot = objects[ot]
            for obj in ev[ot]:
                oot.add(obj)
                relations.append(
                    {event_id: ev[event_id], event_activity: ev[event_activity], event_timestamp: ev[event_timestamp],
                     object_id_column: obj, object_type_column: ot_stri})

    relations = pd.DataFrame(relations)

    if objects_df is None:
        objects = [{object_type_column: x.split(object_type_prefix)[1], object_id_column: y} for x in objects for y in
                   objects[x]]
        objects_df = pd.DataFrame(objects)

    del objects

    df = df[non_object_type_columns]
    df[event_timestamp] = pd.to_datetime(df[event_timestamp])

    df[internal_index] = df.index
    relations[internal_index] = relations.index

    df = df.sort_values([event_timestamp, internal_index])
    relations = relations.sort_values([event_timestamp, internal_index])

    del df[internal_index]
    del relations[internal_index]

    return OCEL(df, objects_df, relations)

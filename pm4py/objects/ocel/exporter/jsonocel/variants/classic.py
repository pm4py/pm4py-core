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
import json
from enum import Enum
from typing import Optional, Dict, Any

import pandas as pd

from pm4py.objects.ocel import constants
from pm4py.objects.ocel.exporter.util import clean_dataframes
from pm4py.objects.ocel.obj import OCEL
from pm4py.objects.ocel.util import attributes_names
from pm4py.objects.ocel.util import related_objects
from pm4py.util import exec_utils


class Parameters(Enum):
    EVENT_ID = constants.PARAM_EVENT_ID
    OBJECT_ID = constants.PARAM_OBJECT_ID
    OBJECT_TYPE = constants.PARAM_OBJECT_TYPE


def apply(ocel: OCEL, target_path: str, parameters: Optional[Dict[Any, Any]] = None):
    """
    Exports an object-centric event log in a JSONOCEL file, using the classic JSON dump

    Parameters
    ------------------
    ocel
        Object-centric event log
    target_path
        Destination path
    parameters
        Parameters of the algorithm, including:
        - Parameters.EVENT_ID => the event ID column
        - Parameters.OBJECT_ID => the object ID column
        - Parameters.OBJECT_TYPE => the object type column
    """
    if parameters is None:
        parameters = {}

    event_id = exec_utils.get_param_value(Parameters.EVENT_ID, parameters, constants.DEFAULT_EVENT_ID)
    object_id = exec_utils.get_param_value(Parameters.OBJECT_ID, parameters, constants.DEFAULT_OBJECT_ID)
    object_type = exec_utils.get_param_value(Parameters.OBJECT_TYPE, parameters, constants.DEFAULT_OBJECT_TYPE)

    all_object_types = list(ocel.objects[object_type].unique())
    all_attribute_names = attributes_names.get_attribute_names(ocel, parameters=parameters)
    global_event_items = ocel.globals[
        constants.OCEL_GLOBAL_EVENT] if constants.OCEL_GLOBAL_EVENT in ocel.globals else constants.DEFAULT_GLOBAL_EVENT
    global_object_items = ocel.globals[
        constants.OCEL_GLOBAL_OBJECT] if constants.OCEL_GLOBAL_OBJECT in ocel.globals else constants.DEFAULT_GLOBAL_OBJECT
    rel_objs = related_objects.related_objects_dct_overall(ocel, parameters=parameters)

    events_items, objects_items = clean_dataframes.get_dataframes_from_ocel(ocel, parameters=parameters)

    result = {}
    result[constants.OCEL_GLOBAL_EVENT] = global_event_items
    result[constants.OCEL_GLOBAL_OBJECT] = global_object_items
    result[constants.OCEL_GLOBAL_LOG] = {}
    result[constants.OCEL_GLOBAL_LOG][constants.OCEL_GLOBAL_LOG_OBJECT_TYPES] = all_object_types
    result[constants.OCEL_GLOBAL_LOG][constants.OCEL_GLOBAL_LOG_ATTRIBUTE_NAMES] = all_attribute_names
    result[constants.OCEL_GLOBAL_LOG][constants.OCEL_GLOBAL_LOG_VERSION] = constants.CURRENT_VERSION
    result[constants.OCEL_GLOBAL_LOG][constants.OCEL_GLOBAL_LOG_ORDERING] = constants.DEFAULT_ORDERING
    result[constants.OCEL_EVENTS_KEY] = {}
    result[constants.OCEL_OBJECTS_KEY] = {}

    events_items = events_items.to_dict("records")
    i = 0
    while i < len(events_items):
        event = events_items[i]
        eid = event[event_id]
        del event[event_id]
        event = {k: v for k, v in event.items() if pd.notnull(v)}
        vmap = {k: v for k, v in event.items() if not k.startswith(constants.OCEL_PREFIX)}
        event = {k: v for k, v in event.items() if k.startswith(constants.OCEL_PREFIX)}
        event[constants.OCEL_VMAP_KEY] = vmap
        event[constants.OCEL_OMAP_KEY] = rel_objs[eid]
        result[constants.OCEL_EVENTS_KEY][eid] = event
        i = i + 1
    del events_items

    objects_items = objects_items.to_dict("records")
    i = 0
    while i < len(objects_items):
        object = objects_items[i]
        oid = object[object_id]
        del object[object_id]
        ovmap = {k: v for k, v in object.items() if pd.notnull(v) and not k.startswith(constants.OCEL_PREFIX)}
        object = {object_type: object[object_type], constants.OCEL_OVMAP_KEY: ovmap}
        result[constants.OCEL_OBJECTS_KEY][oid] = object
        i = i + 1
    del objects_items

    json.dump(result, open(target_path, "w"), indent=2)

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
from pm4py.objects.ocel.obj import OCEL
from pm4py.objects.ocel.util import filtering_utils
from pm4py.objects.ocel.util import ocel_consistency
from pm4py.util import exec_utils, dt_parsing, constants as pm4_constants


class Parameters(Enum):
    EVENT_ID = constants.PARAM_EVENT_ID
    EVENT_ACTIVITY = constants.PARAM_EVENT_ACTIVITY
    EVENT_TIMESTAMP = constants.PARAM_EVENT_TIMESTAMP
    OBJECT_ID = constants.PARAM_OBJECT_ID
    OBJECT_TYPE = constants.PARAM_OBJECT_TYPE
    INTERNAL_INDEX = constants.PARAM_INTERNAL_INDEX
    ENCODING = "encoding"


def get_base_ocel(json_obj: Any, parameters: Optional[Dict[Any, Any]] = None):
    events = []
    relations = []
    objects = []
    o2o = []
    object_changes = []

    event_id = exec_utils.get_param_value(Parameters.EVENT_ID, parameters, constants.DEFAULT_EVENT_ID)
    event_activity = exec_utils.get_param_value(Parameters.EVENT_ACTIVITY, parameters, constants.DEFAULT_EVENT_ACTIVITY)
    event_timestamp = exec_utils.get_param_value(Parameters.EVENT_TIMESTAMP, parameters,
                                                 constants.DEFAULT_EVENT_TIMESTAMP)
    object_id = exec_utils.get_param_value(Parameters.OBJECT_ID, parameters, constants.DEFAULT_OBJECT_ID)
    object_type = exec_utils.get_param_value(Parameters.OBJECT_TYPE, parameters, constants.DEFAULT_OBJECT_TYPE)
    internal_index = exec_utils.get_param_value(Parameters.INTERNAL_INDEX, parameters, constants.DEFAULT_INTERNAL_INDEX)

    parser = dt_parsing.parser.get()

    types_dict = {}
    for obj_id in json_obj[constants.OCEL_OBJECTS_KEY]:
        obj = json_obj[constants.OCEL_OBJECTS_KEY][obj_id]
        obj_type = obj[object_type]
        types_dict[obj_id] = obj_type
        dct = {object_id: obj_id, object_type: obj_type}
        for k, v in obj[constants.OCEL_OVMAP_KEY].items():
            dct[k] = v
        if constants.OCEL_O2O_KEY in obj:
            this_rel_objs = obj[constants.OCEL_O2O_KEY]
            for newel in this_rel_objs:
                target_id = newel[object_id]
                qualifier = newel[constants.DEFAULT_QUALIFIER]
                o2o.append({object_id: obj_id, object_id+"_2": target_id, constants.DEFAULT_QUALIFIER: qualifier})
        objects.append(dct)

    for ev_id in json_obj[constants.OCEL_EVENTS_KEY]:
        ev = json_obj[constants.OCEL_EVENTS_KEY][ev_id]
        dct = {event_id: ev_id, event_timestamp: parser.apply(ev[event_timestamp]),
               event_activity: ev[event_activity]}
        for k, v in ev[constants.OCEL_VMAP_KEY].items():
            dct[k] = v
        this_rel = {}
        for obj in ev[constants.OCEL_OMAP_KEY]:
            this_rel[obj] = {event_id: ev_id, event_activity: ev[event_activity],
                              event_timestamp: parser.apply(ev[event_timestamp]), object_id: obj,
                              object_type: types_dict[obj]}
        if constants.OCEL_TYPED_OMAP_KEY in ev:
            for element in ev[constants.OCEL_TYPED_OMAP_KEY]:
                this_rel[element[object_id]][constants.DEFAULT_QUALIFIER] = element[constants.DEFAULT_QUALIFIER]
        for obj in this_rel:
            relations.append(this_rel[obj])
        events.append(dct)

    if constants.OCEL_OBJCHANGES_KEY in json_obj:
        object_changes = json_obj[constants.OCEL_OBJCHANGES_KEY]

    events = pd.DataFrame(events)
    objects = pd.DataFrame(objects)
    relations = pd.DataFrame(relations)

    events[internal_index] = events.index
    relations[internal_index] = relations.index

    events = events.sort_values([event_timestamp, internal_index])
    relations = relations.sort_values([event_timestamp, internal_index])

    del events[internal_index]
    del relations[internal_index]

    globals = {}
    globals[constants.OCEL_GLOBAL_LOG] = json_obj[constants.OCEL_GLOBAL_LOG]
    globals[constants.OCEL_GLOBAL_EVENT] = json_obj[constants.OCEL_GLOBAL_EVENT]
    globals[constants.OCEL_GLOBAL_OBJECT] = json_obj[constants.OCEL_GLOBAL_OBJECT]

    o2o = pd.DataFrame(o2o) if o2o else None
    object_changes = pd.DataFrame(object_changes) if object_changes else None
    if object_changes is not None and len(object_changes) > 0:
        object_changes[event_timestamp] = pd.to_datetime(object_changes[event_timestamp])
        obj_id_map = objects[[object_id, object_type]].to_dict("records")
        obj_id_map = {x[object_id]: x[object_type] for x in obj_id_map}
        object_changes[object_type] = object_changes[object_id].map(obj_id_map)

    log = OCEL(events=events, objects=objects, relations=relations, o2o=o2o, object_changes=object_changes, globals=globals, parameters=parameters)

    return log


def apply(file_path: str, parameters: Optional[Dict[Any, Any]] = None) -> OCEL:
    """
    Imports an object-centric event log from a JSON-OCEL file, using the default JSON backend of Python

    Parameters
    -----------------
    file_path
        Path to the JSON-OCEL file
    parameters
        Parameters of the algorithm, including:
        - Parameters.EVENT_ID
        - Parameters.EVENT_ACTIVITY
        - Parameters.EVENT_TIMESTAMP
        - Parameters.OBJECT_ID
        - Parameters.OBJECT_TYPE
        - Parameters.INTERNAL_INDEX

    Returns
    ------------------
    ocel
        Object-centric event log
    """
    if parameters is None:
        parameters = {}

    encoding = exec_utils.get_param_value(Parameters.ENCODING, parameters, pm4_constants.DEFAULT_ENCODING)

    F = open(file_path, "r", encoding=encoding)
    json_obj = json.load(F)
    F.close()

    log = get_base_ocel(json_obj, parameters=parameters)

    log = ocel_consistency.apply(log, parameters=parameters)
    log = filtering_utils.propagate_relations_filtering(log, parameters=parameters)

    return log

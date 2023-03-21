import json
from enum import Enum
from typing import Optional, Dict, Any

import pandas as pd

from pm4py.objects.ocel import constants
from pm4py.objects.ocel.obj import OCEL
from pm4py.objects.ocel.util import filtering_utils
from pm4py.util import exec_utils, dt_parsing


class Parameters(Enum):
    EVENT_ID = constants.PARAM_EVENT_ID
    EVENT_ACTIVITY = constants.PARAM_EVENT_ACTIVITY
    EVENT_TIMESTAMP = constants.PARAM_EVENT_TIMESTAMP
    OBJECT_ID = constants.PARAM_OBJECT_ID
    OBJECT_TYPE = constants.PARAM_OBJECT_TYPE
    INTERNAL_INDEX = constants.PARAM_INTERNAL_INDEX


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

    ocel = json.load(open(file_path, "r"))

    events = []
    relations = []
    objects = []

    event_id = exec_utils.get_param_value(Parameters.EVENT_ID, parameters, constants.DEFAULT_EVENT_ID)
    event_activity = exec_utils.get_param_value(Parameters.EVENT_ACTIVITY, parameters, constants.DEFAULT_EVENT_ACTIVITY)
    event_timestamp = exec_utils.get_param_value(Parameters.EVENT_TIMESTAMP, parameters,
                                                 constants.DEFAULT_EVENT_TIMESTAMP)
    object_id = exec_utils.get_param_value(Parameters.OBJECT_ID, parameters, constants.DEFAULT_OBJECT_ID)
    object_type = exec_utils.get_param_value(Parameters.OBJECT_TYPE, parameters, constants.DEFAULT_OBJECT_TYPE)
    internal_index = exec_utils.get_param_value(Parameters.INTERNAL_INDEX, parameters, constants.DEFAULT_INTERNAL_INDEX)

    parser = dt_parsing.parser.get()

    types_dict = {}
    for obj_id in ocel[constants.OCEL_OBJECTS_KEY]:
        obj = ocel[constants.OCEL_OBJECTS_KEY][obj_id]
        obj_type = obj[object_type]
        types_dict[obj_id] = obj_type
        dct = {object_id: obj_id, object_type: obj_type}
        for k, v in obj[constants.OCEL_OVMAP_KEY].items():
            dct[k] = v
        objects.append(dct)

    for ev_id in ocel[constants.OCEL_EVENTS_KEY]:
        ev = ocel[constants.OCEL_EVENTS_KEY][ev_id]
        dct = {event_id: ev_id, event_timestamp: parser.apply(ev[event_timestamp]),
               event_activity: ev[event_activity]}
        for k, v in ev[constants.OCEL_VMAP_KEY].items():
            dct[k] = v
        for obj in ev[constants.OCEL_OMAP_KEY]:
            relations.append({event_id: ev_id, event_activity: ev[event_activity],
                              event_timestamp: parser.apply(ev[event_timestamp]), object_id: obj,
                              object_type: types_dict[obj]})
        events.append(dct)

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
    globals[constants.OCEL_GLOBAL_LOG] = ocel[constants.OCEL_GLOBAL_LOG]
    globals[constants.OCEL_GLOBAL_EVENT] = ocel[constants.OCEL_GLOBAL_EVENT]
    globals[constants.OCEL_GLOBAL_OBJECT] = ocel[constants.OCEL_GLOBAL_OBJECT]

    ocel = OCEL(events=events, objects=objects, relations=relations, globals=globals, parameters=parameters)
    ocel = filtering_utils.propagate_relations_filtering(ocel)

    return ocel

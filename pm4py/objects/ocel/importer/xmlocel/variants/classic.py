from enum import Enum
from typing import Optional, Dict, Any

import pandas as pd
from lxml import etree, objectify

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


def parse_xml(value, tag_str_lower, parser):
    if "float" in tag_str_lower:
        return float(value)
    elif "date" in tag_str_lower:
        return parser.apply(value)
    return str(value)


def apply(file_path: str, parameters: Optional[Dict[Any, Any]] = None) -> OCEL:
    """
    Imports an object-centric event log from a XNK-OCEL file, using LXML

    Parameters
    -----------------
    file_path
        Path to the XML-OCEL file
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

    events = []
    relations = []
    objects = []
    obj_type_dict = {}

    event_id = exec_utils.get_param_value(Parameters.EVENT_ID, parameters, constants.DEFAULT_EVENT_ID)
    event_activity = exec_utils.get_param_value(Parameters.EVENT_ACTIVITY, parameters, constants.DEFAULT_EVENT_ACTIVITY)
    event_timestamp = exec_utils.get_param_value(Parameters.EVENT_TIMESTAMP, parameters,
                                                 constants.DEFAULT_EVENT_TIMESTAMP)
    object_id = exec_utils.get_param_value(Parameters.OBJECT_ID, parameters, constants.DEFAULT_OBJECT_ID)
    object_type = exec_utils.get_param_value(Parameters.OBJECT_TYPE, parameters, constants.DEFAULT_OBJECT_TYPE)
    internal_index = exec_utils.get_param_value(Parameters.INTERNAL_INDEX, parameters, constants.DEFAULT_INTERNAL_INDEX)

    date_parser = dt_parsing.parser.get()

    parser = etree.XMLParser(remove_comments=True)
    tree = objectify.parse(file_path, parser=parser)
    root = tree.getroot()

    for child in root:
        if child.tag.lower().endswith("events"):
            for event in child:
                eve_id = None
                eve_activity = None
                eve_timestamp = None
                eve_omap = {}
                eve_vmap = {}
                for child2 in event:
                    if child2.get("key") == "id":
                        eve_id = child2.get("value")
                    elif child2.get("key") == "timestamp":
                        eve_timestamp = parse_xml(child2.get("value"), child2.tag.lower(), date_parser)
                    elif child2.get("key") == "activity":
                        eve_activity = child2.get("value")
                    elif child2.get("key") == "omap":
                        for child3 in child2:
                            objref = child3.get("value")
                            qualifier = child3.get("qualifier") if "qualifier" in child3.keys() else None
                            eve_omap[objref] = qualifier
                    elif child2.get("key") == "vmap":
                        for child3 in child2:
                            key = child3.get("key")
                            value = parse_xml(child3.get("value"), child3.tag.lower(),
                                                                    date_parser)
                            eve_vmap[key] = value

                event_dict = {event_id: eve_id, event_activity: eve_activity, event_timestamp: eve_timestamp}
                for k, v in eve_vmap.items():
                    event_dict[k] = v
                events.append(event_dict)

                for obj in eve_omap:
                    rel_dict = {event_id: eve_id, event_activity: eve_activity, event_timestamp: eve_timestamp,
                                object_id: obj, constants.DEFAULT_QUALIFIER: eve_omap[obj]}
                    relations.append(rel_dict)
        elif child.tag.lower().endswith("objects"):
            for object in child:
                obj_id = None
                obj_type = None
                obj_ovmap = []
                for child2 in object:
                    if child2.get("key") == "id":
                        obj_id = child2.get("value")
                    elif child2.get("key") == "type":
                        obj_type = child2.get("value")
                    elif child2.get("key") == "ovmap":
                        for child3 in child2:
                            key = child3.get("key")
                            value = parse_xml(child3.get("value"), child3.tag.lower(),
                                                                     date_parser)
                            timestamp = child3.get("timestamp") if "timestamp" in child3.keys() else None
                            obj_ovmap.append((key, value, timestamp))
                dct = {object_id: obj_id, object_type: obj_type}
                for el in obj_ovmap:
                    if el[0] not in dct:
                        dct[el[0]] = el[1]
                objects.append(dct)
                obj_type_dict[obj_id] = obj_type

    for rel in relations:
        rel[object_type] = obj_type_dict[rel[object_id]]

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

    ocel = OCEL(events, objects, relations, globals)
    ocel = filtering_utils.propagate_relations_filtering(ocel)

    return ocel

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
from lxml import etree, objectify

from pm4py.objects.ocel import constants
from pm4py.objects.ocel.obj import OCEL
from pm4py.objects.ocel.util import filtering_utils
from pm4py.util import exec_utils, dt_parsing, pandas_utils
from pm4py.objects.ocel.util import ocel_consistency


class Parameters(Enum):
    EVENT_ID = constants.PARAM_EVENT_ID
    EVENT_ACTIVITY = constants.PARAM_EVENT_ACTIVITY
    EVENT_TIMESTAMP = constants.PARAM_EVENT_TIMESTAMP
    OBJECT_ID = constants.PARAM_OBJECT_ID
    OBJECT_TYPE = constants.PARAM_OBJECT_TYPE
    INTERNAL_INDEX = constants.PARAM_INTERNAL_INDEX
    QUALIFIER = constants.PARAM_QUALIFIER
    CHANGED_FIELD = constants.PARAM_CHNGD_FIELD
    ENCODING = "encoding"


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
    object_changes = []
    o2o = []
    obj_type_dict = {}

    encoding = exec_utils.get_param_value(Parameters.ENCODING, parameters, None)

    event_id = exec_utils.get_param_value(Parameters.EVENT_ID, parameters, constants.DEFAULT_EVENT_ID)
    event_activity = exec_utils.get_param_value(Parameters.EVENT_ACTIVITY, parameters, constants.DEFAULT_EVENT_ACTIVITY)
    event_timestamp = exec_utils.get_param_value(Parameters.EVENT_TIMESTAMP, parameters,
                                                 constants.DEFAULT_EVENT_TIMESTAMP)
    object_id = exec_utils.get_param_value(Parameters.OBJECT_ID, parameters, constants.DEFAULT_OBJECT_ID)
    object_type = exec_utils.get_param_value(Parameters.OBJECT_TYPE, parameters, constants.DEFAULT_OBJECT_TYPE)
    internal_index = exec_utils.get_param_value(Parameters.INTERNAL_INDEX, parameters, constants.DEFAULT_INTERNAL_INDEX)
    qualifier_field = exec_utils.get_param_value(Parameters.QUALIFIER, parameters, constants.DEFAULT_QUALIFIER)
    changed_field = exec_utils.get_param_value(Parameters.CHANGED_FIELD, parameters, constants.DEFAULT_CHNGD_FIELD)

    date_parser = dt_parsing.parser.get()

    parser = etree.XMLParser(remove_comments=True, encoding=encoding)

    F = open(file_path, "rb")
    tree = objectify.parse(F, parser=parser)
    F.close()

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
                                object_id: obj, qualifier_field: eve_omap[obj]}
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
                    else:
                        this_dct = {object_id: obj_id, object_type: obj_type}
                        this_dct[el[0]] = el[1]
                        this_dct[event_timestamp] = date_parser.apply(el[2])
                        this_dct[changed_field] = el[0]
                        object_changes.append(this_dct)
                objects.append(dct)
                obj_type_dict[obj_id] = obj_type
        elif child.tag.lower().endswith("o2o"):
            for rel in child:
                source = rel.get("source")
                target = rel.get("target")
                qualifier = rel.get("qualifier")
                o2o.append({object_id: source, object_id+"_2": target, qualifier_field: qualifier})

    for rel in relations:
        rel[object_type] = obj_type_dict[rel[object_id]]

    events = pandas_utils.instantiate_dataframe(events) if events else None
    objects = pandas_utils.instantiate_dataframe(objects) if objects else None
    relations = pandas_utils.instantiate_dataframe(relations) if relations else None
    o2o = pandas_utils.instantiate_dataframe(o2o) if o2o else None
    object_changes = pandas_utils.instantiate_dataframe(object_changes) if object_changes else None

    events = pandas_utils.insert_index(events, internal_index, reset_index=False, copy_dataframe=False)
    relations = pandas_utils.insert_index(relations, internal_index, reset_index=False, copy_dataframe=False)

    events = events.sort_values([event_timestamp, internal_index])
    relations = relations.sort_values([event_timestamp, internal_index])

    del events[internal_index]
    del relations[internal_index]

    globals = {}

    ocel = OCEL(events=events, objects=objects, relations=relations, globals=globals, o2o=o2o, object_changes=object_changes, parameters=parameters)
    ocel = ocel_consistency.apply(ocel, parameters=parameters)
    ocel = filtering_utils.propagate_relations_filtering(ocel)

    return ocel

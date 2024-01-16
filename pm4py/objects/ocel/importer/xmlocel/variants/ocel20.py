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
        if value == "null":
            return 0
        return float(value)
    elif "date" in tag_str_lower:
        return embed_date_parser(parser.apply, value)
    return str(value)


def embed_date_parser(date_parser, x):
    try:
        return date_parser(x)
    except:
        from dateutil.parser import parse
        try:
            return parse(x)
        except:
            return parse(x, fuzzy=True)


def apply(file_path: str, parameters: Optional[Dict[Any, Any]] = None) -> OCEL:
    if parameters is None:
        parameters = {}

    events_list = []
    relations_list = []
    objects_list = []
    object_changes_list = []
    o2o_list = []

    encoding = exec_utils.get_param_value(Parameters.ENCODING, parameters, None)

    event_id_column = exec_utils.get_param_value(Parameters.EVENT_ID, parameters, constants.DEFAULT_EVENT_ID)
    event_activity_column = exec_utils.get_param_value(Parameters.EVENT_ACTIVITY, parameters, constants.DEFAULT_EVENT_ACTIVITY)
    event_timestamp_column = exec_utils.get_param_value(Parameters.EVENT_TIMESTAMP, parameters,
                                                 constants.DEFAULT_EVENT_TIMESTAMP)
    object_id_column = exec_utils.get_param_value(Parameters.OBJECT_ID, parameters, constants.DEFAULT_OBJECT_ID)
    object_type_column = exec_utils.get_param_value(Parameters.OBJECT_TYPE, parameters, constants.DEFAULT_OBJECT_TYPE)
    internal_index_column = exec_utils.get_param_value(Parameters.INTERNAL_INDEX, parameters, constants.DEFAULT_INTERNAL_INDEX)
    qualifier_field = exec_utils.get_param_value(Parameters.QUALIFIER, parameters, constants.DEFAULT_QUALIFIER)
    changed_field = exec_utils.get_param_value(Parameters.CHANGED_FIELD, parameters, constants.DEFAULT_CHNGD_FIELD)
    obj_type_dict = {}

    date_parser = dt_parsing.parser.get()

    parser = etree.XMLParser(remove_comments=True, encoding=encoding)

    F = open(file_path, "rb")
    tree = objectify.parse(F, parser=parser)
    F.close()

    root = tree.getroot()

    object_type_attributes = {}
    event_type_attributes = {}

    for child in root:
        if child.tag.endswith("object-types"):
            for object_type in child:
                object_type_name = object_type.get("name")
                object_type_attributes[object_type_name] = {}
                for attributes in object_type:
                    for attribute in attributes:
                        attribute_name = attribute.get("name")
                        attribute_type = attribute.get("type")
                        object_type_attributes[object_type_name][attribute_name] = attribute_type
        elif child.tag.endswith("event-types"):
            for event_type in child:
                event_type_name = event_type.get("name")
                event_type_attributes[event_type_name] = {}
                for attributes in event_type:
                    for attribute in attributes:
                        attribute_name = attribute.get("name")
                        attribute_type = attribute.get("type")
                        event_type_attributes[event_type_name][attribute_name] = attribute_type
        elif child.tag.endswith("objects"):
            object_id = None
            object_type = None

            for object in child:
                object_id = object.get("id")
                object_type = object.get("type")

                obj_dict = {object_id_column: object_id, object_type_column: object_type}
                obj_type_dict[object_id] = object_type

                for child2 in object:
                    if child2.tag.endswith("objects"):
                        for target_object in child2:
                            target_object_id = target_object.get("object-id")
                            qualifier = target_object.get("qualifier")

                            o2o_dict = {object_id_column: object_id, object_id_column+"_2": target_object_id, qualifier_field: qualifier}
                            o2o_list.append(o2o_dict)

                    elif child2.tag.endswith("attributes"):
                        for attribute in child2:
                            attribute_name = attribute.get("name")
                            attribute_time = attribute.get("time")
                            try:
                                attribute_type = object_type_attributes[object_type][attribute_name]
                            except:
                                attribute_type = "string"
                            attribute_text = parse_xml(attribute.text, attribute_type, date_parser)
                            if attribute_time == "0" or attribute_time.startswith("1970-01-01T00:00:00"):
                                obj_dict[attribute_name] = attribute_text
                            else:
                                attribute_time = embed_date_parser(date_parser.apply, attribute_time)
                                obj_change_dict = {object_id_column: object_id, object_type_column: object_type, attribute_name: attribute_text, changed_field: attribute_name, event_timestamp_column: attribute_time}
                                object_changes_list.append(obj_change_dict)

                objects_list.append(obj_dict)

        elif child.tag.endswith("events"):
            event_id = None
            event_type = None
            event_time = None

            for event in child:
                event_id = event.get("id")
                event_type = event.get("type")
                event_time = embed_date_parser(date_parser.apply, event.get("time"))

                ev_dict = {event_id_column: event_id, event_activity_column: event_type, event_timestamp_column: event_time}

                for child2 in event:
                    if child2.tag.endswith("objects"):
                        for target_object in child2:
                            target_object_id = target_object.get("object-id")
                            qualifier = target_object.get("qualifier")

                            if target_object_id in obj_type_dict:
                                rel_dict = {event_id_column: event_id, event_activity_column: event_type, event_timestamp_column: event_time, object_id_column: target_object_id, object_type_column: obj_type_dict[target_object_id], qualifier_field: qualifier}
                                relations_list.append(rel_dict)
                    elif child2.tag.endswith("attributes"):
                        for attribute in child2:
                            attribute_name = attribute.get("name")
                            attribute_text = attribute.text
                            try:
                                attribute_type = event_type_attributes[event_type][attribute_name]
                            except:
                                attribute_type = "string"
                            ev_dict[attribute_name] = parse_xml(attribute_text, attribute_type, date_parser)

                events_list.append(ev_dict)

    events_list = pandas_utils.instantiate_dataframe(events_list) if events_list else None
    objects_list = pandas_utils.instantiate_dataframe(objects_list) if objects_list else None
    relations_list = pandas_utils.instantiate_dataframe(relations_list) if relations_list else None
    o2o_list = pandas_utils.instantiate_dataframe(o2o_list) if o2o_list else None
    object_changes_list = pandas_utils.instantiate_dataframe(object_changes_list) if object_changes_list else None
    globals = {}

    events_list[internal_index_column] = events_list.index
    relations_list[internal_index_column] = relations_list.index

    events_list = events_list.sort_values([event_timestamp_column, internal_index_column])
    relations_list = relations_list.sort_values([event_timestamp_column, internal_index_column])

    del events_list[internal_index_column]
    del relations_list[internal_index_column]

    ocel = OCEL(events=events_list, objects=objects_list, relations=relations_list, globals=globals, o2o=o2o_list, object_changes=object_changes_list, parameters=parameters)
    ocel = ocel_consistency.apply(ocel, parameters=parameters)
    ocel = filtering_utils.propagate_relations_filtering(ocel)

    return ocel

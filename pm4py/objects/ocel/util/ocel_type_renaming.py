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
from pm4py.objects.ocel.obj import OCEL
from pm4py.objects.ocel.util import names_stripping
from copy import deepcopy
from typing import Dict, Optional


def __rename_types_from_maps(ocel: OCEL, event_types_map: Optional[Dict[str, str]], object_types_map: Optional[Dict[str, str]]) -> OCEL:
    ret_ocel = deepcopy(ocel)

    if event_types_map is not None:
        ret_ocel.events[ocel.event_activity] = ret_ocel.events[ocel.event_activity].map(event_types_map)
        ret_ocel.relations[ocel.event_activity] = ret_ocel.relations[ocel.event_activity].map(event_types_map)

    if object_types_map is not None:
        ret_ocel.objects[ocel.object_type_column] = ret_ocel.objects[ocel.object_type_column].map(object_types_map)
        ret_ocel.relations[ocel.object_type_column] = ret_ocel.relations[ocel.object_type_column].map(object_types_map)
        ret_ocel.object_changes[ocel.object_type_column] = ret_ocel.object_changes[ocel.object_type_column].map(object_types_map)

    return ret_ocel


def remove_spaces_non_alphanumeric_characters_from_types(ocel: OCEL) -> OCEL:
    """
    Creates a copy of the object-centric event log in which
    spaces and non-alphanumeric characters inside the event/object types are stripped

    Parameters
    ----------------
    ocel
        Object-centric event log

    Returns
    ----------------
    ocel
        Object-centric event log with stripped types
    """
    object_types = ocel.objects[ocel.object_type_column].value_counts().to_dict()
    event_types = ocel.events[ocel.event_activity].value_counts().to_dict()

    object_types_map = {x: names_stripping.apply(x) for x in object_types}
    event_types_map = {x: names_stripping.apply(x) for x in event_types}

    return __rename_types_from_maps(ocel, event_types_map, object_types_map)


def abbreviate_event_types(ocel: OCEL) -> OCEL:
    """
    Creates a copy of the object-centric event log in which
    the event types are replaced by the letters of the alphabet (A being the most frequent event type, ...).
    This is particularly useful to textually abstract the object-centric event log.

    Parameters
    ----------------
    ocel
        Object-centric event log

    Returns
    ----------------
    ocel
        Object-centric event log with alphabetical event types
    """
    event_types = list(ocel.events[ocel.event_activity].value_counts().to_dict())

    event_types_map = {}
    for index, act in enumerate(event_types):
        result = ''
        while index >= 0:
            result = chr((index % 26) + ord('A')) + result
            index = index // 26 - 1
        event_types_map[act] = result

    return __rename_types_from_maps(ocel, event_types_map, None)

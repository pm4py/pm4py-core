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
from pm4py.util import exec_utils, constants, xes_constants
from pm4py.objects.ocel import constants as ocel_constants
from collections import Counter
from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any
from pm4py.statistics.ocel import objects_ot_count
from pm4py.objects.ocel.util import filtering_utils
from copy import copy


class Parameters(Enum):
    EVENT_ID = ocel_constants.PARAM_EVENT_ID
    OBJECT_ID = ocel_constants.PARAM_OBJECT_ID
    OBJECT_TYPE = ocel_constants.PARAM_OBJECT_TYPE


def apply(ocel: OCEL, min_num_obj_type: Dict[str, int], parameters: Optional[Dict[Any, Any]] = None) -> OCEL:
    """
    Filters the events of the object-centric logs which are related to at least
    the specified amount of objects per type.

    E.g. apply(ocel, {"order": 1, "element": 2})

    Would keep the following events:

      ocel:eid ocel:timestamp ocel:activity ocel:type:element ocel:type:order
    0       e1     1980-01-01  Create Order  [i4, i1, i3, i2]            [o1]
    1      e11     1981-01-01  Create Order          [i6, i5]            [o2]
    2      e14     1981-01-04  Create Order          [i8, i7]            [o3]

    Parameters
    ------------------
    ocel
        Object-centric event log
    min_num_obj_type
        Minimum number of objects per type
    parameters
        Parameters of the filter, including:
        - Parameters.EVENT_ID => the event identifier
        - Parameters.OBJECT_ID => the object identifier
        - Parameters.OBJECT_TYPE => the object type

    Returns
    -----------------
    filtered_event_log
        Filtered object-centric event log
    """
    if parameters is None:
        parameters = {}

    event_id = exec_utils.get_param_value(Parameters.EVENT_ID, parameters, ocel.event_id_column)
    object_id = exec_utils.get_param_value(Parameters.OBJECT_ID, parameters, ocel.object_id_column)
    object_type = exec_utils.get_param_value(Parameters.OBJECT_TYPE, parameters, ocel.object_type_column)

    num_obj = objects_ot_count.get_objects_ot_count(ocel, parameters=parameters)

    filt_evs = set()

    for evid, evobjs in num_obj.items():
        is_ok = True
        for k, v in min_num_obj_type.items():
            if not k in evobjs:
                is_ok = False
                break
            elif evobjs[k] < v:
                is_ok = False
                break
        if is_ok:
            filt_evs.add(evid)

    ocel = copy(ocel)
    ocel.events = ocel.events[ocel.events[event_id].isin(filt_evs)]

    return filtering_utils.propagate_event_filtering(ocel, parameters=parameters)

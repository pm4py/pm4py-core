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
from enum import Enum
from pm4py.util import exec_utils
from typing import Optional, Dict, Any


class Parameters(Enum):
    INCLUDE_TIMESTAMPS = "include_timestamps"


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None) -> str:
    """
    Provides a textual description of the provided object-centric event log

    Parameters
    --------------
    ocel
        Object-centric event log
    parameters
        Possible parameters of the algorithm, including:
        - Parameters.INCLUDE_TIMESTAMPS => include the timestamps (or not) in the representation

    Returns
    -------------
    ocel_stri
        Textual representation of the object-centric event log
    """
    if parameters is None:
        parameters = {}

    include_timestamps = exec_utils.get_param_value(Parameters.INCLUDE_TIMESTAMPS, parameters, True)

    object_ots = ocel.objects[[ocel.object_id_column, ocel.object_type_column]].to_dict("records")
    object_ots = {x[ocel.object_id_column]: x[ocel.object_type_column] for x in object_ots}
    events = ocel.events.sort_values([ocel.event_timestamp, ocel.event_activity, ocel.event_id_column]).to_dict("records")
    objects = ocel.objects.sort_values(ocel.object_id_column).to_dict("records")
    relations = ocel.relations.sort_values([ocel.event_timestamp, ocel.event_activity, ocel.object_id_column, ocel.event_id_column])
    tdf = relations.groupby(ocel.object_id_column)[ocel.event_timestamp]
    objects_start = tdf.first().to_dict()
    objects_end = tdf.last().to_dict()
    objects_lifecycle = {x: objects_end[x].timestamp() - objects_start[x].timestamp() for x in objects_start}

    relations = relations.groupby(ocel.event_id_column)[ocel.object_id_column].agg(list).to_dict()

    ret = ["\n\nevents:\n"]

    for ev in events:
        stru = ev[ocel.event_activity] + " ( related objects: "+", ".join(relations[ev[ocel.event_id_column]])  + " ) "
        if include_timestamps:
            stru = stru + " timestamp: "+str(ev[ocel.event_timestamp])
        ret.append(stru)

    ret.append("\nobjects:\n")

    for obj in objects:
        obj_id = obj[ocel.object_id_column]
        stru = obj_id + " object type: "+object_ots[obj_id]
        if include_timestamps:
            stru = stru + " ( lifecycle start: "+str(objects_start[obj_id])+" ; lifecycle end: "+str(objects_end[obj_id])+" ; lifecycle duration: "+str(objects_lifecycle[obj_id])+" )"
        ret.append(stru)

    ret = "\n".join(ret)

    return ret

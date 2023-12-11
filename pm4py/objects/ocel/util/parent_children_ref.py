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
from typing import Optional, Dict, Any


def apply(ocel: OCEL, child_obj_type: str, parent_obj_type: str, parameters: Optional[Dict[Any, Any]] = None) -> OCEL:
    """
    Inserts an object attribute pointing to the parent of a child object,
    by looking at the related objects of the events of the log.
    This requires only the provision of the child object type and of the parent object type.

    Parameters
    --------------
    ocel
        Object-centric event log
    child_obj_type
        Child object type (e.g. item)
    parent_obj_type
        Parent object type (e.g. parent)
    parameters
        Possible parameters of the algorithm

    Returns
    -------------
    ocel
        Enriched object-centric event log
    """
    if parameters is None:
        parameters = {}

    ev_lf = ocel.relations.groupby(ocel.event_id_column)[ocel.object_id_column].agg(list).to_dict()
    obj_types = ocel.objects[[ocel.object_id_column, ocel.object_type_column]].to_dict("records")
    obj_types = {x[ocel.object_id_column]: x[ocel.object_type_column] for x in obj_types}
    parents = {}

    for ev_id, lif in ev_lf.items():
        for obj_id in lif:
            if obj_types[obj_id] == child_obj_type:
                for obj_id_2 in lif:
                    if obj_types[obj_id_2] == parent_obj_type:
                        parents[obj_id] = obj_id_2

    col = ocel.objects[ocel.object_id_column].map(parents)
    if parent_obj_type+"ID" not in ocel.objects.columns:
        ocel.objects[parent_obj_type+"ID"] = col
    else:
        ocel.objects[parent_obj_type+"ID"] = ocel.objects[parent_obj_type+"ID"].fillna(col)

    return ocel

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
from pm4py.algo.filtering.ocel import ot_endpoints


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None):
    """
    Assigns to each event a feature that is 1 when the event starts at least one object of a given type.

    Parameters
    ----------------
    ocel
        OCEL
    parameters
        Parameters of the algorithm

    Returns
    ----------------
    data
        Extracted feature values
    feature_names
        Feature names
    """
    if parameters is None:
        parameters = {}

    ordered_events = list(ocel.events[ocel.event_id_column])

    object_types = list(ocel.objects[ocel.object_type_column].unique())

    map_endpoints = {}
    for ot in object_types:
        map_endpoints[ot] = set(ot_endpoints.filter_start_events_per_object_type(ocel, ot, parameters=parameters).events[ocel.event_id_column])

    feature_names = ["@@event_start_"+ot for ot in object_types]
    data = []

    for ev in ordered_events:
        data.append([])
        for ot in object_types:
            data[-1].append(1 if ev in map_endpoints[ot] else 0)

    return data, feature_names

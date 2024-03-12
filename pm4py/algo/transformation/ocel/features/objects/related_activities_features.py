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


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None):
    """
    Associates to each object and activity in the log the last value of the feature for a related event
    of the given activity, if exists

    Parameters
    ----------------
    ocel
        Object-centric event log
    parameters
        Parameters

    Returns
    -----------------
    data
        Extracted feature values
    feature_names
        Feature names
    """
    if parameters is None:
        parameters = {}

    from pm4py.algo.transformation.ocel.features.events import algorithm as event_based_features

    data_events, feature_names_events = event_based_features.apply(ocel, parameters=parameters)
    dct_dct_events = event_based_features.transform_features_to_dict_dict(ocel, data_events, feature_names_events, parameters=parameters)

    ordered_objects = parameters["ordered_objects"] if "ordered_objects" in parameters else ocel.objects[
        ocel.object_id_column].to_numpy()

    stream = ocel.relations[[ocel.event_id_column, ocel.object_id_column, ocel.event_activity]].to_dict("records")
    obj_rel_evs = {}

    for cou in stream:
        if cou[ocel.object_id_column] not in obj_rel_evs:
            obj_rel_evs[cou[ocel.object_id_column]] = []
        obj_rel_evs[cou[ocel.object_id_column]].append(cou[ocel.event_id_column])

    ev_act = {}
    activities = set()

    for cou in stream:
        ev_act[cou[ocel.event_id_column]] = cou[ocel.event_activity]
        activities.add(cou[ocel.event_activity])

    feature_names = []
    for x in feature_names_events:
        for a in activities:
            feature_names.append("@@ev_act_fea_"+a+"_"+x)

    data = []
    for obj in ordered_objects:
        arr = []
        objs_act = {}
        if obj in obj_rel_evs:
            for ev in obj_rel_evs[obj]:
                objs_act[ev_act[ev]] = ev
        for x in feature_names_events:
            for a in activities:
                if a in objs_act:
                    val = float(dct_dct_events[objs_act[a]][x])
                else:
                    val = 0.0
                arr.append(val)
        data.append(arr)

    return data, feature_names

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
    Adds for each object as features:
    - the duration of its lifecycle
    - the start timestamp
    - the end timestamp

    Parameters
    -----------------
    ocel
        OCEL
    parameters
        Parameters of the algorithm

    Returns
    -----------------
    data
        Values of the added features
    feature_names
        Names of the added features
    """
    if parameters is None:
        parameters = {}

    ordered_objects = parameters["ordered_objects"] if "ordered_objects" in parameters else ocel.objects[
        ocel.object_id_column].to_numpy()

    first_object_timestamp = ocel.relations.groupby(ocel.object_id_column).first()[ocel.event_timestamp].to_dict()
    last_object_timestamp = ocel.relations.groupby(ocel.object_id_column).last()[ocel.event_timestamp].to_dict()

    data = []
    feature_names = ["@@object_lifecycle_duration", "@@object_lifecycle_start_timestamp", "@@object_lifecycle_end_timestamp"]

    for obj in ordered_objects:
        if obj in first_object_timestamp:
            se = first_object_timestamp[obj].timestamp()
            ee = last_object_timestamp[obj].timestamp()
            data.append([float(ee - se), float(se), float(ee)])
        else:
            data.append([0, 0, 0])

    return data, feature_names

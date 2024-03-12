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
from pm4py.util import pandas_utils


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None):
    """
    Adds for each object an one-hot-encoding of the activities performed in its lifecycle

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

    activities = pandas_utils.format_unique(ocel.events[ocel.event_activity].unique())
    lifecycle = ocel.relations.groupby(ocel.object_id_column)[ocel.event_activity].agg(list).to_dict()

    data = []
    feature_names = ["@@ocel_lif_activity_"+str(x) for x in activities]

    for obj in ordered_objects:
        data.append([])
        if obj in lifecycle:
            lif = lifecycle[obj]
        else:
            lif = []
        for act in activities:
            data[-1].append(float(len(list(x for x in lif if x == act))))

    return data, feature_names


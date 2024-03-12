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
    Adds for each object an one-hot-encoding of the paths performed in its lifecycle

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

    lifecycle = ocel.relations.groupby(ocel.object_id_column)[ocel.event_activity].agg(list).to_dict()

    data = []
    paths = {}
    all_paths = set()
    for obj in lifecycle:
        paths[obj] = []
        lobj = lifecycle[obj]
        for i in range(len(lobj)-1):
            path = lobj[i]+"##"+lobj[i+1]
            paths[obj].append(path)
            all_paths.add(path)

    all_paths = sorted(list(all_paths))
    feature_names = ["@@ocel_lif_path_"+str(x) for x in all_paths]

    for obj in ordered_objects:
        lif = paths[obj] if obj in paths else []
        data.append([])
        for p in all_paths:
            data[-1].append(float(len(list(x for x in lif if x == p))))

    return data, feature_names


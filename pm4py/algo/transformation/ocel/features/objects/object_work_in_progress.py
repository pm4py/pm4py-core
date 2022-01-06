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
from pm4py.algo.transformation.ocel.features.objects import object_lifecycle_duration
import pandas as pd


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None):
    """
    Assigns to each object a feature which is the number of objects that are open during the lifecycle
    of the object.

    Parameters
    ----------------
    ocel
        OCEL
    parameters
        Parameters of the algorithm:
            - Parameters.OBJECT_STR_ATTRIBUTES => collection of string attributes to consider for feature extraction.

    Returns
    ----------------
    data
        Extracted feature values
    feature_names
        Feature names
    """
    if parameters is None:
        parameters = {}

    from intervaltree import Interval, IntervalTree
    
    data, feature_names = object_lifecycle_duration.apply(ocel, parameters=parameters)
    obj_dur = pd.DataFrame(data, columns=feature_names)
    obj_dur = obj_dur[["@@object_lifecycle_start_timestamp", "@@object_lifecycle_end_timestamp"]].to_dict("records")
    small_k = 10**-5

    tree = IntervalTree()

    for el in obj_dur:
        tree.add(Interval(el["@@object_lifecycle_start_timestamp"] - small_k,
                          el["@@object_lifecycle_end_timestamp"] + small_k))

    data = []
    feature_names = ["@@object_wip"]

    for el in obj_dur:
        data.append([len(tree[el["@@object_lifecycle_start_timestamp"] - small_k: el["@@object_lifecycle_end_timestamp"] + small_k])])

    return data, feature_names

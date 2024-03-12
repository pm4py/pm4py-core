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

    data, feature_names = object_lifecycle_duration.apply(ocel, parameters=parameters)
    obj_dur = pandas_utils.instantiate_dataframe(data, columns=feature_names)

    obj_dur["@@index"] = obj_dur.index
    obj_dur = obj_dur.to_dict("records")

    data = []
    obj_dur.sort(key=lambda x: (x["@@object_lifecycle_start_timestamp"], x["@@object_lifecycle_end_timestamp"]))
    for i in range(len(obj_dur)):
        j = i + 1
        ct = obj_dur[i]["@@object_lifecycle_end_timestamp"]
        while j < len(obj_dur):
            st = obj_dur[j]["@@object_lifecycle_start_timestamp"]
            if st > ct:
                break
            j = j + 1
        data.append([j - i, obj_dur[i]["@@index"]])
    feature_names = ["@@object_wip"]

    data.sort(key=lambda x: x[1])
    data = [[float(x[0])] for x in data]

    return data, feature_names

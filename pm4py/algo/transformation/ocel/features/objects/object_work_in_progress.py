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

    data, feature_names = object_lifecycle_duration.apply(ocel, parameters=parameters)
    obj_dur = pd.DataFrame(data, columns=feature_names)

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
    data = [[x[0]] for x in data]

    return data, feature_names

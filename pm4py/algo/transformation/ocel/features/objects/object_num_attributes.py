from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any
from enum import Enum
from pm4py.util import exec_utils


class Parameters(Enum):
    OBJECT_NUM_ATTRIBUTES = "num_obj_attr"


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None):
    """
    Enables the extraction of a given collection of numeric object attributes in the feature table
    (specified inside the "num_obj_attr" parameter)

    Parameters
    ----------------
    ocel
        OCEL
    parameters
        Parameters of the algorithm:
            - Parameters.OBJECT_NUM_ATTRIBUTES => collection of numeric attributes to consider for feature extraction

    Returns
    ----------------
    data
        Extracted feature values
    feature_names
        Feature names
    """
    if parameters is None:
        parameters = {}

    data = []
    feature_names = []

    ordered_objects = list(ocel.objects[ocel.object_id_column])
    object_num_attributes = exec_utils.get_param_value(Parameters.OBJECT_NUM_ATTRIBUTES, parameters, None)

    if object_num_attributes is not None:
        feature_names = feature_names + ["@@event_num_"+x for x in object_num_attributes]

        attr_values = {}
        for attr in object_num_attributes:
            values = ocel.objects[[ocel.object_id_column, attr]].dropna(subset=[attr]).to_dict("records")
            values = {x[ocel.object_id_column]: x[attr] for x in values}
            attr_values[attr] = values

        for obj in ordered_objects:
            data.append([])
            for attr in object_num_attributes:
                data[-1].append(float(attr_values[attr][obj]) if obj in attr_values[attr] else 0.0)

    return data, feature_names

from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any
from enum import Enum
from pm4py.util import exec_utils


class Parameters(Enum):
    EVENT_NUM_ATTRIBUTES = "num_ev_attr"


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None):
    """
    Enables the extraction of a given collection of numeric event attributes in the feature table
    (specified inside the "num_ev_attr" parameter).

    Parameters
    ----------------
    ocel
        OCEL
    parameters
        Parameters of the algorithm:
            - Parameters.EVENT_NUM_ATTRIBUTES => collection of numeric attributes to consider for feature extraction

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
    data = []
    feature_names = []

    event_num_attributes = exec_utils.get_param_value(Parameters.EVENT_NUM_ATTRIBUTES, parameters, None)

    if event_num_attributes:
        feature_names = feature_names + ["@@event_num_"+x for x in event_num_attributes]

        attr_values = {}
        for attr in event_num_attributes:
            values = ocel.events[[ocel.event_id_column, attr]].dropna(subset=[attr]).to_dict("records")
            values = {x[ocel.event_id_column]: x[attr] for x in values}
            attr_values[attr] = values

        for ev in ordered_events:
            data.append([])
            for attr in event_num_attributes:
                data[-1].append(float(attr_values[attr][ev]) if ev in attr_values[attr] else 0.0)

    return data, feature_names

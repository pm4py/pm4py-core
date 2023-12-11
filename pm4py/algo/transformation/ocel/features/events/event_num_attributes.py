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

    ordered_events = parameters["ordered_events"] if "ordered_events" in parameters else ocel.events[ocel.event_id_column].to_numpy()

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

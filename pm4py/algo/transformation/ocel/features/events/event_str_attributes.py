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
    EVENT_STR_ATTRIBUTES = "str_ev_attr"


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None):
    """
    One-hot-encoding of a given collection of string event attributes
    (specified inside the "str_ev_attr" parameter)

    Parameters
    ----------------
    ocel
        OCEL
    parameters
        Parameters of the algorithm:
            - Parameters.EVENT_STR_ATTRIBUTES => collection of string attributes to consider for feature extraction

    Returns
    ----------------
    data
        Extracted feature values
    feature_names
        Feature names
    """
    if parameters is None:
        parameters = {}

    ordered_events = parameters["ordered_events"] if "ordered_events" in parameters else ocel.events[
        ocel.event_id_column].to_numpy()

    data = []
    feature_names = []

    event_str_attributes = exec_utils.get_param_value(Parameters.EVENT_STR_ATTRIBUTES, parameters, None)

    if event_str_attributes is not None:
        dct_corr = {}
        dct_corr_values = {}

        for attr in event_str_attributes:
            events_attr_not_na = ocel.events[[ocel.event_id_column, attr]].dropna(subset=[attr]).to_dict("records")
            if events_attr_not_na:
                events_attr_not_na = {x[ocel.event_id_column]: str(x[attr]) for x in events_attr_not_na}
                dct_corr[attr] = events_attr_not_na
                dct_corr_values[attr] = list(set(events_attr_not_na.values()))

        dct_corr_list = list(dct_corr)

        for attr in dct_corr_list:
            for value in dct_corr_values[attr]:
                feature_names.append("@@event_attr_value_"+attr+"_"+value)

        for ev in ordered_events:
            data.append([0.0] * len(feature_names))
            count = 0
            for attr in dct_corr_list:
                if ev in dct_corr[attr]:
                    value = dct_corr[attr][ev]
                    idx = count + dct_corr_values[attr].index(value)
                    data[-1][idx] = 1.0
                count += len(dct_corr_values[attr])

    return data, feature_names

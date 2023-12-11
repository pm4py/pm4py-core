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
from pm4py.algo.transformation.ocel.features.events import algorithm as event_feature_extraction
from pm4py.algo.transformation.ocel.features.events_objects import prefix_features
from pm4py.objects.ocel.util import explode
from copy import copy
from enum import Enum
from pm4py.util import exec_utils


class Parameters(Enum):
    ENABLE_ALL_EO_FEATURES = "enable_all_eo_features"
    ENABLE_EVENT_POINTWISE_FEATURES = "enable_event_pointwise_features"
    ENABLE_PREFIX_FEATURES = "enable_prefix_features"


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None):
    """
    Extract features that are related to the different combinations of events and objects of the OCEL.

    Parameters
    -----------------
    ocel
        Object-centric event log
    parameters
        Parameters of the algorithm, including:
            - Parameters.ENABLE_ALL_EO_FEATURES => enables all the belowmentioned features
            - Parameters.ENABLE_EVENT_POINTWISE_FEATURES => enables the calculation of pointwise features for the events
            - Parameters.ENABLE_PREFIX_FEATURES => enables the prefix features

    Returns
    -----------------
    data
        Values of the features
    feature_names
        Names of the features
    """
    if parameters is None:
        parameters = {}

    enable_all = exec_utils.get_param_value(Parameters.ENABLE_ALL_EO_FEATURES, parameters, True)
    enable_event_pointwise_features = exec_utils.get_param_value(Parameters.ENABLE_EVENT_POINTWISE_FEATURES, parameters, enable_all)
    enable_prefix_features = exec_utils.get_param_value(Parameters.ENABLE_PREFIX_FEATURES, parameters, enable_all)

    exploded_ocel = explode.apply(ocel)
    ordered_events = exploded_ocel.events[exploded_ocel.event_id_column].to_numpy()
    parameters["ordered_events"] = ordered_events

    datas = []
    features_namess = []
    for i in range(len(ordered_events)):
        datas.append([])

    if enable_event_pointwise_features:
        parameters_efe = copy(parameters)
        parameters_efe["enable_all"] = False
        parameters_efe["enable_related_objects_features"] = False
        parameters_efe["enable_event_activity"] = True
        parameters_efe["enable_event_timestamp"] = True
        parameters_efe["enable_event_num_rel_objs_type"] = True
        parameters_efe["enable_event_str_attributes"] = True
        parameters_efe["enable_event_num_attributes"] = True
        parameters_efe["enable_event_start_ot"] = True
        data, feature_names = event_feature_extraction.apply(exploded_ocel, parameters=parameters_efe)
        for i in range(len(data)):
            datas[i] = datas[i] + data[i]
        features_namess = features_namess + feature_names

    if enable_prefix_features:
        data, feature_names = prefix_features.apply(exploded_ocel, parameters=parameters)
        for i in range(len(data)):
            datas[i] = datas[i] + data[i]
        features_namess = features_namess + feature_names

    return datas, features_namess

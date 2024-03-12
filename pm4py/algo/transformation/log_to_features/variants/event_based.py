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
from collections import Counter
from enum import Enum
from typing import Optional, List, Dict, Any, Tuple, Union

import numpy as np

from pm4py.objects.log.obj import EventLog
from pm4py.util import exec_utils
from pm4py.objects.conversion.log import converter


class Parameters(Enum):
    STR_EVENT_ATTRIBUTES = "str_ev_attr"
    NUM_EVENT_ATTRIBUTES = "num_ev_attr"
    FEATURE_NAMES = "feature_names"
    MIN_NUM_DIFF_STR_VALUES = "min_num_diff_str_values"
    MAX_NUM_DIFF_STR_VALUES = "max_num_diff_str_values"


def extract_all_ev_features_names_from_log(log: EventLog, str_ev_attr: List[str], num_ev_attr: List[str],
                                           parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> List[str]:
    """
    Extracts the feature names from an event log.

    Parameters
    ---------------
    log
        Event log
    str_ev_attr
        (if provided) list of string event attributes to consider in extracting the feature names
    num_ev_attr
        (if provided) list of integer event attributes to consider in extracting the feature names
    parameters
        Parameters, including:
            - MIN_NUM_DIFF_STR_VALUES => minimum number of distinct values to include an attribute as feature(s)
            - MAX_NUM_DIFF_STR_VALUES => maximum number of distinct values to include an attribute as feature(s)

    Returns
    ----------------
    feature_names
        List of feature names
    """
    if parameters is None:
        parameters = {}

    min_num_diff_str_values = exec_utils.get_param_value(Parameters.MIN_NUM_DIFF_STR_VALUES, parameters, 2)
    max_num_diff_str_values = exec_utils.get_param_value(Parameters.MAX_NUM_DIFF_STR_VALUES, parameters, 500)

    str_features = {}
    num_features = Counter()
    count_events = 0
    for trace in log:
        for event in trace:
            count_events += 1
            for attr_name in event:
                attr_value = event[attr_name]
                if isinstance(attr_value, str) and (str_ev_attr is None or attr_name in str_ev_attr):
                    if attr_name not in str_features:
                        str_features[attr_name] = set()
                    str_features[attr_name].add("event:" + attr_name + "@" + attr_value)
                elif isinstance(attr_value, int) or isinstance(attr_value, float):
                    if num_ev_attr is None or attr_name in num_ev_attr:
                        num_features["event:" + attr_name] += 1
    num_features = list({x for x, y in num_features.items() if y == count_events})
    str_features = list({z for x, y in str_features.items() for z in y if
                         min_num_diff_str_values <= len(y) <= max_num_diff_str_values})

    feature_names = str_features + num_features
    feature_names = sorted(feature_names)

    return feature_names


def extract_features(log: EventLog, feature_names: List[str], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Tuple[
    Any, List[str]]:
    """
    Extracts the matrix of the features from an event log

    Parameters
    ---------------
    log
        Event log
    feature_names
        Features to consider (in the given order)

    Returns
    -------------
    data
        Data to provide for decision tree learning
    feature_names
        Names of the features, in order
    """
    v1 = max(len(trace) for trace in log)
    v2 = len(feature_names)
    data = np.zeros((len(log), v1, v2), dtype=np.float32)

    for i1, trace in enumerate(log):
        for i2, event in enumerate(trace):
            str_features = set()
            num_features = {}
            for attr_name in event:
                attr_value = event[attr_name]
                if isinstance(attr_value, str):
                    str_features.add("event:" + attr_name + "@" + attr_value)
                elif isinstance(attr_value, int) or isinstance(attr_value, float):
                    num_features["event:" + attr_name] = float(attr_value)
            for attr in str_features:
                if attr in feature_names:
                    data[i1, i2, feature_names.index(attr)] = 1.0
            for attr in num_features:
                if attr in feature_names:
                    data[i1, i2, feature_names.index(attr)] = float(num_features[attr])

    return data, feature_names


def apply(log: EventLog, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Tuple[Any, List[str]]:
    """
    Extracts all the features for the traces of an event log (each trace becomes a vector of vectors, where each
    event has its own vector)

    Parameters
    -----------------
    log
        Event log
    parameters
        Parameters of the algorithm, including:
            - STR_EVENT_ATTRIBUTES => string event attributes to consider in the features extraction
            - NUM_EVENT_ATTRIBUTES => numeric event attributes to consider in the features extraction
            - FEATURE_NAMES => features to consider (in the given order)

    Returns
    -------------
    data
        Data to provide for decision tree learning
    feature_names
        Names of the features, in order
    """
    if parameters is None:
        parameters = {}

    str_ev_attr = exec_utils.get_param_value(Parameters.STR_EVENT_ATTRIBUTES, parameters, None)
    num_ev_attr = exec_utils.get_param_value(Parameters.NUM_EVENT_ATTRIBUTES, parameters, None)
    feature_names = exec_utils.get_param_value(Parameters.FEATURE_NAMES, parameters, None)

    log = converter.apply(log, variant=converter.Variants.TO_EVENT_LOG, parameters=parameters)

    if feature_names is None:
        feature_names = extract_all_ev_features_names_from_log(log, str_ev_attr, num_ev_attr, parameters=parameters)

    return extract_features(log, feature_names, parameters=parameters)

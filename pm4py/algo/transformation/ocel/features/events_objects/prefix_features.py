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
from pm4py.objects.ocel.util import event_prefix_suffix_per_obj
from collections import Counter


class Parameters(Enum):
    ENABLE_ALL_PREFIX_FEATURES = "enable_all_prefix_features"
    ENABLE_PREFIX_LENGTH = "enable_prefix_length"
    ENABLE_PREFIX_TIMEDIFF = "enable_prefix_timediff"
    ENABLE_PREFIX_ONE_HOT_ENCODING = "enable_prefix_1h_encoding"


def apply(exploded_ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None):
    """
    Gets some features out of the exploded OCEL which are based on the prefix of the event (for the current object)

    Parameters
    -----------------
    exploded_ocel
        Exploded object-centric event log
    parameters
        Parameters of the algorithm, including:
            - Parameters.ENABLE_ALL_PREFIX_FEATURES => enables the calculation of all the belowmentioned features
            - Parameters.ENABLE_PREFIX_LENGTH => adds the prefix length as a feature
            - Parameters.ENABLE_PREFIX_TIMEDIFF => adds the difference between the current event timestamp and the
                                                    first event related to the current object.
            - Parameters.ENABLE_PREFIX_ONE_HOT_ENCODING => one-hot-encodes the activities of the prefix.

    Returns
    -----------------
    data
        Values of the features
    feature_names
        Names of the features
    """
    if parameters is None:
        parameters = {}

    enable_all = exec_utils.get_param_value(Parameters.ENABLE_ALL_PREFIX_FEATURES, parameters, True)
    enable_prefix_length = exec_utils.get_param_value(Parameters.ENABLE_PREFIX_LENGTH, parameters, enable_all)
    enable_prefix_timediff = exec_utils.get_param_value(Parameters.ENABLE_PREFIX_TIMEDIFF, parameters, enable_all)
    enable_prefix_1h_encoding = exec_utils.get_param_value(Parameters.ENABLE_PREFIX_ONE_HOT_ENCODING, parameters, enable_all)

    ordered_events = parameters["ordered_events"] if "ordered_events" in parameters else exploded_ocel.events[
        exploded_ocel.event_id_column].to_numpy()

    datas = []
    feature_namess = []

    prefixes = event_prefix_suffix_per_obj.apply(exploded_ocel, parameters=parameters)
    for e1 in prefixes:
        for obj in prefixes[e1]:
            val = prefixes[e1][obj]
            break
        prefixes[e1] = val

    map0 = exploded_ocel.events[[exploded_ocel.event_id_column, exploded_ocel.event_activity, exploded_ocel.event_timestamp]].to_dict("records")
    all_activities = set()
    evid_act_map = {}
    evid_timest_map = {}
    for el in map0:
        evid = el[exploded_ocel.event_id_column]
        act = el[exploded_ocel.event_activity]
        timest = el[exploded_ocel.event_timestamp].timestamp()
        evid_act_map[evid] = act
        evid_timest_map[evid] = timest
        all_activities.add(act)
    all_activities = list(all_activities)

    for ev in ordered_events:
        datas.append([])

    if enable_prefix_length:
        feature_namess.append("@@ev_obj_pref_length")
        for i, ev in enumerate(ordered_events):
            if ev in prefixes:
                datas[i].append(float(len(prefixes[ev])))
            else:
                datas[i].append(0.0)

    if enable_prefix_timediff:
        feature_namess.append("@@ev_obj_pref_timediff")
        for i, ev in enumerate(ordered_events):
            if ev in prefixes:
                datas[i].append(float(evid_timest_map[ev] - evid_timest_map[prefixes[ev][0]]))
            else:
                datas[i].append(0.0)

    if enable_prefix_1h_encoding:
        for act in all_activities:
            feature_namess.append("@@ev_obj_pref_act_"+act)
        for i, ev in enumerate(ordered_events):
            pref_activities = Counter()
            if ev in prefixes:
                pref_activities = Counter([evid_act_map[x] for x in prefixes[ev]])
            arr = []
            for act in all_activities:
                arr.append(float(pref_activities[act]))
            datas[i] = datas[i] + arr

    return datas, feature_namess

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
from enum import Enum
from typing import Optional, Dict, Any, Union, Tuple, List, Set

import pandas as pd

from pm4py.objects.conversion.log import converter
from pm4py.objects.log.obj import EventLog, Trace, Event
from pm4py.objects.log.util import dataframe_utils
from pm4py.util import constants, pandas_utils
from pm4py.util import exec_utils
from pm4py.util import xes_constants as xes
from pm4py.util import xes_constants


class Parameters(Enum):
    ENABLE_ACTIVITY_DEF_REPRESENTATION = "enable_activity_def_representation"
    ENABLE_SUCC_DEF_REPRESENTATION = "enable_succ_def_representation"
    STR_TRACE_ATTRIBUTES = "str_tr_attr"
    STR_EVENT_ATTRIBUTES = "str_ev_attr"
    NUM_TRACE_ATTRIBUTES = "num_tr_attr"
    NUM_EVENT_ATTRIBUTES = "num_ev_attr"
    STR_EVSUCC_ATTRIBUTES = "str_evsucc_attr"
    FEATURE_NAMES = "feature_names"
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    RESOURCE_KEY = constants.PARAMETER_CONSTANT_RESOURCE_KEY
    EPSILON = "epsilon"
    DEFAULT_NOT_PRESENT = "default_not_present"
    ENABLE_ALL_EXTRA_FEATURES = "enable_all_extra_features"
    ENABLE_CASE_DURATION = "enable_case_duration"
    ADD_CASE_IDENTIFIER_COLUMN = "add_case_identifier_column"
    ENABLE_TIMES_FROM_FIRST_OCCURRENCE = "enable_times_from_first_occurrence"
    ENABLE_TIMES_FROM_LAST_OCCURRENCE = "enable_times_from_last_occurrence"
    ENABLE_DIRECT_PATHS_TIMES_LAST_OCC = "enable_direct_paths_times_last_occ"
    ENABLE_INDIRECT_PATHS_TIMES_LAST_OCC = "enable_indirect_paths_times_last_occ"
    ENABLE_WORK_IN_PROGRESS = "enable_work_in_progress"
    ENABLE_RESOURCE_WORKLOAD = "enable_resource_workload"
    ENABLE_FIRST_LAST_ACTIVITY_INDEX = "enable_first_last_activity_index"
    ENABLE_MAX_CONCURRENT_EVENTS = "enable_max_concurrent_events"
    ENABLE_MAX_CONCURRENT_EVENTS_PER_ACTIVITY = "enable_max_concurrent_events_per_activity"
    CASE_ATTRIBUTE_PREFIX = constants.CASE_ATTRIBUTE_PREFIX


def max_concurrent_events(log: EventLog, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Tuple[Any, List[str]]:
    """
    Counts for every trace the maximum number of events (of any activity) that happen concurrently
    (e.g., their time intervals [st1, ct1] and [st2, ct2] have non-empty intersection).

    Parameters
    -----------------
    log
        Event log
    parameters
        Parameters of the algorithm

    Returns
    ----------------
    data
        Numeric value of the features
    feature_names
        Names of the features
    """
    if parameters is None:
        parameters = {}

    start_timestamp_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY, parameters, xes_constants.DEFAULT_TIMESTAMP_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes_constants.DEFAULT_TIMESTAMP_KEY)

    data = []
    feature_names = ["@@max_concurrent_activities_general"]

    for trace in log:
        max_conc = 0
        i = 0
        while i < len(trace)-1:
            conc = 0
            ct = trace[i][timestamp_key].timestamp()
            j = i + 1
            while j < len(trace):
                st = trace[j][start_timestamp_key].timestamp()
                if st > ct:
                    break
                conc = conc + 1
                j = j + 1
            if conc > max_conc:
                max_conc = conc
            i = i + 1
        data.append([float(max_conc)])

    return data, feature_names


def max_concurrent_events_per_activity(log: EventLog, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Tuple[Any, List[str]]:
    """
    Counts for every trace and every activity the maximum number of events of the given activity that happen concurrently
    (e.g., their time intervals [st1, ct1] and [st2, ct2] have non-empty intersection).

    Parameters
    -----------------
    log
        Event log
    parameters
        Parameters of the algorithm

    Returns
    ----------------
    data
        Numeric value of the features
    feature_names
        Names of the features
    """
    if parameters is None:
        parameters = {}

    start_timestamp_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY, parameters, xes_constants.DEFAULT_TIMESTAMP_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes_constants.DEFAULT_TIMESTAMP_KEY)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)

    activities = list(set(y[activity_key] for x in log for y in x))

    data = []
    feature_names = ["@@max_concurrent_activities_like_"+x for x in activities]

    for trace in log:
        max_conc_act = {act: 0 for act in activities}
        i = 0
        while i < len(trace)-1:
            conc = 0
            act = trace[i][activity_key]
            ct = trace[i][timestamp_key].timestamp()
            j = i + 1
            while j < len(trace):
                st = trace[j][start_timestamp_key].timestamp()
                actj = trace[j][activity_key]
                if st > ct:
                    break
                if act == actj:
                    conc = conc + 1
                j = j + 1
            i = i + 1
            max_conc_act[act] = max(max_conc_act[act], conc)
        arr = []
        for act in activities:
            arr.append(float(max_conc_act[act]))
        data.append(arr)

    return data, feature_names


def resource_workload(log: EventLog, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Tuple[Any, List[str]]:
    """
    Calculates for each case, and for each resource of the log, the workload of the resource during
    the lead time of a case. Defaults if a resource is not contained in a case.

    Parameters
    -----------------
    log
        Event log
    parameters
        Parameters of the algorithm

    Returns
    ----------------
    data
        Numeric value of the features
    feature_names
        Names of the features
    """
    if parameters is None:
        parameters = {}

    from intervaltree.intervaltree import IntervalTree, Interval

    start_timestamp_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY, parameters, xes_constants.DEFAULT_TIMESTAMP_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes_constants.DEFAULT_TIMESTAMP_KEY)
    resource_key = exec_utils.get_param_value(Parameters.RESOURCE_KEY, parameters, xes_constants.DEFAULT_RESOURCE_KEY)
    epsilon = exec_utils.get_param_value(Parameters.EPSILON, parameters, 0.000001)
    default_not_present = exec_utils.get_param_value(Parameters.DEFAULT_NOT_PRESENT, parameters, 0)

    tree_dict = {}
    for case in log:
        if case:
            resources = set(x[resource_key] for x in case if resource_key in x)
            st = case[0][start_timestamp_key].timestamp() - epsilon
            ct = case[-1][timestamp_key].timestamp() + epsilon
            for res in resources:
                if res not in tree_dict:
                    tree_dict[res] = IntervalTree()
                tree_dict[res].add(Interval(st, ct))

    resources_list = sorted(list(tree_dict))

    data = []
    feature_names = ["resource_workload@@"+r for r in resources_list]

    for case in log:
        data.append([])
        resources = set(x[resource_key] for x in case if resource_key in x)
        st = case[0][start_timestamp_key].timestamp() - epsilon
        ct = case[-1][timestamp_key].timestamp() + epsilon
        for res in resources_list:
            if res in resources:
                data[-1].append(float(len(tree_dict[res][st:ct])))
            else:
                data[-1].append(float(default_not_present))

    return data, feature_names


def work_in_progress(log: EventLog, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Tuple[Any, List[str]]:
    """
    Calculates for each case, and for each resource of the log, the number of cases which are open during
    the lead time of the case.

    Parameters
    -----------------
    log
        Event log
    parameters
        Parameters of the algorithm

    Returns
    ----------------
    data
        Numeric value of the features
    feature_names
        Names of the features
    """
    if parameters is None:
        parameters = {}

    from intervaltree.intervaltree import IntervalTree, Interval

    start_timestamp_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY, parameters, xes_constants.DEFAULT_TIMESTAMP_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes_constants.DEFAULT_TIMESTAMP_KEY)
    epsilon = exec_utils.get_param_value(Parameters.EPSILON, parameters, 0.000001)
    default_not_present = exec_utils.get_param_value(Parameters.DEFAULT_NOT_PRESENT, parameters, 0)

    tree = IntervalTree()
    for case in log:
        if case:
            st = case[0][start_timestamp_key].timestamp() - epsilon
            ct = case[-1][timestamp_key].timestamp() + epsilon
            tree.add(Interval(st, ct))

    data = []
    feature_names = ["@@work_in_progress"]

    for case in log:
        if case:
            st = case[0][start_timestamp_key].timestamp() - epsilon
            ct = case[-1][timestamp_key].timestamp() + epsilon
            data.append([float(len(tree[st:ct]))])
        else:
            data.append([float(default_not_present)])

    return data, feature_names


def indirect_paths_times_last_occ(log: EventLog, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Tuple[Any, List[str]]:
    """
    Calculates for each case, and for each indirect path of the case, the difference between the start timestamp
    of the later event and the completion timestamp of the first event. Defaults if a path is not present in a case.

    Parameters
    -----------------
    log
        Event log
    parameters
        Parameters of the algorithm

    Returns
    ----------------
    data
        Numeric value of the features
    feature_names
        Names of the features
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    start_timestamp_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY, parameters, xes_constants.DEFAULT_TIMESTAMP_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes_constants.DEFAULT_TIMESTAMP_KEY)
    default_not_present = exec_utils.get_param_value(Parameters.DEFAULT_NOT_PRESENT, parameters, 0)

    all_paths = set()
    for trace in log:
        for i in range(len(trace)-1):
            for j in range(i+2, len(trace)):
                all_paths.add((trace[i][activity_key], trace[j][activity_key]))
    all_paths = sorted(list(all_paths))

    data = []
    feature_names = []
    for p in all_paths:
        feature_names.append("indirectPathPerformanceLastOcc@@"+p[0]+"##"+p[1])

    for trace in log:
        data.append([])
        trace_paths_perf = {}
        for i in range(len(trace)-1):
            for j in range(i+2, len(trace)):
                p = (trace[i][activity_key], trace[j][activity_key])
                tc = trace[i][timestamp_key].timestamp()
                ts = trace[j][start_timestamp_key].timestamp()
                if ts > tc:
                    trace_paths_perf[p] = ts - tc
        for p in all_paths:
            if p in trace_paths_perf:
                data[-1].append(float(trace_paths_perf[p]))
            else:
                data[-1].append(float(default_not_present))

    return data, feature_names


def direct_paths_times_last_occ(log: EventLog, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Tuple[Any, List[str]]:
    """
    Calculates for each case, and for each direct path of the case, the difference between the start timestamp
    of the later event and the completion timestamp of the first event. Defaults if a path is not present in a case.

    Parameters
    -----------------
    log
        Event log
    parameters
        Parameters of the algorithm

    Returns
    ----------------
    data
        Numeric value of the features
    feature_names
        Names of the features
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    start_timestamp_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY, parameters, xes_constants.DEFAULT_TIMESTAMP_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes_constants.DEFAULT_TIMESTAMP_KEY)
    default_not_present = exec_utils.get_param_value(Parameters.DEFAULT_NOT_PRESENT, parameters, 0)

    all_paths = set()
    for trace in log:
        for i in range(len(trace)-1):
            all_paths.add((trace[i][activity_key], trace[i+1][activity_key]))
    all_paths = sorted(list(all_paths))

    data = []
    feature_names = []
    for p in all_paths:
        feature_names.append("directPathPerformanceLastOcc@@"+p[0]+"##"+p[1])

    for trace in log:
        data.append([])
        trace_paths_perf = {}
        for i in range(len(trace)-1):
            p = (trace[i][activity_key], trace[i+1][activity_key])
            tc = trace[i][timestamp_key].timestamp()
            ts = trace[i+1][start_timestamp_key].timestamp()
            if ts > tc:
                trace_paths_perf[p] = ts - tc
        for p in all_paths:
            if p in trace_paths_perf:
                data[-1].append(float(trace_paths_perf[p]))
            else:
                data[-1].append(float(default_not_present))

    return data, feature_names


def times_from_first_occurrence_activity_case(log: EventLog, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Tuple[Any, List[str]]:
    """
    Calculates for each case, and for each activity, the times from the start to the case, and to the end of the case,
    from the first occurrence of the activity in the case.

    Parameters
    -----------------
    log
        Event log
    parameters
        Parameters of the algorithm

    Returns
    ----------------
    data
        Numeric value of the features
    feature_names
        Names of the features
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    start_timestamp_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY, parameters, xes_constants.DEFAULT_TIMESTAMP_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes_constants.DEFAULT_TIMESTAMP_KEY)
    default_not_present = exec_utils.get_param_value(Parameters.DEFAULT_NOT_PRESENT, parameters, 0)

    activities_log = set()
    for trace in log:
        for event in trace:
            activities_log.add(event[activity_key])
    activities_log = sorted(list(activities_log))

    data = []
    feature_names = []
    for act in activities_log:
        feature_names.append("startToFirstOcc@@"+act)
        feature_names.append("firstOccToEnd@@"+act)

    for trace in log:
        data.append([])
        activities_occ = {}
        for i in range(len(trace)):
            if not trace[i][activity_key] in activities_occ:
                activities_occ[trace[i][activity_key]] = i
        for act in activities_log:
            if act in activities_occ:
                ev = trace[activities_occ[act]]
                this_ev_st = ev[start_timestamp_key].timestamp()
                this_ev_ct = ev[timestamp_key].timestamp()
                start_ev_ct = trace[0][timestamp_key].timestamp()
                end_ev_st = trace[-1][start_timestamp_key].timestamp()
                data[-1].append(float(this_ev_st - start_ev_ct))
                data[-1].append(float(end_ev_st - this_ev_ct))
            else:
                data[-1].append(float(default_not_present))
                data[-1].append(float(default_not_present))

    return data, feature_names


def times_from_last_occurrence_activity_case(log: EventLog, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Tuple[Any, List[str]]:
    """
    Calculates for each case, and for each activity, the times from the start to the case, and to the end of the case,
    from the last occurrence of the activity in the case.

    Parameters
    -----------------
    log
        Event log
    parameters
        Parameters of the algorithm

    Returns
    ----------------
    data
        Numeric value of the features
    feature_names
        Names of the features
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    start_timestamp_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY, parameters, xes_constants.DEFAULT_TIMESTAMP_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes_constants.DEFAULT_TIMESTAMP_KEY)
    default_not_present = exec_utils.get_param_value(Parameters.DEFAULT_NOT_PRESENT, parameters, 0)

    activities_log = set()
    for trace in log:
        for event in trace:
            activities_log.add(event[activity_key])
    activities_log = sorted(list(activities_log))

    data = []
    feature_names = []
    for act in activities_log:
        feature_names.append("startToLastOcc@@"+act)
        feature_names.append("lastOccToEnd@@"+act)

    for trace in log:
        data.append([])
        activities_occ = {}
        for i in range(len(trace)):
            activities_occ[trace[i][activity_key]] = i
        for act in activities_log:
            if act in activities_occ:
                ev = trace[activities_occ[act]]
                this_ev_st = ev[start_timestamp_key].timestamp()
                this_ev_ct = ev[timestamp_key].timestamp()
                start_ev_ct = trace[0][timestamp_key].timestamp()
                end_ev_st = trace[-1][start_timestamp_key].timestamp()
                data[-1].append(float(this_ev_st - start_ev_ct))
                data[-1].append(float(end_ev_st - this_ev_ct))
            else:
                data[-1].append(float(default_not_present))
                data[-1].append(float(default_not_present))

    return data, feature_names


def first_last_activity_index_trace(log: EventLog, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Tuple[Any, List[str]]:
    """
    Consider as features the first and the last index of an activity inside a case

    Parameters
    ------------------
    log
        Event log
    parameters
        Parameters, including:
        - Parameters.ACTIVITY_KEY => the attribute to use as activity
        - Parameters.DEFAULT_NOT_PRESENT => the replacement value for activities that are not present for the specific case

    Returns
    -----------------
    data
        Numeric value of the features
    feature_names
        Names of the features
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    default_not_present = exec_utils.get_param_value(Parameters.DEFAULT_NOT_PRESENT, parameters, -1)

    activities_log = set()
    for trace in log:
        for event in trace:
            activities_log.add(event[activity_key])
    activities_log = sorted(list(activities_log))

    data = []
    feature_names = []
    for act in activities_log:
        feature_names.append("firstIndexAct@@"+act)
        feature_names.append("lastIndexAct@@"+act)
    for trace in log:
        data.append([])

        first_occ = {}
        last_occ = {}
        for index, event in enumerate(trace):
            act = event[activity_key]
            last_occ[act] = index
            if act not in first_occ:
                first_occ[act] = index
        for act in activities_log:
            if act not in first_occ:
                data[-1].append(float(default_not_present))
                data[-1].append(float(default_not_present))
            else:
                data[-1].append(float(first_occ[act]))
                data[-1].append(float(last_occ[act]))

    return data, feature_names


def case_duration(log: EventLog, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Tuple[Any, List[str]]:
    """
    Calculates for each case, the case duration (and adds it as a feature)

    Parameters
    -----------------
    log
        Event log
    parameters
        Parameters of the algorithm

    Returns
    ----------------
    data
        Numeric value of the features
    feature_names
        Names of the features
    """
    if parameters is None:
        parameters = {}

    start_timestamp_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY, parameters, xes_constants.DEFAULT_TIMESTAMP_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes_constants.DEFAULT_TIMESTAMP_KEY)

    feature_names = ["@@caseDuration"]
    data = []
    for trace in log:
        if trace:
            data.append([float(trace[-1][timestamp_key].timestamp() - trace[0][start_timestamp_key].timestamp())])
        else:
            data.append([0.0])

    return data, feature_names


def get_string_trace_attribute_rep(trace: Trace, trace_attribute: str) -> str:
    """
    Get a representation of the feature name associated to a string trace attribute value

    Parameters
    ------------
    trace
        Trace of the log
    trace_attribute
        Attribute of the trace to consider

    Returns
    ------------
    rep
        Representation of the feature name associated to a string trace attribute value
    """
    if trace_attribute in trace.attributes:
        return "trace:" + str(trace_attribute) + "@" + str(trace.attributes[trace_attribute])
    return "trace:" + str(trace_attribute) + "@UNDEFINED"


def get_all_string_trace_attribute_values(log: EventLog, trace_attribute: str) -> List[str]:
    """
    Get all string trace attribute values representations for a log

    Parameters
    ------------
    log
        Trace log
    trace_attribute
        Attribute of the trace to consider

    Returns
    ------------
    list
        List containing for each trace a representation of the feature name associated to the attribute
    """
    values = set()
    for trace in log:
        values.add(get_string_trace_attribute_rep(trace, trace_attribute))
    return list(sorted(values))


def get_string_event_attribute_rep(event: Event, event_attribute: str) -> str:
    """
    Get a representation of the feature name associated to a string event attribute value

    Parameters
    ------------
    event
        Single event of a trace
    event_attribute
        Event attribute to consider

    Returns
    ------------
    rep
        Representation of the feature name associated to a string event attribute value
    """
    return "event:" + str(event_attribute) + "@" + str(event[event_attribute])


def get_values_event_attribute_for_trace(trace: Trace, event_attribute: str) -> Set[str]:
    """
    Get all the representations for the events of a trace associated to a string event attribute values

    Parameters
    -------------
    trace
        Trace of the log
    event_attribute
        Event attribute to consider

    Returns
    -------------
    values
        All feature names present for the given attribute in the given trace
    """
    values_trace = set()
    for event in trace:
        if event_attribute in event:
            values_trace.add(get_string_event_attribute_rep(event, event_attribute))
    if not values_trace:
        values_trace.add("event:" + str(event_attribute) + "@UNDEFINED")
    return values_trace


def get_all_string_event_attribute_values(log: EventLog, event_attribute: str) -> List[str]:
    """
    Get all the representations for all the traces of the log associated to a string event attribute values

    Parameters
    ------------
    log
        Trace of the log
    event_attribute
        Event attribute to consider

    Returns
    ------------
    values
        All feature names present for the given attribute in the given log
    """
    values = set()
    for trace in log:
        values = values.union(get_values_event_attribute_for_trace(trace, event_attribute))
    return list(sorted(values))


def get_string_event_attribute_succession_rep(event1: Event, event2: Event, event_attribute: str) -> str:
    """
    Get a representation of the feature name associated to a string event attribute value

    Parameters
    ------------
    event1
        First event of the succession
    event2
        Second event of the succession
    event_attribute
        Event attribute to consider

    Returns
    ------------
    rep
        Representation of the feature name associated to a string event attribute value
    """
    return "succession:" + str(event_attribute) + "@" + str(event1[event_attribute]) + "#" + str(
        event2[event_attribute])


def get_values_event_attribute_succession_for_trace(trace: Trace, event_attribute: str) -> Set[str]:
    """
    Get all the representations for the events of a trace associated to a string event attribute succession values

    Parameters
    -------------
    trace
        Trace of the log
    event_attribute
        Event attribute to consider

    Returns
    -------------
    values
        All feature names present for the given attribute succession in the given trace
    """
    values_trace = set()
    for i in range(len(trace) - 1):
        event1 = trace[i]
        event2 = trace[i + 1]
        if event_attribute in event1 and event_attribute in event2:
            values_trace.add(get_string_event_attribute_succession_rep(event1, event2, event_attribute))
    if not values_trace:
        values_trace.add("succession:" + str(event_attribute) + "@UNDEFINED")
    return values_trace


def get_all_string_event_succession_attribute_values(log: EventLog, event_attribute: str) -> List[str]:
    """
    Get all the representations for all the traces of the log associated to a string event attribute succession values

    Parameters
    ------------
    log
        Trace of the log
    event_attribute
        Event attribute to consider

    Returns
    ------------
    values
        All feature names present for the given attribute succession in the given log
    """
    values = set()
    for trace in log:
        values = values.union(get_values_event_attribute_succession_for_trace(trace, event_attribute))
    return list(sorted(values))


def get_numeric_trace_attribute_rep(trace_attribute: str) -> str:
    """
    Get the feature name associated to a numeric trace attribute

    Parameters
    ------------
    trace_attribute
        Name of the trace attribute

    Returns
    ------------
    feature_name
        Name of the feature
    """
    return "trace:" + trace_attribute


def get_numeric_trace_attribute_value(trace: Trace, trace_attribute: str) -> Union[int, float]:
    """
    Get the value of a numeric trace attribute from a given trace

    Parameters
    ------------
    trace
        Trace of the log

    Returns
    ------------
    value
        Value of the numeric trace attribute for the given trace
    """
    if trace_attribute in trace.attributes:
        return float(trace.attributes[trace_attribute])
    raise Exception("at least a trace without trace attribute: " + trace_attribute)


def get_numeric_event_attribute_rep(event_attribute: str) -> str:
    """
    Get the feature name associated to a numeric event attribute

    Parameters
    ------------
    event_attribute
        Name of the event attribute

    Returns
    -------------
    feature_name
        Name of the feature
    """
    return "event:" + event_attribute


def get_numeric_event_attribute_value(event: Event, event_attribute: str) -> Union[int, float]:
    """
    Get the value of a numeric event attribute from a given event

    Parameters
    -------------
    event
        Event

    Returns
    -------------
    value
        Value of the numeric event attribute for the given event
    """
    if event_attribute in event:
        return float(event[event_attribute])
    return None


def get_numeric_event_attribute_value_trace(trace: Trace, event_attribute: str) -> Union[int, float]:
    """
    Get the value of the last occurrence of a numeric event attribute given a trace

    Parameters
    -------------
    trace
        Trace of the log

    Returns
    -------------
    value
        Value of the last occurrence of a numeric trace attribute for the given trace
    """
    non_zero_values = []
    for event in trace:
        value = get_numeric_event_attribute_value(event, event_attribute)
        if value is not None:
            non_zero_values.append(value)
    if len(non_zero_values) > 0:
        return non_zero_values[-1]
    raise Exception("at least a trace without any event with event attribute: " + event_attribute)


def get_default_representation_with_attribute_names(log: EventLog, parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
                                                    feature_names: Optional[List[str]] = None) -> Tuple[
    Any, List[str], List[str], List[str], List[str], List[str]]:
    """
    Gets the default data representation of an event log (for process tree building)
    returning also the attribute names

    Parameters
    -------------
    log
        Trace log
    parameters
        Possible parameters of the algorithm
    feature_names
        (If provided) Feature to use in the representation of the log

    Returns
    -------------
    data
        Data to provide for decision tree learning
    feature_names
        Names of the features, in order
    """
    from pm4py.statistics.attributes.log.select import select_attributes_from_log_for_tree

    if parameters is None:
        parameters = {}

    enable_activity_def_representation = exec_utils.get_param_value(Parameters.ENABLE_ACTIVITY_DEF_REPRESENTATION,
                                                                    parameters, False)
    enable_succ_def_representation = exec_utils.get_param_value(Parameters.ENABLE_SUCC_DEF_REPRESENTATION, parameters,
                                                                False)

    activity_key = parameters[
        constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY
    blacklist = parameters["blacklist"] if "blacklist" in parameters else []

    str_tr_attr, str_ev_attr, num_tr_attr, num_ev_attr = select_attributes_from_log_for_tree(log)
    str_evsucc_attr = None

    if enable_succ_def_representation:
        str_evsucc_attr = [activity_key]
    if enable_activity_def_representation and activity_key not in str_ev_attr:
        str_ev_attr.append(activity_key)

    str_tr_attr = [x for x in str_tr_attr if x not in blacklist]
    str_ev_attr = [x for x in str_ev_attr if x not in blacklist]
    num_tr_attr = [x for x in num_tr_attr if x not in blacklist]
    num_ev_attr = [x for x in num_ev_attr if x not in blacklist]
    if str_evsucc_attr is not None:
        str_evsucc_attr = [x for x in str_evsucc_attr if x not in blacklist]

    data, feature_names = get_representation(log, str_tr_attr, str_ev_attr, num_tr_attr, num_ev_attr,
                                             str_evsucc_attr=str_evsucc_attr,
                                             feature_names=feature_names)

    return data, feature_names, str_tr_attr, str_ev_attr, num_tr_attr, num_ev_attr


def get_default_representation(log: EventLog, parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
                               feature_names: Optional[List[str]] = None) -> Tuple[Any, List[str]]:
    """
    Gets the default data representation of an event log (for process tree building)

    Parameters
    -------------
    log
        Trace log
    parameters
        Possible parameters of the algorithm
    feature_names
        (If provided) Feature to use in the representation of the log

    Returns
    -------------
    data
        Data to provide for decision tree learning
    feature_names
        Names of the features, in order
    """
    from pm4py.statistics.attributes.log.select import select_attributes_from_log_for_tree

    if parameters is None:
        parameters = {}

    enable_activity_def_representation = exec_utils.get_param_value(Parameters.ENABLE_ACTIVITY_DEF_REPRESENTATION,
                                                                    parameters, True)
    enable_succ_def_representation = exec_utils.get_param_value(Parameters.ENABLE_SUCC_DEF_REPRESENTATION, parameters,
                                                                True)

    activity_key = parameters[
        constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY
    blacklist = parameters["blacklist"] if "blacklist" in parameters else []

    str_tr_attr, str_ev_attr, num_tr_attr, num_ev_attr = select_attributes_from_log_for_tree(log)
    str_evsucc_attr = None

    if enable_succ_def_representation:
        str_evsucc_attr = [activity_key]
    if enable_activity_def_representation and activity_key not in str_ev_attr:
        str_ev_attr.append(activity_key)

    str_tr_attr = [x for x in str_tr_attr if x not in blacklist]
    str_ev_attr = [x for x in str_ev_attr if x not in blacklist]
    num_tr_attr = [x for x in num_tr_attr if x not in blacklist]
    num_ev_attr = [x for x in num_ev_attr if x not in blacklist]
    if str_evsucc_attr is not None:
        str_evsucc_attr = [x for x in str_evsucc_attr if x not in blacklist]

    return get_representation(log, str_tr_attr, str_ev_attr, num_tr_attr, num_ev_attr, str_evsucc_attr=str_evsucc_attr,
                              feature_names=feature_names)


def get_representation(log: EventLog, str_tr_attr: List[str], str_ev_attr: List[str], num_tr_attr: List[str],
                       num_ev_attr: List[str], str_evsucc_attr: Optional[List[str]] = None,
                       feature_names: Optional[List[str]] = None) -> Tuple[Any, List[str]]:
    """
    Get a representation of the event log that is suited for the data part of the decision tree learning

    NOTE: this function only encodes the last value seen for each attribute

    Parameters
    -------------
    log
        Trace log
    str_tr_attr
        List of string trace attributes to consider in data vector creation
    str_ev_attr
        List of string event attributes to consider in data vector creation
    num_tr_attr
        List of numeric trace attributes to consider in data vector creation
    num_ev_attr
        List of numeric event attributes to consider in data vector creation
    str_evsucc_attr
        List of attributes succession of values to consider in data vector creation
    feature_names
        (If provided) Feature to use in the representation of the log

    Returns
    -------------
    data
        Data to provide for decision tree learning
    feature_names
        Names of the features, in order
    """
    data = []
    dictionary = {}
    count = 0
    if feature_names is None:
        feature_names = []
        for trace_attribute in str_tr_attr:
            values = get_all_string_trace_attribute_values(log, trace_attribute)
            for value in values:
                dictionary[value] = count
                feature_names.append(value)
                count = count + 1
        for event_attribute in str_ev_attr:
            values = get_all_string_event_attribute_values(log, event_attribute)
            for value in values:
                dictionary[value] = count
                feature_names.append(value)
                count = count + 1
        for trace_attribute in num_tr_attr:
            dictionary[get_numeric_trace_attribute_rep(trace_attribute)] = count
            feature_names.append(get_numeric_trace_attribute_rep(trace_attribute))
            count = count + 1
        for event_attribute in num_ev_attr:
            dictionary[get_numeric_event_attribute_rep(event_attribute)] = count
            feature_names.append(get_numeric_event_attribute_rep(event_attribute))
            count = count + 1
        if str_evsucc_attr:
            for event_attribute in str_evsucc_attr:
                values = get_all_string_event_succession_attribute_values(log, event_attribute)
                for value in values:
                    dictionary[value] = count
                    feature_names.append(value)
                    count = count + 1
    else:
        count = len(feature_names)
        for index, value in enumerate(feature_names):
            dictionary[value] = index

    for trace in log:
        trace_rep = [0.0] * count
        for trace_attribute in str_tr_attr:
            trace_attr_rep = get_string_trace_attribute_rep(trace, trace_attribute)
            if trace_attr_rep in dictionary:
                trace_rep[dictionary[trace_attr_rep]] = 1.0
        for event_attribute in str_ev_attr:
            values = get_values_event_attribute_for_trace(trace, event_attribute)
            for value in values:
                if value in dictionary:
                    trace_rep[dictionary[value]] = 1.0
        for trace_attribute in num_tr_attr:
            this_value = get_numeric_trace_attribute_rep(trace_attribute)
            if this_value in dictionary:
                trace_rep[dictionary[this_value]] = get_numeric_trace_attribute_value(
                    trace, trace_attribute)
        for event_attribute in num_ev_attr:
            this_value = get_numeric_event_attribute_rep(event_attribute)
            if this_value in dictionary:
                trace_rep[dictionary[this_value]] = get_numeric_event_attribute_value_trace(
                    trace, event_attribute)
        if str_evsucc_attr:
            for event_attribute in str_evsucc_attr:
                values = get_values_event_attribute_succession_for_trace(trace, event_attribute)
                for value in values:
                    if value in dictionary:
                        trace_rep[dictionary[value]] = 1.0
        data.append(trace_rep)
    # data = np.asarray(data)
    return data, feature_names


def apply(log: EventLog, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Tuple[Any, List[str]]:
    """
    Extract the features from an event log (a vector for each trace)

    Parameters
    -----------------
    log
        Log
    parameters
        Parameters of the algorithm, including:
        - STR_TRACE_ATTRIBUTES => string trace attributes to consider in the features extraction
        - STR_EVENT_ATTRIBUTES => string event attributes to consider in the features extraction
        - NUM_TRACE_ATTRIBUTES => numeric trace attributes to consider in the features extraction
        - NUM_EVENT_ATTRIBUTES => numeric event attributes to consider in the features extraction
        - STR_EVSUCC_ATTRIBUTES => succession of event attributes to consider in the features extraction
        - FEATURE_NAMES => features to consider (in the given order)
        - ENABLE_ALL_EXTRA_FEATURES => enables all the extra features
        - ENABLE_CASE_DURATION => enables the case duration as additional feature
        - ENABLE_TIMES_FROM_FIRST_OCCURRENCE => enables the addition of the times from start of the case, to the end
        of the case, from the first occurrence of an activity of a case
        - ADD_CASE_IDENTIFIER_COLUMN => adds the case identifier (string) as column of the feature table (default: False)
        - ENABLE_TIMES_FROM_LAST_OCCURRENCE => enables the addition of the times from start of the case, to the end
        of the case, from the last occurrence of an activity of a case
        - ENABLE_DIRECT_PATHS_TIMES_LAST_OCC => add the duration of the last occurrence of a directed (i, i+1) path
        in the case as feature
        - ENABLE_INDIRECT_PATHS_TIMES_LAST_OCC => add the duration of the last occurrence of an indirect (i, j) path
        in the case as feature
        - ENABLE_WORK_IN_PROGRESS => enables the work in progress (number of concurrent cases) as a feature
        - ENABLE_RESOURCE_WORKLOAD => enables the resource workload as a feature
        - ENABLE_FIRST_LAST_ACTIVITY_INDEX => enables the insertion of the indexes of the activities as features
        - ENABLE_MAX_CONCURRENT_EVENTS => enables the count of the number of concurrent events inside a case
        - ENABLE_MAX_CONCURRENT_EVENTS_PER_ACTIVITY => enables the count of the number of concurrent events per activity

    Returns
    -------------
    data
        Data to provide for decision tree learning
    feature_names
        Names of the features, in order
    """
    if parameters is None:
        parameters = {}

    str_tr_attr = exec_utils.get_param_value(Parameters.STR_TRACE_ATTRIBUTES, parameters, None)
    num_tr_attr = exec_utils.get_param_value(Parameters.NUM_TRACE_ATTRIBUTES, parameters, None)
    str_ev_attr = exec_utils.get_param_value(Parameters.STR_EVENT_ATTRIBUTES, parameters, None)
    num_ev_attr = exec_utils.get_param_value(Parameters.NUM_EVENT_ATTRIBUTES, parameters, None)
    str_evsucc_attr = exec_utils.get_param_value(Parameters.STR_EVSUCC_ATTRIBUTES, parameters, None)
    feature_names = exec_utils.get_param_value(Parameters.FEATURE_NAMES, parameters, None)

    at_least_one_provided = (str_tr_attr is not None) or (num_tr_attr is not None) or (str_ev_attr is not None) or (num_ev_attr is not None)

    if str_tr_attr is None:
        str_tr_attr = []

    if num_tr_attr is None:
        num_tr_attr = []

    if str_ev_attr is None:
        str_ev_attr = []

    if num_ev_attr is None:
        num_ev_attr = []

    if pandas_utils.check_is_pandas_dataframe(log):
        case_attribute_prefix = exec_utils.get_param_value(Parameters.CASE_ATTRIBUTE_PREFIX, parameters, "case:")

        if str_tr_attr or num_tr_attr or str_ev_attr or num_ev_attr:
            columns = list(set([case_attribute_prefix + x for x in str_tr_attr]).union(set([case_attribute_prefix + x for x in num_tr_attr])).union(
                set(str_ev_attr)).union(set(num_ev_attr)))
            fea_df = dataframe_utils.get_features_df(log, columns, parameters=parameters)
            feature_names = list(fea_df.columns)
        else:
            fea_df = dataframe_utils.automatic_feature_extraction_df(log, parameters=parameters)
            feature_names = list(fea_df.columns)
        return fea_df, feature_names
    else:
        enable_all = exec_utils.get_param_value(Parameters.ENABLE_ALL_EXTRA_FEATURES, parameters, False)
        case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, xes_constants.DEFAULT_TRACEID_KEY)
        add_case_identifier_column = exec_utils.get_param_value(Parameters.ADD_CASE_IDENTIFIER_COLUMN, parameters, False)
        enable_case_duration = exec_utils.get_param_value(Parameters.ENABLE_CASE_DURATION, parameters, enable_all)
        enable_times_from_first_occ = exec_utils.get_param_value(Parameters.ENABLE_TIMES_FROM_FIRST_OCCURRENCE,
                                                                 parameters, enable_all)
        enable_times_from_last_occ = exec_utils.get_param_value(Parameters.ENABLE_TIMES_FROM_LAST_OCCURRENCE,
                                                                parameters, enable_all)
        enable_direct_paths_times_last_occ = exec_utils.get_param_value(Parameters.ENABLE_DIRECT_PATHS_TIMES_LAST_OCC,
                                                                        parameters, enable_all)
        enable_indirect_paths_times_last_occ = exec_utils.get_param_value(
            Parameters.ENABLE_INDIRECT_PATHS_TIMES_LAST_OCC, parameters, enable_all)
        enable_work_in_progress = exec_utils.get_param_value(Parameters.ENABLE_WORK_IN_PROGRESS, parameters, enable_all)
        enable_resource_workload = exec_utils.get_param_value(Parameters.ENABLE_RESOURCE_WORKLOAD, parameters, enable_all)
        enable_first_last_activity_index = exec_utils.get_param_value(Parameters.ENABLE_FIRST_LAST_ACTIVITY_INDEX, parameters, enable_all)
        enable_max_concurrent_events = exec_utils.get_param_value(Parameters.ENABLE_MAX_CONCURRENT_EVENTS, parameters, enable_all)
        enable_max_concurrent_events_per_activity = exec_utils.get_param_value(Parameters.ENABLE_MAX_CONCURRENT_EVENTS_PER_ACTIVITY, parameters, enable_all)

        log = converter.apply(log, variant=converter.Variants.TO_EVENT_LOG, parameters=parameters)
        if at_least_one_provided:
            datas, features_namess = get_representation(log, str_tr_attr, str_ev_attr, num_tr_attr, num_ev_attr,
                                      str_evsucc_attr=str_evsucc_attr, feature_names=feature_names)
        else:
            datas, features_namess = get_default_representation(log, parameters=parameters)

        if add_case_identifier_column:
            for i in range(len(datas)):
                datas[i] = [log[i].attributes[case_id_key]] + datas[i]
            features_namess = ["@@case_id_column"] + features_namess

        # add additional features

        if enable_case_duration:
            data, features_names = case_duration(log, parameters=parameters)
            for i in range(len(datas)):
                datas[i] = datas[i] + data[i]
            features_namess = features_namess + features_names

        if enable_times_from_first_occ:
            data, features_names = times_from_first_occurrence_activity_case(log, parameters=parameters)
            for i in range(len(datas)):
                datas[i] = datas[i] + data[i]
            features_namess = features_namess + features_names

        if enable_times_from_last_occ:
            data, features_names = times_from_last_occurrence_activity_case(log, parameters=parameters)
            for i in range(len(datas)):
                datas[i] = datas[i] + data[i]
            features_namess = features_namess + features_names

        if enable_direct_paths_times_last_occ:
            data, features_names = direct_paths_times_last_occ(log, parameters=parameters)
            for i in range(len(datas)):
                datas[i] = datas[i] + data[i]
            features_namess = features_namess + features_names

        if enable_indirect_paths_times_last_occ:
            data, features_names = indirect_paths_times_last_occ(log, parameters=parameters)
            for i in range(len(datas)):
                datas[i] = datas[i] + data[i]
            features_namess = features_namess + features_names

        if enable_work_in_progress:
            data, features_names = work_in_progress(log, parameters=parameters)
            for i in range(len(datas)):
                datas[i] = datas[i] + data[i]
            features_namess = features_namess + features_names

        if enable_resource_workload:
            data, features_names = resource_workload(log, parameters=parameters)
            for i in range(len(datas)):
                datas[i] = datas[i] + data[i]
            features_namess = features_namess + features_names

        if enable_first_last_activity_index:
            data, features_names = first_last_activity_index_trace(log, parameters=parameters)
            for i in range(len(datas)):
                datas[i] = datas[i] + data[i]
            features_namess = features_namess + features_names

        if enable_max_concurrent_events:
            data, features_names = max_concurrent_events(log, parameters=parameters)
            for i in range(len(datas)):
                datas[i] = datas[i] + data[i]
            features_namess = features_namess + features_names

        if enable_max_concurrent_events_per_activity:
            data, features_names = max_concurrent_events_per_activity(log, parameters=parameters)
            for i in range(len(datas)):
                datas[i] = datas[i] + data[i]
            features_namess = features_namess + features_names

        return datas, features_namess

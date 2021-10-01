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
import warnings
from typing import List, Union, Set, List, Tuple

import deprecation
import pandas as pd

from pm4py.meta import VERSION as PM4PY_CURRENT_VERSION
from pm4py.objects.log.obj import EventLog
from pm4py.util import constants
from pm4py.util.pandas_utils import check_is_pandas_dataframe, check_pandas_dataframe_columns
from pm4py.utils import get_properties


def filter_start_activities(log: Union[EventLog, pd.DataFrame], activities: Union[Set[str], List[str]], retain: bool = True) -> \
Union[EventLog, pd.DataFrame]:
    """
    Filter cases having a start activity in the provided list

    Parameters
    --------------
    log
        Log object
    activities
        List start activities
    retain
        if True, we retain the traces containing the given activities, if false, we drop the traces


    Returns
    --------------
    filtered_log
        Filtered log object
    """
    parameters = get_properties(log)
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        from pm4py.algo.filtering.pandas.start_activities import start_activities_filter
        parameters[start_activities_filter.Parameters.POSITIVE] = retain
        return start_activities_filter.apply(log, activities,
                                             parameters=parameters)
    else:
        from pm4py.algo.filtering.log.start_activities import start_activities_filter
        parameters[start_activities_filter.Parameters.POSITIVE] = retain
        return start_activities_filter.apply(log, activities,
                                             parameters=parameters)


def filter_end_activities(log: Union[EventLog, pd.DataFrame], activities:  Union[Set[str], List[str]], retain: bool = True) -> Union[
    EventLog, pd.DataFrame]:
    """
    Filter cases having an end activity in the provided list

    Parameters
    ---------------
    log
        Log object
    activities
        List of admitted end activities
    retain
        if True, we retain the traces containing the given activities, if false, we drop the traces


    Returns
    ---------------
    filtered_log
        Filtered log object
    """
    parameters = get_properties(log)
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        from pm4py.algo.filtering.pandas.end_activities import end_activities_filter
        parameters[end_activities_filter.Parameters.POSITIVE] = retain
        return end_activities_filter.apply(log, activities,
                                           parameters=parameters)
    else:
        from pm4py.algo.filtering.log.end_activities import end_activities_filter
        parameters[end_activities_filter.Parameters.POSITIVE] = retain
        return end_activities_filter.apply(log, activities,
                                           parameters=parameters)


@deprecation.deprecated(deprecated_in='2.1.4', removed_in='2.4.0', current_version=PM4PY_CURRENT_VERSION,
                        details='Filtering method will be removed due to fuzzy naming.\
                        Use: filter_event_attribute_values')
def filter_attribute_values(log, attribute_key, values, level="case", retain=True):
    return filter_event_attribute_values(log, attribute_key, values, level=level, retain=retain)


def filter_event_attribute_values(log: Union[EventLog, pd.DataFrame], attribute_key: str, values:  Union[Set[str], List[str]],
                                  level: str = "case", retain: bool = True) -> Union[EventLog, pd.DataFrame]:
    """
    Filter a log object on the values of some event attribute

    Parameters
    --------------
    log
        Log object
    attribute_key
        Attribute to filter
    values
        Admitted (or forbidden) values
    level
        Specifies how the filter should be applied ('case' filters the cases where at least one occurrence happens,
        'event' filter the events eventually trimming the cases)
    retain
        Specified if the values should be kept or removed

    Returns
    --------------
    filtered_log
        Filtered log object
    """
    parameters = get_properties(log)
    parameters[constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY] = attribute_key
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        from pm4py.algo.filtering.pandas.attributes import attributes_filter
        if level == "event":
            parameters[attributes_filter.Parameters.POSITIVE] = retain
            return attributes_filter.apply_events(log, values,
                                                  parameters=parameters)
        elif level == "case":
            parameters[attributes_filter.Parameters.POSITIVE] = retain
            return attributes_filter.apply(log, values, parameters=parameters)
    else:
        from pm4py.algo.filtering.log.attributes import attributes_filter
        if level == "event":
            parameters[attributes_filter.Parameters.POSITIVE] = retain
            return attributes_filter.apply_events(log, values,
                                                  parameters=parameters)
        elif level == "case":
            parameters[attributes_filter.Parameters.POSITIVE] = retain
            return attributes_filter.apply(log, values, parameters=parameters)


@deprecation.deprecated(deprecated_in='2.1.4', removed_in='2.4.0', current_version=PM4PY_CURRENT_VERSION,
                        details='Filtering method will be removed due to fuzzy naming.\
                        Use: filter_event_attribute_values')
def filter_trace_attribute(log, attribute_key, values, retain=True):
    return filter_trace_attribute_values(log, attribute_key, values, retain=retain)


def filter_trace_attribute_values(log: Union[EventLog, pd.DataFrame], attribute_key: str, values:  Union[Set[str], List[str]],
                                  retain: bool = True) -> Union[EventLog, pd.DataFrame]:
    """
    Filter a log on the values of a trace attribute

    Parameters
    --------------
    log
        Event log
    attribute_key
        Attribute to filter
    values
        Values to filter (list of)
    retain
        Boolean value (keep/discard matching traces)

    Returns
    --------------
    filtered_log
        Filtered event log
    """
    parameters = get_properties(log)
    parameters[constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY] = attribute_key
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        from pm4py.algo.filtering.pandas.attributes import attributes_filter
        parameters[attributes_filter.Parameters.POSITIVE] = retain
        return attributes_filter.apply(log, values,
                                       parameters=parameters)
    else:
        from pm4py.algo.filtering.log.attributes import attributes_filter
        parameters[attributes_filter.Parameters.POSITIVE] = retain
        return attributes_filter.apply_trace_attribute(log, values, parameters=parameters)


def filter_variants(log: Union[EventLog, pd.DataFrame], variants:  Union[Set[str], List[str]], retain: bool = True) -> Union[
    EventLog, pd.DataFrame]:
    """
    Filter a log on a specified set of variants

    Parameters
    ---------------
    log
        Event log
    variants
        collection of variants to filter; A variant should be specified as a list of activity names, e.g., ['a','b','c']
    retain
        boolean; if True all traces conforming to the specified variants are retained; if False, all those traces are removed

    Returns
    --------------
    filtered_log
        Filtered log object
    """
    from pm4py.util import variants_util
    parameters = get_properties(log)
    if variants_util.VARIANT_SPECIFICATION == variants_util.VariantsSpecifications.STRING:
        variants = [",".join(v) for v in variants]
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        from pm4py.algo.filtering.pandas.variants import variants_filter
        parameters[variants_filter.Parameters.POSITIVE] = retain
        return variants_filter.apply(log, variants,
                                     parameters=parameters)
    else:
        from pm4py.algo.filtering.log.variants import variants_filter
        parameters[variants_filter.Parameters.POSITIVE] = retain
        return variants_filter.apply(log, variants,
                                     parameters=parameters)


@deprecation.deprecated(deprecated_in='2.1.3.1', removed_in='2.4.0', current_version=PM4PY_CURRENT_VERSION,
                        details='Filtering method will be removed due to fuzzy interpretation of the threshold.\
                        Will be replaced with two new functions filter_variants_top_k and filter_variants_relative_frequency')
def filter_variants_percentage(log: Union[EventLog, pd.DataFrame], threshold: float = 0.8) -> Union[
    EventLog, pd.DataFrame]:
    """
    Filter a log on the percentage of variants

    Parameters
    ---------------
    log
        Event log
    threshold
        Percentage (scale 0.1) of admitted variants

    Returns
    --------------
    filtered_log
        Filtered log object
    """
    if check_is_pandas_dataframe(log):
        raise Exception(
            "filtering variants percentage on Pandas dataframe is currently not available! please convert the dataframe to event log with the method: log =  pm4py.convert_to_event_log(df)")
    else:
        from pm4py.algo.filtering.log.variants import variants_filter
        return variants_filter.filter_log_variants_percentage(log, percentage=threshold, parameters=get_properties(log))


@deprecation.deprecated(deprecated_in='2.1.3.1', removed_in='2.4.0', current_version=PM4PY_CURRENT_VERSION,
                        details='Use filter_directly_follows_relation')
def filter_paths(log, allowed_paths, retain=True):
    return filter_directly_follows_relation(log, allowed_paths, retain)


def filter_directly_follows_relation(log: Union[EventLog, pd.DataFrame], relations: List[str], retain: bool = True) -> \
        Union[EventLog, pd.DataFrame]:
    """
    Retain traces that contain any of the specified 'directly follows' relations.
    For example, if relations == [('a','b'),('a','c')] and log [<a,b,c>,<a,c,b>,<a,d,b>]
    the resulting log will contain traces describing [<a,b,c>,<a,c,b>].

    Parameters
    ---------------
    log
        Log object
    relations
        List of activity name pairs, which are allowed/forbidden paths
    retain
        Parameter that says whether the paths
        should be kept/removed

    Returns
    ----------------
    filtered_log
        Filtered log object
    """
    parameters = get_properties(log)
    if check_is_pandas_dataframe(log):
        from pm4py.algo.filtering.pandas.paths import paths_filter
        parameters[paths_filter.Parameters.POSITIVE] = retain
        return paths_filter.apply(log, relations, parameters=parameters)
    else:
        from pm4py.algo.filtering.log.paths import paths_filter
        parameters[paths_filter.Parameters.POSITIVE] = retain
        return paths_filter.apply(log, relations, parameters=parameters)


def filter_eventually_follows_relation(log: Union[EventLog, pd.DataFrame], relations: List[str], retain: bool = True) -> \
        Union[EventLog, pd.DataFrame]:
    """
    Retain traces that contain any of the specified 'eventually follows' relations.
    For example, if relations == [('a','b'),('a','c')] and log [<a,b,c>,<a,c,b>,<a,d,b>]
    the resulting log will contain traces describing [<a,b,c>,<a,c,b>,<a,d,b>].

    Parameters
    ---------------
    log
        Log object
    relations
        List of activity name pairs, which are allowed/forbidden paths
    retain
        Parameter that says whether the paths
        should be kept/removed

    Returns
    ----------------
    filtered_log
        Filtered log object
    """
    parameters = get_properties(log)
    if check_is_pandas_dataframe(log):
        from pm4py.algo.filtering.pandas.ltl import ltl_checker
        parameters[ltl_checker.Parameters.POSITIVE] = retain
        if retain:
            cases = set()
        else:
            cases = set(log[constants.CASE_CONCEPT_NAME])
        for path in relations:
            filt_log = ltl_checker.eventually_follows(log, path,
                                                      parameters=parameters)
            this_traces = set(filt_log[constants.CASE_CONCEPT_NAME])
            if retain:
                cases = cases.union(this_traces)
            else:
                cases = cases.intersection(this_traces)
        return log[log[constants.CASE_CONCEPT_NAME].isin(cases)]
    else:
        from pm4py.objects.log.obj import EventLog
        from pm4py.algo.filtering.log.ltl import ltl_checker
        parameters[ltl_checker.Parameters.POSITIVE] = retain
        if retain:
            cases = set()
        else:
            cases = set(id(trace) for trace in log)
        for path in relations:
            filt_log = ltl_checker.eventually_follows(log, path,
                                                      parameters=parameters)
            this_traces = set(id(trace) for trace in filt_log)
            if retain:
                cases = cases.union(this_traces)
            else:
                cases = cases.intersection(this_traces)
        filtered_log = EventLog(attributes=log.attributes, extensions=log.extensions, omni_present=log.omni_present,
                                classifiers=log.classifiers, properties=log.properties)
        for trace in log:
            if id(trace) in cases:
                filtered_log.append(trace)
        return filtered_log


def filter_time_range(log: Union[EventLog, pd.DataFrame], dt1: str, dt2: str, mode="events") -> Union[
    EventLog, pd.DataFrame]:
    """
    Filter a log on a time interval

    Parameters
    ----------------
    log
        Log object
    dt1
        Left extreme of the interval
    dt2
        Right extreme of the interval
    mode
        Modality of filtering (events, traces_contained, traces_intersecting)
        events: any event that fits the time frame is retained
        traces_contained: any trace completely contained in the timeframe is retained
        traces_intersecting: any trace intersecting with the time-frame is retained.

    Returns
    ----------------
    filtered_log
        Filtered log
    """
    if check_is_pandas_dataframe(log):
        from pm4py.algo.filtering.pandas.timestamp import timestamp_filter
        if mode == "events":
            return timestamp_filter.apply_events(log, dt1, dt2, parameters=get_properties(log))
        elif mode == "traces_contained":
            return timestamp_filter.filter_traces_contained(log, dt1, dt2, parameters=get_properties(log))
        elif mode == "traces_intersecting":
            return timestamp_filter.filter_traces_intersecting(log, dt1, dt2, parameters=get_properties(log))
        else:
            warnings.warn('mode provided: ' + mode + ' is not recognized; original log returned!')
            return log
    else:
        from pm4py.algo.filtering.log.timestamp import timestamp_filter
        if mode == "events":
            return timestamp_filter.apply_events(log, dt1, dt2, parameters=get_properties(log))
        elif mode == "traces_contained":
            return timestamp_filter.filter_traces_contained(log, dt1, dt2, parameters=get_properties(log))
        elif mode == "traces_intersecting":
            return timestamp_filter.filter_traces_intersecting(log, dt1, dt2, parameters=get_properties(log))
        else:
            warnings.warn('mode provided: ' + mode + ' is not recognized; original log returned!')
            return log


def filter_between(log: Union[EventLog, pd.DataFrame], act1: str, act2: str) -> Union[EventLog, pd.DataFrame]:
    """
    Finds all the sub-cases leading from an event with activity "act1" to an event with activity "act2" in the log,
    and returns a log containing only them.

    Example:

    Log
    A B C D E F
    A B E F C
    A B F C B C B E F C

    act1 = B
    act2 = C

    Returned sub-cases:
    B C (from the first case)
    B E F C (from the second case)
    B F C (from the third case)
    B C (from the third case)
    B E F C (from the third case)

    Parameters
    -----------------
    log
        Event log / Pandas dataframe
    act1
        Source activity
    act2
        Target activity

    Returns
    -----------------
    filtered_log
        Log containing all the subcases
    """
    parameters = get_properties(log)
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        from pm4py.algo.filtering.pandas.between import between_filter
        return between_filter.apply(log, act1, act2, parameters=parameters)
    else:
        from pm4py.algo.filtering.log.between import between_filter
        return between_filter.apply(log, act1, act2, parameters=parameters)


def filter_case_size(log: Union[EventLog, pd.DataFrame], min_size: int, max_size: int) -> Union[EventLog, pd.DataFrame]:
    """
    Filters the event log, keeping the cases having a length (number of events) included between min_size
    and max_size

    Parameters
    -----------------
    log
        Event log / Pandas dataframe
    min_size
        Minimum allowed number of events
    max_size
        Maximum allowed number of events

    Returns
    ----------------
    filtered_log
        Log with cases having the desidered number of events.
    """
    parameters = get_properties(log)
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        from pm4py.algo.filtering.pandas.cases import case_filter
        case_id = parameters[
            constants.PARAMETER_CONSTANT_CASEID_KEY] if constants.PARAMETER_CONSTANT_CASEID_KEY in parameters else constants.CASE_CONCEPT_NAME
        return case_filter.filter_on_case_size(log, case_id, min_size, max_size)
    else:
        from pm4py.algo.filtering.log.cases import case_filter
        return case_filter.filter_on_case_size(log, min_size, max_size)


def filter_case_performance(log: Union[EventLog, pd.DataFrame], min_performance: float, max_performance: float) -> Union[EventLog, pd.DataFrame]:
    """
    Filters the event log, keeping the cases having a duration (the timestamp of the last event minus the timestamp
    of the first event) included between min_performance and max_performance

    Parameters
    ----------------
    log
        Event log / Pandas dataframe
    min_performance
        Minimum allowed case duration
    max_performance
        Maximum allowed case duration

    Returns
    ----------------
    filtered_log
        Log with cases having a duration in the specified range
    """
    parameters = get_properties(log)
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        from pm4py.algo.filtering.pandas.cases import case_filter
        return case_filter.filter_case_performance(log, min_performance, max_performance, parameters=parameters)
    else:
        from pm4py.algo.filtering.log.cases import case_filter
        return case_filter.filter_case_performance(log, min_performance, max_performance, parameters=parameters)


def filter_activities_rework(log: Union[EventLog, pd.DataFrame], activity: str, min_occurrences: int = 2) -> Union[EventLog, pd.DataFrame]:
    """
    Filters the event log, keeping the cases where the specified activity occurs at least min_occurrences times.

    Parameters
    -----------------
    log
        Event log / Pandas dataframe
    activity
        Activity
    min_occurrences
        Minimum desidered number of occurrences

    Returns
    -----------------
    filtered_log
        Log with cases having at least min_occurrences occurrences of the given activity
    """
    parameters = get_properties(log)
    parameters["min_occurrences"] = min_occurrences
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        from pm4py.algo.filtering.pandas.rework import rework_filter
        return rework_filter.apply(log, activity, parameters=parameters)
    else:
        from pm4py.algo.filtering.log.rework import rework_filter
        return rework_filter.apply(log, activity, parameters=parameters)


def filter_paths_performance(log: Union[EventLog, pd.DataFrame], path: Tuple[str, str], min_performance: float, max_performance: float, keep=True) -> Union[EventLog, pd.DataFrame]:
    """
    Filters the event log, either:
    - (keep=True) keeping the cases having the specified path (tuple of 2 activities) with a duration included between min_performance and max_performance
    - (keep=False) discarding the cases having the specified path with a duration included between min_performance and max_performance

    Parameters
    ----------------
    log
        Event log
    path
        Tuple of two activities (source_activity, target_activity)
    min_performance
        Minimum allowed performance (of the path)
    max_performance
        Maximum allowed performance (of the path)
    keep
        Keep/discard the cases having the specified path with a duration included between min_performance and max_performance

    Returns
    ----------------
    filtered_log
        Filtered log with the desidered behavior
    """
    parameters = get_properties(log)
    parameters["positive"] = keep
    parameters["min_performance"] = min_performance
    parameters["max_performance"] = max_performance
    path = tuple(path)
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        from pm4py.algo.filtering.pandas.paths import paths_filter
        return paths_filter.apply_performance(log, path, parameters=parameters)
    else:
        from pm4py.algo.filtering.log.paths import paths_filter
        return paths_filter.apply_performance(log, path, parameters=parameters)


def filter_variants_top_k(log: Union[EventLog, pd.DataFrame], k: int) -> Union[EventLog, pd.DataFrame]:
    """
    Keeps the top-k variants of the log

    Parameters
    -------------
    log
        Event log
    k
        Number of variants that should be kept
    parameters
        Parameters

    Returns
    -------------
    filtered_log
        Filtered log
    """
    parameters = get_properties(log)
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        from pm4py.algo.filtering.pandas.variants import variants_filter
        return variants_filter.filter_variants_top_k(log, k, parameters=parameters)
    else:
        from pm4py.algo.filtering.log.variants import variants_filter
        return variants_filter.filter_variants_top_k(log, k, parameters=parameters)


def filter_variants_by_coverage_percentage(log: Union[EventLog, pd.DataFrame], min_coverage_percentage: float) -> Union[EventLog, pd.DataFrame]:
    """
    Filters the variants of the log by a coverage percentage
    (e.g., if min_coverage_percentage=0.4, and we have a log with 1000 cases,
    of which 500 of the variant 1, 400 of the variant 2, and 100 of the variant 3,
    the filter keeps only the traces of variant 1 and variant 2).

    Parameters
    ---------------
    log
        Event log
    min_coverage_percentage
        Minimum allowed percentage of coverage
    parameters
        Parameters

    Returns
    ---------------
    filtered_log
        Filtered log
    """
    parameters = get_properties(log)
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        from pm4py.algo.filtering.pandas.variants import variants_filter
        return variants_filter.filter_variants_by_coverage_percentage(log, min_coverage_percentage, parameters=parameters)
    else:
        from pm4py.algo.filtering.log.variants import variants_filter
        return variants_filter.filter_variants_by_coverage_percentage(log, min_coverage_percentage, parameters=parameters)

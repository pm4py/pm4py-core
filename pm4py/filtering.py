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
from typing import List, Union, Set, List, Tuple, Collection, Any, Dict

import deprecation
import pandas as pd

from pm4py.meta import VERSION as PM4PY_CURRENT_VERSION
import pm4py.objects.log.obj
from pm4py.objects.log.obj import EventLog, EventStream
from pm4py.util import constants, xes_constants
from pm4py.util.pandas_utils import check_is_pandas_dataframe, check_pandas_dataframe_columns
from pm4py.utils import get_properties
from pm4py.objects.ocel.obj import OCEL
import datetime


def filter_log_relative_occurrence_event_attribute(log: Union[EventLog, pd.DataFrame], min_relative_stake: float, attribute_key : str = xes_constants.DEFAULT_NAME_KEY, level="cases") -> Union[EventLog, pd.DataFrame]:
    """
    Filters the event log keeping only the events having an attribute value which occurs:
    - in at least the specified (min_relative_stake) percentage of events, when level="events"
    - in at least the specified (min_relative_stake) percentage of cases, when level="cases"

    Parameters
    -------------------
    log
        Event log / Pandas dataframe
    min_relative_stake
        Minimum percentage of cases (expressed as a number between 0 and 1) in which the attribute should occur.
    attribute_key
        The attribute to filter
    level
        The level of the filter (if level="events", then events / if level="cases", then cases)

    Returns
    ------------------
    filtered_log
        Filtered event log
    """
    if not isinstance(log, (pd.DataFrame, pm4py.objects.log.obj.EventLog, pm4py.objects.log.obj.EventStream)):
            raise Exception("the method can be applied only to a traditional event log!")

    parameters = get_properties(log)
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        from pm4py.algo.filtering.pandas.attributes import attributes_filter
        parameters[attributes_filter.Parameters.ATTRIBUTE_KEY] = attribute_key
        parameters[attributes_filter.Parameters.KEEP_ONCE_PER_CASE] = True if level == "cases" else False
        return attributes_filter.filter_df_relative_occurrence_event_attribute(log, min_relative_stake, parameters=parameters)
    else:
        from pm4py.algo.filtering.log.attributes import attributes_filter
        parameters[attributes_filter.Parameters.ATTRIBUTE_KEY] = attribute_key
        parameters[attributes_filter.Parameters.KEEP_ONCE_PER_CASE] = True if level == "cases" else False
        return attributes_filter.filter_log_relative_occurrence_event_attribute(log, min_relative_stake, parameters=parameters)


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
    if not isinstance(log, (pd.DataFrame, pm4py.objects.log.obj.EventLog, pm4py.objects.log.obj.EventStream)):
            raise Exception("the method can be applied only to a traditional event log!")

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
    if not isinstance(log, (pd.DataFrame, pm4py.objects.log.obj.EventLog, pm4py.objects.log.obj.EventStream)):
            raise Exception("the method can be applied only to a traditional event log!")

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
    if not isinstance(log, (pd.DataFrame, pm4py.objects.log.obj.EventLog, pm4py.objects.log.obj.EventStream)):
            raise Exception("the method can be applied only to a traditional event log!")

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
    if not isinstance(log, (pd.DataFrame, pm4py.objects.log.obj.EventLog, pm4py.objects.log.obj.EventStream)):
            raise Exception("the method can be applied only to a traditional event log!")

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
    if not isinstance(log, (pd.DataFrame, pm4py.objects.log.obj.EventLog, pm4py.objects.log.obj.EventStream)):
            raise Exception("the method can be applied only to a traditional event log!")

    from pm4py.util import variants_util
    parameters = get_properties(log)
    if variants_util.VARIANT_SPECIFICATION == variants_util.VariantsSpecifications.STRING:
        variants = [constants.DEFAULT_VARIANT_SEP.join(v) for v in variants]
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
    if not isinstance(log, (pd.DataFrame, pm4py.objects.log.obj.EventLog, pm4py.objects.log.obj.EventStream)):
            raise Exception("the method can be applied only to a traditional event log!")

    if check_is_pandas_dataframe(log):
        raise Exception(
            "filtering variants percentage on Pandas dataframe is currently not available! please convert the dataframe to event log with the method: log =  pm4py.convert_to_event_log(df)")
    else:
        from pm4py.algo.filtering.log.variants import variants_filter
        return variants_filter.filter_log_variants_percentage(log, percentage=threshold, parameters=get_properties(log))


@deprecation.deprecated(deprecated_in='2.1.3.1', removed_in='2.4.0', current_version=PM4PY_CURRENT_VERSION,
                        details='Use filter_directly_follows_relation')
def filter_paths(log, allowed_paths, retain=True):
    if not isinstance(log, (pd.DataFrame, pm4py.objects.log.obj.EventLog, pm4py.objects.log.obj.EventStream)):
            raise Exception("the method can be applied only to a traditional event log!")

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
    if not isinstance(log, (pd.DataFrame, pm4py.objects.log.obj.EventLog, pm4py.objects.log.obj.EventStream)):
            raise Exception("the method can be applied only to a traditional event log!")

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
    if not isinstance(log, (pd.DataFrame, pm4py.objects.log.obj.EventLog, pm4py.objects.log.obj.EventStream)):
            raise Exception("the method can be applied only to a traditional event log!")

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
    if not isinstance(log, (pd.DataFrame, pm4py.objects.log.obj.EventLog, pm4py.objects.log.obj.EventStream)):
            raise Exception("the method can be applied only to a traditional event log!")

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
    if not isinstance(log, (pd.DataFrame, pm4py.objects.log.obj.EventLog, pm4py.objects.log.obj.EventStream)):
            raise Exception("the method can be applied only to a traditional event log!")

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
    if not isinstance(log, (pd.DataFrame, pm4py.objects.log.obj.EventLog, pm4py.objects.log.obj.EventStream)):
            raise Exception("the method can be applied only to a traditional event log!")

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
    if not isinstance(log, (pd.DataFrame, pm4py.objects.log.obj.EventLog, pm4py.objects.log.obj.EventStream)):
            raise Exception("the method can be applied only to a traditional event log!")

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
    if not isinstance(log, (pd.DataFrame, pm4py.objects.log.obj.EventLog, pm4py.objects.log.obj.EventStream)):
            raise Exception("the method can be applied only to a traditional event log!")

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
    if not isinstance(log, (pd.DataFrame, pm4py.objects.log.obj.EventLog, pm4py.objects.log.obj.EventStream)):
            raise Exception("the method can be applied only to a traditional event log!")

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
    if not isinstance(log, (pd.DataFrame, pm4py.objects.log.obj.EventLog, pm4py.objects.log.obj.EventStream)):
            raise Exception("the method can be applied only to a traditional event log!")

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
    if not isinstance(log, (pd.DataFrame, pm4py.objects.log.obj.EventLog, pm4py.objects.log.obj.EventStream)):
            raise Exception("the method can be applied only to a traditional event log!")

    parameters = get_properties(log)
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        from pm4py.algo.filtering.pandas.variants import variants_filter
        return variants_filter.filter_variants_by_coverage_percentage(log, min_coverage_percentage, parameters=parameters)
    else:
        from pm4py.algo.filtering.log.variants import variants_filter
        return variants_filter.filter_variants_by_coverage_percentage(log, min_coverage_percentage, parameters=parameters)


def filter_prefixes(log: Union[EventLog, pd.DataFrame], activity: str, strict=True, first_or_last="first"):
    """
    Filters the log, keeping the prefixes to a given activity. E.g., for a log with traces:

    A,B,C,D
    A,B,Z,A,B,C,D
    A,B,C,D,C,E,C,F

    The prefixes to "C" are respectively:

    A,B
    A,B,Z,A,B
    A,B

    Parameters
    ------------------
    log
        Event log / Pandas dataframe
    activity
        Target activity of the filter
    strict
        Applies the filter strictly (cuts the occurrences of the selected activity).
    first_or_last
        Decides if the first or last occurrence of an activity should be selected as baseline for the filter.

    Returns
    ------------------
    filtered_log
        Filtered log / dataframe
    """
    if not isinstance(log, (pd.DataFrame, pm4py.objects.log.obj.EventLog, pm4py.objects.log.obj.EventStream)):
            raise Exception("the method can be applied only to a traditional event log!")

    parameters = get_properties(log)
    parameters["strict"] = strict
    parameters["first_or_last"] = first_or_last

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        from pm4py.algo.filtering.pandas.prefixes import prefix_filter
        return prefix_filter.apply(log, activity, parameters=parameters)
    else:
        from pm4py.algo.filtering.log.prefixes import prefix_filter
        return prefix_filter.apply(log, activity, parameters=parameters)


def filter_suffixes(log: Union[EventLog, pd.DataFrame], activity: str, strict=True, first_or_last="first"):
    """
    Filters the log, keeping the suffixes from a given activity. E.g., for a log with traces:

    A,B,C,D
    A,B,Z,A,B,C,D
    A,B,C,D,C,E,C,F

    The suffixes from "C" are respectively:

    D
    D
    D,C,E,C,F

    Parameters
    ------------------
    log
        Event log / Pandas dataframe
    activity
        Target activity of the filter
    strict
        Applies the filter strictly (cuts the occurrences of the selected activity).
    first_or_last
        Decides if the first or last occurrence of an activity should be selected as baseline for the filter.

    Returns
    ------------------
    filtered_log
        Filtered log / dataframe
    """
    if not isinstance(log, (pd.DataFrame, pm4py.objects.log.obj.EventLog, pm4py.objects.log.obj.EventStream)):
            raise Exception("the method can be applied only to a traditional event log!")

    parameters = get_properties(log)
    parameters["strict"] = strict
    parameters["first_or_last"] = first_or_last

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        from pm4py.algo.filtering.pandas.suffixes import suffix_filter
        return suffix_filter.apply(log, activity, parameters=parameters)
    else:
        from pm4py.algo.filtering.log.suffixes import suffix_filter
        return suffix_filter.apply(log, activity, parameters=parameters)


def filter_ocel_event_attribute(ocel: OCEL, attribute_key: str, attribute_values: Collection[Any], positive: bool = True) -> OCEL:
    """
    Filters the object-centric event log on the provided event attributes values

    Parameters
    ----------------
    ocel
        Object-centric event log
    attribute_key
        Attribute at the event level
    attribute_values
        Attribute values
    positive
        Decides if the values should be kept (positive=True) or removed (positive=False)

    Returns
    ----------------
    filtered_ocel
        Filtered object-centric event log
    """
    from pm4py.algo.filtering.ocel import event_attributes

    return event_attributes.apply(ocel, attribute_values, parameters={event_attributes.Parameters.ATTRIBUTE_KEY: attribute_key, event_attributes.Parameters.POSITIVE: positive})


def filter_ocel_object_attribute(ocel: OCEL, attribute_key: str, attribute_values: Collection[Any], positive: bool = True) -> OCEL:
    """
    Filters the object-centric event log on the provided object attributes values

    Parameters
    ----------------
    ocel
        Object-centric event log
    attribute_key
        Attribute at the event level
    attribute_values
        Attribute values
    positive
        Decides if the values should be kept (positive=True) or removed (positive=False)

    Returns
    ----------------
    filtered_ocel
        Filtered object-centric event log
    """
    from pm4py.algo.filtering.ocel import object_attributes

    return object_attributes.apply(ocel, attribute_values, parameters={object_attributes.Parameters.ATTRIBUTE_KEY: attribute_key, object_attributes.Parameters.POSITIVE: positive})


def filter_ocel_object_types_allowed_activities(ocel: OCEL, correspondence_dict: Dict[str, Collection[str]]) -> OCEL:
    """
    Filters an object-centric event log keeping only the specified object types
    with the specified activity set (filters out the rest).

    Parameters
    ----------------
    ocel
        Object-centric event log
    correspondence_dict
        Dictionary containing, for every object type of interest, a
        collection of allowed activities.  Example:

        {"order": ["Create Order"], "element": ["Create Order", "Create Delivery"]}

        Keeps only the object types "order" and "element".
        For the "order" object type, only the activity "Create Order" is kept.
        For the "element" object type, only the activities "Create Order" and "Create Delivery" are kept.

    Returns
    -----------------
    filtered_ocel
        Filtered object-centric event log
    """
    from pm4py.algo.filtering.ocel import activity_type_matching

    return activity_type_matching.apply(ocel, correspondence_dict)


def filter_ocel_object_per_type_count(ocel: OCEL, min_num_obj_type: Dict[str, int]) -> OCEL:
    """
    Filters the events of the object-centric logs which are related to at least
    the specified amount of objects per type.

    E.g. pm4py.filter_object_per_type_count(ocel, {"order": 1, "element": 2})

    Would keep the following events:

      ocel:eid ocel:timestamp ocel:activity ocel:type:element ocel:type:order
    0       e1     1980-01-01  Create Order  [i4, i1, i3, i2]            [o1]
    1      e11     1981-01-01  Create Order          [i6, i5]            [o2]
    2      e14     1981-01-04  Create Order          [i8, i7]            [o3]

    Parameters
    ------------------
    ocel
        Object-centric event log
    min_num_obj_type
        Minimum number of objects per type

    Returns
    -----------------
    filtered_event_log
        Filtered object-centric event log
    """
    from pm4py.algo.filtering.ocel import objects_ot_count

    return objects_ot_count.apply(ocel, min_num_obj_type)


def filter_ocel_start_events_per_object_type(ocel: OCEL, object_type: str) -> OCEL:
    """
    Filters the events in which a new object for the given object type is spawn.
    (E.g. an event with activity "Create Order" might spawn new orders).

    Parameters
    ------------------
    ocel
        Object-centric event log
    object_type
        Object type to consider

    Returns
    ------------------
    filtered_ocel
        Filtered object-centric event log
    """
    from pm4py.algo.filtering.ocel import ot_endpoints
    return ot_endpoints.filter_start_events_per_object_type(ocel, object_type)


def filter_ocel_end_events_per_object_type(ocel: OCEL, object_type: str) -> OCEL:
    """
    Filters the events in which an object for the given object type terminates its lifecycle.
    (E.g. an event with activity "Pay Order" might terminate an order).

    Parameters
    ------------------
    ocel
        Object-centric event log
    object_type
        Object type to consider

    Returns
    ------------------
    filtered_ocel
        Filtered object-centric event log
    """
    from pm4py.algo.filtering.ocel import ot_endpoints
    return ot_endpoints.filter_end_events_per_object_type(ocel, object_type)


def filter_ocel_events_timestamp(ocel: OCEL, min_timest: Union[datetime.datetime, str], max_timest: Union[datetime.datetime, str], timestamp_key: str = "ocel:timestamp") -> OCEL:
    """
    Filters the object-centric event log keeping events in the provided timestamp range

    Parameters
    -----------------
    ocel
        Object-centric event log
    min_timest
        Left extreme of the allowed timestamp interval (provided in the format: YYYY-mm-dd HH:MM:SS)
    max_timest
        Right extreme of the allowed timestamp interval (provided in the format: YYYY-mm-dd HH:MM:SS)
    timestamp_key
        The attribute to use as timestamp (default: ocel:timestamp)

    Returns
    -----------------
    filtered_ocel
        Filtered object-centric event log
    """
    from pm4py.algo.filtering.ocel import event_attributes
    return event_attributes.apply_timestamp(ocel, min_timest, max_timest, parameters={"pm4py:param:timestamp_key": timestamp_key})

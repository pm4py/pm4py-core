import warnings

import deprecation

from pm4py import VERSION as PM4PY_CURRENT_VERSION
from pm4py.util import constants
from pm4py.util.pandas_utils import check_is_dataframe, check_dataframe_columns


def filter_start_activities(log, activities, retain=True):
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
    if check_is_dataframe(log):
        check_dataframe_columns(log)
        from pm4py.algo.filtering.pandas.start_activities import start_activities_filter
        return start_activities_filter.apply(log, activities,
                                             parameters={start_activities_filter.Parameters.POSITIVE: retain})
    else:
        from pm4py.algo.filtering.log.start_activities import start_activities_filter
        return start_activities_filter.apply(log, activities,
                                             parameters={start_activities_filter.Parameters.POSITIVE: retain})


def filter_end_activities(log, activities, retain=True):
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
    if check_is_dataframe(log):
        check_dataframe_columns(log)
        from pm4py.algo.filtering.pandas.end_activities import end_activities_filter
        return end_activities_filter.apply(log, activities,
                                           parameters={end_activities_filter.Parameters.POSITIVE: retain})
    else:
        from pm4py.algo.filtering.log.end_activities import end_activities_filter
        return end_activities_filter.apply(log, activities,
                                           parameters={end_activities_filter.Parameters.POSITIVE: retain})


@deprecation.deprecated(deprecated_in='2.1.4', removed_in='2.3.0', current_version=PM4PY_CURRENT_VERSION,
                        details='Filtering method will be removed due to fuzzy naming.\
                        Use: filter_event_attribute_values')
def filter_attribute_values(log, attribute_key, values, level="case", retain=True):
    return filter_event_attribute_values(log, attribute_key, values, level=level, retain=retain)


def filter_event_attribute_values(log, attribute_key, values, level="case", retain=True):
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
    if check_is_dataframe(log):
        check_dataframe_columns(log)
        from pm4py.algo.filtering.pandas.attributes import attributes_filter
        if level == "event":
            return attributes_filter.apply_events(log, values,
                                                  parameters={constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY: attribute_key,
                                                              attributes_filter.Parameters.POSITIVE: retain})
        elif level == "case":
            return attributes_filter.apply(log, values, parameters={
                constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY: attribute_key,
                attributes_filter.Parameters.POSITIVE: retain})
    else:
        from pm4py.algo.filtering.log.attributes import attributes_filter
        if level == "event":
            return attributes_filter.apply_events(log, values,
                                                  parameters={constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY: attribute_key,
                                                              attributes_filter.Parameters.POSITIVE: retain})
        elif level == "case":
            return attributes_filter.apply(log, values, parameters={
                constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY: attribute_key,
                attributes_filter.Parameters.POSITIVE: retain})


@deprecation.deprecated(deprecated_in='2.1.4', removed_in='2.3.0', current_version=PM4PY_CURRENT_VERSION,
                        details='Filtering method will be removed due to fuzzy naming.\
                        Use: filter_event_attribute_values')
def filter_trace_attribute(log, attribute_key, values, retain=True):
    return filter_trace_attribute_values(log, attribute_key, values, retain=retain)


def filter_trace_attribute_values(log, attribute_key, values, retain=True):
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
    if check_is_dataframe(log):
        check_dataframe_columns(log)
        from pm4py.algo.filtering.pandas.attributes import attributes_filter
        return attributes_filter.apply(log, values,
                                       parameters={attributes_filter.Parameters.ATTRIBUTE_KEY: attribute_key,
                                                   attributes_filter.Parameters.POSITIVE: retain})
    else:
        from pm4py.algo.filtering.log.attributes import attributes_filter
        return attributes_filter.apply_trace_attribute(log, values, parameters={
            attributes_filter.Parameters.ATTRIBUTE_KEY: attribute_key, attributes_filter.Parameters.POSITIVE: retain})


def filter_variants(log, variants, retain=True):
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
    if check_is_dataframe(log):
        check_dataframe_columns(log)
        from pm4py.algo.filtering.pandas.variants import variants_filter
        return variants_filter.apply(log, [",".join(v) for v in variants],
                                     parameters={variants_filter.Parameters.POSITIVE: retain})
    else:
        from pm4py.algo.filtering.log.variants import variants_filter
        return variants_filter.apply(log, [",".join(v) for v in variants],
                                     parameters={variants_filter.Parameters.POSITIVE: retain})


@deprecation.deprecated(deprecated_in='2.1.3.1', removed_in='2.3.0', current_version=PM4PY_CURRENT_VERSION,
                        details='Filtering method will be removed due to fuzzy interpretation of the threshold.\
                        Will be replaced with two new functions filter_variants_top_k and filter_variants_relative_frequency')
def filter_variants_percentage(log, threshold=0.8):
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
    if check_is_dataframe(log):
        raise Exception(
            "filtering variants percentage on Pandas dataframe is currently not available! please convert the dataframe to event log with the method: log =  pm4py.convert_to_event_log(df)")
    else:
        from pm4py.algo.filtering.log.variants import variants_filter
        return variants_filter.filter_log_variants_percentage(log, percentage=threshold)


@deprecation.deprecated(deprecated_in='2.1.3.1', removed_in='2.3.0', current_version=PM4PY_CURRENT_VERSION,
                        details='Use filter_directly_follows_relation')
def filter_paths(log, allowed_paths, retain=True):
    return filter_directly_follows_relation(log, allowed_paths, retain)


def filter_directly_follows_relation(log, relations, retain=True):
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
    if check_is_dataframe(log):
        from pm4py.algo.filtering.pandas.paths import paths_filter
        return paths_filter.apply(log, relations, parameters={paths_filter.Parameters.POSITIVE: retain})
    else:
        from pm4py.algo.filtering.log.paths import paths_filter
        return paths_filter.apply(log, relations, parameters={paths_filter.Parameters.POSITIVE: retain})


def filter_eventually_follows_relation(log, relations, retain=True):
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
    if check_is_dataframe(log):
        from pm4py.algo.filtering.pandas.ltl import ltl_checker
        if retain:
            cases = set()
        else:
            cases = set(log[constants.CASE_CONCEPT_NAME])
        for path in relations:
            filt_log = ltl_checker.A_eventually_B(log, path[0], path[1],
                                                  parameters={ltl_checker.Parameters.POSITIVE: retain})
            this_traces = set(filt_log[constants.CASE_CONCEPT_NAME])
            if retain:
                cases = cases.union(this_traces)
            else:
                cases = cases.intersection(this_traces)
        return log[log[constants.CASE_CONCEPT_NAME].isin(cases)]
    else:
        from pm4py.objects.log.log import EventLog
        from pm4py.algo.filtering.log.ltl import ltl_checker
        if retain:
            cases = set()
        else:
            cases = set(id(trace) for trace in log)
        for path in relations:
            filt_log = ltl_checker.A_eventually_B(log, path[0], path[1],
                                                  parameters={ltl_checker.Parameters.POSITIVE: retain})
            this_traces = set(id(trace) for trace in filt_log)
            if retain:
                cases = cases.union(this_traces)
            else:
                cases = cases.intersection(this_traces)
        filtered_log = EventLog(attributes=log.attributes, extensions=log.extensions, omni_present=log.omni_present,
                                classifiers=log.classifiers)
        for trace in log:
            if id(trace) in cases:
                filtered_log.append(trace)
        return filtered_log


def filter_time_range(log, dt1, dt2, mode="events"):
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
    if check_is_dataframe(log):
        from pm4py.algo.filtering.pandas.timestamp import timestamp_filter
        if mode == "events":
            return timestamp_filter.apply_events(log, dt1, dt2)
        elif mode == "traces_contained":
            return timestamp_filter.filter_traces_contained(log, dt1, dt2)
        elif mode == "traces_intersecting":
            return timestamp_filter.filter_traces_intersecting(log, dt1, dt2)
        else:
            warnings.warn('mode provided: ' + mode + ' is not recognized; original log returned!')
            return log
    else:
        from pm4py.algo.filtering.log.timestamp import timestamp_filter
        if mode == "events":
            return timestamp_filter.apply_events(log, dt1, dt2)
        elif mode == "traces_contained":
            return timestamp_filter.filter_traces_contained(log, dt1, dt2)
        elif mode == "traces_intersecting":
            return timestamp_filter.filter_traces_intersecting(log, dt1, dt2)
        else:
            warnings.warn('mode provided: ' + mode + ' is not recognized; original log returned!')
            return log

'''
PM4Py – A Process Mining Library for Python
Copyright (C) 2026 Process Intelligence Solutions GmbH

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see this software project's root or
visit <https://www.gnu.org/licenses/>.

Website: https://processintelligence.solutions
Contact: info@processintelligence.solutions
'''
__doc__ = """
The ``pm4py.filtering`` module contains the filtering features offered in ``pm4py``.
"""

from typing import Union, Set, List, Tuple, Collection, Any, Dict, Optional
from collections import Counter

import pandas as pd

from pm4py.objects.log.obj import EventLog
from pm4py.util import constants, xes_constants, pandas_utils, nx_utils
import warnings
from pm4py.util.pandas_utils import (
    check_is_pandas_dataframe,
    check_pandas_dataframe_columns,
)
from pm4py.utils import (
    get_properties,
    __event_log_deprecation_warning,
    is_polars_lazyframe,
)
from pm4py.objects.ocel.obj import OCEL
from pm4py.utils import __event_log_filtering_level_warning
import datetime


def _get_dataframe_filtering_package(df):
    if is_polars_lazyframe(df):
        import pm4py.algo.filtering.polars as filtering_pkg
    else:
        import pm4py.algo.filtering.pandas as filtering_pkg

    return filtering_pkg


def _is_dataframe_like(obj):
    return check_is_pandas_dataframe(obj) or is_polars_lazyframe(obj)


def _normalize_sequence_argument(value):
    """Normalize a prefix/suffix input into the list-of-list structure expected by Polars filters."""
    if isinstance(value, str):
        return [[value]]
    if isinstance(value, (list, tuple)):
        if value and all(isinstance(elem, (list, tuple)) for elem in value):
            return [list(elem) if isinstance(elem, tuple) else list(elem) for elem in value]
        if all(isinstance(elem, str) for elem in value):
            return [list(value)]
    return [[str(value)]]


def filter_log_relative_occurrence_event_attribute(
    log: Union[EventLog, pd.DataFrame],
    min_relative_stake: float,
    attribute_key: str = xes_constants.DEFAULT_NAME_KEY,
    level: str = "cases",
    timestamp_key: str = "time:timestamp",
    case_id_key: str = "case:concept:name",
) -> Union[EventLog, pd.DataFrame]:
    """
    Filters the event log, keeping only the events that have an attribute value which occurs:
    - in at least the specified (min_relative_stake) percentage of events when level="events",
    - in at least the specified (min_relative_stake) percentage of cases when level="cases".

    :param log: Event log or Pandas DataFrame.
    :param min_relative_stake: Minimum percentage of cases (expressed as a number between 0 and 1) in which the attribute should occur.
    :param attribute_key: The attribute to filter.
    :param level: The level of the filter (if level="events", then events; if level="cases", then cases).
    :param timestamp_key: Attribute to be used for the timestamp.
    :param case_id_key: Attribute to be used as case identifier.
    :return: Filtered event log or Pandas DataFrame.

    .. code-block:: python3

        import pm4py

        filtered_dataframe = pm4py.filter_log_relative_occurrence_event_attribute(
            dataframe,
            0.5,
            attribute_key='concept:name',
            level='cases',
            case_id_key='case:concept:name',
            timestamp_key='time:timestamp'
        )
    """
    __event_log_deprecation_warning(log)

    parameters = get_properties(
        log,
        timestamp_key=timestamp_key,
        case_id_key=case_id_key,
        activity_key=attribute_key,
    )
    if _is_dataframe_like(log):
        check_pandas_dataframe_columns(
            log, timestamp_key=timestamp_key, case_id_key=case_id_key
        )
        filtering_pkg = _get_dataframe_filtering_package(log)
        attributes_filter = filtering_pkg.attributes.attributes_filter

        parameters[attributes_filter.Parameters.ATTRIBUTE_KEY] = attribute_key
        parameters[attributes_filter.Parameters.KEEP_ONCE_PER_CASE] = (
            True if level == "cases" else False
        )
        return attributes_filter.filter_df_relative_occurrence_event_attribute(
            log, min_relative_stake, parameters=parameters
        )
    else:
        from pm4py.algo.filtering.log.attributes import attributes_filter

        parameters[attributes_filter.Parameters.ATTRIBUTE_KEY] = attribute_key
        parameters[attributes_filter.Parameters.KEEP_ONCE_PER_CASE] = (
            True if level == "cases" else False
        )
        return (
            attributes_filter.filter_log_relative_occurrence_event_attribute(
                log, min_relative_stake, parameters=parameters
            )
        )


def filter_start_activities(
    log: Union[EventLog, pd.DataFrame],
    activities: Union[Set[str], List[str]],
    retain: bool = True,
    activity_key: str = "concept:name",
    timestamp_key: str = "time:timestamp",
    case_id_key: str = "case:concept:name",
) -> Union[EventLog, pd.DataFrame]:
    """
    Filters cases that have a start activity in the provided list.

    :param log: Event log or Pandas DataFrame.
    :param activities: Collection of start activities.
    :param retain: If True, retains the traces containing the given start activities; if False, drops the traces.
    :param activity_key: Attribute to be used for the activity.
    :param timestamp_key: Attribute to be used for the timestamp.
    :param case_id_key: Attribute to be used as case identifier.
    :return: Filtered event log or Pandas DataFrame.

    .. code-block:: python3

        import pm4py

        filtered_dataframe = pm4py.filter_start_activities(
            dataframe,
            ['Act. A'],
            activity_key='concept:name',
            case_id_key='case:concept:name',
            timestamp_key='time:timestamp'
        )
    """
    __event_log_deprecation_warning(log)

    parameters = get_properties(
        log,
        activity_key=activity_key,
        timestamp_key=timestamp_key,
        case_id_key=case_id_key,
    )
    if _is_dataframe_like(log):
        check_pandas_dataframe_columns(
            log,
            activity_key=activity_key,
            timestamp_key=timestamp_key,
            case_id_key=case_id_key,
        )
        filtering_pkg = _get_dataframe_filtering_package(log)
        start_activities_filter = (
            filtering_pkg.start_activities.start_activities_filter
        )

        parameters[start_activities_filter.Parameters.POSITIVE] = retain
        return start_activities_filter.apply(
            log, activities, parameters=parameters
        )
    else:
        from pm4py.algo.filtering.log.start_activities import (
            start_activities_filter,
        )

        parameters[start_activities_filter.Parameters.POSITIVE] = retain
        return start_activities_filter.apply(
            log, activities, parameters=parameters
        )


def filter_end_activities(
    log: Union[EventLog, pd.DataFrame],
    activities: Union[Set[str], List[str]],
    retain: bool = True,
    activity_key: str = "concept:name",
    timestamp_key: str = "time:timestamp",
    case_id_key: str = "case:concept:name",
) -> Union[EventLog, pd.DataFrame]:
    """
    Filters cases that have an end activity in the provided list.

    :param log: Event log or Pandas DataFrame.
    :param activities: Collection of end activities.
    :param retain: If True, retains the traces containing the given end activities; if False, drops the traces.
    :param activity_key: Attribute to be used for the activity.
    :param timestamp_key: Attribute to be used for the timestamp.
    :param case_id_key: Attribute to be used as case identifier.
    :return: Filtered event log or Pandas DataFrame.

    .. code-block:: python3

        import pm4py

        filtered_dataframe = pm4py.filter_end_activities(
            dataframe,
            ['Act. Z'],
            activity_key='concept:name',
            case_id_key='case:concept:name',
            timestamp_key='time:timestamp'
        )
    """
    __event_log_deprecation_warning(log)

    parameters = get_properties(
        log,
        activity_key=activity_key,
        timestamp_key=timestamp_key,
        case_id_key=case_id_key,
    )
    if _is_dataframe_like(log):
        check_pandas_dataframe_columns(
            log,
            activity_key=activity_key,
            timestamp_key=timestamp_key,
            case_id_key=case_id_key,
        )
        filtering_pkg = _get_dataframe_filtering_package(log)
        end_activities_filter = (
            filtering_pkg.end_activities.end_activities_filter
        )

        parameters[end_activities_filter.Parameters.POSITIVE] = retain
        return end_activities_filter.apply(
            log, activities, parameters=parameters
        )
    else:
        from pm4py.algo.filtering.log.end_activities import (
            end_activities_filter,
        )

        parameters[end_activities_filter.Parameters.POSITIVE] = retain
        return end_activities_filter.apply(
            log, activities, parameters=parameters
        )


def filter_event_attribute_values(
    log: Union[EventLog, pd.DataFrame],
    attribute_key: str,
    values: Union[Set[str], List[str]],
    level: Optional[str] = None,
    retain: bool = True,
    case_id_key: str = "case:concept:name",
) -> Union[EventLog, pd.DataFrame]:
    """
    Filters a log object based on the values of a specified event attribute.

    :param log: Event log or Pandas DataFrame.
    :param attribute_key: Attribute to filter.
    :param values: Admitted or forbidden values.
    :param level: Specifies how the filter should be applied ('case' filters the cases where at least one occurrence happens; 'event' filters the events, potentially trimming the cases).
    :param retain: Specifies if the values should be kept or removed.
    :param case_id_key: Attribute to be used as case identifier.
    :return: Filtered event log or Pandas DataFrame.

    .. code-block:: python3

        import pm4py

        filtered_dataframe = pm4py.filter_event_attribute_values(
            dataframe,
            'concept:name',
            ['Act. A', 'Act. Z'],
            case_id_key='case:concept:name'
        )
    """
    __event_log_deprecation_warning(log)

    if level is None:
        __event_log_filtering_level_warning()

    parameters = get_properties(log, case_id_key=case_id_key)
    parameters[constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY] = attribute_key
    if _is_dataframe_like(log):
        check_pandas_dataframe_columns(log, case_id_key=case_id_key)
        filtering_pkg = _get_dataframe_filtering_package(log)
        attributes_filter = filtering_pkg.attributes.attributes_filter

        if level == "event":
            parameters[attributes_filter.Parameters.POSITIVE] = retain
            return attributes_filter.apply_events(
                log, values, parameters=parameters
            )
        elif level == "case":
            parameters[attributes_filter.Parameters.POSITIVE] = retain
            return attributes_filter.apply(log, values, parameters=parameters)
    else:
        from pm4py.algo.filtering.log.attributes import attributes_filter

        if level == "event":
            parameters[attributes_filter.Parameters.POSITIVE] = retain
            return attributes_filter.apply_events(
                log, values, parameters=parameters
            )
        elif level == "case":
            parameters[attributes_filter.Parameters.POSITIVE] = retain
            return attributes_filter.apply(log, values, parameters=parameters)


def filter_trace_attribute_values(
    log: Union[EventLog, pd.DataFrame],
    attribute_key: str,
    values: Union[Set[str], List[str]],
    retain: bool = True,
    case_id_key: str = "case:concept:name",
) -> Union[EventLog, pd.DataFrame]:
    """
    Filters a log based on the values of a specified trace attribute.

    :param log: Event log or Pandas DataFrame.
    :param attribute_key: Attribute to filter.
    :param values: Collection of values to filter.
    :param retain: Boolean value indicating whether to keep or discard matching traces.
    :param case_id_key: Attribute to be used as case identifier.
    :return: Filtered event log or Pandas DataFrame.

    .. code-block:: python3

        import pm4py

        filtered_dataframe = pm4py.filter_trace_attribute_values(
            dataframe,
            'case:creator',
            ['Mike'],
            case_id_key='case:concept:name'
        )
    """
    __event_log_deprecation_warning(log)

    parameters = get_properties(log, case_id_key=case_id_key)
    parameters[constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY] = attribute_key
    if _is_dataframe_like(log):
        check_pandas_dataframe_columns(log, case_id_key=case_id_key)
        filtering_pkg = _get_dataframe_filtering_package(log)
        attributes_filter = filtering_pkg.attributes.attributes_filter

        parameters[attributes_filter.Parameters.POSITIVE] = retain
        return attributes_filter.apply(log, values, parameters=parameters)
    else:
        from pm4py.algo.filtering.log.attributes import attributes_filter

        parameters[attributes_filter.Parameters.POSITIVE] = retain
        return attributes_filter.apply_trace_attribute(
            log, values, parameters=parameters
        )


def filter_variants(
    log: Union[EventLog, pd.DataFrame],
    variants: Union[Set[str], List[str], List[Tuple[str]]],
    retain: bool = True,
    activity_key: str = "concept:name",
    timestamp_key: str = "time:timestamp",
    case_id_key: str = "case:concept:name",
) -> Union[EventLog, pd.DataFrame]:
    """
    Filters a log based on a specified set of variants.

    :param log: Event log or Pandas DataFrame.
    :param variants: Collection of variants to filter. A variant should be specified as a list of tuples of activity names, e.g., [('a', 'b', 'c')].
    :param retain: Boolean indicating whether to retain (if True) or remove (if False) traces conforming to the specified variants.
    :param activity_key: Attribute to be used for the activity.
    :param timestamp_key: Attribute to be used for the timestamp.
    :param case_id_key: Attribute to be used as case identifier.
    :return: Filtered event log or Pandas DataFrame.

    .. code-block:: python3

        import pm4py

        filtered_dataframe = pm4py.filter_variants(
            dataframe,
            [('Act. A', 'Act. B', 'Act. Z'), ('Act. A', 'Act. C', 'Act. Z')],
            activity_key='concept:name',
            case_id_key='case:concept:name',
            timestamp_key='time:timestamp'
        )
    """
    __event_log_deprecation_warning(log)

    from pm4py.util import variants_util

    parameters = get_properties(
        log,
        activity_key=activity_key,
        timestamp_key=timestamp_key,
        case_id_key=case_id_key,
    )
    if _is_dataframe_like(log):
        check_pandas_dataframe_columns(
            log,
            activity_key=activity_key,
            timestamp_key=timestamp_key,
            case_id_key=case_id_key,
        )
        filtering_pkg = _get_dataframe_filtering_package(log)
        variants_filter = filtering_pkg.variants.variants_filter

        parameters[variants_filter.Parameters.POSITIVE] = retain
        return variants_filter.apply(log, variants, parameters=parameters)
    else:
        from pm4py.algo.filtering.log.variants import variants_filter

        parameters[variants_filter.Parameters.POSITIVE] = retain
        return variants_filter.apply(log, variants, parameters=parameters)


def filter_directly_follows_relation(
    log: Union[EventLog, pd.DataFrame],
    relations: List[str],
    retain: bool = True,
    activity_key: str = "concept:name",
    timestamp_key: str = "time:timestamp",
    case_id_key: str = "case:concept:name",
) -> Union[EventLog, pd.DataFrame]:
    """
    Retains traces that contain any of the specified 'directly follows' relations.
    For example, if relations == [('a','b'),('a','c')] and log [<a,b,c>,<a,c,b>,<a,d,b>],
    the resulting log will contain traces describing [<a,b,c>,<a,c,b>].

    :param log: Event log or Pandas DataFrame.
    :param relations: List of activity name pairs, representing allowed or forbidden paths.
    :param retain: Boolean indicating whether the paths should be kept (if True) or removed (if False).
    :param activity_key: Attribute to be used for the activity.
    :param timestamp_key: Attribute to be used for the timestamp.
    :param case_id_key: Attribute to be used as case identifier.
    :return: Filtered event log or Pandas DataFrame.

    .. code-block:: python3

        import pm4py

        filtered_dataframe = pm4py.filter_directly_follows_relation(
            dataframe,
            [('A', 'B'), ('A', 'C')],
            activity_key='concept:name',
            case_id_key='case:concept:name',
            timestamp_key='time:timestamp'
        )
    """
    __event_log_deprecation_warning(log)

    parameters = get_properties(
        log,
        activity_key=activity_key,
        timestamp_key=timestamp_key,
        case_id_key=case_id_key,
    )
    if _is_dataframe_like(log):
        filtering_pkg = _get_dataframe_filtering_package(log)
        paths_filter = filtering_pkg.paths.paths_filter

        parameters[paths_filter.Parameters.POSITIVE] = retain
        return paths_filter.apply(log, relations, parameters=parameters)
    else:
        from pm4py.algo.filtering.log.paths import paths_filter

        parameters[paths_filter.Parameters.POSITIVE] = retain
        return paths_filter.apply(log, relations, parameters=parameters)


def filter_eventually_follows_relation(
    log: Union[EventLog, pd.DataFrame],
    relations: List[str],
    retain: bool = True,
    activity_key: str = "concept:name",
    timestamp_key: str = "time:timestamp",
    case_id_key: str = "case:concept:name",
) -> Union[EventLog, pd.DataFrame]:
    """
    Retains traces that contain any of the specified 'eventually follows' relations.
    For example, if relations == [('a','b'),('a','c')] and log [<a,b,c>,<a,c,b>,<a,d,b>],
    the resulting log will contain traces describing [<a,b,c>,<a,c,b>,<a,d,b>].

    :param log: Event log or Pandas DataFrame.
    :param relations: List of activity name pairs, representing allowed or forbidden paths.
    :param retain: Boolean indicating whether the paths should be kept (if True) or removed (if False).
    :param activity_key: Attribute to be used for the activity.
    :param timestamp_key: Attribute to be used for the timestamp.
    :param case_id_key: Attribute to be used as case identifier.
    :return: Filtered event log or Pandas DataFrame.

    .. code-block:: python3

        import pm4py

        filtered_dataframe = pm4py.filter_eventually_follows_relation(
            dataframe,
            [('A', 'B'), ('A', 'C')],
            activity_key='concept:name',
            case_id_key='case:concept:name',
            timestamp_key='time:timestamp'
        )
    """
    __event_log_deprecation_warning(log)

    parameters = get_properties(
        log,
        activity_key=activity_key,
        timestamp_key=timestamp_key,
        case_id_key=case_id_key,
    )
    if _is_dataframe_like(log):
        filtering_pkg = _get_dataframe_filtering_package(log)
        ltl_checker = filtering_pkg.ltl.ltl_checker

        parameters[ltl_checker.Parameters.POSITIVE] = retain

        if not is_polars_lazyframe(log):
            if retain:
                cases = set()
            else:
                cases = set(log[case_id_key].to_numpy().tolist())
            for path in relations:
                filt_log = ltl_checker.eventually_follows(
                    log, path, parameters=parameters
                )
                this_traces = set(filt_log[case_id_key].to_numpy().tolist())
                if retain:
                    cases = cases.union(this_traces)
                else:
                    cases = cases.intersection(this_traces)
            return log[log[case_id_key].isin(cases)]
        else:
            import polars as pl  # type: ignore[import-untyped]

            case_frames = []
            for path in relations:
                filt_log = ltl_checker.eventually_follows(
                    log, path, parameters=parameters
                )
                case_frames.append(
                    filt_log.select(pl.col(case_id_key)).unique()
                )

            if retain:
                if not case_frames:
                    return log.filter(pl.lit(False))
                cases_frame = pl.concat(case_frames).unique()
                return log.join(cases_frame, on=case_id_key, how="inner", maintain_order="left")
            else:
                if not case_frames:
                    return log
                cases_frame = case_frames[0]
                for frame in case_frames[1:]:
                    cases_frame = cases_frame.join(
                        frame, on=case_id_key, how="inner",
                        maintain_order="left",
                    )
                return log.join(cases_frame, on=case_id_key, how="inner", maintain_order="left")
    else:
        from pm4py.algo.filtering.log.ltl import ltl_checker

        parameters[ltl_checker.Parameters.POSITIVE] = retain
        if retain:
            cases = set()
        else:
            cases = set(id(trace) for trace in log)
        for path in relations:
            filt_log = ltl_checker.eventually_follows(
                log, path, parameters=parameters
            )
            this_traces = set(id(trace) for trace in filt_log)
            if retain:
                cases = cases.union(this_traces)
            else:
                cases = cases.intersection(this_traces)
        filtered_log = EventLog(
            attributes=log.attributes,
            extensions=log.extensions,
            omni_present=log.omni_present,
            classifiers=log.classifiers,
            properties=log.properties,
        )
        for trace in log:
            if id(trace) in cases:
                filtered_log.append(trace)
        return filtered_log


def filter_time_range(
    log: Union[EventLog, pd.DataFrame],
    dt1: str,
    dt2: str,
    mode: str = "events",
    timestamp_key: str = "time:timestamp",
    case_id_key: str = "case:concept:name",
) -> Union[EventLog, pd.DataFrame]:
    """
    Filters a log based on a time interval.

    :param log: Event log or Pandas DataFrame.
    :param dt1: Left extreme of the interval.
    :param dt2: Right extreme of the interval.
    :param mode: Modality of filtering. Supported:
                 - 'events': keep events within timeframe.
                 - 'traces_contained': keep traces fully contained in timeframe.
                 - 'traces_intersecting': keep traces intersecting timeframe.
                 - 'traces_starting_in': keep traces whose first event is in timeframe.
                 - 'traces_starting_in_exclude': exclude traces whose first event is in timeframe.
                 - 'traces_completing_in': keep traces whose last event is in timeframe.
                 - 'traces_completing_in_exclude': exclude traces whose last event is in timeframe.
    :param timestamp_key: Attribute to be used for the timestamp.
    :param case_id_key: Attribute to be used as case identifier.
    :return: Filtered event log or Pandas DataFrame.
    """
    __event_log_deprecation_warning(log)

    properties = get_properties(
        log, timestamp_key=timestamp_key, case_id_key=case_id_key
    )

    # Helper: compute "positive" flag from mode for the new variants
    def _positive_from_mode(m: str) -> bool:
        return not (m.endswith("_exclude"))

    if _is_dataframe_like(log):
        filtering_pkg = _get_dataframe_filtering_package(log)
        timestamp_filter = filtering_pkg.timestamp.timestamp_filter

        if mode == "events":
            return timestamp_filter.apply_events(
                log, dt1, dt2, parameters=properties
            )
        elif mode == "traces_contained":
            return timestamp_filter.filter_traces_contained(
                log, dt1, dt2, parameters=properties
            )
        elif mode == "traces_intersecting":
            return timestamp_filter.filter_traces_intersecting(
                log, dt1, dt2, parameters=properties
            )
        elif mode in ("traces_starting_in", "traces_starting_in_exclude"):
            params = dict(properties)
            params["positive"] = _positive_from_mode(mode)
            return timestamp_filter.filter_traces_starting_in_timeframe(
                log, dt1, dt2, parameters=params
            )
        elif mode in ("traces_completing_in", "traces_completing_in_exclude"):
            params = dict(properties)
            params["positive"] = _positive_from_mode(mode)
            return timestamp_filter.filter_traces_completing_in_timeframe(
                log, dt1, dt2, parameters=params
            )
        else:
            if constants.SHOW_INTERNAL_WARNINGS:
                warnings.warn(
                    f"Mode provided: {mode} is not recognized; original log returned!"
                )
            return log
    else:
        from pm4py.algo.filtering.log.timestamp import timestamp_filter

        if mode == "events":
            return timestamp_filter.apply_events(
                log, dt1, dt2, parameters=properties
            )
        elif mode == "traces_contained":
            return timestamp_filter.filter_traces_contained(
                log, dt1, dt2, parameters=properties
            )
        elif mode == "traces_intersecting":
            return timestamp_filter.filter_traces_intersecting(
                log, dt1, dt2, parameters=properties
            )
        elif mode in ("traces_starting_in", "traces_starting_in_exclude"):
            params = dict(properties)
            params["positive"] = _positive_from_mode(mode)
            return timestamp_filter.filter_traces_starting_in_timeframe(
                log, dt1, dt2, parameters=params
            )
        elif mode in ("traces_completing_in", "traces_completing_in_exclude"):
            params = dict(properties)
            params["positive"] = _positive_from_mode(mode)
            return timestamp_filter.filter_traces_completing_in_timeframe(
                log, dt1, dt2, parameters=params
            )
        else:
            if constants.SHOW_INTERNAL_WARNINGS:
                warnings.warn(
                    f"Mode provided: {mode} is not recognized; original log returned!"
                )
            return log


def filter_between(
    log: Union[EventLog, pd.DataFrame],
    act1: Union[str, List[str]],
    act2: Union[str, List[str]],
    activity_key: str = "concept:name",
    timestamp_key: str = "time:timestamp",
    case_id_key: str = "case:concept:name",
) -> Union[EventLog, pd.DataFrame]:
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

    :param log: Event log or Pandas DataFrame.
    :param act1: Source activity or collection of activities.
    :param act2: Target activity or collection of activities.
    :param activity_key: Attribute to be used for the activity.
    :param timestamp_key: Attribute to be used for the timestamp.
    :param case_id_key: Attribute to be used as case identifier.
    :return: Filtered event log or Pandas DataFrame.

    .. code-block:: python3

        import pm4py

        filtered_dataframe = pm4py.filter_between(
            dataframe,
            'A',
            'D',
            activity_key='concept:name',
            case_id_key='case:concept:name',
            timestamp_key='time:timestamp'
        )
    """
    __event_log_deprecation_warning(log)

    parameters = get_properties(
        log,
        activity_key=activity_key,
        timestamp_key=timestamp_key,
        case_id_key=case_id_key,
    )
    if _is_dataframe_like(log):
        check_pandas_dataframe_columns(
            log,
            activity_key=activity_key,
            timestamp_key=timestamp_key,
            case_id_key=case_id_key,
        )
        filtering_pkg = _get_dataframe_filtering_package(log)
        between_filter = filtering_pkg.between.between_filter

        return between_filter.apply(log, act1, act2, parameters=parameters)
    else:
        from pm4py.algo.filtering.log.between import between_filter

        return between_filter.apply(log, act1, act2, parameters=parameters)


def filter_case_size(
    log: Union[EventLog, pd.DataFrame],
    min_size: int,
    max_size: int,
    case_id_key: str = "case:concept:name",
) -> Union[EventLog, pd.DataFrame]:
    """
    Filters the event log, keeping cases that have a length (number of events) between min_size and max_size.

    :param log: Event log or Pandas DataFrame.
    :param min_size: Minimum allowed number of events.
    :param max_size: Maximum allowed number of events.
    :param case_id_key: Attribute to be used as case identifier.
    :return: Filtered event log or Pandas DataFrame.

    .. code-block:: python3

        import pm4py

        filtered_dataframe = pm4py.filter_case_size(
            dataframe,
            5,
            10,
            case_id_key='case:concept:name'
        )
    """
    __event_log_deprecation_warning(log)

    parameters = get_properties(log, case_id_key=case_id_key)
    if _is_dataframe_like(log):
        check_pandas_dataframe_columns(log, case_id_key=case_id_key)
        filtering_pkg = _get_dataframe_filtering_package(log)
        case_filter = filtering_pkg.cases.case_filter

        case_id = (
            parameters[constants.PARAMETER_CONSTANT_CASEID_KEY]
            if constants.PARAMETER_CONSTANT_CASEID_KEY in parameters
            else constants.CASE_CONCEPT_NAME
        )
        return case_filter.filter_on_case_size(
            log, case_id, min_size, max_size
        )
    else:
        from pm4py.algo.filtering.log.cases import case_filter

        return case_filter.filter_on_case_size(log, min_size, max_size)


def filter_case_performance(
    log: Union[EventLog, pd.DataFrame],
    min_performance: float,
    max_performance: float,
    timestamp_key: str = "time:timestamp",
    case_id_key: str = "case:concept:name",
) -> Union[EventLog, pd.DataFrame]:
    """
    Filters the event log, keeping cases that have a duration (the timestamp of the last event minus the timestamp
    of the first event) between min_performance and max_performance.

    :param log: Event log or Pandas DataFrame.
    :param min_performance: Minimum allowed case duration.
    :param max_performance: Maximum allowed case duration.
    :param timestamp_key: Attribute to be used for the timestamp.
    :param case_id_key: Attribute to be used as case identifier.
    :return: Filtered event log or Pandas DataFrame.

    .. code-block:: python3

        import pm4py

        filtered_dataframe = pm4py.filter_case_performance(
            dataframe,
            3600.0,
            86400.0,
            timestamp_key='time:timestamp',
            case_id_key='case:concept:name'
        )
    """
    __event_log_deprecation_warning(log)

    parameters = get_properties(
        log, timestamp_key=timestamp_key, case_id_key=case_id_key
    )
    if _is_dataframe_like(log):
        check_pandas_dataframe_columns(
            log, timestamp_key=timestamp_key, case_id_key=case_id_key
        )
        filtering_pkg = _get_dataframe_filtering_package(log)
        case_filter = filtering_pkg.cases.case_filter

        return case_filter.filter_case_performance(
            log, min_performance, max_performance, parameters=parameters
        )
    else:
        from pm4py.algo.filtering.log.cases import case_filter

        return case_filter.filter_case_performance(
            log, min_performance, max_performance, parameters=parameters
        )


def filter_activities_rework(
    log: Union[EventLog, pd.DataFrame],
    activity: str,
    min_occurrences: int = 2,
    activity_key: str = "concept:name",
    timestamp_key: str = "time:timestamp",
    case_id_key: str = "case:concept:name",
) -> Union[EventLog, pd.DataFrame]:
    """
    Filters the event log, keeping cases where the specified activity occurs at least min_occurrences times.

    :param log: Event log or Pandas DataFrame.
    :param activity: Activity to consider.
    :param min_occurrences: Minimum desired number of occurrences.
    :param activity_key: Attribute to be used for the activity.
    :param timestamp_key: Attribute to be used for the timestamp.
    :param case_id_key: Attribute to be used as case identifier.
    :return: Filtered event log or Pandas DataFrame.

    .. code-block:: python3

        import pm4py

        filtered_dataframe = pm4py.filter_activities_rework(
            dataframe,
            'Approve Order',
            2,
            activity_key='concept:name',
            timestamp_key='time:timestamp',
            case_id_key='case:concept:name'
        )
    """
    __event_log_deprecation_warning(log)

    parameters = get_properties(
        log,
        activity_key=activity_key,
        timestamp_key=timestamp_key,
        case_id_key=case_id_key,
    )
    parameters["min_occurrences"] = min_occurrences
    is_polars = is_polars_lazyframe(log)
    if _is_dataframe_like(log):
        check_pandas_dataframe_columns(
            log,
            activity_key=activity_key,
            timestamp_key=timestamp_key,
            case_id_key=case_id_key,
        )
        filtering_pkg = _get_dataframe_filtering_package(log)
        rework_filter = filtering_pkg.rework.rework_filter

        if is_polars:
            if hasattr(rework_filter, "apply_activity_set"):
                return rework_filter.apply_activity_set(
                    log, {activity}, parameters=parameters
                )
            return rework_filter.apply(log, parameters=parameters)

        return rework_filter.apply(log, activity, parameters=parameters)
    else:
        from pm4py.algo.filtering.log.rework import rework_filter

        return rework_filter.apply(log, activity, parameters=parameters)


def filter_paths_performance(
    log: Union[EventLog, pd.DataFrame],
    path: Tuple[str, str],
    min_performance: float,
    max_performance: float,
    keep: bool = True,
    activity_key: str = "concept:name",
    timestamp_key: str = "time:timestamp",
    case_id_key: str = "case:concept:name",
) -> Union[EventLog, pd.DataFrame]:
    """
    Filters the event log based on the performance of specified paths.

    - If keep=True, retains cases having the specified path (tuple of 2 activities) with a duration between min_performance and max_performance.
    - If keep=False, discards cases having the specified path with a duration between min_performance and max_performance.

    :param log: Event log or Pandas DataFrame.
    :param path: Tuple of two activities (source_activity, target_activity).
    :param min_performance: Minimum allowed performance of the path.
    :param max_performance: Maximum allowed performance of the path.
    :param keep: Boolean indicating whether to keep (if True) or discard (if False) the cases with the specified performance.
    :param activity_key: Attribute to be used for the activity.
    :param timestamp_key: Attribute to be used for the timestamp.
    :param case_id_key: Attribute to be used as case identifier.
    :return: Filtered event log or Pandas DataFrame.

    .. code-block:: python3

        import pm4py

        filtered_dataframe = pm4py.filter_paths_performance(
            dataframe,
            ('A', 'D'),
            3600.0,
            86400.0,
            activity_key='concept:name',
            timestamp_key='time:timestamp',
            case_id_key='case:concept:name'
        )
    """
    __event_log_deprecation_warning(log)

    parameters = get_properties(
        log,
        activity_key=activity_key,
        timestamp_key=timestamp_key,
        case_id_key=case_id_key,
    )
    parameters["positive"] = keep
    parameters["min_performance"] = min_performance
    parameters["max_performance"] = max_performance

    path = tuple(path)
    if _is_dataframe_like(log):
        check_pandas_dataframe_columns(
            log,
            activity_key=activity_key,
            timestamp_key=timestamp_key,
            case_id_key=case_id_key,
        )
        filtering_pkg = _get_dataframe_filtering_package(log)
        paths_filter = filtering_pkg.paths.paths_filter

        return paths_filter.apply_performance(log, path, parameters=parameters)
    else:
        from pm4py.algo.filtering.log.paths import paths_filter

        return paths_filter.apply_performance(log, path, parameters=parameters)


def filter_variants_top_k(
    log: Union[EventLog, pd.DataFrame],
    k: int,
    activity_key: str = "concept:name",
    timestamp_key: str = "time:timestamp",
    case_id_key: str = "case:concept:name",
) -> Union[EventLog, pd.DataFrame]:
    """
    Keeps the top-k variants of the log.

    :param log: Event log or Pandas DataFrame.
    :param k: Number of variants to keep.
    :param activity_key: Attribute to be used for the activity.
    :param timestamp_key: Attribute to be used for the timestamp.
    :param case_id_key: Attribute to be used as case identifier.
    :return: Filtered event log or Pandas DataFrame.

    .. code-block:: python3

        import pm4py

        filtered_dataframe = pm4py.filter_variants_top_k(
            dataframe,
            5,
            activity_key='concept:name',
            timestamp_key='time:timestamp',
            case_id_key='case:concept:name'
        )
    """
    __event_log_deprecation_warning(log)

    parameters = get_properties(
        log,
        activity_key=activity_key,
        timestamp_key=timestamp_key,
        case_id_key=case_id_key,
    )
    if _is_dataframe_like(log):
        check_pandas_dataframe_columns(
            log,
            activity_key=activity_key,
            timestamp_key=timestamp_key,
            case_id_key=case_id_key,
        )
        filtering_pkg = _get_dataframe_filtering_package(log)
        variants_filter = filtering_pkg.variants.variants_filter

        return variants_filter.filter_variants_top_k(
            log, k, parameters=parameters
        )
    else:
        from pm4py.algo.filtering.log.variants import variants_filter

        return variants_filter.filter_variants_top_k(
            log, k, parameters=parameters
        )


def filter_variants_by_coverage_percentage(
    log: Union[EventLog, pd.DataFrame],
    min_coverage_percentage: float,
    activity_key: str = "concept:name",
    timestamp_key: str = "time:timestamp",
    case_id_key: str = "case:concept:name",
) -> Union[EventLog, pd.DataFrame]:
    """
    Filters the variants of the log based on a coverage percentage.
    For example, if min_coverage_percentage=0.4 and the log has 1000 cases with:
    - 500 cases of variant 1,
    - 400 cases of variant 2,
    - 100 cases of variant 3,
    the filter keeps only the traces of variant 1 and variant 2.

    :param log: Event log or Pandas DataFrame.
    :param min_coverage_percentage: Minimum allowed percentage of coverage.
    :param activity_key: Attribute to be used for the activity.
    :param timestamp_key: Attribute to be used for the timestamp.
    :param case_id_key: Attribute to be used as case identifier.
    :return: Filtered event log or Pandas DataFrame.

    .. code-block:: python3

        import pm4py

        filtered_dataframe = pm4py.filter_variants_by_coverage_percentage(
            dataframe,
            0.1,
            activity_key='concept:name',
            timestamp_key='time:timestamp',
            case_id_key='case:concept:name'
        )
    """
    __event_log_deprecation_warning(log)

    parameters = get_properties(
        log,
        activity_key=activity_key,
        timestamp_key=timestamp_key,
        case_id_key=case_id_key,
    )
    if _is_dataframe_like(log):
        check_pandas_dataframe_columns(
            log,
            activity_key=activity_key,
            timestamp_key=timestamp_key,
            case_id_key=case_id_key,
        )
        filtering_pkg = _get_dataframe_filtering_package(log)
        variants_filter = filtering_pkg.variants.variants_filter

        return variants_filter.filter_variants_by_coverage_percentage(
            log, min_coverage_percentage, parameters=parameters
        )
    else:
        from pm4py.algo.filtering.log.variants import variants_filter

        return variants_filter.filter_variants_by_coverage_percentage(
            log, min_coverage_percentage, parameters=parameters
        )


def filter_prefixes(
    log: Union[EventLog, pd.DataFrame],
    activity: str,
    strict: bool = True,
    first_or_last: str = "first",
    activity_key: str = "concept:name",
    timestamp_key: str = "time:timestamp",
    case_id_key: str = "case:concept:name",
) -> Union[EventLog, pd.DataFrame]:
    """
    Filters the log, keeping the prefixes leading up to a given activity.
    For example, for a log with traces:
    - A,B,C,D
    - A,B,Z,A,B,C,D
    - A,B,C,D,C,E,C,F

    The prefixes to "C" are respectively:
    - A,B
    - A,B,Z,A,B
    - A,B

    :param log: Event log or Pandas DataFrame.
    :param activity: Target activity for the filter.
    :param strict: Applies the filter strictly, cutting the occurrences of the selected activity.
    :param first_or_last: Decides if the first or last occurrence of an activity should be selected as the baseline for the filter.
    :param activity_key: Attribute to be used for the activity.
    :param timestamp_key: Attribute to be used for the timestamp.
    :param case_id_key: Attribute to be used as case identifier.
    :return: Filtered event log or Pandas DataFrame.

    .. code-block:: python3

        import pm4py

        filtered_dataframe = pm4py.filter_prefixes(
            dataframe,
            'Act. C',
            activity_key='concept:name',
            timestamp_key='time:timestamp',
            case_id_key='case:concept:name'
        )
    """
    __event_log_deprecation_warning(log)

    parameters = get_properties(
        log,
        activity_key=activity_key,
        timestamp_key=timestamp_key,
        case_id_key=case_id_key,
    )
    parameters["strict"] = strict
    parameters["first_or_last"] = first_or_last

    if _is_dataframe_like(log):
        check_pandas_dataframe_columns(
            log,
            activity_key=activity_key,
            timestamp_key=timestamp_key,
            case_id_key=case_id_key,
        )
        filtering_pkg = _get_dataframe_filtering_package(log)
        prefix_filter = filtering_pkg.prefixes.prefix_filter
        prefixes_arg = (
            _normalize_sequence_argument(activity)
            if is_polars_lazyframe(log)
            else activity
        )

        return prefix_filter.apply(log, prefixes_arg, parameters=parameters)
    else:
        from pm4py.algo.filtering.log.prefixes import prefix_filter

        return prefix_filter.apply(log, activity, parameters=parameters)


def filter_suffixes(
    log: Union[EventLog, pd.DataFrame],
    activity: str,
    strict: bool = True,
    first_or_last: str = "first",
    activity_key: str = "concept:name",
    timestamp_key: str = "time:timestamp",
    case_id_key: str = "case:concept:name",
) -> Union[EventLog, pd.DataFrame]:
    """
    Filters the log, keeping the suffixes starting from a given activity.
    For example, for a log with traces:
    - A,B,C,D
    - A,B,Z,A,B,C,D
    - A,B,C,D,C,E,C,F

    The suffixes from "C" are respectively:
    - D
    - D
    - D,C,E,C,F

    :param log: Event log or Pandas DataFrame.
    :param activity: Target activity for the filter.
    :param strict: Applies the filter strictly, cutting the occurrences of the selected activity.
    :param first_or_last: Decides if the first or last occurrence of an activity should be selected as the baseline for the filter.
    :param activity_key: Attribute to be used for the activity.
    :param timestamp_key: Attribute to be used for the timestamp.
    :param case_id_key: Attribute to be used as case identifier.
    :return: Filtered event log or Pandas DataFrame.

    .. code-block:: python3

        import pm4py

        filtered_dataframe = pm4py.filter_suffixes(
            dataframe,
            'Act. C',
            activity_key='concept:name',
            timestamp_key='time:timestamp',
            case_id_key='case:concept:name'
        )
    """
    __event_log_deprecation_warning(log)

    parameters = get_properties(
        log,
        activity_key=activity_key,
        timestamp_key=timestamp_key,
        case_id_key=case_id_key,
    )
    parameters["strict"] = strict
    parameters["first_or_last"] = first_or_last

    if _is_dataframe_like(log):
        check_pandas_dataframe_columns(
            log,
            activity_key=activity_key,
            timestamp_key=timestamp_key,
            case_id_key=case_id_key,
        )
        filtering_pkg = _get_dataframe_filtering_package(log)
        suffix_filter = filtering_pkg.suffixes.suffix_filter
        suffixes_arg = (
            _normalize_sequence_argument(activity)
            if is_polars_lazyframe(log)
            else activity
        )

        return suffix_filter.apply(log, suffixes_arg, parameters=parameters)
    else:
        from pm4py.algo.filtering.log.suffixes import suffix_filter

        return suffix_filter.apply(log, activity, parameters=parameters)


def filter_ocel_event_attribute(
    ocel: OCEL,
    attribute_key: str,
    attribute_values: Collection[Any],
    positive: bool = True,
) -> OCEL:
    """
    Filters the object-centric event log based on the provided event attribute values.

    :param ocel: Object-centric event log.
    :param attribute_key: Attribute at the event level to filter.
    :param attribute_values: Collection of attribute values to keep or remove.
    :param positive: Determines whether the values should be kept (True) or removed (False).
    :return: Filtered OCEL.

    .. code-block:: python3

        import pm4py

        filtered_ocel = pm4py.filter_ocel_event_attribute(
            ocel,
            'ocel:activity',
            ['A', 'B', 'D']
        )
    """
    from pm4py.algo.filtering.ocel import event_attributes

    return event_attributes.apply(
        ocel,
        attribute_values,
        parameters={
            event_attributes.Parameters.ATTRIBUTE_KEY: attribute_key,
            event_attributes.Parameters.POSITIVE: positive,
        },
    )


def filter_ocel_object_attribute(
    ocel: OCEL,
    attribute_key: str,
    attribute_values: Collection[Any],
    positive: bool = True,
) -> OCEL:
    """
    Filters the object-centric event log based on the provided object attribute values.

    :param ocel: Object-centric event log.
    :param attribute_key: Attribute at the object level to filter.
    :param attribute_values: Collection of attribute values to keep or remove.
    :param positive: Determines whether the values should be kept (True) or removed (False).
    :return: Filtered OCEL.

    .. code-block:: python3

        import pm4py

        filtered_ocel = pm4py.filter_ocel_object_attribute(
            ocel,
            'ocel:type',
            ['order']
        )
    """
    from pm4py.algo.filtering.ocel import object_attributes

    return object_attributes.apply(
        ocel,
        attribute_values,
        parameters={
            object_attributes.Parameters.ATTRIBUTE_KEY: attribute_key,
            object_attributes.Parameters.POSITIVE: positive,
        },
    )


def filter_ocel_object_types_allowed_activities(
    ocel: OCEL, correspondence_dict: Dict[str, Collection[str]]
) -> OCEL:
    """
    Filters an object-centric event log, keeping only the specified object types with the specified set of allowed activities.

    :param ocel: Object-centric event log.
    :param correspondence_dict: Dictionary containing, for every object type of interest, a collection of allowed activities.
                                Example: {"order": ["Create Order"], "element": ["Create Order", "Create Delivery"]}.
    :return: Filtered OCEL.

    .. code-block:: python3

        import pm4py

        filtered_ocel = pm4py.filter_ocel_object_types_allowed_activities(
            ocel,
            {'order': ['create order', 'pay order'], 'item': ['create item', 'deliver item']}
        )
    """
    from pm4py.algo.filtering.ocel import activity_type_matching

    return activity_type_matching.apply(ocel, correspondence_dict)


def filter_ocel_object_per_type_count(
    ocel: OCEL, min_num_obj_type: Dict[str, int]
) -> OCEL:
    """
    Filters the events of the object-centric logs that are related to at
    least the specified number of objects per type.

    Example::

        pm4py.filter_object_per_type_count(ocel, {"order": 1, "element": 2})

    Would keep the following events::

          ocel:eid ocel:timestamp ocel:activity ocel:type:element ocel:type:order
        0       e1     1980-01-01  Create Order  [i4, i1, i3, i2]            [o1]
        1      e11     1981-01-01  Create Order          [i6, i5]            [o2]
        2      e14     1981-01-04  Create Order          [i8, i7]            [o3]

    :param ocel: Object-centric event log.
    :param min_num_obj_type: Minimum number of objects per type.
    :return: Filtered OCEL.

    .. code-block:: python3

        import pm4py

        filtered_ocel = pm4py.filter_ocel_object_per_type_count(
            ocel,
            {'order': 1, 'element': 2}
        )

    """
    from pm4py.algo.filtering.ocel import objects_ot_count

    return objects_ot_count.apply(ocel, min_num_obj_type)


def filter_ocel_start_events_per_object_type(
    ocel: OCEL, object_type: str
) -> OCEL:
    """
    Filters the events in which a new object of the given object type is spawned.
    For example, an event with activity "Create Order" might spawn new orders.

    :param ocel: Object-centric event log.
    :param object_type: Object type to consider.
    :return: Filtered OCEL.

    .. code-block:: python3

        import pm4py

        filtered_ocel = pm4py.filter_ocel_start_events_per_object_type(
            ocel,
            'delivery'
        )
    """
    from pm4py.algo.filtering.ocel import ot_endpoints

    return ot_endpoints.filter_start_events_per_object_type(ocel, object_type)


def filter_ocel_end_events_per_object_type(
    ocel: OCEL, object_type: str
) -> OCEL:
    """
    Filters the events in which an object of the given object type terminates its lifecycle.
    For example, an event with activity "Pay Order" might terminate an order.

    :param ocel: Object-centric event log.
    :param object_type: Object type to consider.
    :return: Filtered OCEL.

    .. code-block:: python3

        import pm4py

        filtered_ocel = pm4py.filter_ocel_end_events_per_object_type(
            ocel,
            'delivery'
        )
    """
    from pm4py.algo.filtering.ocel import ot_endpoints

    return ot_endpoints.filter_end_events_per_object_type(ocel, object_type)


def filter_ocel_events_timestamp(
    ocel: OCEL,
    min_timest: Union[datetime.datetime, str],
    max_timest: Union[datetime.datetime, str],
    timestamp_key: str = "ocel:timestamp",
) -> OCEL:
    """
    Filters the object-centric event log, keeping events within the provided timestamp range.

    :param ocel: Object-centric event log.
    :param min_timest: Left extreme of the allowed timestamp interval (format: YYYY-mm-dd HH:MM:SS).
    :param max_timest: Right extreme of the allowed timestamp interval (format: YYYY-mm-dd HH:MM:SS).
    :param timestamp_key: The attribute to use as timestamp (default: ocel:timestamp).
    :return: Filtered OCEL.

    .. code-block:: python3

        import pm4py

        filtered_ocel = pm4py.filter_ocel_events_timestamp(
            ocel,
            '1990-01-01 00:00:00',
            '2010-01-01 00:00:00'
        )
    """
    from pm4py.algo.filtering.ocel import event_attributes

    return event_attributes.apply_timestamp(
        ocel,
        min_timest,
        max_timest,
        parameters={"pm4py:param:timestamp_key": timestamp_key},
    )


def filter_four_eyes_principle(
    log: Union[EventLog, pd.DataFrame],
    activity1: str,
    activity2: str,
    activity_key: str = "concept:name",
    timestamp_key: str = "time:timestamp",
    case_id_key: str = "case:concept:name",
    resource_key: str = "org:resource",
    keep_violations: bool = False,
) -> Union[EventLog, pd.DataFrame]:
    """
    Filters out the cases of the log that violate the four-eyes principle on the provided activities.

    :param log: Event log or Pandas DataFrame.
    :param activity1: First activity.
    :param activity2: Second activity.
    :param activity_key: Attribute to be used for the activity.
    :param timestamp_key: Attribute to be used for the timestamp.
    :param case_id_key: Attribute to be used as case identifier.
    :param resource_key: Attribute to be used as resource.
    :param keep_violations: Boolean indicating whether to discard (if False) or retain (if True) the violations.
    :return: Filtered event log or Pandas DataFrame.

    .. code-block:: python3

        import pm4py

        filtered_dataframe = pm4py.filter_four_eyes_principle(
            dataframe,
            'Act. A',
            'Act. B',
            activity_key='concept:name',
            resource_key='org:resource',
            timestamp_key='time:timestamp',
            case_id_key='case:concept:name'
        )
    """
    __event_log_deprecation_warning(log)

    properties = get_properties(
        log,
        activity_key=activity_key,
        timestamp_key=timestamp_key,
        case_id_key=case_id_key,
        resource_key=resource_key,
    )
    properties["positive"] = not keep_violations

    if _is_dataframe_like(log):
        check_pandas_dataframe_columns(
            log,
            activity_key=activity_key,
            timestamp_key=timestamp_key,
            case_id_key=case_id_key,
        )

        filtering_pkg = _get_dataframe_filtering_package(log)
        ltl_checker = filtering_pkg.ltl.ltl_checker

        return ltl_checker.four_eyes_principle(
            log, activity1, activity2, parameters=properties
        )
    else:
        from pm4py.algo.filtering.log.ltl import ltl_checker

        return ltl_checker.four_eyes_principle(
            log, activity1, activity2, parameters=properties
        )


def filter_activity_done_different_resources(
    log: Union[EventLog, pd.DataFrame],
    activity: str,
    activity_key: str = "concept:name",
    timestamp_key: str = "time:timestamp",
    case_id_key: str = "case:concept:name",
    resource_key: str = "org:resource",
    keep_violations: bool = True,
) -> Union[EventLog, pd.DataFrame]:
    """
    Filters the cases where an activity is performed by different resources multiple times.

    :param log: Event log or Pandas DataFrame.
    :param activity: Activity to consider.
    :param activity_key: Attribute to be used for the activity.
    :param timestamp_key: Attribute to be used for the timestamp.
    :param case_id_key: Attribute to be used as case identifier.
    :param resource_key: Attribute to be used as resource.
    :param keep_violations: Boolean indicating whether to discard (if False) or retain (if True) the violations.
    :return: Filtered event log or Pandas DataFrame.

    .. code-block:: python3

        import pm4py

        filtered_dataframe = pm4py.filter_activity_done_different_resources(
            dataframe,
            'Act. A',
            activity_key='concept:name',
            resource_key='org:resource',
            timestamp_key='time:timestamp',
            case_id_key='case:concept:name'
        )
    """
    __event_log_deprecation_warning(log)

    properties = get_properties(
        log,
        activity_key=activity_key,
        timestamp_key=timestamp_key,
        case_id_key=case_id_key,
        resource_key=resource_key,
    )
    properties["positive"] = keep_violations

    if _is_dataframe_like(log):
        check_pandas_dataframe_columns(
            log,
            activity_key=activity_key,
            timestamp_key=timestamp_key,
            case_id_key=case_id_key,
        )

        filtering_pkg = _get_dataframe_filtering_package(log)
        ltl_checker = filtering_pkg.ltl.ltl_checker

        return ltl_checker.attr_value_different_persons(
            log, activity, parameters=properties
        )
    else:
        from pm4py.algo.filtering.log.ltl import ltl_checker

        return ltl_checker.attr_value_different_persons(
            log, activity, parameters=properties
        )


def filter_trace_segments(
    log: Union[EventLog, pd.DataFrame],
    admitted_traces: List[List[str]],
    positive: bool = True,
    activity_key: str = "concept:name",
    timestamp_key: str = "time:timestamp",
    case_id_key: str = "case:concept:name",
) -> Union[EventLog, pd.DataFrame]:
    """
    Filters an event log based on a set of trace segments. A trace is a
    sequence of activities and "...".

    where:

    - "..." before an activity indicates that other activities can precede the given activity.
    - "..." after an activity indicates that other activities can follow the given activity.

    Examples:

    - pm4py.filter_trace_segments(log, [["A", "B"]]) retains only cases with the exact process variant A,B.
    - pm4py.filter_trace_segments(log, [["...", "A", "B"]]) retains only cases ending with activities A,B.
    - pm4py.filter_trace_segments(log, [["A", "B", "..."]]) retains only cases starting with activities A,B.
    - pm4py.filter_trace_segments(log, [["...", "A", "B", "C", "..."], ["...", "D", "E", "F", "..."]]) retains cases where:
        - At any point, there is A followed by B followed by C,
        - And at any other point, there is D followed by E followed by F.

    :param log: Event log or Pandas DataFrame.
    :param admitted_traces: Collection of trace segments to admit based on the criteria above.
    :param positive: Boolean indicating whether to keep (if True) or discard (if False) the cases satisfying the filter.
    :param activity_key: Attribute to be used for the activity.
    :param timestamp_key: Attribute to be used for the timestamp.
    :param case_id_key: Attribute to be used as case identifier.
    :return: Filtered event log or Pandas DataFrame.

    .. code-block:: python3

        import pm4py

        log = pm4py.read_xes("tests/input_data/running-example.xes")

        filtered_log = pm4py.filter_trace_segments(
            log,
            [["...", "check ticket", "decide", "reinitiate request", "..."]]
        )
        print(filtered_log)

    """
    __event_log_deprecation_warning(log)

    parameters = get_properties(
        log,
        activity_key=activity_key,
        timestamp_key=timestamp_key,
        case_id_key=case_id_key,
    )
    parameters["positive"] = positive

    if _is_dataframe_like(log):
        check_pandas_dataframe_columns(
            log,
            activity_key=activity_key,
            timestamp_key=timestamp_key,
            case_id_key=case_id_key,
        )
        filtering_pkg = _get_dataframe_filtering_package(log)
        trace_filter = filtering_pkg.traces.trace_filter

        return trace_filter.apply(log, admitted_traces, parameters=parameters)
    else:
        from pm4py.algo.filtering.log.traces import trace_filter

        return trace_filter.apply(log, admitted_traces, parameters=parameters)


def filter_ocel_object_types(
    ocel: OCEL,
    obj_types: Collection[str],
    positive: bool = True,
    level: int = 1,
) -> OCEL:
    """
    Filters the object types of an object-centric event log.

    :param ocel: Object-centric event log.
    :param obj_types: Object types to keep or remove.
    :param positive: Boolean indicating whether to keep (True) or remove (False) the specified object types.
    :param level: Recursively expands the set of object identifiers until the specified level.
    :return: Filtered OCEL.

    .. code-block:: python3

        import pm4py

        ocel = pm4py.read_ocel('log.jsonocel')
        filtered_ocel = pm4py.filter_ocel_object_types(
            ocel,
            ['order']
        )
    """
    from copy import copy
    from pm4py.objects.ocel.util import filtering_utils

    if level == 1:
        filtered_ocel = copy(ocel)
        if positive:
            filtered_ocel.objects = filtered_ocel.objects[
                filtered_ocel.objects[filtered_ocel.object_type_column].isin(
                    obj_types
                )
            ]
        else:
            filtered_ocel.objects = filtered_ocel.objects[
                ~filtered_ocel.objects[filtered_ocel.object_type_column].isin(
                    obj_types
                )
            ]
        return filtering_utils.propagate_object_filtering(filtered_ocel)
    else:
        object_ids = pandas_utils.format_unique(
            ocel.objects[
                ocel.objects[ocel.object_type_column].isin(obj_types)
            ][ocel.object_id_column].unique()
        )
        return filter_ocel_objects(
            ocel, object_ids, level=level, positive=positive
        )


def filter_ocel_objects(
    ocel: OCEL,
    object_identifiers: Collection[str],
    positive: bool = True,
    level: int = 1,
) -> OCEL:
    """
    Filters the object identifiers of an object-centric event log.

    :param ocel: Object-centric event log.
    :param object_identifiers: Object identifiers to keep or remove.
    :param positive: Boolean indicating whether to keep (True) or remove (False) the specified object identifiers.
    :param level: Recursively expands the set of object identifiers until the specified level.
    :return: Filtered OCEL.

    .. code-block:: python3

        import pm4py

        ocel = pm4py.read_ocel('log.jsonocel')
        filtered_ocel = pm4py.filter_ocel_objects(
            ocel,
            ['o1'],
            level=1
        )
    """
    object_identifiers = set(object_identifiers)
    if level > 1:
        ev_rel_obj = (
            ocel.relations.groupby(ocel.event_id_column)[ocel.object_id_column]
            .agg(list)
            .to_dict()
        )
        objects_ids = ocel.objects[ocel.object_id_column].to_numpy().tolist()
        graph = {o: set() for o in objects_ids}
        for ev in ev_rel_obj:
            rel_obj = ev_rel_obj[ev]
            for o1 in rel_obj:
                for o2 in rel_obj:
                    if o1 != o2:
                        graph[o1].add(o2)
        while level > 1:
            curr = list(object_identifiers)
            for el in curr:
                for el2 in graph[el]:
                    object_identifiers.add(el2)
            level = level - 1
    from copy import copy
    from pm4py.objects.ocel.util import filtering_utils

    filtered_ocel = copy(ocel)
    if positive:
        filtered_ocel.objects = filtered_ocel.objects[
            filtered_ocel.objects[ocel.object_id_column].isin(
                object_identifiers
            )
        ]
    else:
        filtered_ocel.objects = filtered_ocel.objects[
            ~filtered_ocel.objects[ocel.object_id_column].isin(
                object_identifiers
            )
        ]
    filtered_ocel = filtering_utils.propagate_object_filtering(filtered_ocel)
    return filtered_ocel

def filter_ocel_events(
    ocel: OCEL, event_identifiers: Collection[str], positive: bool = True
) -> OCEL:
    """
    Filters the event identifiers of an object-centric event log.

    :param ocel: Object-centric event log.
    :param event_identifiers: Event identifiers to keep or remove.
    :param positive: Boolean indicating whether to keep (True) or remove (False) the specified event identifiers.
    :return: Filtered OCEL.

    .. code-block:: python3

        import pm4py

        ocel = pm4py.read_ocel('log.jsonocel')
        filtered_ocel = pm4py.filter_ocel_events(
            ocel,
            ['e1']
        )
    """
    from copy import copy
    from pm4py.objects.ocel.util import filtering_utils

    filtered_ocel = copy(ocel)
    if positive:
        filtered_ocel.events = filtered_ocel.events[
            filtered_ocel.events[ocel.event_id_column].isin(event_identifiers)
        ]
    else:
        filtered_ocel.events = filtered_ocel.events[
            ~filtered_ocel.events[ocel.event_id_column].isin(event_identifiers)
        ]
    return filtering_utils.propagate_event_filtering(filtered_ocel)


def filter_ocel_activities_connected_object_type(
    ocel: OCEL, object_type: str
) -> OCEL:
    """
    Filter an OCEL on the set of activities executed on objects of the given object type.

    :param ocel: object-centric event log
    :param object_type: object type
    :rtype: ``OCEL``

    .. code-block:: python3

        import pm4py

        ocel = pm4py.read_ocel2("tests/input_data/ocel/ocel20_example.xmlocel")
        filtered_ocel = pm4py.filter_ocel_activities_connected_object_type(ocel, "Purchase Order")
        print(filtered_ocel)
    """
    from copy import copy
    from pm4py.objects.ocel.util import filtering_utils

    relations = ocel.relations[
        ocel.relations[ocel.object_type_column] == object_type
    ]
    activities = relations[ocel.event_activity].unique()
    filtered_ocel = copy(ocel)
    filtered_ocel.relations = filtered_ocel.relations[
        filtered_ocel.relations[ocel.event_activity].isin(activities)
    ]

    return filtering_utils.propagate_relations_filtering(filtered_ocel)


def filter_ocel_cc_object(
    ocel: OCEL,
    object_id: str,
    conn_comp: Optional[List[List[str]]] = None,
    return_conn_comp: bool = False,
) -> Union[OCEL, Tuple[OCEL, List[List[str]]]]:
    """
    Returns the connected component of the object-centric event log to which the specified object belongs.

    :param ocel: Object-centric event log.
    :param object_id: Object identifier.
    :param conn_comp: (Optional) Precomputed connected components of the OCEL objects.
    :param return_conn_comp: If True, returns the filtered OCEL along with the computed connected components.
    :return: Filtered OCEL, optionally with the list of connected components.

    .. code-block:: python3

        import pm4py

        ocel = pm4py.read_ocel('log.jsonocel')
        filtered_ocel = pm4py.filter_ocel_cc_object(
            ocel,
            'order1'
        )
    """
    if conn_comp is None:
        from pm4py.algo.transformation.ocel.graphs import (
            object_interaction_graph,
        )

        g0 = object_interaction_graph.apply(ocel)
        g = nx_utils.Graph()

        for edge in g0:
            g.add_edge(edge[0], edge[1])

        conn_comp = list(nx_utils.connected_components(g))

    for cc in conn_comp:
        if object_id in cc:
            if return_conn_comp:
                return filter_ocel_objects(ocel, cc), conn_comp
            else:
                return filter_ocel_objects(ocel, cc)

    if return_conn_comp:
        return filter_ocel_objects(ocel, [object_id]), conn_comp
    else:
        return filter_ocel_objects(ocel, [object_id])


def filter_ocel_cc_length(
    ocel: OCEL, min_cc_length: int, max_cc_length: int
) -> OCEL:
    """
    Keeps only the objects in an OCEL belonging to a connected component with a length
    falling within the specified range.

    Reference:
    Adams, Jan Niklas, et al. "Defining cases and variants for object-centric event data."
    2022 4th International Conference on Process Mining (ICPM). IEEE, 2022.

    :param ocel: Object-centric event log.
    :param min_cc_length: Minimum allowed length for the connected component.
    :param max_cc_length: Maximum allowed length for the connected component.
    :return: Filtered OCEL.

    .. code-block:: python3

        import pm4py

        filtered_ocel = pm4py.filter_ocel_cc_length(
            ocel,
            2,
            10
        )
    """
    from pm4py.algo.transformation.ocel.graphs import object_interaction_graph

    g0 = object_interaction_graph.apply(ocel)
    g = nx_utils.Graph()

    for edge in g0:
        g.add_edge(edge[0], edge[1])

    conn_comp = list(nx_utils.connected_components(g))
    conn_comp = [
        x for x in conn_comp if min_cc_length <= len(x) <= max_cc_length
    ]
    objs = [y for x in conn_comp for y in x]

    return filter_ocel_objects(ocel, objs)


def filter_ocel_cc_otype(
    ocel: OCEL, otype: str, positive: bool = True
) -> OCEL:
    """
    Filters the objects belonging to connected components that have at least one object of the specified type.

    Reference:
    Adams, Jan Niklas, et al. "Defining cases and variants for object-centric event data."
    2022 4th International Conference on Process Mining (ICPM). IEEE, 2022.

    :param ocel: Object-centric event log.
    :param otype: Object type to consider.
    :param positive: Boolean indicating whether to keep (True) or discard (False) the objects in these components.
    :return: Filtered OCEL.

    .. code-block:: python3

        import pm4py

        ocel = pm4py.read_ocel('log.jsonocel')
        filtered_ocel = pm4py.filter_ocel_cc_otype(
            ocel,
            'order'
        )
    """
    if positive:
        objs = set(
            ocel.objects[ocel.objects[ocel.object_type_column] == otype][
                ocel.object_id_column
            ]
        )
    else:
        objs = set(
            ocel.objects[~(ocel.objects[ocel.object_type_column] == otype)][
                ocel.object_id_column
            ]
        )

    from pm4py.algo.transformation.ocel.graphs import object_interaction_graph

    g0 = object_interaction_graph.apply(ocel)
    g = nx_utils.Graph()

    for edge in g0:
        g.add_edge(edge[0], edge[1])

    conn_comp = list(nx_utils.connected_components(g))
    conn_comp = [x for x in conn_comp if len(set(x).intersection(objs)) > 0]

    objs = [y for x in conn_comp for y in x]

    return filter_ocel_objects(ocel, objs)


def filter_ocel_cc_activity(ocel: OCEL, activity: str) -> OCEL:
    """
    Filters the objects belonging to connected components that include at least one event with the specified activity.

    Reference:
    Adams, Jan Niklas, et al. "Defining cases and variants for object-centric event data."
    2022 4th International Conference on Process Mining (ICPM). IEEE, 2022.

    :param ocel: Object-centric event log.
    :param activity: Activity to consider.
    :return: Filtered OCEL.

    .. code-block:: python3

        import pm4py

        ocel = pm4py.read_ocel('log.jsonocel')
        filtered_ocel = pm4py.filter_ocel_cc_activity(
            ocel,
            'Create Order'
        )
    """
    evs = (
        ocel.events[ocel.events[ocel.event_activity] == activity][
            ocel.event_id_column
        ]
        .to_numpy()
        .tolist()
    )
    objs = pandas_utils.format_unique(
        ocel.relations[ocel.relations[ocel.event_id_column].isin(evs)][
            ocel.object_id_column
        ].unique()
    )

    from pm4py.algo.transformation.ocel.graphs import object_interaction_graph

    g0 = object_interaction_graph.apply(ocel)
    g = nx_utils.Graph()

    for edge in g0:
        g.add_edge(edge[0], edge[1])

    conn_comp = list(nx_utils.connected_components(g))
    conn_comp = [x for x in conn_comp if len(set(x).intersection(objs)) > 0]

    objs = [y for x in conn_comp for y in x]

    return filter_ocel_objects(ocel, objs)


def filter_dfg_activities_percentage(
    dfg: Dict[Tuple[str, str], int],
    start_activities: Dict[str, int],
    end_activities: Dict[str, int],
    percentage: float = 0.2,
) -> Tuple[Dict[Tuple[str, str], int], Dict[str, int], Dict[str, int]]:
    """
    Filters the DFG on the provided percentage of activities.

    :param dfg: frequency directly-follows graph
    :param start_activities: dictionary of the start activities
    :param end_activities: dictionary of the end activities
    :param percentage: percentage of activities to keep

    .. code-block:: python3

        import pm4py

        log = pm4py.read_xes('tests/input_data/receipt.xes')
        dfg, sa, ea = pm4py.discover_dfg(log)
        dfg, sa, ea = pm4py.filter_dfg_activities_percentage(dfg, sa, ea, percentage=0.2)
        pm4py.view_dfg(dfg, sa, ea, format='svg')
    """
    activities_entering_arcs = Counter()
    activities_exiting_arcs = Counter()
    all_activities = set()
    for arc, count in dfg.items():
        activities_entering_arcs[arc[0]] += count
        activities_exiting_arcs[arc[1]] += count
        all_activities.add(arc[0])
        all_activities.add(arc[1])
    activities_frequency = {
        a: max(activities_entering_arcs[a], activities_exiting_arcs[a])
        for a in all_activities
    }

    from pm4py.algo.filtering.dfg.dfg_filtering import (
        filter_dfg_on_activities_percentage,
    )

    dfg, start_activities, end_activities, activities_frequency = (
        filter_dfg_on_activities_percentage(
            dfg,
            start_activities,
            end_activities,
            activities_frequency,
            percentage=percentage,
        )
    )

    return dfg, start_activities, end_activities


def filter_dfg_paths_percentage(
    dfg: Dict[Tuple[str, str], int],
    start_activities: Dict[str, int],
    end_activities: Dict[str, int],
    percentage: float = 0.2,
) -> Tuple[Dict[Tuple[str, str], int], Dict[str, int], Dict[str, int]]:
    """
    Filters the DFG on the provided percentage of paths.

    :param dfg: frequency directly-follows graph
    :param start_activities: dictionary of the start activities
    :param end_activities: dictionary of the end activities
    :param percentage: percentage of paths to keep

    .. code-block:: python3

        import pm4py

        log = pm4py.read_xes('tests/input_data/receipt.xes')
        dfg, sa, ea = pm4py.discover_dfg(log)
        dfg, sa, ea = pm4py.filter_dfg_paths_percentage(dfg, sa, ea, percentage=0.2)
        pm4py.view_dfg(dfg, sa, ea, format='svg')
    """
    activities_entering_arcs = Counter()
    activities_exiting_arcs = Counter()
    all_activities = set()
    for arc, count in dfg.items():
        activities_entering_arcs[arc[0]] += count
        activities_exiting_arcs[arc[1]] += count
        all_activities.add(arc[0])
        all_activities.add(arc[1])
    activities_frequency = {
        a: max(activities_entering_arcs[a], activities_exiting_arcs[a])
        for a in all_activities
    }

    from pm4py.algo.filtering.dfg.dfg_filtering import (
        filter_dfg_on_paths_percentage,
    )

    dfg, start_activities, end_activities, activities_frequency = (
        filter_dfg_on_paths_percentage(
            dfg,
            start_activities,
            end_activities,
            activities_frequency,
            percentage=percentage,
        )
    )

    return dfg, start_activities, end_activities

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
The ``pm4py.ml`` module contains the machine learning features offered in ``pm4py``.
"""

from typing import Union, Tuple, Any, List, Collection, Optional
import pandas as pd
import numpy as np
from pm4py.objects.ocel.obj import OCEL
from pm4py.objects.log.obj import EventLog
from pm4py.utils import __event_log_deprecation_warning
import random
from copy import copy
from pm4py.util.pandas_utils import (
    check_is_pandas_dataframe,
    check_pandas_dataframe_columns,
)
from pm4py.utils import get_properties, constants, pandas_utils, is_polars_lazyframe, check_is_pandas_dataframe


def split_train_test(
    log: Union[EventLog, pd.DataFrame],
    train_percentage: float = 0.8,
    case_id_key: str = "case:concept:name",
) -> Union[Tuple[EventLog, EventLog], Tuple[pd.DataFrame, pd.DataFrame]]:
    """
    Splits an event log into a training log and a test log for machine learning purposes.

    This function separates the provided log into two parts based on the specified training percentage.
    It ensures that entire cases are included in either the training set or the test set.

    :param log: The event log or Pandas DataFrame to be split.
    :param train_percentage: Fraction of cases to be included in the training log (between 0.0 and 1.0).
    :param case_id_key: Attribute to be used as the case identifier.
    :return: A tuple containing the training and test event logs or DataFrames.
    :rtype: ``Union[Tuple[EventLog, EventLog], Tuple[pd.DataFrame, pd.DataFrame]]``

    .. code-block:: python3

        import pm4py

        train_df, test_df = pm4py.split_train_test(dataframe, train_percentage=0.75)
    """
    __event_log_deprecation_warning(log)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        cases = pandas_utils.format_unique(log[case_id_key].unique())
        train_cases = set()
        test_cases = set()
        for c in cases:
            r = random.random()
            if r <= train_percentage:
                train_cases.add(c)
            else:
                test_cases.add(c)
        train_df = log[log[case_id_key].isin(train_cases)]
        test_df = log[log[case_id_key].isin(test_cases)]
        return train_df, test_df
    else:
        from pm4py.objects.log.util import split_train_test

        return split_train_test.split(log, train_percentage=train_percentage)


def get_prefixes_from_log(
    log: Union[EventLog, pd.DataFrame],
    length: int,
    case_id_key: str = "case:concept:name",
) -> Union[EventLog, pd.DataFrame]:
    """
    Retrieves prefixes of traces in a log up to a specified length.

    The returned log contains prefixes of each trace:

    - If a trace has a length less than or equal to the specified length, it is included as-is.
    - If a trace exceeds the specified length, it is truncated to that length.

    :param log: The event log or Pandas DataFrame from which to extract prefixes.
    :param length: The maximum length of prefixes to extract.
    :param case_id_key: Attribute to be used as the case identifier.
    :return: A log containing the prefixes of the original log.
    :rtype: ``Union[EventLog, pd.DataFrame]``

    .. code-block:: python3

        import pm4py

        trimmed_df = pm4py.get_prefixes_from_log(dataframe, length=5, case_id_key='case:concept:name')
    """
    __event_log_deprecation_warning(log)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, case_id_key=case_id_key)
        from pm4py.util import pandas_utils

        log = pandas_utils.insert_ev_in_tr_index(log, case_id=case_id_key)
        return log[log[constants.DEFAULT_INDEX_IN_TRACE_KEY] <= (length - 1)]
    else:
        from pm4py.objects.log.util import get_prefixes

        return get_prefixes.get_prefixes_from_log(log, length)


def extract_outcome_enriched_dataframe(
    log: Union[EventLog, pd.DataFrame],
    activity_key: str = "concept:name",
    timestamp_key: str = "time:timestamp",
    case_id_key: str = "case:concept:name",
    start_timestamp_key: str = "time:timestamp",
) -> pd.DataFrame:
    """
    Enriches a dataframe with additional outcome-related columns computed from the entire case.

    This function adds columns that model the outcome of each case by computing metrics such as
    arrival rates and service waiting times.

    :param log: The event log or Pandas DataFrame to be enriched.
    :param activity_key: Attribute to be used for the activity.
    :param timestamp_key: Attribute to be used for the timestamp.
    :param case_id_key: Attribute to be used as the case identifier.
    :param start_timestamp_key: Attribute to be used as the start timestamp.
    :return: An enriched Pandas DataFrame with additional outcome-related columns.
    :rtype: ``pd.DataFrame``

    .. code-block:: python3

        import pm4py

        enriched_df = pm4py.extract_outcome_enriched_dataframe(
            log,
            activity_key='concept:name',
            timestamp_key='time:timestamp',
            case_id_key='case:concept:name',
            start_timestamp_key='time:timestamp'
        )
    """
    __event_log_deprecation_warning(log)

    properties = get_properties(
        log,
        activity_key=activity_key,
        case_id_key=case_id_key,
        timestamp_key=timestamp_key,
    )

    if not check_is_pandas_dataframe(log):
        from pm4py.objects.conversion.log import converter as log_converter
        log = log_converter.apply(
            log,
            variant=log_converter.Variants.TO_DATA_FRAME,
            parameters=properties,
        )

    log = copy(log)
    fea_df = extract_features_dataframe(
        log,
        activity_key=activity_key,
        timestamp_key=timestamp_key,
        case_id_key=case_id_key,
        include_case_id=True,
    )
    log = pandas_utils.insert_case_arrival_finish_rate(
        log,
        timestamp_column=timestamp_key,
        case_id_column=case_id_key,
        start_timestamp_column=start_timestamp_key,
    )
    log = pandas_utils.insert_case_service_waiting_time(
        log,
        timestamp_column=timestamp_key,
        case_id_column=case_id_key,
        start_timestamp_column=start_timestamp_key,
    )

    if is_polars_lazyframe(log):
        return log.join(fea_df, on=case_id_key, maintain_order="left")
    else:
        return log.merge(fea_df, on=case_id_key)


def extract_features_dataframe(
    log: Union[EventLog, pd.DataFrame],
    str_tr_attr: Optional[List[str]] = None,
    num_tr_attr: Optional[List[str]] = None,
    str_ev_attr: Optional[List[str]] = None,
    num_ev_attr: Optional[List[str]] = None,
    str_evsucc_attr: Optional[List[str]] = None,
    activity_key: str = "concept:name",
    timestamp_key: str = "time:timestamp",
    case_id_key: Optional[str] = None,
    resource_key: str = "org:resource",
    include_case_id: bool = False,
    count_occurrences: bool = False,
    enable_numeric_attribute_statistics: bool = False,
    numeric_attribute_aggregations: Optional[Collection[str]] = None,
    **kwargs,
) -> pd.DataFrame:
    r"""
    Extracts a dataframe containing features for each case in the provided
    log object.

    This function processes the log to generate a set of features that can be used for machine learning tasks.
    Features can include both case-level and event-level attributes, with options for one-hot encoding.

    :param log: The event log or Pandas DataFrame from which to extract features.
    :param str_tr_attr: (Optional) List of string attributes at the case level to extract as features.
    :param num_tr_attr: (Optional) List of numeric attributes at the case level to extract as features.
    :param str_ev_attr: (Optional) List of string attributes at the event level to extract as features (one-hot encoded).
    :param num_ev_attr: (Optional) List of numeric attributes at the event level to extract as features
                       (uses the last value per attribute in a case).
    :param str_evsucc_attr: (Optional) List of string successor attributes at the event level to extract as features.
    :param activity_key: Attribute to be used as the activity identifier.
    :param timestamp_key: Attribute to be used for timestamps.
    :param case_id_key: (Optional) Attribute to be used as the case identifier. If not provided, the default is used.
    :param resource_key: Attribute to be used as the resource identifier.
    :param include_case_id: Whether to include the case identifier column in the features table.
    :param count_occurrences: If True, count occurrences of string attributes instead of binary encoding.
    :param enable_numeric_attribute_statistics: If True, expand numeric attributes to aggregation columns. If False,
                                                keep the existing ``ATTRIBUTE`` last-value column unless
                                                ``numeric_attribute_aggregations`` is provided. If not provided,
                                                defaults to False.
    :param numeric_attribute_aggregations: Optional collection of numeric aggregations to compute. Supported values are
                                           ``last``, ``first``, ``min``, ``max``, ``mean``, ``median``, ``stdev``,
                                           and ``sum``. Applied only to numeric attributes whose names do not start
                                           with ``@@``.
    :param \**kwargs: Additional keyword arguments to pass to the feature extraction algorithm.
    :return: A Pandas DataFrame containing the extracted features for each case.
    :rtype: ``pd.DataFrame``

    .. code-block:: python3

        import pm4py

        features_df = pm4py.extract_features_dataframe(
            dataframe,
            activity_key='concept:name',
            case_id_key='case:concept:name',
            timestamp_key='time:timestamp'
        )
    """
    __event_log_deprecation_warning(log)

    parameters = kwargs if kwargs else {}

    properties = get_properties(
        log,
        activity_key=activity_key,
        timestamp_key=timestamp_key,
        case_id_key=case_id_key,
    )
    for prop in properties:
        parameters[prop] = properties[prop]

    parameters["str_tr_attr"] = str_tr_attr or []
    parameters["num_tr_attr"] = num_tr_attr or []
    parameters["str_ev_attr"] = str_ev_attr or []
    parameters["num_ev_attr"] = num_ev_attr or []
    parameters["str_evsucc_attr"] = str_evsucc_attr or []
    parameters["add_case_identifier_column"] = include_case_id
    parameters["count_occurrences"] = count_occurrences
    if enable_numeric_attribute_statistics is None:
        enable_numeric_attribute_statistics = False
    parameters["enable_numeric_attribute_statistics"] = (
        enable_numeric_attribute_statistics
    )
    if numeric_attribute_aggregations is not None:
        parameters["numeric_attribute_aggregations"] = (
            numeric_attribute_aggregations
        )

    from pm4py.algo.transformation.trace_encodings import (
        algorithm as trace_encodings,
    )

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(
            log,
            activity_key=activity_key,
            case_id_key=case_id_key,
            timestamp_key=timestamp_key,
        )

    data, feature_names = trace_encodings.apply(log, parameters=parameters)
    if is_polars_lazyframe(data):
        return data

    return pandas_utils.instantiate_dataframe(data, columns=feature_names)


def extract_ocel_features(
    ocel: OCEL,
    obj_type: str,
    enable_object_lifecycle_paths: bool = True,
    enable_object_work_in_progress: bool = False,
    object_str_attributes: Optional[Collection[str]] = None,
    object_num_attributes: Optional[Collection[str]] = None,
    include_obj_id: bool = False,
    debug: bool = False,
) -> pd.DataFrame:
    """
    Extracts a set of features from an object-centric event log (OCEL) for objects of a specified type.

    This function computes various features based on the lifecycle paths and work-in-progress metrics
    of objects within the OCEL. It also supports encoding of string and numeric object attributes.

    The approach is based on:
    Berti, A., Herforth, J., Qafari, M.S. et al. Graph-based feature extraction on object-centric event logs.
    Int J Data Sci Anal (2023). https://doi.org/10.1007/s41060-023-00428-2

    :param ocel: The object-centric event log from which to extract features.
    :param obj_type: The object type to consider for feature extraction.
    :param enable_object_lifecycle_paths: Whether to enable the "lifecycle paths" feature.
    :param enable_object_work_in_progress: Whether to enable the "work in progress" feature,
                                           which has a high computational cost.
    :param object_str_attributes: (Optional) Collection of string attributes at the object level to one-hot encode.
    :param object_num_attributes: (Optional) Collection of numeric attributes at the object level to encode.
    :param include_obj_id: Whether to include the object identifier as a column in the features DataFrame.
    :param debug: Whether to enable debugging mode to track the feature extraction process.
    :return: A Pandas DataFrame containing the extracted features for the specified object type.
    :rtype: ``pd.DataFrame``

    .. code-block:: python3

        import pm4py

        ocel = pm4py.read_ocel('log.jsonocel')
        fea_df = pm4py.extract_ocel_features(ocel, "item")
    """
    if object_str_attributes is None:
        object_str_attributes = []

    if object_num_attributes is None:
        object_num_attributes = []

    parameters = {
        "filter_per_type": obj_type,
        "enable_object_lifecycle_paths": enable_object_lifecycle_paths,
        "enable_object_work_in_progress": enable_object_work_in_progress,
        "enable_object_str_attributes": bool(object_str_attributes),
        "enable_object_num_attributes": bool(object_num_attributes),
        "str_obj_attr": object_str_attributes,
        "num_obj_attr": object_num_attributes,
        "debug": debug,
    }

    from pm4py.algo.transformation.ocel.features.objects import (
        algorithm as ocel_feature_extraction,
    )

    data, feature_names = ocel_feature_extraction.apply(
        ocel, parameters=parameters
    )

    dataframe = pandas_utils.instantiate_dataframe(data, columns=feature_names)
    dataframe = dataframe.dropna(how="any", axis=1)
    dataframe = dataframe.select_dtypes(include=np.number)

    if include_obj_id:
        objects_with_type = ocel.objects[
            [ocel.object_id_column, ocel.object_type_column]
        ].to_dict(orient="records")
        objects_with_type = [
            x[ocel.object_id_column]
            for x in objects_with_type
            if x[ocel.object_type_column] == obj_type
        ]
        dataframe[ocel.object_id_column] = objects_with_type

    return dataframe


def extract_temporal_features_dataframe(
    log: Union[EventLog, pd.DataFrame],
    grouper_freq: str = "W",
    activity_key: str = "concept:name",
    timestamp_key: str = "time:timestamp",
    case_id_key: Optional[str] = None,
    start_timestamp_key: str = "time:timestamp",
    resource_key: str = "org:resource",
) -> pd.DataFrame:
    """
    Extracts temporal features from a log object and returns them as a dataframe.

    This function computes temporal metrics based on the specified grouping frequency, which can be
    daily (D), weekly (W), monthly (M), or yearly (Y). These features are useful for analyzing
    system dynamics and simulation in the context of process mining.

    The approach is based on:
    Pourbafrani, Mahsa, Sebastiaan J. van Zelst, and Wil MP van der Aalst.
    "Supporting automatic system dynamics model generation for simulation in the context of process mining."
    International Conference on Business Information Systems. Springer, Cham, 2020.

    :param log: The event log or Pandas DataFrame from which to extract temporal features.
    :param grouper_freq: The frequency to use for grouping (e.g., 'D' for daily, 'W' for weekly,
                         'M' for monthly, 'Y' for yearly).
    :param activity_key: Attribute to be used as the activity identifier.
    :param timestamp_key: Attribute to be used for timestamps.
    :param case_id_key: (Optional) Attribute to be used as the case identifier. If not provided, the default is used.
    :param start_timestamp_key: Attribute to be used as the start timestamp.
    :param resource_key: Attribute to be used as the resource identifier.
    :return: A Pandas DataFrame containing the extracted temporal features.
    :rtype: ``pd.DataFrame``

    .. code-block:: python3

        import pm4py

        temporal_features_df = pm4py.extract_temporal_features_dataframe(
            dataframe,
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

    parameters["grouper_freq"] = grouper_freq
    parameters["pm4py:param:activity_key"] = activity_key
    parameters["pm4py:param:timestamp_key"] = timestamp_key
    if case_id_key is not None:
        parameters["pm4py:param:case_id_key"] = case_id_key
    parameters["pm4py:param:start_timestamp_key"] = (
        start_timestamp_key
    )
    parameters["pm4py:param:resource_key"] = resource_key

    if is_polars_lazyframe(log):
        from pm4py.algo.transformation.trace_encodings.variants import temporal_lazy as temporal
    else:
        from pm4py.algo.transformation.trace_encodings.variants import temporal

    return temporal.apply(log, parameters=parameters)


def extract_target_vector(
    log: Union[EventLog, pd.DataFrame],
    variant: str,
    activity_key: str = "concept:name",
    timestamp_key: str = "time:timestamp",
    case_id_key: str = "case:concept:name",
) -> Tuple[Any, List[str]]:
    """
    Extracts the target vector from a log object for a specific machine learning use case.

    Supported variants include:

    - 'next_activity': Predicts the next activity in a case.
    - 'next_time': Predicts the timestamp of the next activity.
    - 'remaining_time': Predicts the remaining time for the case.

    :param log: The event log or Pandas DataFrame from which to extract the target vector.
    :param variant: The variant of the algorithm to use. Must be one of:
                    'next_activity', 'next_time', 'remaining_time'.
    :param activity_key: Attribute to be used as the activity identifier.
    :param timestamp_key: Attribute to be used for timestamps.
    :param case_id_key: Attribute to be used as the case identifier.
    :return: A tuple containing the target vector and a list of class labels (if applicable).
    :rtype: ``Tuple[Any, List[str]]``

    :raises Exception: If an unsupported variant is provided.

    .. code-block:: python3

        import pm4py

        vector_next_act, class_next_act = pm4py.extract_target_vector(
            log,
            'next_activity',
            activity_key='concept:name',
            timestamp_key='time:timestamp',
            case_id_key='case:concept:name'
        )
        vector_next_time, class_next_time = pm4py.extract_target_vector(
            log,
            'next_time',
            activity_key='concept:name',
            timestamp_key='time:timestamp',
            case_id_key='case:concept:name'
        )
        vector_rem_time, class_rem_time = pm4py.extract_target_vector(
            log,
            'remaining_time',
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

    from pm4py.algo.transformation.log_to_target import (
        algorithm as log_to_target,
    )

    var_map = {
        "next_activity": log_to_target.Variants.NEXT_ACTIVITY,
        "next_time": log_to_target.Variants.NEXT_TIME,
        "remaining_time": log_to_target.Variants.REMAINING_TIME,
    }

    if variant not in var_map:
        raise Exception(
            "Please provide the variant as one of the following: 'next_activity', 'next_time', 'remaining_time'."
        )

    target, classes = log_to_target.apply(
        log, variant=var_map[variant], parameters=parameters
    )
    return target, classes

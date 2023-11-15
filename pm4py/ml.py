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
__doc__ = """
The ``pm4py.ml`` module contains the machine learning features offered in ``pm4py``
"""

from typing import Union, Tuple, Any, List, Collection, Optional
import pandas as pd
import numpy as np
from pm4py.objects.ocel.obj import OCEL
from pm4py.objects.log.obj import EventLog, EventStream
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.utils import __event_log_deprecation_warning
import random
from pm4py.util.pandas_utils import check_is_pandas_dataframe, check_pandas_dataframe_columns
from pm4py.utils import get_properties, constants, pandas_utils


def split_train_test(log: Union[EventLog, pd.DataFrame], train_percentage: float = 0.8, case_id_key="case:concept:name") -> Union[
    Tuple[EventLog, EventLog], Tuple[pd.DataFrame, pd.DataFrame]]:
    """
    Split an event log in a training log and a test log (for machine learning purposes).
    Returns the training and the test event log.

    :param log: event log / Pandas dataframe
    :param train_percentage: fraction of traces to be included in the training log (from 0.0 to 1.0)
    :param case_id_key: attribute to be used as case identifier
    :rtype: ``Union[Tuple[EventLog, EventLog], Tuple[pd.DataFrame, pd.DataFrame]]``

    .. code-block:: python3

        import pm4py

        train_df, test_df = pm4py.split_train_test(dataframe, train_percentage=0.75)
    """
    __event_log_deprecation_warning(log)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        cases = set(log[case_id_key].unique())
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


def get_prefixes_from_log(log: Union[EventLog, pd.DataFrame], length: int, case_id_key: str = "case:concept:name") -> Union[EventLog, pd.DataFrame]:
    """
    Gets the prefixes of a log of a given length. The returned log object contain the prefixes:
    - if a trace has lower or identical length, it is included as-is
    - if a trace has greater length, it is cut

    :param log: event log / Pandas dataframe
    :param length: length
    :param case_id_key: attribute to be used as case identifier
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
        return log[log[constants.DEFAULT_INDEX_IN_TRACE_KEY] <= (length-1)]
    else:
        from pm4py.objects.log.util import get_prefixes
        return get_prefixes.get_prefixes_from_log(log, length)


def extract_outcome_enriched_dataframe(log: Union[EventLog, pd.DataFrame], activity_key: str = "concept:name",
                                       timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name",
                                       start_timestamp_key: str = "time:timestamp") -> pd.DataFrame:
    """
    Inserts additional columns in the dataframe which are computed on the overall case, so they model the
    outcome of the case.

    :param log: event log / Pandas dataframe
    :param activity_key: attribute to be used for the activity
    :param timestamp_key: attribute to be used for the timestamp
    :param case_id_key: attribute to be used as case identifier
    :param start_timestamp_key: attribute to be used as start timestamp
    :rtype: ``pd.DataFrame``

    .. code-block:: python3

        import pm4py

        enriched_df = pm4py.extract_outcome_enriched_dataframe(log, activity_key='concept:name', timestamp_key='time:timestamp', case_id_key='case:concept:name', start_timestamp_key='time:timestamp')

    """
    __event_log_deprecation_warning(log)

    properties = get_properties(log, activity_key=activity_key, case_id_key=case_id_key, timestamp_key=timestamp_key)

    log = log_converter.apply(log, variant=log_converter.Variants.TO_DATA_FRAME, parameters=properties)

    from pm4py.util import pandas_utils

    fea_df = extract_features_dataframe(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key, include_case_id=True)
    log2 = pandas_utils.insert_case_arrival_finish_rate(log.copy(), timestamp_column=timestamp_key, case_id_column=case_id_key, start_timestamp_column=start_timestamp_key)
    log2 = pandas_utils.insert_case_service_waiting_time(log2.copy(), timestamp_column=timestamp_key, case_id_column=case_id_key, start_timestamp_column=start_timestamp_key)

    return log2.merge(fea_df, left_on=case_id_key, right_on=case_id_key)


def extract_features_dataframe(log: Union[EventLog, pd.DataFrame], str_tr_attr=None, num_tr_attr=None, str_ev_attr=None, num_ev_attr=None, str_evsucc_attr=None, activity_key="concept:name", timestamp_key="time:timestamp", case_id_key=None, resource_key="org:resource", include_case_id: bool = False, **kwargs) -> pd.DataFrame:
    """
    Extracts a dataframe containing the features of each case of the provided log object

    :param log: log object (event log / Pandas dataframe)
    :param str_tr_attr: (if provided) string attributes at the case level which should be extracted as features
    :param num_tr_attr: (if provided) numeric attributes at the case level which should be extracted as features
    :param str_ev_attr: (if provided) string attributes at the event level which should be extracted as features (one-hot encoding)
    :param num_ev_attr: (if provided) numeric attributes at the event level which should be extracted as features (last value per attribute in a case)
    :param activity_key: the attribute to be used as activity
    :param timestamp_key: the attribute to be used as timestamp
    :param case_id_key: (if provided, otherwise default) the attribute to be used as case identifier
    :param resource_key: the attribute to be used as resource
    :param include_case_id: includes the case identifier column in the features table
    :rtype: ``pd.DataFrame``

    .. code-block:: python3

        import pm4py

        features_df = pm4py.extract_features_dataframe(dataframe, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
    """
    __event_log_deprecation_warning(log)

    parameters = {}
    if kwargs is not None:
        parameters = kwargs

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    for prop in properties:
        parameters[prop] = properties[prop]

    parameters["str_tr_attr"] = str_tr_attr
    parameters["num_tr_attr"] = num_tr_attr
    parameters["str_ev_attr"] = str_ev_attr
    parameters["num_ev_attr"] = num_ev_attr
    parameters["str_evsucc_attr"] = str_evsucc_attr
    parameters["add_case_identifier_column"] = include_case_id

    from pm4py.algo.transformation.log_to_features import algorithm as log_to_features

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, case_id_key=case_id_key, timestamp_key=timestamp_key)

    data, feature_names = log_to_features.apply(log, parameters=parameters)

    return pd.DataFrame(data, columns=feature_names)


def extract_ocel_features(ocel: OCEL, obj_type: str, enable_object_lifecycle_paths: bool = True, enable_object_work_in_progress: bool = False, object_str_attributes: Optional[Collection[str]] = None, object_num_attributes: Optional[Collection[str]] = None, include_obj_id: bool = False, debug: bool = False) -> pd.DataFrame:
    """
    Extracts from an object-centric event log a set of features (returned as dataframe) computed on the OCEL
    for the objects of a given object type.

    Implements the approach described in:
    Berti, A., Herforth, J., Qafari, M.S. et al. Graph-based feature extraction on object-centric event logs. Int J Data Sci Anal (2023). https://doi.org/10.1007/s41060-023-00428-2

    :param ocel: object-centric event log
    :param obj_type: object type that should be considered
    :param enable_object_lifecycle_paths: enables the "lifecycle paths" feature
    :param enable_object_work_in_progress: enables the "work in progress" feature (which has an high computational cost)
    :param object_str_attributes: string attributes at the object level to one-hot encode during the feature extraction
    :param object_num_attributes: numeric attributes at the object level to one-hot encode during the feature extraction
    :param include_obj_id: includes the object identifier as column of the "features" dataframe
    :param debug: enables debugging mode (telling at which point of the feature extraction you are)
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

    parameters = {}
    parameters["filter_per_type"] = obj_type
    parameters["enable_object_lifecycle_paths"] = enable_object_lifecycle_paths
    parameters["enable_object_work_in_progress"] = enable_object_work_in_progress
    parameters["enable_object_str_attributes"] = len(object_str_attributes) > 0
    parameters["enable_object_num_attributes"] = len(object_num_attributes) > 0
    parameters["str_obj_attr"] = object_str_attributes
    parameters["num_obj_attr"] = object_num_attributes
    parameters["debug"] = debug

    from pm4py.algo.transformation.ocel.features.objects import algorithm as ocel_feature_extraction

    data, feature_names = ocel_feature_extraction.apply(ocel, parameters=parameters)

    dataframe = pd.DataFrame(data, columns=feature_names)
    dataframe.dropna(how="any", axis=1, inplace=True)
    dataframe = dataframe.select_dtypes(include=np.number)

    if include_obj_id:
        objects_with_type = ocel.objects[[ocel.object_id_column, ocel.object_type_column]].to_dict("records")
        objects_with_type = [x[ocel.object_id_column] for x in objects_with_type if x[ocel.object_type_column] == obj_type]
        dataframe[ocel.object_id_column] = objects_with_type

    return dataframe


def extract_temporal_features_dataframe(log: Union[EventLog, pd.DataFrame], grouper_freq="W", activity_key="concept:name", timestamp_key="time:timestamp", case_id_key=None, start_timestamp_key="time:timestamp", resource_key="org:resource") -> pd.DataFrame:
    """
    Extracts a dataframe containing the temporal features of the provided log object

    Implements the approach described in the paper:
    Pourbafrani, Mahsa, Sebastiaan J. van Zelst, and Wil MP van der Aalst. "Supporting automatic system dynamics model generation for simulation in the context of process mining." International Conference on Business Information Systems. Springer, Cham, 2020.

    :param log: log object (event log / Pandas dataframe)
    :param grouper_freq: the grouping frequency (D, W, M, Y) to use
    :param activity_key: the attribute to be used as activity
    :param timestamp_key: the attribute to be used as timestamp
    :param case_id_key: (if provided, otherwise default) the attribute to be used as case identifier
    :param resource_key: the attribute to be used as resource
    :param start_timestamp_key: the attribute to be used as start timestamp
    :rtype: ``pd.DataFrame``

    .. code-block:: python3

        import pm4py

        temporal_features_df = pm4py.extract_temporal_features_dataframe(dataframe, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
    """
    __event_log_deprecation_warning(log)

    parameters = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    from pm4py.algo.transformation.log_to_features.variants import temporal

    parameters[temporal.Parameters.GROUPER_FREQ] = grouper_freq
    parameters[temporal.Parameters.ACTIVITY_COLUMN] = activity_key
    parameters[temporal.Parameters.TIMESTAMP_COLUMN] = timestamp_key
    if case_id_key is not None:
        parameters[temporal.Parameters.CASE_ID_COLUMN] = case_id_key
    parameters[temporal.Parameters.START_TIMESTAMP_COLUMN] = start_timestamp_key
    parameters[temporal.Parameters.RESOURCE_COLUMN] = resource_key

    return temporal.apply(log, parameters=parameters)


def extract_target_vector(log: Union[EventLog, pd.DataFrame], variant: str, activity_key="concept:name", timestamp_key="time:timestamp", case_id_key="case:concept:name") -> Tuple[Any, List[str]]:
    """
    Extracts from a log object the target vector for a specific ML use case
    (next activity, next time, remaining time)

    :param log: log object (event log / Pandas dataframe)
    :param variant: variant of the algorithm to be used: next_activity, next_time, remaining_time
    :param activity_key: the attribute to be used as activity
    :param timestamp_key: the attribute to be used as timestamp
    :param case_id_key: the attribute to be used as case identifier
    :rtype: ``Tuple[Any, List[str]]``

    .. code-block:: python3

        import pm4py

        vector_next_act, class_next_act = pm4py.extract_target_vector(log, 'next_activity', activity_key='concept:name', timestamp_key='time:timestamp', case_id_key='case:concept:name')
        vector_next_time, class_next_time = pm4py.extract_target_vector(log, 'next_time', activity_key='concept:name', timestamp_key='time:timestamp', case_id_key='case:concept:name')
        vector_rem_time, class_rem_time = pm4py.extract_target_vector(log, 'remaining_time', activity_key='concept:name', timestamp_key='time:timestamp', case_id_key='case:concept:name')

    """
    __event_log_deprecation_warning(log)

    parameters = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    from pm4py.algo.transformation.log_to_target import algorithm as log_to_target

    var_map = {"next_activity": log_to_target.Variants.NEXT_ACTIVITY, "next_time": log_to_target.Variants.NEXT_TIME,
               "remaining_time": log_to_target.Variants.REMAINING_TIME}

    if variant not in var_map:
        raise Exception(
            "please provide the variant between: next_activity, next_time, remaining_time")

    target, classes = log_to_target.apply(log, variant=var_map[variant], parameters=parameters)
    return target, classes

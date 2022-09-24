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

from typing import Union, Tuple
import pandas as pd
from pm4py.objects.log.obj import EventLog, EventStream
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.util import constants
from pm4py.utils import __event_log_deprecation_warning
import random
from pm4py.util.pandas_utils import check_is_pandas_dataframe, check_pandas_dataframe_columns
from pm4py.utils import get_properties
from copy import copy


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
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
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
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, case_id_key=case_id_key)
        from pm4py.util import pandas_utils
        log = pandas_utils.insert_ev_in_tr_index(log, case_id=case_id_key)
        return log[log[constants.DEFAULT_INDEX_IN_TRACE_KEY] <= (length-1)]
    else:
        from pm4py.objects.log.util import get_prefixes
        return get_prefixes.get_prefixes_from_log(log, length)


def extract_features_dataframe(log: Union[EventLog, pd.DataFrame], str_tr_attr=None, num_tr_attr=None, str_ev_attr=None, num_ev_attr=None, str_evsucc_attr=None, activity_key="concept:name", timestamp_key="time:timestamp", case_id_key="case:concept:name", resource_key="org:resource", **kwargs) -> pd.DataFrame:
    """
    Extracts a dataframe containing the features of each case of the provided log object

    :param log: log object (event log / Pandas dataframe)
    :param str_tr_attr: (if provided) string attributes at the case level which should be extracted as features
    :param num_tr_attr: (if provided) numeric attributes at the case level which should be extracted as features
    :param str_ev_attr: (if provided) string attributes at the event level which should be extracted as features (one-hot encoding)
    :param num_ev_attr: (if provided) numeric attributes at the event level which should be extracted as features (last value per attribute in a case)
    :param activity_key: the attribute to be used as activity
    :param timestamp_key: the attribute to be used as timestamp
    :param case_id_key: the attribute to be used as case identifier
    :param resource_key: the attribute to be used as resource
    :rtype: ``pd.DataFrame``

    .. code-block:: python3

        import pm4py

        trimmed_df = pm4py.get_prefixes_from_log(dataframe, length=5, case_id_key='case:concept:name')
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
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

    from pm4py.algo.transformation.log_to_features import algorithm as log_to_features

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, case_id_key=case_id_key, timestamp_key=timestamp_key)

    data, feature_names = log_to_features.apply(log, parameters=parameters)

    return pd.DataFrame(data, columns=feature_names)

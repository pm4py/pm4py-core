__doc__ = """
PM4Py offers some features useful for the application of machine learning techniques.

* `Feature extraction from an event log`_
* `Split a log into training/test log`_
* `Get fixed-length prefixes from an event log`_

.. _Feature extraction from an event log: pm4py.html#pm4py.ml.extract_features_dataframe
.. _Split a log into training/test log: pm4py.html#pm4py.ml.split_train_test
.. _Get fixed-length prefixes from an event log: pm4py.html#pm4py.ml.get_prefixes_from_log

"""

from typing import Union, Tuple
import pandas as pd
from pm4py.objects.log.obj import EventLog, EventStream
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.util import constants
from pm4py.utils import __event_log_deprecation_warning
import random
from pm4py.util.pandas_utils import check_is_pandas_dataframe, check_pandas_dataframe_columns
from copy import copy


def split_train_test(log: Union[EventLog, pd.DataFrame], train_percentage: float = 0.8) -> Union[
    Tuple[EventLog, EventLog], Tuple[pd.DataFrame, pd.DataFrame]]:
    """
    Split an event log in a training log and a test log (for machine learning purposes)

    Parameters
    --------------
    log
        Event log / Pandas dataframe
    train_percentage
        Fraction of traces to be included in the training log (from 0.0 to 1.0)

    Returns
    --------------
    training_log
        Training event log
    test_log
        Test event log
    """
    # Variant that is Pandas native: YES
    # Unit test: YES
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        cases = set(log[constants.CASE_CONCEPT_NAME].unique())
        train_cases = set()
        test_cases = set()
        for c in cases:
            r = random.random()
            if r <= train_percentage:
                train_cases.add(c)
            else:
                test_cases.add(c)
        train_df = log[log[constants.CASE_CONCEPT_NAME].isin(train_cases)]
        test_df = log[log[constants.CASE_CONCEPT_NAME].isin(test_cases)]
        return train_df, test_df
    else:
        from pm4py.objects.log.util import split_train_test
        return split_train_test.split(log, train_percentage=train_percentage)


def get_prefixes_from_log(log: Union[EventLog, pd.DataFrame], length: int, case_id_key: str = "case:concept:name") -> Union[EventLog, pd.DataFrame]:
    """
    Gets the prefixes of a log of a given length

    Parameters
    ----------------
    log
        Event log / Pandas dataframe
    length
        Length
    case_id_key
        attribute to be used as case identifier

    Returns
    ----------------
    prefix_log
        Log contain the prefixes:
        - if a trace has lower or identical length, it is included as-is
        - if a trace has greater length, it is cut
    """
    # Variant that is Pandas native: YES
    # Unit test: YES
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


def extract_features_dataframe(log: Union[EventLog, pd.DataFrame], str_tr_attr=None, num_tr_attr=None, str_ev_attr=None, num_ev_attr=None, str_evsucc_attr=None, **kwargs) -> pd.DataFrame:
    """
    Extracts a dataframe containing the features of each case of the provided log object

    Parameters
    ----------------
    log
        Log object (event log / Pandas dataframe)
    str_tr_attr
        (if provided) string attributes at the case level which should be extracted as features
    num_tr_attr
        (if provided) numeric attributes at the case level which should be extracted as features
    str_ev_attr
        (if provided) string attributes at the event level which should be extracted as features (one-hot encoding)
    num_ev_attr
        (if provided) numeric attributes at the event level which should be extracted as features (last value per attribute in a case)

    Returns
    ---------------
    fea_df
        Feature dataframe
    """
    # Variant that is Pandas native: YES
    # Unit test: YES
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    parameters = {}
    if kwargs is not None:
        parameters = kwargs

    parameters["str_tr_attr"] = str_tr_attr
    parameters["num_tr_attr"] = num_tr_attr
    parameters["str_ev_attr"] = str_ev_attr
    parameters["num_ev_attr"] = num_ev_attr
    parameters["str_evsucc_attr"] = str_evsucc_attr

    from pm4py.algo.transformation.log_to_features import algorithm as log_to_features

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)

    data, feature_names = log_to_features.apply(log, parameters=parameters)

    return pd.DataFrame(data, columns=feature_names)

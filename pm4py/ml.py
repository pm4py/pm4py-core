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
from typing import Union, Tuple
import pandas as pd
from pm4py.objects.log.obj import EventLog
from pm4py.util import constants
import random


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
    if type(log) is pd.DataFrame:
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


def get_prefixes_from_log(log: Union[EventLog, pd.DataFrame], length: int) -> Union[EventLog, pd.DataFrame]:
    """
    Gets the prefixes of a log of a given length

    Parameters
    ----------------
    log
        Event log / Pandas dataframe
    length
        Length

    Returns
    ----------------
    prefix_log
        Log contain the prefixes:
        - if a trace has lower or identical length, it is included as-is
        - if a trace has greater length, it is cut
    """
    if type(log) is pd.DataFrame:
        from pm4py.util import pandas_utils
        log = pandas_utils.insert_ev_in_tr_index(log)
        return log[log[constants.DEFAULT_INDEX_IN_TRACE_KEY] <= (length-1)]
    else:
        from pm4py.objects.log.util import get_prefixes
        return get_prefixes.get_prefixes_from_log(log, length)

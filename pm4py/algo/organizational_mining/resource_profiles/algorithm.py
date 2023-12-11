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
from pm4py.algo.organizational_mining.resource_profiles.variants import pandas, log
import pandas as pd
from pm4py.objects.log.obj import EventLog
from typing import Union, Optional, Dict, Any
from pm4py.util import pandas_utils
from datetime import datetime


def distinct_activities(log_obj: Union[pd.DataFrame, EventLog], t1: Union[datetime, str], t2: Union[datetime, str], r: str,
                        parameters: Optional[Dict[Any, Any]] = None) -> int:
    """
    Number of distinct activities done by a resource in a given time interval [t1, t2)

    Metric RBI 1.1 in Pika, Anastasiia, et al.
    "Mining resource profiles from event logs." ACM Transactions on Management Information Systems (TMIS) 8.1 (2017): 1-30.

    Parameters
    -----------------
    log_obj
        Log object
    t1
        Left interval
    t2
        Right interval
    r
        Resource

    Returns
    -----------------
    distinct_activities
        Distinct activities
    """
    if pandas_utils.check_is_pandas_dataframe(log_obj):
        return pandas.distinct_activities(log_obj, t1, t2, r, parameters=parameters)
    else:
        return log.distinct_activities(log_obj, t1, t2, r, parameters=parameters)


def activity_frequency(log_obj: Union[pd.DataFrame, EventLog], t1: Union[datetime, str], t2: Union[datetime, str], r: str, a: str,
                        parameters: Optional[Dict[Any, Any]] = None) -> float:
    """
    Fraction of completions of a given activity a, by a given resource r, during a given time slot, [t1, t2),
    with respect to the total number of activity completions by resource r during [t1, t2)

    Metric RBI 1.3 in Pika, Anastasiia, et al.
    "Mining resource profiles from event logs." ACM Transactions on Management Information Systems (TMIS) 8.1 (2017): 1-30.

    Parameters
    -----------------
    log_obj
        Log object
    t1
        Left interval
    t2
        Right interval
    r
        Resource
    a
        Activity

    Returns
    ----------------
    metric
        Value of the metric
    """
    if pandas_utils.check_is_pandas_dataframe(log_obj):
        return pandas.activity_frequency(log_obj, t1, t2, r, a, parameters=parameters)
    else:
        return log.activity_frequency(log_obj, t1, t2, r, a, parameters=parameters)


def activity_completions(log_obj: Union[pd.DataFrame, EventLog], t1: Union[datetime, str], t2: Union[datetime, str], r: str,
                        parameters: Optional[Dict[Any, Any]] = None) -> int:
    """
    The number of activity instances completed by a given resource during a given time slot.

    Metric RBI 2.1 in Pika, Anastasiia, et al.
    "Mining resource profiles from event logs." ACM Transactions on Management Information Systems (TMIS) 8.1 (2017): 1-30.

    Parameters
    -----------------
    log_obj
        Log object
    t1
        Left interval
    t2
        Right interval
    r
        Resource

    Returns
    ----------------
    metric
        Value of the metric
    """
    if pandas_utils.check_is_pandas_dataframe(log_obj):
        return pandas.activity_completions(log_obj, t1, t2, r, parameters=parameters)
    else:
        return log.activity_completions(log_obj, t1, t2, r, parameters=parameters)


def case_completions(log_obj: Union[pd.DataFrame, EventLog], t1: Union[datetime, str], t2: Union[datetime, str], r: str,
                        parameters: Optional[Dict[Any, Any]] = None) -> int:
    """
    The number of cases completed during a given time slot in which a given resource was involved.

    Metric RBI 2.2 in Pika, Anastasiia, et al.
    "Mining resource profiles from event logs." ACM Transactions on Management Information Systems (TMIS) 8.1 (2017): 1-30.

    Parameters
    -----------------
    log_obj
        Log object
    t1
        Left interval
    t2
        Right interval
    r
        Resource

    Returns
    ----------------
    metric
        Value of the metric
    """
    if pandas_utils.check_is_pandas_dataframe(log_obj):
        return pandas.case_completions(log_obj, t1, t2, r, parameters=parameters)
    else:
        return log.case_completions(log_obj, t1, t2, r, parameters=parameters)


def fraction_case_completions(log_obj: Union[pd.DataFrame, EventLog], t1: Union[datetime, str], t2: Union[datetime, str], r: str,
                        parameters: Optional[Dict[Any, Any]] = None) -> float:
    """
    The fraction of cases completed during a given time slot in which a given resource was involved with respect to the
    total number of cases completed during the time slot.

    Metric RBI 2.3 in Pika, Anastasiia, et al.
    "Mining resource profiles from event logs." ACM Transactions on Management Information Systems (TMIS) 8.1 (2017): 1-30.

    Parameters
    -----------------
    log_obj
        Log object
    t1
        Left interval
    t2
        Right interval
    r
        Resource

    Returns
    ----------------
    metric
        Value of the metric
    """
    if pandas_utils.check_is_pandas_dataframe(log_obj):
        return pandas.fraction_case_completions(log_obj, t1, t2, r, parameters=parameters)
    else:
        return log.fraction_case_completions(log_obj, t1, t2, r, parameters=parameters)


def average_workload(log_obj: Union[pd.DataFrame, EventLog], t1: Union[datetime, str], t2: Union[datetime, str], r: str,
                     parameters: Optional[Dict[Any, Any]] = None) -> float:
    """
    The average number of activities started by a given resource but not completed at a moment in time.

    Metric RBI 2.4 in Pika, Anastasiia, et al.
    "Mining resource profiles from event logs." ACM Transactions on Management Information Systems (TMIS) 8.1 (2017): 1-30.

    Parameters
    -----------------
    log_obj
        Log object
    t1
        Left interval
    t2
        Right interval
    r
        Resource

    Returns
    ----------------
    metric
        Value of the metric
    """
    if pandas_utils.check_is_pandas_dataframe(log_obj):
        return pandas.average_workload(log_obj, t1, t2, r, parameters=parameters)
    else:
        return log.average_workload(log_obj, t1, t2, r, parameters=parameters)


def multitasking(log_obj: Union[pd.DataFrame, EventLog], t1: Union[datetime, str], t2: Union[datetime, str], r: str,
                 parameters: Optional[Dict[Any, Any]] = None) -> float:
    """
    The fraction of active time during which a given resource is involved in more than one activity with respect
    to the resource's active time.

    Metric RBI 3.1 in Pika, Anastasiia, et al.
    "Mining resource profiles from event logs." ACM Transactions on Management Information Systems (TMIS) 8.1 (2017): 1-30.

    Parameters
    -----------------
    log_obj
        Log object
    t1
        Left interval
    t2
        Right interval
    r
        Resource

    Returns
    ----------------
    metric
        Value of the metric
    """
    if pandas_utils.check_is_pandas_dataframe(log_obj):
        return pandas.multitasking(log_obj, t1, t2, r, parameters=parameters)
    else:
        return log.multitasking(log_obj, t1, t2, r, parameters=parameters)


def average_duration_activity(log_obj: Union[pd.DataFrame, EventLog], t1: Union[datetime, str], t2: Union[datetime, str], r: str, a: str,
                       parameters: Optional[Dict[Any, Any]] = None) -> float:
    """
    The average duration of instances of a given activity completed during a given time slot by a given resource.

    Metric RBI 4.3 in Pika, Anastasiia, et al.
    "Mining resource profiles from event logs." ACM Transactions on Management Information Systems (TMIS) 8.1 (2017): 1-30.

    Parameters
    -----------------
    log_obj
        Log object
    t1
        Left interval
    t2
        Right interval
    r
        Resource
    a
        Activity

    Returns
    ----------------
    metric
        Value of the metric
    """
    if pandas_utils.check_is_pandas_dataframe(log_obj):
        return pandas.average_duration_activity(log_obj, t1, t2, r, a, parameters=parameters)
    else:
        return log.average_duration_activity(log_obj, t1, t2, r, a, parameters=parameters)


def average_case_duration(log_obj: Union[pd.DataFrame, EventLog], t1: Union[datetime, str], t2: Union[datetime, str], r: str,
                          parameters: Optional[Dict[Any, Any]] = None) -> float:
    """
    The average duration of cases completed during a given time slot in which a given resource was involved.

    Metric RBI 4.4 in Pika, Anastasiia, et al.
    "Mining resource profiles from event logs." ACM Transactions on Management Information Systems (TMIS) 8.1 (2017): 1-30.

    Parameters
    -----------------
    log_obj
        Log object
    t1
        Left interval
    t2
        Right interval
    r
        Resource

    Returns
    ----------------
    metric
        Value of the metric
    """
    if pandas_utils.check_is_pandas_dataframe(log_obj):
        return pandas.average_case_duration(log_obj, t1, t2, r, parameters=parameters)
    else:
        return log.average_case_duration(log_obj, t1, t2, r, parameters=parameters)


def interaction_two_resources(log_obj: Union[pd.DataFrame, EventLog], t1: Union[datetime, str], t2: Union[datetime, str], r1: str, r2: str,
                              parameters: Optional[Dict[Any, Any]] = None) -> float:
    """
    The number of cases completed during a given time slot in which two given resources were involved.

    Metric RBI 5.1 in Pika, Anastasiia, et al.
    "Mining resource profiles from event logs." ACM Transactions on Management Information Systems (TMIS) 8.1 (2017): 1-30.

    Parameters
    -----------------
    log_obj
        Log object
    t1
        Left interval
    t2
        Right interval
    r1
        Resource 1
    r2
        Resource 2

    Returns
    ----------------
    metric
        Value of the metric
    """
    if pandas_utils.check_is_pandas_dataframe(log_obj):
        return pandas.interaction_two_resources(log_obj, t1, t2, r1, r2, parameters=parameters)
    else:
        return log.interaction_two_resources(log_obj, t1, t2, r1, r2, parameters=parameters)


def social_position(log_obj: Union[pd.DataFrame, EventLog], t1: Union[datetime, str], t2: Union[datetime, str], r: str,
                              parameters: Optional[Dict[Any, Any]] = None) -> float:
    """
    The fraction of resources involved in the same cases with a given resource during a given time slot with
    respect to the total number of resources active during the time slot.

    Metric RBI 5.2 in Pika, Anastasiia, et al.
    "Mining resource profiles from event logs." ACM Transactions on Management Information Systems (TMIS) 8.1 (2017): 1-30.

    Parameters
    -----------------
    log_obj
        Log object
    t1
        Left interval
    t2
        Right interval
    r
        Resource

    Returns
    ----------------
    metric
        Value of the metric
    """
    if pandas_utils.check_is_pandas_dataframe(log_obj):
        return pandas.social_position(log_obj, t1, t2, r, parameters=parameters)
    else:
        return log.social_position(log_obj, t1, t2, r, parameters=parameters)

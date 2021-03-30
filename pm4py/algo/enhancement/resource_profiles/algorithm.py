from pm4py.algo.enhancement.resource_profiles.variants import log, pandas
import pandas as pd
from pm4py.objects.log.log import EventLog
from typing import Union, Optional, Dict, Any
from datetime import datetime


def distinct_activities(log_obj: Union[pd.DataFrame, EventLog], t1: Union[datetime, str], t2: Union[datetime, str], r: str,
                        parameters: Optional[Dict[str, Any]] = None) -> int:
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
    if type(log_obj) is pd.DataFrame:
        return pandas.distinct_activities(log_obj, t1, t2, r, parameters=parameters)
    else:
        return log.distinct_activities(log_obj, t1, t2, r, parameters=parameters)


def activity_frequency(log_obj: Union[pd.DataFrame, EventLog], t1: Union[datetime, str], t2: Union[datetime, str], r: str, a: str,
                        parameters: Optional[Dict[str, Any]] = None) -> float:
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
    if type(log_obj) is pd.DataFrame:
        return pandas.activity_frequency(log_obj, t1, t2, r, a, parameters=parameters)
    else:
        return log.activity_frequency(log_obj, t1, t2, r, a, parameters=parameters)


def activity_completions(log_obj: Union[pd.DataFrame, EventLog], t1: Union[datetime, str], t2: Union[datetime, str], r: str,
                        parameters: Optional[Dict[str, Any]] = None) -> int:
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
    if type(log_obj) is pd.DataFrame:
        return pandas.activity_completions(log_obj, t1, t2, r, parameters=parameters)
    else:
        return log.activity_completions(log_obj, t1, t2, r, parameters=parameters)


def case_completions(log_obj: Union[pd.DataFrame, EventLog], t1: Union[datetime, str], t2: Union[datetime, str], r: str,
                        parameters: Optional[Dict[str, Any]] = None) -> int:
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
    if type(log_obj) is pd.DataFrame:
        return pandas.case_completions(log_obj, t1, t2, r, parameters=parameters)
    else:
        return log.case_completions(log_obj, t1, t2, r, parameters=parameters)


def fraction_case_completions(log_obj: Union[pd.DataFrame, EventLog], t1: Union[datetime, str], t2: Union[datetime, str], r: str,
                        parameters: Optional[Dict[str, Any]] = None) -> float:
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
    if type(log_obj) is pd.DataFrame:
        return pandas.fraction_case_completions(log_obj, t1, t2, r, parameters=parameters)
    else:
        return log.fraction_case_completions(log_obj, t1, t2, r, parameters=parameters)


def average_workload(log_obj: Union[pd.DataFrame, EventLog], t1: Union[datetime, str], t2: Union[datetime, str], r: str,
                     parameters: Optional[Dict[str, Any]] = None) -> float:
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
    if type(log_obj) is pd.DataFrame:
        return pandas.average_workload(log_obj, t1, t2, r, parameters=parameters)
    else:
        return log.average_workload(log_obj, t1, t2, r, parameters=parameters)

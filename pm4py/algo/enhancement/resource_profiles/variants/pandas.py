from datetime import datetime
from enum import Enum
from typing import Union, Optional, Dict, Any

import pandas as pd
import pytz

from pm4py.util import exec_utils, constants, xes_constants
from pm4py.util.vers_checker import check_pandas_ge_024


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    RESOURCE_KEY = constants.PARAMETER_CONSTANT_RESOURCE_KEY


def get_dt_from_string(dt: Union[datetime, str]) -> datetime:
    """
    If the date is expressed as string, do the conversion to a datetime.datetime object

    Parameters
    -----------
    dt
        Date (string or datetime.datetime)

    Returns
    -----------
    dt
        Datetime object
    """
    if type(dt) is str:
        dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")

    needs_conversion = check_pandas_ge_024()
    if needs_conversion:
        dt = dt.replace(tzinfo=pytz.utc)
        dt = pd.to_datetime(dt, utc=True)

    return dt


def distinct_activities(df: pd.DataFrame, t1: Union[datetime, str], t2: Union[datetime, str], r: str,
                        parameters: Optional[Dict[str, Any]] = None) -> int:
    """
    Number of distinct activities done by a resource in a given time interval [t1, t2)

    Metric RBI 1.1 in Pika, Anastasiia, et al. "Mining resource profiles from event logs." ACM Transactions on Management Information Systems (TMIS) 8.1 (2017): 1-30.

    Parameters
    -----------------
    df
        Dataframe
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
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    resource_key = exec_utils.get_param_value(Parameters.RESOURCE_KEY, parameters, xes_constants.DEFAULT_RESOURCE_KEY)

    t1 = get_dt_from_string(t1)
    t2 = get_dt_from_string(t2)

    df = df[[activity_key, timestamp_key, resource_key]]
    df = df[df[resource_key] == r]
    df = df[df[timestamp_key] >= t1]
    df = df[df[timestamp_key] < t2]

    return df[activity_key].nunique()

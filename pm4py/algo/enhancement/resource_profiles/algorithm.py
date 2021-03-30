from pm4py.algo.enhancement.resource_profiles.variants import log, pandas
import pandas as pd
from pm4py.objects.log.log import EventLog
from typing import Union, Optional, Dict, Any
from datetime import datetime


def distinct_activities(log_obj: Union[pd.DataFrame, EventLog], t1: Union[datetime, str], t2: Union[datetime, str], r: str,
                        parameters: Optional[Dict[str, Any]] = None) -> int:
    """
    Number of distinct activities done by a resource in a given time interval [t1, t2)

    Metric RBI 1.1 in Pika, Anastasiia, et al. "Mining resource profiles from event logs." ACM Transactions on Management Information Systems (TMIS) 8.1 (2017): 1-30.


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


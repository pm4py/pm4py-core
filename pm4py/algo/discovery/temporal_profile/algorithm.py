from typing import Optional, Dict, Any, Union

import pandas as pd

from pm4py.algo.discovery.temporal_profile.variants import log, dataframe
from pm4py.objects.log.obj import EventLog
from pm4py.util import typing


def apply(elog: Union[EventLog, pd.DataFrame], parameters: Optional[Dict[Any, Any]] = None) -> typing.TemporalProfile:
    """
    Discovers the temporal profile out of the provided log object.

    Implements the approach described in:
    Stertz, Florian, Jürgen Mangler, and Stefanie Rinderle-Ma. "Temporal Conformance Checking at Runtime based on Time-infused Process Models." arXiv preprint arXiv:2008.07262 (2020).

    Parameters
    ----------
    elog
        Event log
    parameters
        Parameters, including:
        - Parameters.ACTIVITY_KEY => the attribute to use as activity
        - Parameters.START_TIMESTAMP_KEY => the attribute to use as start timestamp
        - Parameters.TIMESTAMP_KEY => the attribute to use as timestamp

    Returns
    -------
    temporal_profile
        Temporal profile of the log
    """
    if type(elog) is pd.DataFrame:
        return dataframe.apply(elog, parameters=parameters)

    return log.apply(elog, parameters=parameters)

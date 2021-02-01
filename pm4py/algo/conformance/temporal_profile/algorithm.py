import pkgutil
from typing import Optional, Dict, Any, Union

import pandas as pd

from pm4py.algo.conformance.temporal_profile.variants import log
from pm4py.objects.log.log import EventLog
from pm4py.util import typing


def apply(elog: Union[EventLog, pd.DataFrame], temporal_profile: typing.TemporalProfile,
          parameters: Optional[Dict[Any, Any]] = None) -> typing.TemporalProfileConformanceResults:
    """
    Checks the conformance of the log using the provided temporal profile.

    Implements the approach described in:
    Stertz, Florian, Jürgen Mangler, and Stefanie Rinderle-Ma. "Temporal Conformance Checking at Runtime based on Time-infused Process Models." arXiv preprint arXiv:2008.07262 (2020).


    Parameters
    ---------------
    elog
        Event log
    temporal_profile
        Temporal profile
    parameters
        Parameters of the algorithm, including:
         - Parameters.ACTIVITY_KEY => the attribute to use as activity
         - Parameters.START_TIMESTAMP_KEY => the attribute to use as start timestamp
         - Parameters.TIMESTAMP_KEY => the attribute to use as timestamp
         - Parameters.ZETA => multiplier for the standard deviation

    Returns
    ---------------
    list_dev
        A list containing, for each trace, all the deviations.
        Each deviation is a tuple with four elements:
        - 1) The source activity of the recorded deviation
        - 2) The target activity of the recorded deviation
        - 3) The time passed between the occurrence of the source activity and the target activity
        - 4) The value of (time passed - mean)/std for this occurrence (zeta).
    """
    if pkgutil.find_loader("pandas"):
        import pandas as pd
        from pm4py.algo.conformance.temporal_profile.variants import dataframe

        if type(elog) is pd.DataFrame:
            return dataframe.apply(elog, temporal_profile, parameters=parameters)
    return log.apply(elog, temporal_profile, parameters=parameters)

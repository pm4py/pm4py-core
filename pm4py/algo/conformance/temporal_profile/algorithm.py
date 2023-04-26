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

from typing import Optional, Dict, Any, Union

import pandas as pd

from pm4py.algo.conformance.temporal_profile.variants import log, dataframe
from pm4py.objects.log.obj import EventLog
from pm4py.util import typing, exec_utils, constants, xes_constants
from pm4py.objects.conversion.log import converter as log_converter
from enum import Enum


class Parameters(Enum):
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY


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
    if type(elog) is pd.DataFrame:
        return dataframe.apply(elog, temporal_profile, parameters=parameters)
    else:
        elog = log_converter.apply(elog, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)
        return log.apply(elog, temporal_profile, parameters=parameters)


def get_diagnostics_dataframe(elog: Union[EventLog, pd.DataFrame], conf_result: typing.TemporalProfileConformanceResults, parameters: Optional[Dict[Any, Any]] = None) -> pd.DataFrame:
    """
    Gets the diagnostics dataframe from a log and the results
    of temporal profle-based conformance checking

    Parameters
    --------------
    log
        Event log
    conf_result
        Results of conformance checking

    Returns
    --------------
    diagn_dataframe
        Diagnostics dataframe
    """
    if parameters is None:
        parameters = {}

    if type(elog) is pd.DataFrame:
        case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
        cases = list(elog[case_id_key].unique())
    else:
        elog = log_converter.apply(elog, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)
        case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, xes_constants.DEFAULT_TRACEID_KEY)
        cases = [x.attributes[case_id_key] for x in elog]

    case = []
    source_activities = []
    target_activities = []
    throughput = []
    num_st_devs = []

    for i in range(len(conf_result)):
        for el in conf_result[i]:
            case.append(cases[i])
            source_activities.append(el[0])
            target_activities.append(el[1])
            throughput.append(el[2])
            num_st_devs.append(el[3])

    dataframe = pd.DataFrame({"case": case, "source_activity": source_activities, "target_activity": target_activities, "throughput": throughput, "num_st_devs": num_st_devs})

    return dataframe

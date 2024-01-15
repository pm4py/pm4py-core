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

from pm4py.objects.log.obj import EventLog, EventStream
import pandas as pd
from typing import Union, Optional, Dict, Any
from pm4py.objects.conversion.log import converter as log_converter
from enum import Enum
from pm4py.util import exec_utils, constants, xes_constants, pandas_utils


class Parameters(Enum):
    ARRIVAL_RATE = "arrival_rate"
    FINISH_RATE = "finish_rate"
    CASE_ID_COLUMN = constants.PARAMETER_CONSTANT_CASEID_KEY
    START_TIMESTAMP_COLUMN = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    TIMESTAMP_COLUMN = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    RESOURCE_COLUMN = constants.PARAMETER_CONSTANT_RESOURCE_KEY
    ACTIVITY_COLUMN = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    GROUPER_FREQ = "grouper_freq"
    SERVICE_TIME = "service_time"
    WAITING_TIME = "waiting_time"
    SOJOURN_TIME = "sojourn_time"
    DIFF_START_END = "diff_start_end"


def apply(log: Union[EventLog, EventStream, pd.DataFrame], parameters: Optional[Dict[Any, Any]] = None) -> pd.DataFrame:
    """
    Extracts temporal features with the provided granularity from the Pandas dataframe.

    Implements the approach described in the paper:
    Pourbafrani, Mahsa, Sebastiaan J. van Zelst, and Wil MP van der Aalst. "Supporting automatic system dynamics model generation for simulation in the context of process mining." International Conference on Business Information Systems. Springer, Cham, 2020.

    Parameters
    ---------------
    log
        Event log / Event stream / Pandas dataframe
    parameters
        Parameters of the algorithm, including:
        - Parameters.GROUPER_FREQ => the time interval to be used for the grouping
        - Parameters.ARRIVAL_RATE => column of the dataframe which is going to host the arrival rate
        - Parameters.FINISH_RATE => column of the dataframe which is going to host the finishing rate
        - Parameters.SERVICE_TIME => column of the dataframe which is going to host the service time
        - Parameters.WAITING_TIME => column of the dataframe which is going to host the waiting time
        - Parameters.SOJOURN_TIME => column of the dataframe which is going to host the sojourn time
        - Parameters.CASE_ID_COLUMN => case ID column in the dataframe (default: case:concept:name)
        - Parameters.ACTIVITY_COLUMN => activity column in the dataframe (default: concept:name)
        - Parameters.TIMESTAMP_COLUMN => timestamp column in the dataframe (default: time:timestamp)
        - Parameters.RESOURCE_COLUMN => resource column in the dataframe (default: org:resource)
        - Parameters.START_TIMESTAMP_COLUMN => start timestamp column in the dataframe (if not provided, the timestamp column is used)

    Returns
    ----------------
    features_df
        Dataframe with temporal features
    """
    if parameters is None:
        parameters = {}

    grouper_freq = exec_utils.get_param_value(Parameters.GROUPER_FREQ, parameters, "W")
    timestamp_column = exec_utils.get_param_value(Parameters.TIMESTAMP_COLUMN, parameters, xes_constants.DEFAULT_TIMESTAMP_KEY)
    start_timestamp_column = exec_utils.get_param_value(Parameters.START_TIMESTAMP_COLUMN, parameters, None)
    if start_timestamp_column is None:
        start_timestamp_column = timestamp_column
    case_id_column = exec_utils.get_param_value(Parameters.CASE_ID_COLUMN, parameters, constants.CASE_CONCEPT_NAME)
    diff_start_end = exec_utils.get_param_value(Parameters.DIFF_START_END, parameters, "@@diff_start_end")
    arrival_rate = exec_utils.get_param_value(Parameters.ARRIVAL_RATE, parameters, "@@arrival_rate")
    finish_rate = exec_utils.get_param_value(Parameters.FINISH_RATE, parameters, "@@finish_rate")
    service_time = exec_utils.get_param_value(Parameters.SERVICE_TIME, parameters, "@@service_time")
    waiting_time = exec_utils.get_param_value(Parameters.WAITING_TIME, parameters, "@@waiting_time")
    sojourn_time = exec_utils.get_param_value(Parameters.SOJOURN_TIME, parameters, "@@sojourn_time")
    resource_column = exec_utils.get_param_value(Parameters.RESOURCE_COLUMN, parameters, xes_constants.DEFAULT_RESOURCE_KEY)
    activity_column = exec_utils.get_param_value(Parameters.ACTIVITY_COLUMN, parameters, xes_constants.DEFAULT_NAME_KEY)

    log = log_converter.apply(log, variant=log_converter.Variants.TO_DATA_FRAME, parameters=parameters)
    log = pandas_utils.insert_case_arrival_finish_rate(log, case_id_column=case_id_column, timestamp_column=timestamp_column, arrival_rate_column=arrival_rate, finish_rate_column=finish_rate)
    log = pandas_utils.insert_case_service_waiting_time(log, case_id_column=case_id_column, timestamp_column=timestamp_column, diff_start_end_column=diff_start_end, service_time_column=service_time, sojourn_time_column=sojourn_time, waiting_time_column=waiting_time)

    grouped_log = log.groupby(pandas_utils.get_grouper(key=start_timestamp_column, freq=grouper_freq))

    final_values = []

    for gkey, gval in grouped_log:
        dct = {}
        dct["timestamp"] = gkey

        gval_first = gval.groupby(case_id_column).first()

        dct["unique_resources"] = gval[resource_column].nunique()
        dct["unique_cases"] = gval[case_id_column].nunique()
        dct["unique_activities"] = gval[activity_column].nunique()
        dct["num_events"] = len(gval)

        dct["average_arrival_rate"] = gval_first[arrival_rate].mean()
        dct["average_finish_rate"] = gval_first[finish_rate].mean()

        dct["average_waiting_time"] = gval_first[waiting_time].mean()
        dct["average_sojourn_time"] = gval_first[sojourn_time].mean()
        dct["average_service_time"] = gval_first[service_time].mean()

        final_values.append(dct)

    dataframe = pandas_utils.instantiate_dataframe(final_values)
    dataframe = dataframe.fillna(0)
    return dataframe

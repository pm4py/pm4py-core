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
import pandas as pd

from pm4py.util.xes_constants import DEFAULT_TIMESTAMP_KEY
from pm4py.util.constants import CASE_CONCEPT_NAME
from pm4py.util import exec_utils
from pm4py.util import constants, pandas_utils
from enum import Enum
from typing import Optional, Dict, Any, Union


class Parameters(Enum):
    ATTRIBUTE_KEY = constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    MAX_NO_POINTS_SAMPLE = "max_no_of_points_to_sample"
    KEEP_ONCE_PER_CASE = "keep_once_per_case"


def get_case_arrival_avg(df: pd.DataFrame, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> float:
    """
    Gets the average time interlapsed between case starts

    Parameters
    --------------
    df
        Pandas dataframe
    parameters
        Parameters of the algorithm, including:
            Parameters.TIMESTAMP_KEY -> attribute of the log to be used as timestamp

    Returns
    --------------
    case_arrival_avg
        Average time interlapsed between case starts
    """
    if parameters is None:
        parameters = {}

    caseid_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME)
    timest_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, DEFAULT_TIMESTAMP_KEY)

    first_df = df.groupby(caseid_glue).first()

    first_df = first_df.sort_values(timest_key)

    first_df_shift = first_df.shift(-1)

    first_df_shift.columns = [str(col) + '_2' for col in first_df_shift.columns]

    df_successive_rows = pandas_utils.concat([first_df, first_df_shift], axis=1)
    df_successive_rows['interlapsed_time'] = pandas_utils.get_total_seconds(df_successive_rows[timest_key + '_2'] - df_successive_rows[timest_key])

    df_successive_rows = df_successive_rows.dropna(subset=['interlapsed_time'])

    return df_successive_rows['interlapsed_time'].mean()


def get_case_dispersion_avg(df, parameters=None):
    """
    Gets the average time interlapsed between case ends

    Parameters
    --------------
    df
        Pandas dataframe
    parameters
        Parameters of the algorithm, including:
            Parameters.TIMESTAMP_KEY -> attribute of the log to be used as timestamp

    Returns
    --------------
    case_dispersion_avg
        Average time interlapsed between the completion of cases
    """
    if parameters is None:
        parameters = {}

    caseid_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME)
    timest_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, DEFAULT_TIMESTAMP_KEY)

    first_df = df.groupby(caseid_glue).last()

    first_df = first_df.sort_values(timest_key)

    first_df_shift = first_df.shift(-1)

    first_df_shift.columns = [str(col) + '_2' for col in first_df_shift.columns]

    df_successive_rows = pandas_utils.concat([first_df, first_df_shift], axis=1)
    df_successive_rows['interlapsed_time'] = pandas_utils.get_total_seconds(df_successive_rows[timest_key + '_2'] - df_successive_rows[timest_key])

    df_successive_rows = df_successive_rows.dropna(subset=['interlapsed_time'])

    return df_successive_rows['interlapsed_time'].mean()

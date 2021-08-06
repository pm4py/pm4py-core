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
from enum import Enum

from pm4py.util import exec_utils, constants, xes_constants
from pm4py.util.business_hours import soj_time_business_hours_diff
import pandas as pd
from typing import Optional, Dict, Any, Union, Tuple, List, Set


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    BUSINESS_HOURS = "business_hours"
    WORKTIMING = "worktiming"
    WEEKENDS = "weekends"


DIFF_KEY = "@@diff"


def apply(dataframe: pd.DataFrame, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Dict[str, float]:
    """
    Gets the sojourn time per activity on a Pandas dataframe

    Parameters
    --------------
    dataframe
        Pandas dataframe
    parameters
        Parameters of the algorithm, including:
        - Parameters.ACTIVITY_KEY => activity key
        - Parameters.START_TIMESTAMP_KEY => start timestamp key
        - Parameters.TIMESTAMP_KEY => timestamp key
        - Parameters.BUSINESS_HOURS => calculates the difference of time based on the business hours, not the total time.
                                        Default: False
        - Parameters.WORKTIMING => work schedule of the company (provided as a list where the first number is the start
            of the work time, and the second number is the end of the work time), if business hours are enabled
                                        Default: [7, 17] (work shift from 07:00 to 17:00)
        - Parameters.WEEKENDS => indexes of the days of the week that are weekend
                                        Default: [6, 7] (weekends are Saturday and Sunday)

    Returns
    --------------
    soj_time_dict
        Sojourn time dictionary
    """
    if parameters is None:
        parameters = {}

    business_hours = exec_utils.get_param_value(Parameters.BUSINESS_HOURS, parameters, False)
    worktiming = exec_utils.get_param_value(Parameters.WORKTIMING, parameters, [7, 17])
    weekends = exec_utils.get_param_value(Parameters.WEEKENDS, parameters, [6, 7])

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    start_timestamp_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY, parameters,
                                                     xes_constants.DEFAULT_TIMESTAMP_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)

    if business_hours:
        dataframe[DIFF_KEY] = dataframe.apply(
            lambda x: soj_time_business_hours_diff(x[start_timestamp_key], x[timestamp_key], worktiming,
                                                   weekends), axis=1)
    else:
        dataframe[DIFF_KEY] = (
                dataframe[timestamp_key] - dataframe[start_timestamp_key]).astype('timedelta64[s]')

    dataframe = dataframe.reset_index()

    ret_dict = dataframe.groupby(activity_key)[DIFF_KEY].mean().to_dict()
    # assure to avoid problems with np.float64, by using the Python float type
    for el in ret_dict:
        ret_dict[el] = float(ret_dict[el])

    return ret_dict

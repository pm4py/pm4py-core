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
from enum import Enum

from pm4py.util import exec_utils, constants, xes_constants, pandas_utils
from pm4py.util.business_hours import soj_time_business_hours_diff
from typing import Optional, Dict, Any, Union


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    AGGREGATION_MEASURE = "aggregationMeasure"
    BUSINESS_HOURS = "business_hours"
    BUSINESS_HOUR_SLOTS = "business_hour_slots"
    WORKCALENDAR = "workcalendar"


DIFF_KEY = "@@diff"


def apply(dataframe: pd.DataFrame, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Dict[str, float]:
    """
    Gets the service time per activity on a Pandas dataframe

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
        - Parameters.BUSINESS_HOURS_SLOTS =>
        work schedule of the company, provided as a list of tuples where each tuple represents one time slot of business
        hours. One slot i.e. one tuple consists of one start and one end time given in seconds since week start, e.g.
        [
            (7 * 60 * 60, 17 * 60 * 60),
            ((24 + 7) * 60 * 60, (24 + 12) * 60 * 60),
            ((24 + 13) * 60 * 60, (24 + 17) * 60 * 60),
        ]
        meaning that business hours are Mondays 07:00 - 17:00 and Tuesdays 07:00 - 12:00 and 13:00 - 17:00
        - Parameters.AGGREGATION_MEASURE => performance aggregation measure (sum, min, max, mean, median)

    Returns
    --------------
    soj_time_dict
        Service time dictionary
    """
    if parameters is None:
        parameters = {}

    business_hours = exec_utils.get_param_value(Parameters.BUSINESS_HOURS, parameters, False)
    business_hours_slots = exec_utils.get_param_value(Parameters.BUSINESS_HOUR_SLOTS, parameters, constants.DEFAULT_BUSINESS_HOUR_SLOTS)

    workcalendar = exec_utils.get_param_value(Parameters.WORKCALENDAR, parameters, constants.DEFAULT_BUSINESS_HOURS_WORKCALENDAR)

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    start_timestamp_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY, parameters,
                                                     xes_constants.DEFAULT_TIMESTAMP_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    aggregation_measure = exec_utils.get_param_value(Parameters.AGGREGATION_MEASURE,
                                                     parameters, "mean")

    if business_hours:
        dataframe[DIFF_KEY] = dataframe.apply(
            lambda x: soj_time_business_hours_diff(x[start_timestamp_key], x[timestamp_key], business_hours_slots, workcalendar), axis=1)
    else:
        dataframe[DIFF_KEY] = pandas_utils.get_total_seconds(dataframe[timestamp_key] - dataframe[start_timestamp_key])

    dataframe = dataframe.reset_index()

    column = dataframe.groupby(activity_key)[DIFF_KEY]
    if aggregation_measure == "median":
        ret_dict = column.median().to_dict()
    elif aggregation_measure == "min":
        ret_dict = column.min().to_dict()
    elif aggregation_measure == "max":
        ret_dict = column.max().to_dict()
    elif aggregation_measure == "sum":
        ret_dict = column.sum().to_dict()
    else:
        ret_dict = column.mean().to_dict()

    # assure to avoid problems with np.float64, by using the Python float type
    for el in ret_dict:
        ret_dict[el] = float(ret_dict[el])

    return ret_dict

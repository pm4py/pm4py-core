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
from collections import Counter
from enum import Enum
from statistics import mean, median, stdev

from pm4py.util import constants, exec_utils
from pm4py.util import xes_constants as xes_util
from pm4py.util.business_hours import BusinessHours
from typing import Optional, Dict, Any, Union, Tuple
from pm4py.objects.log.obj import EventLog, EventStream


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    AGGREGATION_MEASURE = "aggregationMeasure"
    BUSINESS_HOURS = "business_hours"
    WORKTIMING = "worktiming"
    WEEKENDS = "weekends"


def apply(log: Union[EventLog, EventStream], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Dict[Tuple[str, str], float]:
    return performance(log, parameters=parameters)


def performance(log: Union[EventLog, EventStream], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Dict[Tuple[str, str], float]:
    """
    Measure performance between couples of attributes in the DFG graph

    Parameters
    ----------
    log
        Log
    parameters
        Possible parameters passed to the algorithms:
            aggregationMeasure -> performance aggregation measure (min, max, mean, median)
            activity_key -> Attribute to use as activity
            timestamp_key -> Attribute to use as timestamp
        - Parameters.BUSINESS_HOURS => calculates the difference of time based on the business hours, not the total time.
                                        Default: False
        - Parameters.WORKTIMING => work schedule of the company (provided as a list where the first number is the start
            of the work time, and the second number is the end of the work time), if business hours are enabled
                                        Default: [7, 17] (work shift from 07:00 to 17:00)
        - Parameters.WEEKENDS => indexes of the days of the week that are weekend
                                        Default: [6, 7] (weekends are Saturday and Sunday)
    Returns
    -------
    dfg
        DFG graph
    """

    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_util.DEFAULT_NAME_KEY)
    start_timestamp_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY, parameters,
                                                     xes_util.DEFAULT_TIMESTAMP_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes_util.DEFAULT_TIMESTAMP_KEY)
    aggregation_measure = exec_utils.get_param_value(Parameters.AGGREGATION_MEASURE, parameters, "mean")

    business_hours = exec_utils.get_param_value(Parameters.BUSINESS_HOURS, parameters, False)
    worktiming = exec_utils.get_param_value(Parameters.WORKTIMING, parameters, [7, 17])
    weekends = exec_utils.get_param_value(Parameters.WEEKENDS, parameters, [6, 7])

    if business_hours:
        dfgs0 = map((lambda t: [
            ((t[i - 1][activity_key], t[i][activity_key]),
             max(0, BusinessHours(t[i - 1][timestamp_key].replace(tzinfo=None),
                                  t[i][start_timestamp_key].replace(tzinfo=None), worktiming=worktiming,
                                  weekends=weekends).getseconds()))
            for i in range(1, len(t))]), log)
    else:
        dfgs0 = map((lambda t: [
            ((t[i - 1][activity_key], t[i][activity_key]),
             max(0, (t[i][start_timestamp_key] - t[i - 1][timestamp_key]).total_seconds()))
            for i in range(1, len(t))]), log)
    ret0 = {}
    for el in dfgs0:
        for couple in el:
            if not couple[0] in ret0:
                ret0[couple[0]] = []
            ret0[couple[0]].append(couple[1])
    ret = Counter()
    for key in ret0:
        if aggregation_measure == "median":
            ret[key] = median(ret0[key])
        elif aggregation_measure == "min":
            ret[key] = min(ret0[key])
        elif aggregation_measure == "max":
            ret[key] = max(ret0[key])
        elif aggregation_measure == "stdev":
            ret[key] = stdev(ret0[key]) if len(ret0[key]) > 1 else 0
        elif aggregation_measure == "sum":
            ret[key] = sum(ret0[key])
        elif aggregation_measure == "raw_values":
            ret[key] = ret0[key]
        elif aggregation_measure == "all":
            ret[key] = {"median": median(ret0[key]), "min": min(ret0[key]), "max": max(ret0[key]),
                        "stdev": stdev(ret0[key]) if len(ret0[key]) > 1 else 0, "sum": sum(ret0[key]), "mean": mean(ret0[key])}
        else:
            ret[key] = mean(ret0[key])

    return ret

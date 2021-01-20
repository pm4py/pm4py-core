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
from statistics import mean

from pm4py.util import exec_utils, constants, xes_constants
from pm4py.objects.conversion.log import converter as log_converter

class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY


DIFF_KEY = "@@diff"


def apply(log, parameters=None):
    """
    Gets the sojourn time per activity on an event log object

    Parameters
    --------------
    dataframe
        Pandas dataframe
    parameters
        Parameters of the algorithm, including:
        - Parameters.ACTIVITY_KEY => activity key
        - Parameters.START_TIMESTAMP_KEY => start timestamp key
        - Parameters.TIMESTAMP_KEY => timestamp key

    Returns
    --------------
    soj_time_dict
        Sojourn time dictionary
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, parameters=parameters)

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    start_timestamp_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY, parameters,
                                                     xes_constants.DEFAULT_TIMESTAMP_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)

    durations_dict = {}
    activities = [ev[activity_key] for trace in log for ev in trace]
    for act in activities:
        durations_dict[act] = []

    for trace in log:
        for event in trace:
            activity = event[activity_key]
            start_time = event[start_timestamp_key].timestamp()
            complete_time = event[timestamp_key].timestamp()
            durations_dict[activity].append(complete_time - start_time)

    for act in durations_dict:
        durations_dict[act] = mean(durations_dict[act])

    return durations_dict

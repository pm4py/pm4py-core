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
from pm4py.util import constants
from pm4py.util import xes_constants as xes
from pm4py.objects.log.log import EventLog
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.util import sorting
from pm4py.util.business_hours import BusinessHours


def insert_time_from_previous(log, parameters=None):
    """
    Inserts the time from the previous event, both in normal and business hours

    Parameters
    -------------
    log
        Event log
    parameters
        Parameters of the algorithm

    Returns
    -------------
    enriched_log
        Enriched log (with the time passed from the previous event)
    """
    if parameters is None:
        parameters = {}

    timestamp_key = parameters[
        constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] if constants.PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else xes.DEFAULT_TIMESTAMP_KEY
    worktiming = parameters["worktiming"] if "worktiming" in parameters else [7, 17]
    weekends = parameters["weekends"] if "weekends" in parameters else [6, 7]

    if not type(log) is EventLog:
        log = log_converter.apply(log)

    log = sorting.sort_timestamp_log(log, timestamp_key)

    for trace in log:
        if trace:
            trace[0]["@@passed_time_from_previous"] = 0
            trace[0]["@@approx_bh_passed_time_from_previous"] = 0

            i = 1
            while i < len(trace):
                trace[i]["@@passed_time_from_previous"] = (trace[i][timestamp_key] - trace[i - 1][timestamp_key]).total_seconds()
                bh = BusinessHours(trace[i - 1][timestamp_key].replace(tzinfo=None),
                                   trace[i][timestamp_key].replace(tzinfo=None),
                                   worktiming=worktiming,
                                   weekends=weekends)
                trace[i]["@@approx_bh_passed_time_from_previous"] = bh.getseconds()
                i = i + 1

    return log

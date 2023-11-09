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
from pm4py.util.xes_constants import DEFAULT_TIMESTAMP_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_TIMESTAMP_KEY
from enum import Enum
from pm4py.util import exec_utils

from typing import Optional, Dict, Any, Union
from pm4py.objects.log.obj import EventLog, Trace
from pm4py.objects.conversion.log import converter as log_converter


class Parameters(Enum):
    TIMESTAMP_KEY = PARAMETER_CONSTANT_TIMESTAMP_KEY


def filter_on_case_performance(log: EventLog, inf_perf: float, sup_perf: float, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> EventLog:
    """
    Gets a filtered log keeping only traces that satisfy the given performance requirements

    Parameters
    ------------
    log
        Log
    inf_perf
        Lower bound on the performance
    sup_perf
        Upper bound on the performance
    parameters
        Parameters

    Returns
    -----------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, DEFAULT_TIMESTAMP_KEY)
    filtered_log = EventLog([trace for trace in log if satisfy_perf(trace, inf_perf, sup_perf, timestamp_key)])
    return filtered_log


def filter_on_ncases(log: EventLog, max_no_cases: int = 1000) -> EventLog:
    """
    Get only a specified number of traces from a log

    Parameters
    -----------
    log
        Log
    max_no_cases
        Desidered number of traces from the log

    Returns
    -----------
    filtered_log
        Filtered log
    """
    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG)

    filtered_log = EventLog(log[:min(len(log), max_no_cases)])
    return filtered_log


def filter_on_case_size(log: EventLog, min_case_size: int = 2, max_case_size=None) -> EventLog:
    """
    Get only traces in the log with a given size

    Parameters
    -----------
    log
        Log
    min_case_size
        Minimum desidered size of traces
    max_case_size
        Maximum desidered size of traces

    Returns
    -----------
    filtered_log
        Filtered log
    """
    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG)

    if max_case_size is not None:
        filtered_log = EventLog([trace for trace in log if min_case_size <= len(trace) <= max_case_size])
    else:
        filtered_log = EventLog([trace for trace in log if len(trace) >= min_case_size])
    return filtered_log


def satisfy_perf(trace: Trace, inf_perf: float, sup_perf: float, timestamp_key: str) -> bool:
    """
    Checks if the trace satisfy the performance requirements

    Parameters
    -----------
    trace
        Trace
    inf_perf
        Lower bound on the performance
    sup_perf
        Upper bound on the performance
    timestamp_key
        Timestamp key

    Returns
    -----------
    boolean
        Boolean (is True if the trace satisfy the given performance requirements)
    """
    if trace:
        trace_duration = (trace[-1][timestamp_key] - trace[0][timestamp_key]).total_seconds()
        return inf_perf <= trace_duration <= sup_perf
    return False


def filter_case_performance(log, inf_perf, sup_perf, parameters=None):
    return filter_on_case_performance(log, inf_perf, sup_perf, parameters=parameters)


def apply(df, parameters=None):
    del df
    del parameters
    raise NotImplementedError("apply method not available for case filter")


def apply_auto_filter(df, parameters=None):
    del df
    del parameters
    raise NotImplementedError("apply_auto_filter method not available for case filter")

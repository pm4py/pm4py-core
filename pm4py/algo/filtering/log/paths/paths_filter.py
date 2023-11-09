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

from pm4py.util import exec_utils
from pm4py.util import xes_constants as xes
from pm4py.util.constants import PARAMETER_CONSTANT_ATTRIBUTE_KEY, PARAMETER_CONSTANT_TIMESTAMP_KEY, DEFAULT_VARIANT_SEP
import sys

from typing import Optional, Dict, Any, Union, Tuple, List
from pm4py.objects.log.obj import EventLog, Trace
from pm4py.objects.conversion.log import converter as log_converter


class Parameters(Enum):
    ATTRIBUTE_KEY = PARAMETER_CONSTANT_ATTRIBUTE_KEY
    DECREASING_FACTOR = "decreasingFactor"
    POSITIVE = "positive"
    TIMESTAMP_KEY = PARAMETER_CONSTANT_TIMESTAMP_KEY
    MIN_PERFORMANCE = "min_performance"
    MAX_PERFORMANCE = "max_performance"


def apply(log: EventLog, paths: List[Tuple[str, str]], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> EventLog:
    """
    Apply a filter on traces containing / not containing a path

    Parameters
    -----------
    log
        Log
    paths
        Paths that we are looking for (expressed as tuple of 2 strings)
    parameters
        Parameters of the algorithm, including:
            Parameters.ATTRIBUTE_KEY -> Attribute identifying the activity in the log
            Parameters.POSITIVE -> Indicate if events should be kept/removed

    Returns
    -----------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    attribute_key = exec_utils.get_param_value(Parameters.ATTRIBUTE_KEY, parameters, xes.DEFAULT_NAME_KEY)
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)
    filtered_log = EventLog(list(), attributes=log.attributes, extensions=log.extensions, classifiers=log.classifiers,
                            omni_present=log.omni_present, properties=log.properties)
    for trace in log:
        found = False
        for i in range(len(trace) - 1):
            path = (trace[i][attribute_key], trace[i + 1][attribute_key])
            if path in paths:
                found = True
                break
        if (found and positive) or (not found and not positive):
            filtered_log.append(trace)
    return filtered_log


def apply_performance(log: EventLog, provided_path: Tuple[str, str], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> EventLog:
    """
    Filters the cases of an event log where there is at least one occurrence of the provided path
    occurring in the defined timedelta range.

    Parameters
    ----------------
    log
        Event log
    provided_path
        Path between two activities (expressed as tuple)
    parameters
        Parameters of the filter, including:
            Parameters.ATTRIBUTE_KEY -> Attribute identifying the activity in the log
            Parameters.TIMESTAMP_KEY -> Attribute identifying the timestamp in the log
            Parameters.POSITIVE -> Indicate if events should be kept/removed
            Parameters.MIN_PERFORMANCE -> Minimal allowed performance of the provided path
            Parameters.MAX_PERFORMANCE -> Maximal allowed performance of the provided path

    Returns
    ----------------
    filtered_log
        Filtered event log
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    attribute_key = exec_utils.get_param_value(Parameters.ATTRIBUTE_KEY, parameters, xes.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes.DEFAULT_TIMESTAMP_KEY)
    min_performance = exec_utils.get_param_value(Parameters.MIN_PERFORMANCE, parameters, 0)
    max_performance = exec_utils.get_param_value(Parameters.MAX_PERFORMANCE, parameters, sys.maxsize)
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)
    filtered_log = EventLog(list(), attributes=log.attributes, extensions=log.extensions, classifiers=log.classifiers,
                            omni_present=log.omni_present, properties=log.properties)
    for trace in log:
        found = False
        for i in range(len(trace) - 1):
            path = (trace[i][attribute_key], trace[i + 1][attribute_key])
            if path == provided_path:
                timediff = trace[i + 1][timestamp_key].timestamp() - trace[i][timestamp_key].timestamp()
                if min_performance <= timediff <= max_performance:
                    found = True
                    break
        if (found and positive) or (not found and not positive):
            filtered_log.append(trace)
    return filtered_log


def get_paths_from_log(log, attribute_key="concept:name"):
    """
    Get the paths of the log along with their count

    Parameters
    ----------
    log
        Log
    attribute_key
        Attribute key (must be specified if different from concept:name)

    Returns
    ----------
    paths
        Dictionary of paths associated with their count
    """
    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG)

    paths = {}
    for trace in log:
        for i in range(0, len(trace) - 1):
            if attribute_key in trace[i] and attribute_key in trace[i + 1]:
                path = trace[i][attribute_key] + DEFAULT_VARIANT_SEP + trace[i + 1][attribute_key]
                if path not in paths:
                    paths[path] = 0
                paths[path] = paths[path] + 1
    return paths


def get_sorted_paths_list(paths):
    """
    Gets sorted paths list

    Parameters
    ----------
    paths
        Dictionary of paths associated with their count

    Returns
    ----------
    listpaths
        Sorted paths list
    """
    listpaths = []
    for p in paths:
        listpaths.append([p, paths[p]])
    listpaths = sorted(listpaths, key=lambda x: x[1], reverse=True)
    return listpaths


def get_paths_threshold(plist, decreasing_factor):
    """
    Get end attributes cutting threshold

    Parameters
    ----------
    plist
        List of paths ordered by number of occurrences
    decreasing_factor
        Decreasing factor of the algorithm

    Returns
    ---------
    threshold
        Paths cutting threshold
    """

    threshold = plist[0][1]
    for i in range(1, len(plist)):
        value = plist[i][1]
        if value > threshold * decreasing_factor:
            threshold = value
    return threshold


def filter_log_by_paths(log, paths, variants, vc, threshold, attribute_key="concept:name"):
    """
    Keep only paths which number of occurrences is above the threshold (or they belong to the first variant)

    Parameters
    ----------
    log
        Log
    paths
        Dictionary of paths associated with their count
    variants
        (If specified) Dictionary with variant as the key and the list of traces as the value
    vc
        List of variant names along with their count
    threshold
        Cutting threshold (remove paths which number of occurrences is below the threshold)
    attribute_key
        (If specified) Specify the attribute key to use (default concept:name)

    Returns
    ----------
    filtered_log
        Filtered log
    """
    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG)

    filtered_log = EventLog(list(), attributes=log.attributes, extensions=log.extensions, classifiers=log.classifiers,
                            omni_present=log.omni_present, properties=log.properties)
    fvft = variants[vc[0][0]][0]
    fvp = set()
    for i in range(0, len(fvft) - 1):
        path = fvft[i][attribute_key] + DEFAULT_VARIANT_SEP + fvft[i + 1][attribute_key]
        fvp.add(path)
    for trace in log:
        new_trace = Trace()
        jj = 0
        if len(trace) > 0:
            new_trace.append(trace[0])
            for j in range(1, len(trace) - 1):
                jj = j
                if j >= len(trace):
                    break
                if attribute_key in trace[j] and attribute_key in trace[j + 1]:
                    path = trace[j][attribute_key] + DEFAULT_VARIANT_SEP + trace[j + 1][attribute_key]
                    if path in paths:
                        if path in fvp or paths[path] >= threshold:
                            new_trace.append(trace[j])
                            new_trace.append(trace[j + 1])
        if len(trace) > 1 and not jj == len(trace):
            new_trace.append(trace[-1])
        if len(new_trace) > 0:
            for attr in trace.attributes:
                new_trace.attributes[attr] = trace.attributes[attr]
            filtered_log.append(new_trace)
    return filtered_log

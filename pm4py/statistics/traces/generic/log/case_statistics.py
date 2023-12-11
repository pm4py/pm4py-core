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
from pm4py.statistics.variants.log import get as variants_get
from pm4py.util.xes_constants import DEFAULT_TIMESTAMP_KEY
from pm4py.util.xes_constants import DEFAULT_TRACEID_KEY
from pm4py.statistics.traces.generic.common import case_duration as case_duration_commons
from pm4py.util.business_hours import BusinessHours
import numpy as np
from enum import Enum
from pm4py.util import exec_utils
from pm4py.util import constants
from typing import Optional, Dict, Any, Union, List
from pm4py.objects.log.obj import EventLog
from pm4py.objects.conversion.log import converter as log_converter


class Parameters(Enum):
    ATTRIBUTE_KEY = constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY

    MAX_VARIANTS_TO_RETURN = "max_variants_to_return"
    VARIANTS = "variants"
    VAR_DURATIONS = "var_durations"

    ENABLE_SORT = "enable_sort"
    SORT_BY_INDEX = "sort_by_index"
    SORT_ASCENDING = "sort_ascending"
    MAX_RET_CASES = "max_ret_cases"
    BUSINESS_HOURS = "business_hours"
    BUSINESS_HOUR_SLOTS = "business_hour_slots"
    WORKCALENDAR = "workcalendar"

    INDEXED_LOG = "indexed_log"


def get_variant_statistics(log: EventLog, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Union[List[Dict[str, int]], List[Dict[List[str], int]]]:
    """
    Gets a dictionary whose key is the variant and as value there
    is the list of traces that share the variant

    Parameters
    ----------
    log
        Log
    parameters
        Parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> Attribute identifying the activity in the log
            Parameters.MAX_VARIANTS_TO_RETURN -> Maximum number of variants to return
            Parameters.VARIANT -> If provided, avoid recalculation of the variants

    Returns
    ----------
    variants_list
        List of variants along the statistics
    """

    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    max_variants_to_return = exec_utils.get_param_value(Parameters.MAX_VARIANTS_TO_RETURN, parameters, None)
    varnt = exec_utils.get_param_value(Parameters.VARIANTS, parameters, variants_get.get_variants(log,
                                                                                              parameters=parameters))
    var_durations = exec_utils.get_param_value(Parameters.VAR_DURATIONS, parameters, None)
    if var_durations is None:
        var_durations = {}
    variants_list = []
    for var in varnt:
        var_el = {"variant": var, "count": len(varnt[var])}
        if var in var_durations:
            average = np.mean(var_durations[var])
            var_el["caseDuration"] = average
        variants_list.append(var_el)
    variants_list = sorted(variants_list, key=lambda x: (x["count"], x["variant"]), reverse=True)
    if max_variants_to_return:
        variants_list = variants_list[:min(len(variants_list), max_variants_to_return)]
    return variants_list


def get_cases_description(log: EventLog,  parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Dict[str, Dict[str, Any]]:
    """
    Get a description of traces present in the log

    Parameters
    -----------
    log
        Log
    parameters
        Parameters of the algorithm, including:
        Parameters.CASE_ID_KEY -> Trace attribute in which the case ID is contained
        Parameters.TIMESTAMP_KEY -> Column that identifies the timestamp
        Parameters.ENABLE_SORT -> Enable sorting of traces
        Parameters.SORT_BY_INDEX ->         Sort the traces using this index:
            0 -> case ID
            1 -> start time
            2 -> end time
            3 -> difference
        Parameters.SORT_ASCENDING -> Set sort direction (boolean; it true then the sort direction is ascending, otherwise
        descending)
        Parameters.MAX_RET_CASES -> Set the maximum number of returned traces

    Returns
    -----------
    ret
        Dictionary of traces associated to their start timestamp, their end timestamp and their duration
    """

    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, DEFAULT_TRACEID_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, DEFAULT_TIMESTAMP_KEY)
    enable_sort = exec_utils.get_param_value(Parameters.ENABLE_SORT, parameters, True)
    sort_by_index = exec_utils.get_param_value(Parameters.SORT_BY_INDEX, parameters, 0)
    sort_ascending = exec_utils.get_param_value(Parameters.SORT_ASCENDING, parameters, True)
    max_ret_cases = exec_utils.get_param_value(Parameters.MAX_RET_CASES, parameters, None)
    business_hours = exec_utils.get_param_value(Parameters.BUSINESS_HOURS, parameters, False)
    business_hours_slots = exec_utils.get_param_value(Parameters.BUSINESS_HOUR_SLOTS, parameters, constants.DEFAULT_BUSINESS_HOUR_SLOTS)

    workcalendar = exec_utils.get_param_value(Parameters.WORKCALENDAR, parameters, constants.DEFAULT_BUSINESS_HOURS_WORKCALENDAR)

    statistics_list = []

    for index, trace in enumerate(log):
        if trace:
            ci = trace.attributes[case_id_key] if case_id_key in trace.attributes else "EMPTY" + str(index)
            st = trace[0][timestamp_key]
            et = trace[-1][timestamp_key]
            if business_hours:
                bh = BusinessHours(st, et,
                                   business_hour_slots=business_hours_slots, workcalendar=workcalendar)
                diff = bh.get_seconds()
            else:
                diff = et.timestamp() - st.timestamp()
            st = st.timestamp()
            et = et.timestamp()
            statistics_list.append([ci, st, et, diff])

    if enable_sort:
        statistics_list = sorted(statistics_list, key=lambda x: x[sort_by_index], reverse=not sort_ascending)

    if max_ret_cases is not None:
        statistics_list = statistics_list[:min(len(statistics_list), max_ret_cases)]

    statistics_dict = {}

    for el in statistics_list:
        statistics_dict[str(el[0])] = {"startTime": el[1], "endTime": el[2], "caseDuration": el[3]}

    return statistics_dict


def index_log_caseid(log, parameters=None):
    """
    Index a log according to case ID

    Parameters
    -----------
    log
        Log object
    parameters
        Possible parameters of the algorithm, including:
            Parameters.CASE_ID_KEY -> Trace attribute in which the Case ID is contained

    Returns
    -----------
    dict
        Dictionary that has the case IDs as keys and the corresponding case as value
    """

    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, DEFAULT_TRACEID_KEY)
    indexed_log = {}

    for trace in log:
        trace_id = trace.attributes[case_id_key]
        indexed_log[trace_id] = trace

    return indexed_log


def get_events(log: EventLog, case_id: str, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> List[Dict[str, Any]]:
    """
    Get events belonging to the specified case

    Parameters
    -----------
    log
        Log object
    case_id
        Required case ID
    parameters
        Possible parameters of the algorithm, including:
            Parameters.CASE_ID_KEY -> Trace attribute in which the case ID is contained
            Parameters.INDEXED_LOG -> Indexed log (if it has been calculated previously)

    Returns
    ----------
    list_eve
        List of events belonging to the case
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    indexed_log = exec_utils.get_param_value(Parameters.INDEXED_LOG, parameters, index_log_caseid(log,
                                                                                                 parameters))

    list_eve = []
    for event in indexed_log[case_id]:
        list_eve.append(dict(event))
    return list_eve


def get_all_case_durations(log: EventLog, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> List[float]:
    """
    Gets all the case durations out of the log

    Parameters
    ------------
    log
        Log object
    parameters
        Possible parameters of the algorithm

    Returns
    ------------
    duration_values
        List of all duration values
    """
    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    cases = get_cases_description(log, parameters=parameters)
    duration_values = [x["caseDuration"] for x in cases.values()]

    return sorted(duration_values)


def get_first_quartile_case_duration(log: EventLog, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> float:
    """
    Gets the first quartile out of the log

    Parameters
    -------------
    log
        Log
    parameters
        Possible parameters of the algorithm

    Returns
    -------------
    value
        First quartile value
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    duration_values = get_all_case_durations(log, parameters=parameters)
    if duration_values:
        return duration_values[int((len(duration_values) * 3) / 4)]
    return 0


def get_median_case_duration(log: EventLog, parameters: Optional[Dict[Union[str, Parameters], Any]] = None):
    """
    Gets the median case duration out of the log

    Parameters
    -------------
    log
        Log
    parameters
        Possible parameters of the algorithm

    Returns
    -------------
    value
        Median duration value
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    duration_values = get_all_case_durations(log, parameters=parameters)
    if duration_values:
        return duration_values[int(len(duration_values) / 2)]
    return 0


def get_kde_caseduration(log, parameters=None):
    """
    Gets the estimation of KDE density for the case durations calculated on the log

    Parameters
    --------------
    log
        Log object
    parameters
        Possible parameters of the algorithm, including:
            Parameters.GRAPH_POINTS -> number of points to include in the graph

    Returns
    --------------
    x
        X-axis values to represent
    y
        Y-axis values to represent
    """
    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    return case_duration_commons.get_kde_caseduration(get_all_case_durations(log, parameters=parameters),
                                                      parameters=parameters)


def get_kde_caseduration_json(log, parameters=None):
    """
    Gets the estimation of KDE density for the case durations calculated on the log
    (expressed as JSON)

    Parameters
    --------------
    log
        Log object
    parameters
        Possible parameters of the algorithm, including:
            Parameters.GRAPH_POINTS -> number of points to include in the graph
            Parameters.CASE_ID_KEY -> Column hosting the Case ID

    Returns
    --------------
    json
        JSON representing the graph points
    """
    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    cases = get_cases_description(log, parameters=parameters)
    duration_values = [x["caseDuration"] for x in cases.values()]

    return case_duration_commons.get_kde_caseduration_json(duration_values, parameters=parameters)

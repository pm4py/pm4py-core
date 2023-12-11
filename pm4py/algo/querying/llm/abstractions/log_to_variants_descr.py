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

from pm4py.objects.conversion.log import converter as log_converter
from typing import Union, Optional, Dict, Any, List, Tuple
from pm4py.objects.log.obj import EventLog, EventStream
from enum import Enum
from pm4py.util import exec_utils, constants, xes_constants
import pandas as pd
import numpy as np
import math


class Parameters(Enum):
    INCLUDE_FREQUENCY = "include_frequency"
    INCLUDE_PERFORMANCE = "include_performance"
    MAX_LEN = "max_len"
    RELATIVE_FREQUENCY = "relative_frequency"
    RESPONSE_HEADER = "response_header"
    PRIMARY_PERFORMANCE_AGGREGATION = "primary_performance_aggregation"
    SECONDARY_PERFORMANCE_AGGREGATION = "secondary_performance_aggregation"
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY


def abstraction_from_variants_freq_perf_list(vars_list: List[Tuple[List[str], int, float, float]], parameters: Optional[Dict[Any, Any]] = None) -> str:
    """
    Obtains a textual abstraction from a list of variants provided along their frequency and performance values.
    Each variant of the list is expressed in the form:
        (('A', 'B', 'C'), 1000, 86400.0, 172800.0)
    where ('A', 'B', 'C') is the tuple of activities executed in the variant, 1000 is the number of occurrences of
    this variant in the event log, 86400.0 is an aggregation (mean) of the throughput times of the cases belonging to
    this variant, 172800.0 is an aggregation (stdev, so standard deviation) of the throughput times of these cases.

    Minimal viable example:

        from pm4py.algo.querying.llm.abstractions import log_to_variants_descr

        vars_list = [(('A', 'B', 'C'), 1000, 86400.0, 172800.0), (('A', 'B'), 500, 3600.0, 43200.0)]
        print(log_to_variants_descr.abstraction_from_variants_freq_perf_list(vars_list))

    Parameters
    ---------------
    vars_list
        List of variants, expressed as explained above
    parameters
        Optional parameters of the algorithm, including:
            - Parameters.RELATIVE_FREQUENCY => decides if the the frequency of the variants should be normalized to a relative
                                                frequency
            - Parameters.PRIMARY_PERFORMANCE_AGGREGATION => primary performance metric to be used to express the performance of the arcs (e.g., mean). Available options: mean, median, stdev, min, max, sum
            - Parameters.SECONDARY_PERFORMANCE_AGGREGATION => secondary performance metric to be used to express the performance of the arcs (e.g., stdev). Available options: mean, median, stdev, min, max, sum
            - Parameters.MAX_LEN => desidered length of the textual abstraction
            - Parameters.RESPONSE_HEADER => includes an header in the textual abstraction, which explains the context
            - Parameters.INCLUDE_FREQUENCY => includes the frequency of the arcs in the textual abstraction
            - Parameters.INCLUDE_PERFORMANCE => includes the performance of the arcs in the textual abstraction

    Returns
    --------------
    textual_abstraction
        Textual abstraction of the variants
    """
    if parameters is None:
        parameters = {}

    relative_frequency = exec_utils.get_param_value(Parameters.RELATIVE_FREQUENCY, parameters, False)
    max_len = exec_utils.get_param_value(Parameters.MAX_LEN, parameters, constants.OPENAI_MAX_LEN)
    response_header = exec_utils.get_param_value(Parameters.RESPONSE_HEADER, parameters, True)
    include_frequency = exec_utils.get_param_value(Parameters.INCLUDE_FREQUENCY, parameters, True)
    include_performance = exec_utils.get_param_value(Parameters.INCLUDE_PERFORMANCE, parameters, True)
    primary_performance_aggregation = exec_utils.get_param_value(Parameters.PRIMARY_PERFORMANCE_AGGREGATION, parameters, "mean")
    secondary_performance_aggregation = exec_utils.get_param_value(Parameters.SECONDARY_PERFORMANCE_AGGREGATION, parameters, None)

    ret = "If I have a process with the following process variants:\n\n" if response_header else "\n\n"
    for v in vars_list:
        if len(ret) > max_len:
            break
        stru = " " + " -> " .join(v[0]) + " "
        if include_frequency or include_performance:
            stru = stru + "("
            if include_frequency:
                stru = stru + " frequency = "
                stru = stru + str(v[1])
                if relative_frequency:
                    stru = stru + "\%"
                stru = stru + " "
            if include_performance:
                stru = stru + " performance = "
                stru = stru + "%.3f" % (v[2])
                stru = stru + " "
                if secondary_performance_aggregation is not None and v[3] is not None:
                    stru = stru + " " + secondary_performance_aggregation + " = "
                    stru = stru + "%.3f" % (v[3])
                    stru = stru + " "
            stru = stru + ")\n"
        ret = ret + stru
    ret = ret + "\n\n"
    return ret


def compute_perf_aggregation(perf_values: List[float], perf_agg: str) -> float:
    """
    Computes an aggregation of a list of performance values

    Minimal viable example:
        compute_perf_aggregation([3600.0, 7200.0], 'mean')

    Parameters
    --------------
    perf_values
        List of performance values
    perf_agg
        Desired aggregation (mean, median, stdev, sum, min, max)

    Returns
    --------------
    agg_value
        Aggregated value
    """
    if perf_agg == "mean":
        return float(np.mean(perf_values))
    elif perf_agg == "median":
        return float(np.median(perf_values))
    elif perf_agg == "stdev" and len(perf_values) > 1:
        return float(np.std(perf_values))
    elif perf_agg == "sum":
        return float(np.sum(perf_values))
    elif perf_agg == "min":
        return float(np.min(perf_values))
    elif perf_agg == "max":
        return float(np.max(perf_values))


def apply(log_obj: Union[EventLog, EventStream, pd.DataFrame], parameters: Optional[Dict[Any, Any]] = None) -> str:
    """
    Gets the textual abstraction of the variants of a specified log object.

    Minimal viable example:

        import pm4py
        from pm4py.algo.querying.llm.abstractions import log_to_variants_descr

        log = pm4py.read_xes('tests/input_data/running-example.xes')
        print(log_to_variants_descr.apply(log))

    Parameters
    ---------------
    log_obj
        Log object
    parameters
        Optional parameters of the algorithm, including:
        - Parameters.ACTIVITY_KEY => the attribute of the log to be used as activity
        - Parameters.TIMESTAMP_KEY => the attribute of the log to be used as timestamp
        - Parameters.CASE_ID_KEY => the attribute of the log to be used as case identifier
        - Parameters.RELATIVE_FREQUENCY => decides if the the frequency of the variants should be normalized to a relative
                                            frequency
        - Parameters.PRIMARY_PERFORMANCE_AGGREGATION => primary performance metric to be used to express the performance of the arcs (e.g., mean). Available options: mean, median, stdev, min, max, sum
        - Parameters.SECONDARY_PERFORMANCE_AGGREGATION => secondary performance metric to be used to express the performance of the arcs (e.g., stdev). Available options: mean, median, stdev, min, max, sum

    Returns
    --------------
    textual_abstraction
        Textual abstraction of the variants of an event log object
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
    relative_frequency = exec_utils.get_param_value(Parameters.RELATIVE_FREQUENCY, parameters, False)
    primary_performance_aggregation = exec_utils.get_param_value(Parameters.PRIMARY_PERFORMANCE_AGGREGATION, parameters, "mean")
    secondary_performance_aggregation = exec_utils.get_param_value(Parameters.SECONDARY_PERFORMANCE_AGGREGATION, parameters, None)

    log_obj = log_converter.apply(log_obj, variant=log_converter.Variants.TO_DATA_FRAME, parameters=parameters)
    gdf = log_obj.groupby(case_id_key)
    variants = gdf[activity_key].agg(list).to_dict()
    variants = {c: tuple(v) for c, v in variants.items()}
    gdf = gdf[timestamp_key]
    start_time = gdf.min().to_dict()
    start_time = {x: y.timestamp() for x, y in start_time.items()}
    end_time = gdf.max().to_dict()
    end_time = {x: y.timestamp() for x, y in end_time.items()}
    diff = {x: end_time[x]-start_time[x] for x in start_time}
    vars_list = {}
    num_cases = log_obj[case_id_key].nunique()

    for c, v in variants.items():
        if v not in vars_list:
            vars_list[v] = []
        vars_list[v].append(diff[c])

    for k, v in vars_list.items():
        freq = max(1, math.floor((len(v)*100.0)/num_cases)) if relative_frequency else len(v)
        primary_perf = compute_perf_aggregation(v, primary_performance_aggregation)
        secondary_perf = compute_perf_aggregation(v, secondary_performance_aggregation)
        tup = (freq, primary_perf, secondary_perf)
        vars_list[k] = tup

    vars_list = [(x, y[0], y[1], y[2]) for x, y in vars_list.items()]
    vars_list = sorted(vars_list, key=lambda x: (x[1], x[2], x[0]), reverse=True)

    return abstraction_from_variants_freq_perf_list(vars_list, parameters=parameters)

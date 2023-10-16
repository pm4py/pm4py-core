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
from pm4py.algo.discovery.dfg.adapters.pandas import df_statistics
from typing import Union, Optional, Dict, Any, Tuple
from pm4py.objects.log.obj import EventLog, EventStream
from enum import Enum
from pm4py.util import exec_utils, constants, xes_constants
import pandas as pd
import math
import numpy as np


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


def abstraction_from_frequency_performance_dfg(freq_dfg: Dict[Tuple[str, str], int], perf_dfg: Dict[Tuple[str, str], Dict[str, float]], parameters: Optional[Dict[Any, Any]] = None) -> str:
    """
    Obtains the abstraction starting from the knowledge of the frequency of the paths, and their performance.

    Minimal viable example:

        import pm4py
        from pm4py.algo.querying.llm.abstractions import log_to_dfg_descr

        log = pm4py.read_xes('tests/input_data/running-example.xes')
        freq_dfg, sa, ea = pm4py.discover_dfg(log)
        perf_dfg, sa, ea = pm4py.discover_performance_dfg(log)
        print(log_to_dfg_descr.abstraction_from_frequency_performance_dfg(freq_dfg, perf_dfg))

    Parameters
    ---------------
    freq_dfg
        Dictionary associating to each path its frequency
    perf_dfg
        Dictionary associating to each path its performance. A path ('A', 'B') is associated to a dictionary
        containing performance metrics, i.e. ('A', 'B'): {'mean': 86400, 'stdev': 86400} means that:
        - the average time between the activities A and B is 1 day
        - also the standard deviation of the times between A and B is 1 day
    parameters
        Optional parameters of the algorithm, including:
                - Parameters.RELATIVE_FREQUENCY => (boolean) decides if the frequency DFG should be normalized to a relative
                                            frequency
                - Parameters.INCLUDE_FREQUENCY => includes the frequency of the arcs in the textual abstraction
                - Parameters.INCLUDE_PERFORMANCE => includes the performance of the arcs in the textual abstraction
                - Parameters.MAX_LEN => desidered length of the textual abstraction
                - Parameters.RESPONSE_HEADER => includes an header in the textual abstraction, which explains the context
                - Parameters.PRIMARY_PERFORMANCE_AGGREGATION => primary performance metric to be used to express the performance of the arcs (e.g., mean). Available options: mean, median, stdev, min, max, sum
                - Parameters.SECONDARY_PERFORMANCE_AGGREGATION => secondary performance metric to be used to express the performance of the arcs (e.g., stdev). Available options: mean, median, stdev, min, max, sum
    Returns
    ---------------
    textual_abstraction
        Textual abstraction
    """
    if parameters is None:
        parameters = {}

    relative_frequency = exec_utils.get_param_value(Parameters.RELATIVE_FREQUENCY, parameters, False)
    include_frequency = exec_utils.get_param_value(Parameters.INCLUDE_FREQUENCY, parameters, True)
    include_performance = exec_utils.get_param_value(Parameters.INCLUDE_PERFORMANCE, parameters, True)
    max_len = exec_utils.get_param_value(Parameters.MAX_LEN, parameters, constants.OPENAI_MAX_LEN)
    response_header = exec_utils.get_param_value(Parameters.RESPONSE_HEADER, parameters, True)
    primary_performance_aggregation = exec_utils.get_param_value(Parameters.PRIMARY_PERFORMANCE_AGGREGATION, parameters, "mean")
    secondary_performance_aggregation = exec_utils.get_param_value(Parameters.SECONDARY_PERFORMANCE_AGGREGATION, parameters, None)

    paths = sorted([(x, y) for x, y in freq_dfg.items()], key=lambda z: (z[1], z[0]), reverse=True)
    paths = [x[0] for x in paths]

    ret = "If I have a process with flow:\n\n" if response_header else "\n\n"
    for p in paths:
        if len(ret) > max_len:
            break
        stru = "%s -> %s " % (p[0], p[1])
        if include_frequency or include_performance:
            stru = stru + "("
            if include_frequency:
                stru = stru + " frequency = "
                stru = stru + str(freq_dfg[p])
                if relative_frequency:
                    stru = stru + "\%"
                stru = stru + " "
            if include_performance:
                stru = stru + " performance = "
                stru = stru + "%.3f" % perf_dfg[p][primary_performance_aggregation]
                stru = stru + " "
                if secondary_performance_aggregation is not None and secondary_performance_aggregation in perf_dfg[p] and perf_dfg[p][secondary_performance_aggregation] is not None and not np.isnan(perf_dfg[p][secondary_performance_aggregation]):
                    stru = stru + " " + secondary_performance_aggregation + " = "
                    stru = stru + "%.3f" % perf_dfg[p][secondary_performance_aggregation]
                    stru = stru + " "
            stru = stru + ")\n"
        ret = ret + stru
    ret = ret + "\n\n"
    return ret


def apply(log_obj: Union[EventLog, EventStream, pd.DataFrame], parameters: Optional[Dict[Any, Any]] = None) -> str:
    """
    Gets the textual abstraction of the directly-follows graph computed on the provided log object.

    Minimal viable example:
        import pm4py
        from pm4py.algo.querying.llm.abstractions import log_to_dfg_descr

        log = pm4py.read_xes('tests/input_data/running-example.xes')
        print(log_to_dfg_descr.apply(log))

    Parameters
    ---------------
    log_obj
        Log object (event log / Pandas dataframe)
    parameters
        Optional Parameters of the algorithm, including:
            - Parameters.ACTIVITY_KEY => the attribute to be used as activity
            - Parameters.TIMESTAMP_KEY => the attribute to be used as timestamp
            - Parameters.CASE_ID_KEY => the attribute to be used as case ID
            - Parameters.RELATIVE_FREQUENCY => (boolean) decides if the frequency DFG should be normalized to a relative
                                                frequency
            - Parameters.INCLUDE_FREQUENCY => includes the frequency of the arcs in the textual abstraction
            - Parameters.INCLUDE_PERFORMANCE => includes the performance of the arcs in the textual abstraction
            - Parameters.MAX_LEN => desidered length of the textual abstraction
            - Parameters.RESPONSE_HEADER => includes an header in the textual abstraction, which explains the context
            - Parameters.PRIMARY_PERFORMANCE_AGGREGATION => primary performance metric to be used to express the performance of the arcs (e.g., mean). Available options: mean, median, stdev, min, max, sum
            - Parameters.SECONDARY_PERFORMANCE_AGGREGATION => secondary performance metric to be used to express the performance of the arcs (e.g., stdev). Available options: mean, median, stdev, min, max, sum

    Returns
    ---------------
    textual_abstraction
        Textual abstraction
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
    relative_frequency = exec_utils.get_param_value(Parameters.RELATIVE_FREQUENCY, parameters, False)

    log_obj = log_converter.apply(log_obj, variant=log_converter.Variants.TO_DATA_FRAME, parameters=parameters)
    freq_dfg, perf_dfg = df_statistics.get_dfg_graph(log_obj, measure="both", perf_aggregation_key="all", activity_key=activity_key, case_id_glue=case_id_key, timestamp_key=timestamp_key)
    if relative_frequency:
        freq_dfg = df_statistics.get_dfg_graph(log_obj, measure="frequency", activity_key=activity_key, case_id_glue=case_id_key, timestamp_key=timestamp_key, keep_once_per_case=True)
        num_cases = log_obj[case_id_key].nunique()
        freq_dfg = {x: max(1, math.floor((y*100.0)/num_cases)) for x, y in freq_dfg.items()}

    return abstraction_from_frequency_performance_dfg(freq_dfg, perf_dfg, parameters=parameters)

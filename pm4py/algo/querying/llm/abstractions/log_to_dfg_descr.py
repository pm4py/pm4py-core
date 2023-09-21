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
from typing import Union, Optional, Dict, Any
from pm4py.objects.log.obj import EventLog, EventStream
from enum import Enum
from pm4py.util import exec_utils, constants, xes_constants
import pandas as pd
import math


class Parameters(Enum):
    INCLUDE_FREQUENCY = "include_frequency"
    INCLUDE_PERFORMANCE = "include_performance"
    MAX_LEN = "max_len"
    RELATIVE_FREQUENCY = "relative_frequency"
    RESPONSE_HEADER = "response_header"
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY


def apply(log_obj: Union[EventLog, EventStream, pd.DataFrame], parameters: Optional[Dict[Any, Any]] = None) -> str:
    if parameters is None:
        parameters = {}

    include_frequency = exec_utils.get_param_value(Parameters.INCLUDE_FREQUENCY, parameters, True)
    include_performance = exec_utils.get_param_value(Parameters.INCLUDE_PERFORMANCE, parameters, True)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
    max_len = exec_utils.get_param_value(Parameters.MAX_LEN, parameters, constants.OPENAI_MAX_LEN)
    relative_frequency = exec_utils.get_param_value(Parameters.RELATIVE_FREQUENCY, parameters, False)
    response_header = exec_utils.get_param_value(Parameters.RESPONSE_HEADER, parameters, True)

    log_obj = log_converter.apply(log_obj, variant=log_converter.Variants.TO_DATA_FRAME, parameters=parameters)
    freq_dfg, perf_dfg = df_statistics.get_dfg_graph(log_obj, measure="both", activity_key=activity_key, case_id_glue=case_id_key, timestamp_key=timestamp_key)
    if relative_frequency:
        freq_dfg = df_statistics.get_dfg_graph(log_obj, measure="frequency", activity_key=activity_key, case_id_glue=case_id_key, timestamp_key=timestamp_key, keep_once_per_case=True)
        num_cases = log_obj[case_id_key].nunique()
        freq_dfg = {x: max(1, math.floor((y*100.0)/num_cases)) for x, y in freq_dfg.items()}

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
                stru = stru + str(perf_dfg[p])
                stru = stru + " "
            stru = stru + ")\n"
        ret = ret + stru
    ret = ret + "\n\n"
    return ret

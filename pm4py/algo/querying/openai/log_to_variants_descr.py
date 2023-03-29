from pm4py.objects.conversion.log import converter as log_converter
from typing import Union, Optional, Dict, Any
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
    relative_frequency = exec_utils.get_param_value(Parameters.RELATIVE_FREQUENCY, parameters, False)
    max_len = exec_utils.get_param_value(Parameters.MAX_LEN, parameters, constants.OPENAI_MAX_LEN)
    response_header = exec_utils.get_param_value(Parameters.RESPONSE_HEADER, parameters, True)

    log_obj = log_converter.apply(log_obj, variant=log_converter.Variants.TO_DATA_FRAME, parameters=parameters)
    gdf = log_obj.groupby(case_id_key)
    variants = gdf[activity_key].agg(tuple).to_dict()
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
        perf = float(np.mean(v))
        vars_list[k] = (freq, perf)

    vars_list = [(x, y[0], y[1]) for x, y in vars_list.items()]
    vars_list = sorted(vars_list, key=lambda x: (x[1], x[2], x[0]), reverse=True)

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
                stru = stru + str(v[2])
                stru = stru + " "
            stru = stru + ")\n"
        ret = ret + stru
    ret = ret + "\n\n"
    return ret

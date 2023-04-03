from typing import Optional, Dict, Any, Union
from pm4py.objects.log.obj import EventLog, EventStream
from enum import Enum
from pm4py.util import exec_utils, constants, xes_constants
from pm4py.objects.conversion.log import converter as log_converter

import pandas as pd


class Parameters(Enum):
    RESPONSE_HEADER = "response_header"
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    MAX_LEN = "max_len"


def apply(log_obj: Union[EventLog, EventStream, pd.DataFrame], parameters: Optional[Dict[Any, Any]] = None) -> str:
    """
    Given a log object, returns a representation of the (last) events of a stream corresponding to the log object.

    Parameters
    --------------
    log_obj
        Log object
    parameters
        Parameters of the algorithm, including:
        - Parameters.RESPONSE_HEADER => includes the header in the response
        - Parameters.TIMESTAMP_KEY => the attribute to be used as timestamp
        - Parameters.MAX_LEN => maximum length of the resulting stream

    Returns
    --------------
    descr
        String representing the stream of events
    """
    if parameters is None:
        parameters = {}

    parameters["stream_postprocessing"] = True
    event_stream = log_converter.apply(log_obj, variant=log_converter.Variants.TO_EVENT_STREAM, parameters=parameters)._list
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    response_header = exec_utils.get_param_value(Parameters.RESPONSE_HEADER, parameters, True)
    max_len = exec_utils.get_param_value(Parameters.MAX_LEN, parameters, constants.OPENAI_MAX_LEN)

    event_stream.sort(key=lambda x: x[timestamp_key], reverse=True)

    ret = ["\n"]
    interet = []
    summ = 2

    if response_header:
        header = "If I have the following stream of events:\n"
        summ += len(header) + 1
        ret.append(header)

    for ev in event_stream:
        if summ > max_len:
            break
        stru = str(ev)
        summ += len(stru) + 1
        interet.append(stru)

    interet.reverse()
    ret = ret+interet+["\n"]
    return "\n".join(ret)

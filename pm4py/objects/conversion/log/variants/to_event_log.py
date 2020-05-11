from copy import copy
from copy import deepcopy
from enum import Enum

import pandas

import pm4py
from pm4py import util as pmutil
from pm4py.objects.conversion.log import constants
from pm4py.objects.conversion.log.variants import to_event_stream
from pm4py.objects.log import log as log_instance
from pm4py.util import xes_constants as xes


class Parameters(Enum):
    STREAM_POST_PROCESSING = False
    DEEP_COPY = False
    CASE_ID_KEY = 'case:concept:name'
    CASE_ATTRIBUTE_PREFIX = 'case:'


# this parameter is deprecated should be removed...
DEEPCOPY = constants.DEEPCOPY


# helper function, should be removed later...
def __parse_parameters(parameters):
    if DEEPCOPY in parameters:
        parameters[Parameters.DEEP_COPY] = parameters[DEEPCOPY]
    if pmutil.constants.PARAMETER_CONSTANT_CASEID_KEY in parameters:
        parameters[Parameters.CASE_ID_KEY] = parameters[pmutil.constants.PARAMETER_CONSTANT_CASEID_KEY]
    if pmutil.constants.PARAMETER_KEY_CASE_ATTRIBUTE_PRFIX in parameters:
        parameters[Parameters.CASE_ATTRIBUTE_PREFIX] = parameters[pmutil.constants.PARAMETER_KEY_CASE_ATTRIBUTE_PRFIX]
    return parameters


def __generate_to_stream_parameters(parameters):
    # utility in case a df is an input, which is first converted to an event stream.
    stream_param = dict()
    if Parameters.STREAM_POST_PROCESSING in parameters:
        stream_param[to_event_stream.Parameters.STREAM_POST_PROCESSING] = parameters[
            Parameters.STREAM_POST_PROCESSING]
    if Parameters.DEEP_COPY in parameters:
        stream_param[to_event_stream.Parameters.DEEP_COPY] = parameters[Parameters.DEEP_COPY]
    if Parameters.CASE_ATTRIBUTE_PREFIX in parameters:
        stream_param[to_event_stream.Parameters.CASE_ATTRIBUTE_PREFIX] = parameters[Parameters.CASE_ATTRIBUTE_PREFIX]
    return stream_param


def apply(log, parameters=None):
    parameters = dict() if parameters is None else __parse_parameters(parameters)
    if isinstance(log, pandas.core.frame.DataFrame):
        log = to_event_stream.apply(log, parameters=__generate_to_stream_parameters(parameters))
    if isinstance(log, pm4py.objects.log.log.EventStream) and (not isinstance(log, pm4py.objects.log.log.EventLog)):
        glue = parameters[
            Parameters.CASE_ID_KEY] if Parameters.CASE_ID_KEY in parameters else Parameters.CASE_ID_KEY.value
        case_pref = parameters[
            Parameters.CASE_ATTRIBUTE_PREFIX] if Parameters.CASE_ATTRIBUTE_PREFIX in parameters else Parameters.CASE_ATTRIBUTE_PREFIX.value
        enable_deepcopy = parameters[Parameters.DEEP_COPY] if Parameters.DEEP_COPY in parameters else False
        return __transform_event_stream_to_event_log(log, case_glue=glue, include_case_attributes=True,
                                                     case_attribute_prefix=case_pref, enable_deepcopy=enable_deepcopy)
    return log


def __transform_event_stream_to_event_log(log, case_glue=Parameters.CASE_ID_KEY.value,
                                          include_case_attributes=True,
                                          case_attribute_prefix=Parameters.CASE_ATTRIBUTE_PREFIX.value,
                                          enable_deepcopy=False):
    """
    Converts the event stream to an event log

    Parameters
    ----------
    log: :class:`pm4py.log.log.EventLog`
        An event stream
    case_glue:
        Case identifier. Default is 'case:concept:name'
    include_case_attributes:
        Default is True
    case_attribute_prefix:
        Default is 'case:'
    enable_deepcopy
        Enables deepcopy (avoid references between input and output objects)

    Returns
        -------
    log : :class:`pm4py.log.log.EventLog`
        An event log
    """
    if enable_deepcopy:
        log = deepcopy(log)

    traces = {}
    for orig_event in log:
        event = copy(orig_event)
        glue = event[case_glue]
        if glue not in traces:
            trace_attr = {}
            if include_case_attributes:
                for k in event.keys():
                    if k.startswith(case_attribute_prefix):
                        trace_attr[k.replace(case_attribute_prefix, '')] = event[k]
                if xes.DEFAULT_TRACEID_KEY not in trace_attr:
                    trace_attr[xes.DEFAULT_TRACEID_KEY] = glue
            traces[glue] = log_instance.Trace(attributes=trace_attr)

        if include_case_attributes:
            for k in list(event.keys()):
                if k.startswith(case_attribute_prefix):
                    del event[k]

        traces[glue].append(event)
    return log_instance.EventLog(traces.values(), attributes=log.attributes, classifiers=log.classifiers,
                                 omni_present=log.omni_present, extensions=log.extensions)

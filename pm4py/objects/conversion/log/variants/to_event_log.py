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
from copy import copy
from copy import deepcopy
from enum import Enum

from pm4py.objects.conversion.log import constants
from pm4py.objects.conversion.log.variants import to_event_stream
from pm4py.objects.log import obj as log_instance
from pm4py.util import xes_constants as xes
from pm4py.util import exec_utils, constants as pmconstants, pandas_utils
import pandas as pd


class Parameters(Enum):
    DEEP_COPY = constants.DEEPCOPY
    STREAM_POST_PROCESSING = constants.STREAM_POSTPROCESSING
    CASE_ATTRIBUTE_PREFIX = "case_attribute_prefix"
    CASE_ID_KEY = pmconstants.PARAMETER_CONSTANT_CASEID_KEY


def apply(log, parameters=None):
    if parameters is None:
        parameters = {}

    if type(log) is log_instance.Trace or type(log) is log_instance.EventLog:
        return log

    enable_deepcopy = exec_utils.get_param_value(Parameters.DEEP_COPY, parameters, False)
    glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, pmconstants.CASE_CONCEPT_NAME)
    case_pref = exec_utils.get_param_value(Parameters.CASE_ATTRIBUTE_PREFIX, parameters,
                                           "case:")

    if pandas_utils.check_is_pandas_dataframe(log):
        log = to_event_stream.apply(log, parameters=parameters)

    if isinstance(log, log_instance.EventStream) and (not isinstance(log, log_instance.EventLog)):
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
                                 omni_present=log.omni_present, extensions=log.extensions, properties=log.properties)

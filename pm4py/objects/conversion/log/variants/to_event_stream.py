import math
from copy import deepcopy
from enum import Enum

import pandas

from pm4py.objects.conversion.log import constants
from pm4py.objects.log import log as log_instance
from pm4py.objects.log.log import EventLog, Event
from pm4py.util import constants as pmutil


class Parameters(Enum):
    DEEP_COPY = False
    STREAM_POST_PROCESSING = False
    CASE_ATTRIBUTE_PREFIX = 'case:'


DEEPCOPY = constants.DEEPCOPY
STREAM_POST_PROCESSING = constants.STREAM_POSTPROCESSING


def __parse_parameters(parameters):
    if DEEPCOPY in parameters:
        parameters[Parameters.DEEP_COPY] = parameters[DEEPCOPY]
    if STREAM_POST_PROCESSING in parameters:
        parameters[Parameters.STREAM_POST_PROCESSING] = parameters[STREAM_POST_PROCESSING]
    if pmutil.PARAMETER_KEY_CASE_ATTRIBUTE_PRFIX in parameters:
        parameters[Parameters.CASE_ATTRIBUTE_PREFIX] = parameters[pmutil.PARAMETER_KEY_CASE_ATTRIBUTE_PRFIX]
    return parameters


def __postprocess_stream(list_events):
    """
    Postprocess the list of events of the stream in order to make sure
    that there are no NaN/NaT values

    Parameters
    -------------
    list_events
        List of events

    Returns
    -------------
    list_events
        Postprocessed stream
    """
    for event in list_events:
        event_keys = list(event.keys())
        for k in event_keys:
            if type(event[k]) is pandas._libs.tslibs.nattype.NaTType:
                del event[k]
                continue
            if (type(event[k]) is float or type(event[k]) is int) and math.isnan(event[k]):
                del event[k]
                continue
    return list_events


def apply(log, parameters=None):
    """
      Converts the event log to an event stream

      Parameters
      ----------
      log: :class:`pm4py.log.log.EventLog`
          An Event log
      include_case_attributes:
          Default is True
      case_attribute_prefix:
          Default is 'case:'
      enable_deepcopy
          Enables deepcopy (avoid references between input and output objects)

      Returns
          -------
      log : :class:`pm4py.log.log.EventLog`
          An Event stream
      """
    parameters = dict() if parameters is None else __parse_parameters(parameters)
    if isinstance(log, pandas.core.frame.DataFrame):
        list_events = log.to_dict('records')
        if Parameters.STREAM_POST_PROCESSING in parameters and parameters[Parameters.STREAM_POST_PROCESSING]:
            list_events = __postprocess_stream(list_events)
        for i in range(len(list_events)):
            list_events[i] = Event(list_events[i])
        log = log_instance.EventStream(list_events, attributes={'origin': 'csv'})
    if isinstance(log, EventLog):
        case_pref = parameters[
            Parameters.CASE_ATTRIBUTE_PREFIX] if Parameters.CASE_ATTRIBUTE_PREFIX in parameters else Parameters.CASE_ATTRIBUTE_PREFIX.value
        enable_deepcopy = parameters[
            Parameters.DEEP_COPY] if Parameters.DEEP_COPY in parameters else Parameters.DEEP_COPY.value

        return __transform_event_log_to_event_stream(log, include_case_attributes=True,
                                                     case_attribute_prefix=case_pref, enable_deepcopy=enable_deepcopy)
    return log


def __transform_event_log_to_event_stream(log, include_case_attributes=True,
                                          case_attribute_prefix=pmutil.CASE_ATTRIBUTE_PREFIX, enable_deepcopy=False):
    """
      Converts the event log to an event stream

      Parameters
      ----------
      log: :class:`pm4py.log.log.EventLog`
          An Event log
      include_case_attributes:
          Default is True
      case_attribute_prefix:
          Default is 'case:'
      enable_deepcopy
          Enables deepcopy (avoid references between input and output objects)

      Returns
          -------
      log : :class:`pm4py.log.log.EventLog`
          An Event stream
      """
    if enable_deepcopy:
        log = deepcopy(log)

    events = []
    for trace in log:
        for event in trace:
            if include_case_attributes:
                for key, value in trace.attributes.items():
                    event[case_attribute_prefix + key] = value
            # fix 14/02/2019: since the XES standard does not force to specify a case ID, when event log->event stream
            # conversion is done, the possibility to get back the original event log is lost
            if pmutil.CASE_ATTRIBUTE_GLUE not in event:
                event[pmutil.CASE_ATTRIBUTE_GLUE] = str(hash(trace))
            events.append(event)
    return log_instance.EventStream(events, attributes=log.attributes, classifiers=log.classifiers,
                                    omni_present=log.omni_present, extensions=log.extensions)

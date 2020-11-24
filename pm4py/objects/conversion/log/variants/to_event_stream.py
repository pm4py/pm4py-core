import math
import pkgutil
from copy import deepcopy
from enum import Enum

from pm4py.objects.conversion.log import constants
from pm4py.objects.log import log as log_instance
from pm4py.objects.log.log import EventLog, Event, XESExtension
from pm4py.util import constants as pmutil
from pm4py.util import exec_utils, pandas_utils, xes_constants


class Parameters(Enum):
    DEEP_COPY = constants.DEEPCOPY
    STREAM_POST_PROCESSING = constants.STREAM_POSTPROCESSING
    CASE_ATTRIBUTE_PREFIX = "case_attribute_prefix"


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
    import pandas

    for event in list_events:
        event_keys = list(event.keys())
        for k in event_keys:
            if type(event[k]) is pandas._libs.tslibs.nattype.NaTType:
                del event[k]
                continue
            if (type(event[k]) is float or type(event[k]) is int) and math.isnan(event[k]):
                del event[k]
                continue
            ev_str = str(event[k]).lower()
            if ev_str == "none" or ev_str == "null" or len(ev_str) == 0:
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
    if parameters is None:
        parameters = {}

    stream_post_processing = exec_utils.get_param_value(Parameters.STREAM_POST_PROCESSING, parameters, False)
    case_pref = exec_utils.get_param_value(Parameters.CASE_ATTRIBUTE_PREFIX, parameters, 'case:')
    enable_deepcopy = exec_utils.get_param_value(Parameters.DEEP_COPY, parameters, False)

    if pkgutil.find_loader("pandas"):
        import pandas
        if isinstance(log, pandas.core.frame.DataFrame):
            extensions = __detect_extensions(log)
            list_events = pandas_utils.to_dict_records(log)
            if stream_post_processing:
                list_events = __postprocess_stream(list_events)
            for i in range(len(list_events)):
                list_events[i] = Event(list_events[i])
            log = log_instance.EventStream(list_events, attributes={'origin': 'csv'})
            for ex in extensions:
                log.extensions[ex.name] = {
                    xes_constants.KEY_PREFIX: ex.prefix,
                    xes_constants.KEY_URI: ex.uri}
    if isinstance(log, EventLog):
        return __transform_event_log_to_event_stream(log, include_case_attributes=True,
                                                     case_attribute_prefix=case_pref, enable_deepcopy=enable_deepcopy)
    return log


def __detect_extensions(df):
    extensions = set()
    for col in df.columns:
        for single_key in col.split(':'):
            for ext in XESExtension:
                if single_key == ext.prefix:
                    extensions.add(ext)
    return extensions


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
    events = []
    for trace in log:
        for event in trace:
            new_event = deepcopy(event) if enable_deepcopy else event
            if include_case_attributes:
                for key, value in trace.attributes.items():
                    new_event[case_attribute_prefix + key] = value
            # fix 14/02/2019: since the XES standard does not force to specify a case ID, when event log->event stream
            # conversion is done, the possibility to get back the original event log is lost
            if pmutil.CASE_ATTRIBUTE_GLUE not in new_event:
                new_event[pmutil.CASE_ATTRIBUTE_GLUE] = str(hash(trace))
            events.append(new_event)
    return log_instance.EventStream(events, attributes=log.attributes, classifiers=log.classifiers,
                                    omni_present=log.omni_present, extensions=log.extensions)

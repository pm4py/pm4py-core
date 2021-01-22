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
    INCLUDE_CASE_ATTRIBUTES = "include_case_attributes"
    COMPRESS = "compress"


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
            typ_k = type(event[k])
            if typ_k is pandas._libs.tslibs.nattype.NaTType:
                del event[k]
                continue
            elif (typ_k is float or typ_k is int) and math.isnan(event[k]):
                del event[k]
                continue
            elif event[k] is None:
                del event[k]
                continue
    return list_events


def __compress(list_events):
    """
    Compress a list of events,
    using one instantiation for the same key/value.

    Parameters
    --------------
    list_events
        List of events of the stream

    Returns
    --------------
    :param list_events:
    :return:
    """
    compress_dict = {}
    i = 0
    while i < len(list_events):
        # create a new event where keys and values are compressed
        comp_ev = {}
        for k, v in list_events[i].items():
            # check if the key has already been instantiated.
            # in that case, use the current instantiation.
            if k not in compress_dict:
                compress_dict[k] = k
            else:
                k = compress_dict[k]
            # check if the value has already been instantiated.
            # in that case, use the current instantiation
            if v not in compress_dict:
                compress_dict[v] = v
            else:
                v = compress_dict[v]
            # saves the compressed keys and values in the dictionary
            comp_ev[k] = v
        list_events[i] = comp_ev
        i = i + 1
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
    enable_deepcopy = exec_utils.get_param_value(Parameters.DEEP_COPY, parameters, True)
    include_case_attributes = exec_utils.get_param_value(Parameters.INCLUDE_CASE_ATTRIBUTES, parameters, True)
    compress = exec_utils.get_param_value(Parameters.COMPRESS, parameters, True)

    if pkgutil.find_loader("pandas"):
        import pandas
        if isinstance(log, pandas.DataFrame):
            extensions = __detect_extensions(log)
            list_events = pandas_utils.to_dict_records(log)
            if stream_post_processing:
                list_events = __postprocess_stream(list_events)
            if compress:
                list_events = __compress(list_events)
            for i in range(len(list_events)):
                list_events[i] = Event(list_events[i])
            log = log_instance.EventStream(list_events, attributes={'origin': 'csv'})
            for ex in extensions:
                log.extensions[ex.name] = {
                    xes_constants.KEY_PREFIX: ex.prefix,
                    xes_constants.KEY_URI: ex.uri}
    if isinstance(log, EventLog):
        return __transform_event_log_to_event_stream(log, include_case_attributes=include_case_attributes,
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

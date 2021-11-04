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

from typing import Dict

from pm4py.objects.log.obj import EventLog
from pm4py.util import xes_constants as xes
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY
from pm4py.util.regex import SharedObj, get_new_char


def get_encoded_trace(trace, mapping, parameters=None):
    """
    Gets the encoding of the provided trace

    Parameters
    -------------
    trace
        Trace of the event log
    mapping
        Mapping (activity to symbol)

    Returns
    -------------
    trace_str
        Trace string
    """
    if parameters is None:
        parameters = {}

    activity_key = parameters[
        PARAMETER_CONSTANT_ACTIVITY_KEY] if PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY

    trace_str = "".join([mapping[x[activity_key]] for x in trace if x[activity_key] in mapping])

    return trace_str


def get_encoded_log(log, mapping, parameters=None):
    """
    Gets the encoding of the provided log

    Parameters
    -------------
    log
        Event log
    mapping
        Mapping (activity to symbol)

    Returns
    -------------
    list_str
        List of encoded strings
    """
    if parameters is None:
        parameters = {}

    list_str = list()

    for trace in log:
        list_str.append(get_encoded_trace(trace, mapping, parameters=parameters))

    return list_str


def form_encoding_dictio_from_log(log, parameters=None):
    """
    Forms the encoding dictionary from the current log

    Parameters
    -------------
    log
        Event log
    parameters
        Parameters of the algorithm

    Returns
    -------------
    encoding_dictio
        Encoding dictionary
    """
    from pm4py.statistics.attributes.log import get as attributes_get

    if parameters is None:
        parameters = {}

    activity_key = parameters[
        PARAMETER_CONSTANT_ACTIVITY_KEY] if PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY

    shared_obj = SharedObj()

    activities = attributes_get.get_attribute_values(log, activity_key, parameters=parameters)

    mapping = {}

    for act in activities:
        get_new_char(act, shared_obj)
        mapping[act] = shared_obj.mapping_dictio[act]

    return mapping


def form_encoding_dictio_from_two_logs(log1: EventLog, log2: EventLog, parameters=None) -> \
Dict[str, str]:
    """
    Forms the encoding dictionary from a couple of logs

    Parameters
    ----------------
    log1
        First log
    log2
        Second log
    parameters
        Parameters of the algorithm

    Returns
    ----------------
    encoding_dictio
        Encoding dictionary
    """
    from pm4py.statistics.attributes.log import get as attributes_get

    if parameters is None:
        parameters = {}

    activity_key = parameters[
        PARAMETER_CONSTANT_ACTIVITY_KEY] if PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY

    shared_obj = SharedObj()

    activities_log_1 = attributes_get.get_attribute_values(log1, activity_key, parameters=parameters)
    activities_log_2 = attributes_get.get_attribute_values(log2, activity_key, parameters=parameters)

    mapping = {}

    for act in activities_log_1:
        if act not in mapping:
            get_new_char(act, shared_obj)
            mapping[act] = shared_obj.mapping_dictio[act]

    for act in activities_log_2:
        if act not in mapping:
            get_new_char(act, shared_obj)
            mapping[act] = shared_obj.mapping_dictio[act]

    return mapping

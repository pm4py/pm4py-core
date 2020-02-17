from pm4py.statistics.attributes.log import get as attributes_get
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY
from pm4py.util.regex import SharedObj, get_new_char
from pm4py.util import xes_constants as xes


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

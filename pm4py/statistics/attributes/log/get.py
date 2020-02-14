from pm4py.statistics.attributes.common import get as attributes_common
from pm4py.objects.conversion.log import factory as log_conv_fact
from pm4py.objects.log.log import EventLog
from pm4py.util import xes_constants as xes
from pm4py.util.xes_constants import DEFAULT_TIMESTAMP_KEY

DEFAULT_MAX_CASES_FOR_ATTR_SELECTION = 50


def get_all_trace_attributes_from_log(log):
    """
    Get all trace attributes from the log

    Parameters
    ------------
    log
        Log

    Returns
    ------------
    all_attributes
        All trace attributes from the log
    """
    all_attributes = set()
    for trace in log:
        all_attributes = all_attributes.union(set(trace.attributes.keys()))
    if xes.DEFAULT_TRACEID_KEY in all_attributes:
        all_attributes.remove(xes.DEFAULT_TRACEID_KEY)
    return all_attributes


def get_all_event_attributes_from_log(log):
    """
    Get all events attributes from the log

    Parameters
    -------------
    log
        Log

    Returns
    -------------
    all_attributes
        All trace attributes from the log
    """
    all_attributes = set()
    for trace in log:
        for event in trace:
            all_attributes = all_attributes.union(set(event.keys()))
    if xes.DEFAULT_TRANSITION_KEY in all_attributes:
        all_attributes.remove(xes.DEFAULT_TRANSITION_KEY)
    return all_attributes


def get_attribute_values(log, attribute_key, parameters=None):
    """
    Get the attribute values of the log for the specified attribute along with their count

    Parameters
    ----------
    log
        Log
    attribute_key
        Attribute for which we would like to know the values along with their count
    parameters
        Possible parameters of the algorithm

    Returns
    ----------
    attributes
        Dictionary of attributes associated with their count
    """
    if parameters is None:
        parameters = {}

    attributes = {}

    for trace in log:
        for event in trace:
            if attribute_key in event:
                attribute = event[attribute_key]
                if attribute not in attributes:
                    attributes[attribute] = 0
                attributes[attribute] = attributes[attribute] + 1

    return attributes


def get_trace_attribute_values(log, attribute_key, parameters=None):
    """
    Get the attribute values of the log for the specified attribute along with their count

    Parameters
    ------------
    log
        Log
    attribute_key
        Attribute for which we wish to get the values along with their count
    parameters
        Possible parameters of the algorithm

    Returns
    ------------
    attributes
        Dictionary of attributes associated with their count
    """
    if parameters is None:
        parameters = {}

    attributes = {}

    for trace in log:
        if attribute_key in trace.attributes:
            attribute = trace.attributes[attribute_key]
            if attribute not in attributes:
                attributes[attribute] = 0
            attributes[attribute] = attributes[attribute] + 1

    return attributes


def get_kde_numeric_attribute(log, attribute, parameters=None):
    """
    Gets the KDE estimation for the distribution of a numeric attribute values

    Parameters
    -------------
    log
        Event stream object (if log, is converted)
    attribute
        Numeric attribute to analyse
    parameters
        Possible parameters of the algorithm, including:
            graph_points -> number of points to include in the graph


    Returns
    --------------
    x

        X-axis values to represent
    y
        Y-axis values to represent
    """

    if type(log) is EventLog:
        event_log = log_conv_fact.apply(log, variant=log_conv_fact.TO_EVENT_STREAM)
    else:
        event_log = log

    values = [event[attribute] for event in event_log if attribute in event]

    return attributes_common.get_kde_numeric_attribute(values, parameters=parameters)


def get_kde_numeric_attribute_json(log, attribute, parameters=None):
    """
    Gets the KDE estimation for the distribution of a numeric attribute values
    (expressed as JSON)

    Parameters
    -------------
    log
        Event log object (if log, is converted)
    attribute
        Numeric attribute to analyse
    parameters
        Possible parameters of the algorithm, including:
            graph_points -> number of points to include in the graph


    Returns
    --------------
    x
        X-axis values to represent
    y
        Y-axis values to represent
    """

    if type(log) is EventLog:
        event_log = log_conv_fact.apply(log, variant=log_conv_fact.TO_EVENT_STREAM)
    else:
        event_log = log

    values = [event[attribute] for event in event_log if attribute in event]

    return attributes_common.get_kde_numeric_attribute_json(values, parameters=parameters)


def get_kde_date_attribute(log, attribute=DEFAULT_TIMESTAMP_KEY, parameters=None):
    """
    Gets the KDE estimation for the distribution of a date attribute values

    Parameters
    -------------
    log
        Event stream object (if log, is converted)
    attribute
        Date attribute to analyse
    parameters
        Possible parameters of the algorithm, including:
            graph_points -> number of points to include in the graph


    Returns
    --------------
    x
        X-axis values to represent
    y
        Y-axis values to represent
    """

    if type(log) is EventLog:
        event_log = log_conv_fact.apply(log, variant=log_conv_fact.TO_EVENT_STREAM)
    else:
        event_log = log

    values = [event[attribute].replace(tzinfo=None) for event in event_log if attribute in event]

    return attributes_common.get_kde_date_attribute(values, parameters=parameters)


def get_kde_date_attribute_json(log, attribute=DEFAULT_TIMESTAMP_KEY, parameters=None):
    """
    Gets the KDE estimation for the distribution of a date attribute values
    (expressed as JSON)

    Parameters
    -------------
    log
        Event stream object (if log, is converted)
    attribute
        Date attribute to analyse
    parameters
        Possible parameters of the algorithm, including:
            graph_points -> number of points to include in the graph


    Returns
    --------------
    x
        X-axis values to represent
    y
        Y-axis values to represent
    """

    if type(log) is EventLog:
        event_log = log_conv_fact.apply(log, variant=log_conv_fact.TO_EVENT_STREAM)
    else:
        event_log = log

    values = [event[attribute].replace(tzinfo=None) for event in event_log if attribute in event]

    return attributes_common.get_kde_date_attribute_json(values, parameters=parameters)

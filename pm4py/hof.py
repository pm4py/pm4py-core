import warnings
from typing import Callable, Any, Union

from pm4py.objects.log import obj as log_inst
import pandas as pd
from pm4py.objects.log.obj import EventLog, EventStream
from pm4py.utils import __event_log_deprecation_warning
import deprecation


@deprecation.deprecated("2.3.0", "3.0.0", details="the EventLog class will be removed in a future release.")
def filter_log(f: Callable[[Any], bool], log: log_inst.EventLog) -> Union[log_inst.EventLog, log_inst.EventStream]:
    """
    Filters the log according to a given (lambda) function.

    Parameters
    ----------
    f
        function that specifies the filter criterion, may be a lambda
    log
        event log; either EventLog or EventStream Object

    Returns
    -------
    log
        filtered event log if object provided is correct; original log if not correct

    """
    # Variant that is Pandas native: NO
    # Unit test: YES
    __event_log_deprecation_warning(log)

    if isinstance(log, log_inst.EventLog):
        return log_inst.EventLog(list(filter(f, log)), attributes=log.attributes, classifiers=log.classifiers,
                                 omni_present=log.omni_present, extensions=log.extensions, properties=log.properties)
    elif isinstance(log, log_inst.EventStream):
        return log_inst.EventStream(list(filter(f, log)), attributes=log.attributes, classifiers=log.classifiers,
                                    omni_present=log.omni_present, extensions=log.extensions, properties=log.properties)
    else:
        warnings.warn('input log object not of appropriate type, filter() not applied')
        return log


def filter_trace(f: Callable[[Any], bool], trace: log_inst.Trace) -> log_inst.Trace:
    """
    Filters the trace according to a given (lambda) function.

    Parameters
    ----------
    f
        function that specifies the filter criterion, may be a lambda
    trace
        trace; PM4Py trace object

    Returns
    -------
    trace
        filtered trace if object provided is correct; original log if not correct
    """
    # Variant that is Pandas native: NO
    # Unit test: YES
    __event_log_deprecation_warning(trace)

    if isinstance(trace, log_inst.Trace):
        return log_inst.Trace(list(filter(f, trace)), attributes=trace.attributes)
    else:
        warnings.warn('input trace object is not of the appropriate type, filter() not applied')


@deprecation.deprecated("2.3.0", "3.0.0", details="the EventLog class will be removed in a future release.")
def sort_log(log: log_inst.EventLog, key, reverse: bool = False) -> Union[log_inst.EventLog, log_inst.EventStream]:
    """
    Sorts the event log according to a given key.

    Parameters
    ----------
    log
        event log object; either EventLog or EventStream
    key
        sorting key
    reverse
        indicates whether sorting should be reversed or not

    Returns
    -------
        sorted event log if object provided is correct; original log if not correct
    """
    # Variant that is Pandas native: NO
    # Unit test: YES
    __event_log_deprecation_warning(log)

    if isinstance(log, log_inst.EventLog):
        return log_inst.EventLog(sorted(log, key=key, reverse=reverse), attributes=log.attributes,
                                 classifiers=log.classifiers, omni_present=log.omni_present, extensions=log.extensions, properties=log.properties)
    elif isinstance(log, log_inst.EventStream):
        return log_inst.EventStream(sorted(log, key=key, reverse=reverse), attributes=log.attributes,
                                    classifiers=log.classifiers,
                                    omni_present=log.omni_present, extensions=log.extensions, properties=log.properties)
    else:
        warnings.warn('input log object not of appropriate type, sorted() not applied')
        return log


@deprecation.deprecated("2.3.0", "3.0.0", details="the EventLog class will be removed in a future release.")
def sort_trace(trace: log_inst.Trace, key, reverse: bool = False) -> log_inst.Trace:
    """

    Parameters
    ----------
    trace
        input trace
    key
        sorting key
    reverse
        indicate whether sorting should be reversed (default False)

    Returns
    -------
        sorted trace if object provided is correct; original log if not correct
    """
    # Variant that is Pandas native: NO
    # Unit test: YES
    __event_log_deprecation_warning(trace)

    if isinstance(trace, log_inst.Trace):
        return log_inst.Trace(sorted(trace, key=key, reverse=reverse))
    else:
        warnings.warn('input trace object not of appropriate type, sorted() not applied')
        return trace

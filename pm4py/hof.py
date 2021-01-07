import warnings

from pm4py.objects.log import log as log_inst


def filter_log(f, log):
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
    if isinstance(log, log_inst.EventLog):
        return log_inst.EventLog(list(filter(f, log)), attributes=log.attributes, classifiers=log.classifiers,
                                 omni_present=log.omni_present, extensions=log.extensions)
    elif isinstance(log, log_inst.EventStream):
        return log_inst.EventStream(list(filter(f, log)), attributes=log.attributes, classifiers=log.classifiers,
                                    omni_present=log.omni_present, extensions=log.extensions)
    else:
        warnings.warn('input log object not of appropriate type, filter() not applied')
        return log


def filter_trace(f, trace):
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
    if isinstance(trace, log_inst.Trace):
        return log_inst.Trace(list(filter(f, trace)), attributes=trace.attributes)
    else:
        warnings.warn('input trace object is not of the appropriate type, filter() not applied')


def sort_log(log, key, reverse=False):
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
    if isinstance(log, log_inst.EventLog):
        return log_inst.EventLog(sorted(log, key=key, reverse=reverse), attributes=log.attributes,
                                 classifiers=log.classifiers, omni_present=log.omni_present, extensions=log.extensions)
    elif isinstance(log, log_inst.EventStream):
        return log_inst.EventStream(sorted(log, key=key, reverse=reverse), attributes=log.attributes,
                                    classifiers=log.classifiers,
                                    omni_present=log.omni_present, extensions=log.extensions)
    else:
        warnings.warn('input log object not of appropriate type, sorted() not applied')
        return log


def sort_trace(trace, key, reverse=False):
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
    if isinstance(trace, log_inst.Trace):
        return log_inst.Trace(sorted(trace, key=key, reverse=reverse))
    else:
        warnings.warn('input trace object not of appropriate type, sorted() not applied')
        return trace

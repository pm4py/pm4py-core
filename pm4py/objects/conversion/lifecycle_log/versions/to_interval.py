def apply(log, parameters=None):
    """
    Converts a log to interval format (e.g. an event has two timestamps)
    from lifecycle format (an event has only a timestamp, and a transition lifecycle)

    Parameters
    -------------
    log
        Log (expressed in the lifecycle format)
    parameters
        Possible parameters of the method (activity, timestamp key, start timestamp key, transition ...)

    Returns
    -------------
    log
        Interval event log
    """
    if parameters is None:
        parameters = {}

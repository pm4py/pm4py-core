def apply(log, parameters=None):
    """
    Converts a log from interval format (e.g. an event has two timestamps)
    to lifecycle format (an event has only a timestamp, and a transition lifecycle)

    Parameters
    -------------
    log
        Log (expressed in the interval format)
    parameters
        Possible parameters of the method (activity, timestamp key, start timestamp key, transition ...)

    Returns
    -------------
    log
        Lifecycle event log
    """
    if parameters is None:
        parameters = {}

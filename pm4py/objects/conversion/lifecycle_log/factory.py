from pm4py.objects.conversion.lifecycle_log.versions import to_interval, to_lifecycle

TO_INTERVAL = "to_interval"
TO_LIFECYCLE = "to_lifecycle"

VERSIONS = {TO_INTERVAL: to_interval.apply, TO_LIFECYCLE: to_lifecycle.apply}


def apply(log, variant=TO_LIFECYCLE, parameters=None):
    """
    Converts a log from lifecycle to interval, and viceversa

    Parameters
    ------------
    log
        Event log
    variant
        Variant of the conversion to apply, possible values: to_interval, to_lifecycle
    parameters
        Possible parameters of the method (activity, timestamp key, start timestamp key, transition ...)

    Returns
    ------------
    log
        Transformed event log
    """
    return VERSIONS[variant](log, parameters=parameters)

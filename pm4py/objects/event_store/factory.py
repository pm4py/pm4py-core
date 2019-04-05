from pm4py.objects.event_store.versions import sliding_window

SLIDING_WINDOW = "sliding_window"

VERSIONS = {SLIDING_WINDOW: sliding_window.SlidingWindowEventStore}


def apply(variant=SLIDING_WINDOW, parameters=None):
    """
    Create an event store of the given variant and with the given parameters

    Parameters
    ------------
    variant
        Variant
    parameters
        Parameters of the algorithm

    Returns
    ------------
    event_store
        Instance of an event store
    """
    return VERSIONS[variant](parameters=parameters)

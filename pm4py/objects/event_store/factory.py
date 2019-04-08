from pm4py.objects.event_store.versions import sliding_window, reservoir_sampling_event_based, reservoir_sampling_case_based

SLIDING_WINDOW = "sliding_window"
RESERVOIR_SAMPLING_EVENT_BASED = "reservoir_sampling_event_based"
RESERVOIR_SAMPLING_CASE_BASED = "reservoir_sampling_case_based"

VERSIONS = {SLIDING_WINDOW: sliding_window.SlidingWindowEventStore,
            RESERVOIR_SAMPLING_EVENT_BASED: reservoir_sampling_event_based.ReservoirSamplingEventBasedStore,
            RESERVOIR_SAMPLING_CASE_BASED: reservoir_sampling_case_based.ReservoirSamplingTraceBasedStore}


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

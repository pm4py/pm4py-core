from pm4py.objects.log.log import EventLog, Trace, Event
from pm4py.statistics.traces.pandas import case_statistics
from pm4py.objects.log.util import xes


def apply(df, parameters=None):
    """
    Convert a dataframe into a log containing 1 case per variant (only control-flow
    perspective is considered)

    Parameters
    -------------
    df
        Dataframe
    parameters
        Parameters of the algorithm

    Returns
    -------------
    log
        Event log
    """
    if parameters is None:
        parameters = {}
    variant_stats = case_statistics.get_variant_statistics(df, parameters=parameters)
    log = EventLog()
    for vd in variant_stats:
        variant = vd['variant'].split(",")
        trace = Trace()
        for activity in variant:
            event = Event()
            event[xes.DEFAULT_NAME_KEY] = activity
            trace.append(event)
        log.append(trace)
    return log

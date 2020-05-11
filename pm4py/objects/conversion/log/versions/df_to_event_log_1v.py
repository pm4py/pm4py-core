from pm4py.objects.log.log import EventLog, Trace, Event
from pm4py.util import xes_constants as xes
import deprecation

@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='conversion versions are deprecated; use conversion variants instead')
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
    from pm4py.statistics.traces.pandas import case_statistics

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

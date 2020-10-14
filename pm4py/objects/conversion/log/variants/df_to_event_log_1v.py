from pm4py.objects.log.log import EventLog, Trace, Event
from pm4py.util import xes_constants as xes
from pm4py.util import constants as pm4_constants


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
    activity_key = parameters[
        pm4_constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if pm4_constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY
    log = EventLog()
    for vd in variant_stats:
        variant = vd['variant'].split(",")
        trace = Trace()
        for activity in variant:
            event = Event()
            event[activity_key] = activity
            trace.append(event)
        log.append(trace)
    return log

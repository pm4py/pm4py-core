from pm4py.objects.log.log import EventLog, Trace, Event
from pm4py.util import xes_constants as xes
from pm4py.util import constants as pm4_constants

RETURN_VARIANTS = 'return_variants'


def apply(df, parameters=None):
    """
    Convert a dataframe into a log containing N case per variant (only control-flow
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

    return_variants = parameters[RETURN_VARIANTS] if RETURN_VARIANTS in parameters else False

    case_glue = parameters[
        pm4_constants.PARAMETER_CONSTANT_CASEID_KEY] if pm4_constants.PARAMETER_CONSTANT_CASEID_KEY in parameters else pm4_constants.CASE_CONCEPT_NAME

    variant_stats = case_statistics.get_variant_statistics(df, parameters=parameters)

    log = EventLog()
    all_variants_log = {}
    for vd in variant_stats:
        variant = vd['variant'].split(",")
        variant_count = vd[case_glue]
        trace = Trace()
        for activity in variant:
            event = Event()
            event[xes.DEFAULT_NAME_KEY] = activity
            trace.append(event)
        all_variants_log[vd['variant']] = []
        for i in range(variant_count):
            log.append(trace)
            all_variants_log[vd['variant']].append(len(log)-1)

    if return_variants:
        return log, all_variants_log

    return log

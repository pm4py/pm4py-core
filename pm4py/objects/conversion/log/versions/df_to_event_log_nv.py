from pm4py.objects.log.log import EventLog, Trace, Event
from pm4py.statistics.traces.pandas import case_statistics
from pm4py.objects.log.util import xes
from pm4py.util import constants as pm4_constants
from pm4py.algo.filtering.common.filtering_constants import CASE_CONCEPT_NAME

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
    if parameters is None:
        parameters = {}

    return_variants = parameters[RETURN_VARIANTS] if RETURN_VARIANTS in parameters else False

    case_glue = parameters[
        pm4_constants.PARAMETER_CONSTANT_CASEID_KEY] if pm4_constants.PARAMETER_CONSTANT_CASEID_KEY in parameters else CASE_CONCEPT_NAME

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

from pm4py.algo.discovery.dfg.variants import native, performance
from typing import Optional, Dict, Any
from pm4py.objects.log.obj import EventLog
from pm4py.objects.conversion.log import converter as log_converter


def apply(log: EventLog, activity: str, parameters: Optional[Dict[Any, Any]] = None) -> Dict[str, Any]:
    """
    Gets the time passed from each preceding activity

    Parameters
    -------------
    log
        Log
    activity
        Activity that we are considering
    parameters
        Possible parameters of the algorithm

    Returns
    -------------
    dictio
        Dictionary containing a 'pre' key with the
        list of aggregates times from each preceding activity to the given activity
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    dfg_frequency = native.native(log, parameters=parameters)
    dfg_performance = performance.performance(log, parameters=parameters)

    pre = []
    sum_perf_pre = 0.0
    sum_acti_pre = 0.0

    for entry in dfg_performance.keys():
        if entry[1] == activity:
            pre.append([entry[0], float(dfg_performance[entry]), int(dfg_frequency[entry])])
            sum_perf_pre = sum_perf_pre + float(dfg_performance[entry]) * float(dfg_frequency[entry])
            sum_acti_pre = sum_acti_pre + float(dfg_frequency[entry])

    perf_acti_pre = 0.0
    if sum_acti_pre > 0:
        perf_acti_pre = sum_perf_pre / sum_acti_pre

    return {"pre": pre, "pre_avg_perf": perf_acti_pre}

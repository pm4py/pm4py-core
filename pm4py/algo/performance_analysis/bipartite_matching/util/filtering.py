from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.util import constants
import pm4py.algo.performance_analysis.bipartite_matching.util.shared_variables as sv


def filter_traces(log):
    """
    Filter out the traces do not contain given variables

    Parameters
    ------------
    log
        Event log
    Returns
    ------------
    log
        Filtered event log
    """
    log_start = attributes_filter.apply(log, sv.start,
                                        parameters={constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY: sv.classifier,
                                                    "positive": True})

    log_end = attributes_filter.apply(log_start, sv.end,
                                      parameters={constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY: sv.classifier,
                                                  "positive": True})
    return log_end


def trim_log(log):
    """
    Filter out events not in the given variable list

    Parameters
    ------------
    log
        Event log
    Returns
    ------------
    log
        Filtered event log
    """
    log_trimmed = attributes_filter.apply_events(log, sv.start + sv.end,
                                                 parameters={constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY: sv.classifier,
                                                             "positive": True})
    return log_trimmed

from pm4py.util import constants
from pm4py.util import xes_constants as xes
from pm4py.objects.log.log import EventLog
from pm4py.objects.conversion.log import factory as log_conv_factory
from pm4py.objects.log.util import sorting
from pm4py.util.business_hours import BusinessHours


def insert_time_from_previous(log, parameters=None):
    """
    Inserts the time from the previous event, both in normal and business hours

    Parameters
    -------------
    log
        Event log
    parameters
        Parameters of the algorithm

    Returns
    -------------
    enriched_log
        Enriched log (with the time passed from the previous event)
    """
    if parameters is None:
        parameters = {}

    timestamp_key = parameters[
        constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] if constants.PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else xes.DEFAULT_TIMESTAMP_KEY
    worktiming = parameters["worktiming"] if "worktiming" in parameters else [7, 17]
    weekends = parameters["weekends"] if "weekends" in parameters else [6, 7]

    if not type(log) is EventLog:
        log = log_conv_factory.apply(log)

    log = sorting.sort_timestamp_log(log, timestamp_key)

    for trace in log:
        if trace:
            trace[0]["@@passed_time_from_previous"] = 0
            trace[0]["@@approx_bh_passed_time_from_previous"] = 0

            i = 1
            while i < len(trace):
                trace[i]["@@passed_time_from_previous"] = (trace[i][timestamp_key] - trace[i - 1][timestamp_key]).total_seconds()
                bh = BusinessHours(trace[i - 1][timestamp_key].replace(tzinfo=None),
                                   trace[i][timestamp_key].replace(tzinfo=None),
                                   worktiming=worktiming,
                                   weekends=weekends)
                trace[i]["@@approx_bh_passed_time_from_previous"] = bh.getseconds()
                i = i + 1

    return log

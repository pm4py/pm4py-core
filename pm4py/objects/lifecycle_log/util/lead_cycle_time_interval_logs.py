from pm4py.util import constants
from pm4py.objects.log.util import xes
from pm4py.objects.conversion.lifecycle_log import factory as lifecycle_factory
from pm4py.util import business_hours


def assign_lead_cycle_time(log, parameters=None):
    """
    Assigns the lead and cycle time to an interval log

    Parameters
    -------------
    log
        Interval log
    parameters
        Parameters of the algorithm, including: start_timestamp_key, timestamp_key,

    :param log:
    :param parameters:
    :return:
    """
    if parameters is None:
        parameters = {}

    start_timestamp_key = parameters[
        constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY] if constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY in parameters else xes.DEFAULT_START_TIMESTAMP_KEY
    timestamp_key = parameters[
        constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] if constants.PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else xes.DEFAULT_TIMESTAMP_KEY
    worktiming = parameters["worktiming"] if "worktiming" in parameters else [7, 17]
    weekends = parameters["weekends"] if "weekends" in parameters else [6, 7]

    interval_log = lifecycle_factory.apply(log, variant=lifecycle_factory.TO_INTERVAL, parameters=parameters)

    for trace in interval_log:
        approx_partial_lead_time = 0
        approx_partial_cycle_time = 0
        approx_wasted_time = 0
        max_et = None
        max_et_seconds = 0
        for i in range(len(trace)):
            this_wasted_time = 0
            st = trace[i][start_timestamp_key]
            st_seconds = st.timestamp()
            et = trace[i][timestamp_key]
            et_seconds = et.timestamp()

            if max_et_seconds > 0 and st_seconds > max_et_seconds:
                bh_unworked = business_hours.BusinessHours(max_et.replace(tzinfo=None), st.replace(tzinfo=None),
                                                           worktiming=worktiming, weekends=weekends)
                unworked_sec = bh_unworked.getseconds()
                approx_partial_lead_time = approx_partial_lead_time + unworked_sec
                approx_wasted_time = approx_wasted_time + unworked_sec
                this_wasted_time = unworked_sec

            if st_seconds > max_et_seconds:
                bh = business_hours.BusinessHours(st.replace(tzinfo=None), et.replace(tzinfo=None),
                                                  worktiming=worktiming, weekends=weekends)
                approx_bh_duration = bh.getseconds()

                approx_partial_cycle_time = approx_partial_cycle_time + approx_bh_duration
                approx_partial_lead_time = approx_partial_lead_time + approx_bh_duration
            elif st_seconds < max_et_seconds and et_seconds > max_et_seconds:
                bh = business_hours.BusinessHours(max_et.replace(tzinfo=None), et.replace(tzinfo=None),
                                                  worktiming=worktiming, weekends=weekends)
                approx_bh_duration = bh.getseconds()

                approx_partial_cycle_time = approx_partial_cycle_time + approx_bh_duration
                approx_partial_lead_time = approx_partial_lead_time + approx_bh_duration

            if et_seconds > max_et_seconds:
                max_et_seconds = et_seconds
                max_et = et

            ratio_cycle_lead_time = 1
            if approx_partial_lead_time > 0:
                ratio_cycle_lead_time = approx_partial_cycle_time / approx_partial_lead_time

            trace[i]["@@approx_bh_partial_cycle_time"] = approx_partial_cycle_time
            trace[i]["@@approx_bh_partial_lead_time"] = approx_partial_lead_time
            trace[i]["@@approx_bh_overall_wasted_time"] = approx_wasted_time
            trace[i]["@@approx_bh_this_wasted_time"] = this_wasted_time
            trace[i]["@approx_bh_ratio_cycle_lead_time"] = ratio_cycle_lead_time

    return interval_log

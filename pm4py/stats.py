__doc__ = """
In this section, different statistics that could be computed on top of event logs are explained.

* Endpoints
    * `Start activities`_
    * `End activities`_
* Attributes
    * `Event attributes`_
    * `Case attributes`_
    * `Values for the event attributes`_
    * `Values for the case attributes`_
* `Variants`_
* Throughput Times
    * `All cases`_
    * `Specific case`_
* `Cycle Time`_
* Activity-specific statistics
    * `Activities rework`_
    * `Activities position summary`_

.. _Start activities: pm4py.html#pm4py.stats.get_start_activities
.. _End activities: pm4py.html#pm4py.stats.get_end_activities
.. _Event attributes: pm4py.html#pm4py.stats.get_event_attributes
.. _Case attributes: pm4py.html#pm4py.stats.get_trace_attributes
.. _Values for the event attributes: pm4py.html#pm4py.stats.get_event_attribute_values
.. _Values for the case attributes: pm4py.html#pm4py.stats.get_trace_attribute_values
.. _Variants: pm4py.html#pm4py.stats.get_variants_as_tuples
.. _All cases: pm4py.html#pm4py.stats.get_all_case_durations
.. _Specific case: pm4py.html#pm4py.stats.get_case_duration
.. _Cycle Time: pm4py.html#pm4py.stats.get_cycle_time
.. _Activities rework: pm4py.html#pm4py.stats.get_variants_as_tuples
.. _Activities position summary: pm4py.html#pm4py.stats.get_activity_position_summary

"""

from typing import Dict, Union, List, Tuple, Collection
from typing import Set, Optional
from collections import Counter

import pandas as pd

from pm4py.objects.log.obj import EventLog, Trace, EventStream
from pm4py.util.pandas_utils import check_is_pandas_dataframe, check_pandas_dataframe_columns, insert_ev_in_tr_index
from pm4py.utils import get_properties, __event_log_deprecation_warning
from pm4py.util import xes_constants, constants
from copy import copy
from pm4py.objects.log.pandas_log_wrapper import PandasLogWrapper
import deprecation


def get_start_activities(log: Union[EventLog, pd.DataFrame], activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> Dict[str, int]:
    """
    Returns the start activities from a log object

    Parameters
    ---------------
    log
        Log object
    activity_key
        attribute to be used for the activity
    timestamp_key
        attribute to be used for the timestamp
    case_id_key
        attribute to be used as case identifier

    Returns
    ---------------
    start_activities
        Dictionary of start activities along with their count
    """
    # Variant that is Pandas native: YES
    # Unit test: YES
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        from pm4py.statistics.start_activities.pandas import get
        return get.get_start_activities(log, parameters=properties)
    else:
        from pm4py.statistics.start_activities.log import get
        return get.get_start_activities(log, parameters=properties)


def get_end_activities(log: Union[EventLog, pd.DataFrame], activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> Dict[str, int]:
    """
    Returns the end activities of a log

    Parameters
    ---------------
    log
        Lob object
    activity_key
        attribute to be used for the activity
    timestamp_key
        attribute to be used for the timestamp
    case_id_key
        attribute to be used as case identifier

    Returns
    ---------------
    end_activities
        Dictionary of end activities along with their count
    """
    # Variant that is Pandas native: YES
    # Unit test: YES
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        from pm4py.statistics.end_activities.pandas import get
        return get.get_end_activities(log, parameters=properties)
    else:
        from pm4py.statistics.end_activities.log import get
        return get.get_end_activities(log, parameters=properties)


def get_event_attributes(log: Union[EventLog, pd.DataFrame]) -> List[str]:
    """
    Returns the attributes at the event level of the log

    Parameters
    ---------------
    log
        Log object

    Returns
    ---------------
    attributes_list
        List of attributes contained in the log
    """
    # Variant that is Pandas native: YES
    # Unit test: YES
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        return list(log.columns)
    else:
        from pm4py.statistics.attributes.log import get
        return list(get.get_all_event_attributes_from_log(log))


def get_trace_attributes(log: Union[EventLog, pd.DataFrame]) -> List[str]:
    """
    Gets the attributes at the trace level of a log object

    Parameters
    ----------------
    log
        Log object

    Returns
    ---------------
    trace_attributes_list
        List of attributes at the trace level
    """
    # Variant that is Pandas native: YES
    # Unit test: YES
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    from pm4py.util import constants
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        return [x for x in list(log.columns) if x.startswith(constants.CASE_ATTRIBUTE_PREFIX)]
    else:
        from pm4py.statistics.attributes.log import get
        return list(get.get_all_trace_attributes_from_log(log))


def get_event_attribute_values(log: Union[EventLog, pd.DataFrame], attribute: str, count_once_per_case=False, case_id_key: str = "case:concept:name") -> Dict[str, int]:
    """
    Returns the values for a specified attribute

    Parameters
    ---------------
    log
        Log object
    attribute
        Attribute
    count_once_per_case
        If True, consider only an occurrence of the given attribute value inside a case
        (if there are multiple events sharing the same attribute value, count only 1 occurrence)
    case_id_key
        attribute to be used as case identifier

    Returns
    ---------------
    attribute_values
        Dictionary of values along with their count
    """
    # Variant that is Pandas native: YES
    # Unit test: YES
    if type(log) not in [pd.DataFrame, EventLog, EventStream, PandasLogWrapper]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    parameters = get_properties(log, case_id_key=case_id_key)
    parameters["keep_once_per_case"] = count_once_per_case
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        from pm4py.statistics.attributes.pandas import get
        return get.get_attribute_values(log, attribute, parameters=parameters)
    else:
        from pm4py.statistics.attributes.log import get
        return get.get_attribute_values(log, attribute, parameters=parameters)


def get_trace_attribute_values(log: Union[EventLog, pd.DataFrame], attribute: str, case_id_key: str = "case:concept:name") -> Dict[str, int]:
    """
    Returns the values for a specified trace attribute

    Parameters
    ---------------
    log
        Log object
    attribute
        Attribute
    case_id_key
        attribute to be used as case identifier

    Returns
    ---------------
    attribute_values
        Dictionary of values along with their count
    """
    # Variant that is Pandas native: YES
    # Unit test: YES
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    parameters = get_properties(log, case_id_key=case_id_key)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        from pm4py.statistics.attributes.pandas import get
        return get.get_attribute_values(log, attribute, parameters=parameters)
    else:
        from pm4py.statistics.attributes.log import get
        return get.get_trace_attribute_values(log, attribute, parameters=parameters)


def get_variants(log: Union[EventLog, pd.DataFrame], activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> Dict[str, List[Trace]]:
    """
    Gets the variants from the log

    Parameters
    --------------
    log
        Event log
    activity_key
        attribute to be used for the activity
    timestamp_key
        attribute to be used for the timestamp
    case_id_key
        attribute to be used as case identifier

    Returns
    --------------
    variants
        Dictionary of variants along with their count
    """
    return get_variants_as_tuples(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)


def get_variants_as_tuples(log: Union[EventLog, pd.DataFrame], activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> Dict[Tuple[str], List[Trace]]:
    """
    Gets the variants from the log
    (where the keys are tuples and not strings)

    Parameters
    --------------
    log
        Event log
    activity_key
        attribute to be used for the activity
    timestamp_key
        attribute to be used for the timestamp
    case_id_key
        attribute to be used as case identifier

    Returns
    --------------
    variants
        Dictionary of variants along with their count
    """
    # Variant that is Pandas native: YES
    # Unit test: YES
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        from pm4py.statistics.variants.pandas import get
        return get.get_variants_count(log, parameters=properties)
    else:
        from pm4py.statistics.variants.log import get
        return get.get_variants(log, parameters=properties)


def get_minimum_self_distances(log: Union[EventLog, pd.DataFrame], activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> Dict[str, int]:
    '''
    This algorithm computes the minimum self-distance for each activity observed in an event log.
    The self distance of a in <a> is infinity, of a in <a,a> is 0, in <a,b,a> is 1, etc.
    The minimum self distance is the minimal observed self distance value in the event log.

    Parameters
    ----------
    log
        event log (either pandas.DataFrame, EventLog or EventStream)
    activity_key
        attribute to be used for the activity
    timestamp_key
        attribute to be used for the timestamp
    case_id_key
        attribute to be used as case identifier

    Returns
    -------
        dict mapping an activity to its self-distance, if it exists, otherwise it is not part of the dict.
    '''
    # Variant that is Pandas native: YES
    # Unit test: YES
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    from pm4py.algo.discovery.minimum_self_distance import algorithm as msd_algo
    return msd_algo.apply(log, parameters=properties)


def get_minimum_self_distance_witnesses(log: Union[EventLog, pd.DataFrame], activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> Dict[str, Set[str]]:
    '''
        This function derives the minimum self distance witnesses.
        The self distance of a in <a> is infinity, of a in <a,a> is 0, in <a,b,a> is 1, etc.
        The minimum self distance is the minimal observed self distance value in the event log.
        A 'witness' is an activity that witnesses the minimum self distance.
        For example, if the minimum self distance of activity a in some log L is 2, then,
        if trace <a,b,c,a> is in log L, b and c are a witness of a.

        Parameters
        ----------
        log
            Event Log to use
        activity_key
            attribute to be used for the activity
        timestamp_key
            attribute to be used for the timestamp
        case_id_key
            attribute to be used as case identifier

        Returns
        -------
        Dictionary mapping each activity to a set of witnesses.

        '''
    # Variant that is Pandas native: YES
    # Unit test: YES
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    from pm4py.algo.discovery.minimum_self_distance import algorithm as msd_algo
    from pm4py.algo.discovery.minimum_self_distance import utils as msdw_algo
    return msdw_algo.derive_msd_witnesses(log, msd_algo.apply(log, parameters=get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)))


def get_case_arrival_average(log: Union[EventLog, pd.DataFrame], activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> float:
    """
    Gets the average difference between the start times of two consecutive cases

    Parameters
    ---------------
    log
        Log object
    activity_key
        attribute to be used for the activity
    timestamp_key
        attribute to be used for the timestamp
    case_id_key
        attribute to be used as case identifier

    Returns
    ---------------
    case_arrival_average
        Average difference between the start times of two consecutive cases
    """
    # Variant that is Pandas native: YES
    # Unit test: YES
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        from pm4py.statistics.traces.generic.pandas import case_arrival
        return case_arrival.get_case_arrival_avg(log, parameters=properties)
    else:
        from pm4py.statistics.traces.generic.log import case_arrival
        return case_arrival.get_case_arrival_avg(log, parameters=properties)


def get_rework_cases_per_activity(log: Union[EventLog, pd.DataFrame], activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> Dict[str, int]:
    """
    Find out for which activities of the log the rework (more than one occurrence in the trace for the activity)
    occurs.
    The output is a dictionary associating to each of the aforementioned activities
    the number of cases for which the rework occurred.

    Parameters
    ------------------
    log
        Log object
    activity_key
        attribute to be used for the activity
    timestamp_key
        attribute to be used for the timestamp
    case_id_key
        attribute to be used as case identifier

    Returns
    ------------------
    rework_dictionary
        Dictionary associating to each of the aforementioned activities the number of cases for which the rework
        occurred.
    """
    # Variant that is Pandas native: YES
    # Unit test: YES
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        from pm4py.statistics.rework.pandas import get as rework_get
        return rework_get.apply(log, parameters=properties)
    else:
        from pm4py.statistics.rework.log import get as rework_get
        return rework_get.apply(log, parameters=properties)


@deprecation.deprecated("2.3.0", "3.0.0", details="the get_case_overlap function will be removed in a future release.")
def get_case_overlap(log: Union[EventLog, pd.DataFrame], activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> List[int]:
    """
    Associates to each case in the log the number of cases concurrently open

    Parameters
    ------------------
    log
        Log object
    activity_key
        attribute to be used for the activity
    timestamp_key
        attribute to be used for the timestamp
    case_id_key
        attribute to be used as case identifier

    Returns
    ------------------
    overlap_list
        List that for each case (identified by its index in the log) tells how many other cases
        are concurrently open.
    """
    # Variant that is Pandas native: YES
    # Unit test: YES
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        from pm4py.statistics.overlap.cases.pandas import get as cases_overlap
        return cases_overlap.apply(log, parameters=properties)
    else:
        from pm4py.statistics.overlap.cases.log import get as cases_overlap
        return cases_overlap.apply(log, parameters=properties)


def get_cycle_time(log: Union[EventLog, pd.DataFrame], activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> float:
    """
    Calculates the cycle time of the event log.

    The definition that has been followed is the one proposed in:
    https://www.presentationeze.com/presentations/lean-manufacturing-just-in-time/lean-manufacturing-just-in-time-full-details/process-cycle-time-analysis/calculate-cycle-time/#:~:text=Cycle%20time%20%3D%20Average%20time%20between,is%2024%20minutes%20on%20average.

    So:
    Cycle time  = Average time between completion of units.

    Example taken from the website:
    Consider a manufacturing facility, which is producing 100 units of product per 40 hour week.
    The average throughput rate is 1 unit per 0.4 hours, which is one unit every 24 minutes.
    Therefore the cycle time is 24 minutes on average.

    Parameters
    -----------------
    log
        Log object
    activity_key
        attribute to be used for the activity
    timestamp_key
        attribute to be used for the timestamp
    case_id_key
        attribute to be used as case identifier

    Returns
    -----------------
    cycle_time
        Cycle time (calculated with the aforementioned formula).
    """
    # Variant that is Pandas native: YES
    # Unit test: YES
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        from pm4py.statistics.traces.cycle_time.pandas import get as cycle_time
        return cycle_time.apply(log, parameters=properties)
    else:
        from pm4py.statistics.traces.cycle_time.log import get as cycle_time
        return cycle_time.apply(log, parameters=properties)


def get_all_case_durations(log: Union[EventLog, pd.DataFrame], business_hours: bool = False, worktiming: List[int] = [7, 17], weekends: List[int] = [6, 7], activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> List[float]:
    """
    Gets the durations of the cases in the event log

    Parameters
    ---------------
    log
        Event log
    business_hours
        Enables/disables the computation based on the business hours (default: False)
    worktiming
        (If the business hours are enabled) The hour range in which the resources of the log are working (default: 7 to 17)
    weekends
        (If the business hours are enabled) The weekends days (default: Saturday (6), Sunday (7))
    activity_key
        attribute to be used for the activity
    timestamp_key
        attribute to be used for the timestamp
    case_id_key
        attribute to be used as case identifier

    Returns
    ---------------
    durations
        Case durations (as list)
    """
    # Variant that is Pandas native: YES
    # Unit test: YES
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    properties["business_hours"] = business_hours
    properties["worktiming"] = worktiming
    properties["weekends"] = weekends
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        from pm4py.statistics.traces.generic.pandas import case_statistics
        cd = case_statistics.get_cases_description(log, parameters=properties)
        return sorted([x["caseDuration"] for x in cd.values()])
    else:
        from pm4py.statistics.traces.generic.log import case_statistics
        return case_statistics.get_all_case_durations(log, parameters=properties)


def get_case_duration(log: Union[EventLog, pd.DataFrame], case_id: str, business_hours: bool = False, worktiming: List[int] = [7, 17], weekends: List[int] = [6, 7], activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: Optional[str] = None) -> float:
    """
    Gets the duration of a specific case

    Parameters
    -------------------
    log
        Event log
    case_id
        Case identifier
    business_hours
        Enables/disables the computation based on the business hours (default: False)
    worktiming
        (If the business hours are enabled) The hour range in which the resources of the log are working (default: 7 to 17)
    weekends
        (If the business hours are enabled) The weekends days (default: Saturday (6), Sunday (7))
    activity_key
        attribute to be used for the activity
    timestamp_key
        attribute to be used for the timestamp
    case_id_key
        attribute to be used as case identifier

    Returns
    ------------------
    duration
        Duration of the given case
    """
    # Variant that is Pandas native: YES
    # Unit test: YES
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    properties["business_hours"] = business_hours
    properties["worktiming"] = worktiming
    properties["weekends"] = weekends
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        from pm4py.statistics.traces.generic.pandas import case_statistics
        cd = case_statistics.get_cases_description(log, parameters=properties)
        return cd[case_id]["caseDuration"]
    else:
        from pm4py.statistics.traces.generic.log import case_statistics
        cd = case_statistics.get_cases_description(log, parameters=properties)
        return cd[case_id]["caseDuration"]


def get_activity_position_summary(log: Union[EventLog, pd.DataFrame], activity: str, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> Dict[int, int]:
    """
    Given an event log, returns a dictionary which summarize the positions
    of the activities in the different cases of the event log.
    E.g., if an activity happens 1000 times in the position 1 (the second event of a case),
    and 500 times in the position 2 (the third event of a case), then the returned dictionary would be:
    {1: 1000, 2: 500}

    Parameters
    -----------------
    log
        Event log object / Pandas dataframe
    activity
        Activity to consider
    activity_key
        attribute to be used for the activity
    timestamp_key
        attribute to be used for the timestamp
    case_id_key
        attribute to be used as case identifier

    Returns
    -----------------
    pos_dict_summary
        Summary of the positions of the activity in the trace (e.g. {1: 1000, 2: 500})
    """
    # Variant that is Pandas native: YES
    # Unit test: YES
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    activity_key = properties[
        constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in properties else xes_constants.DEFAULT_NAME_KEY
    case_id_key = properties[
        constants.PARAMETER_CONSTANT_CASEID_KEY] if constants.PARAMETER_CONSTANT_CASEID_KEY in properties else constants.CASE_CONCEPT_NAME

    if check_is_pandas_dataframe(log):
        log = insert_ev_in_tr_index(log, case_id_key, "@@index_in_trace")
        ret = log[log[activity_key] == activity]["@@index_in_trace"].value_counts().to_dict()
        return ret
    else:
        ret = Counter()
        for trace in log:
            for i in range(len(trace)):
                this_act = trace[i][activity_key]
                if this_act == activity:
                    ret[i] += 1
        return dict(ret)

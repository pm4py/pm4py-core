'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
from datetime import datetime
from enum import Enum
from typing import Union, Optional, Dict, Any, Tuple

from pm4py.objects.conversion.log import converter
from pm4py.objects.log.obj import EventLog, Event
from pm4py.util import exec_utils, constants, xes_constants
from pm4py.algo.filtering.common.timestamp.timestamp_common import get_dt_from_string
from statistics import mean


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    RESOURCE_KEY = constants.PARAMETER_CONSTANT_RESOURCE_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY


def distinct_activities(log: EventLog, t1: Union[datetime, str], t2: Union[datetime, str], r: str,
                        parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> int:
    """
    Number of distinct activities done by a resource in a given time interval [t1, t2)

    Metric RBI 1.1 in Pika, Anastasiia, et al.
    "Mining resource profiles from event logs." ACM Transactions on Management Information Systems (TMIS) 8.1 (2017): 1-30.

    Parameters
    -----------------
    log
        Event log
    t1
        Left interval
    t2
        Right interval
    r
        Resource

    Returns
    -----------------
    distinct_activities
        Distinct activities
    """
    if parameters is None:
        parameters = {}

    log = converter.apply(log, variant=converter.Variants.TO_EVENT_STREAM, parameters={"deepcopy": False, "include_case_attributes": False})

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    resource_key = exec_utils.get_param_value(Parameters.RESOURCE_KEY, parameters, xes_constants.DEFAULT_RESOURCE_KEY)

    t1 = get_dt_from_string(t1)
    t2 = get_dt_from_string(t2)

    log = [x for x in log if t1 <= x[timestamp_key] < t2 and x[resource_key] == r]
    return len(set(x[activity_key] for x in log))


def activity_frequency(log: EventLog, t1: Union[datetime, str], t2: Union[datetime, str], r: str, a: str,
                       parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> float:
    """
    Fraction of completions of a given activity a, by a given resource r, during a given time slot, [t1, t2),
    with respect to the total number of activity completions by resource r during [t1, t2)

    Metric RBI 1.3 in Pika, Anastasiia, et al.
    "Mining resource profiles from event logs." ACM Transactions on Management Information Systems (TMIS) 8.1 (2017): 1-30.

    Parameters
    -----------------
    log
        Event log
    t1
        Left interval
    t2
        Right interval
    r
        Resource
    a
        Activity

    Returns
    ----------------
    metric
        Value of the metric
    """
    if parameters is None:
        parameters = {}

    log = converter.apply(log, variant=converter.Variants.TO_EVENT_STREAM, parameters={"deepcopy": False, "include_case_attributes": False})

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    resource_key = exec_utils.get_param_value(Parameters.RESOURCE_KEY, parameters, xes_constants.DEFAULT_RESOURCE_KEY)

    t1 = get_dt_from_string(t1)
    t2 = get_dt_from_string(t2)
    log = [x for x in log if t1 <= x[timestamp_key] < t2 and x[resource_key] == r]
    total = len(log)

    log = [x for x in log if x[activity_key] == a]
    activity_a = len(log)

    return float(activity_a) / float(total) if total > 0 else 0.0


def activity_completions(log: EventLog, t1: Union[datetime, str], t2: Union[datetime, str], r: str,
                         parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> int:
    """
    The number of activity instances completed by a given resource during a given time slot.

    Metric RBI 2.1 in Pika, Anastasiia, et al.
    "Mining resource profiles from event logs." ACM Transactions on Management Information Systems (TMIS) 8.1 (2017): 1-30.

    Parameters
    -----------------
    log
        Event log
    t1
        Left interval
    t2
        Right interval
    r
        Resource

    Returns
    ----------------
    metric
        Value of the metric
    """
    if parameters is None:
        parameters = {}

    log = converter.apply(log, variant=converter.Variants.TO_EVENT_STREAM, parameters={"deepcopy": False, "include_case_attributes": False})

    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    resource_key = exec_utils.get_param_value(Parameters.RESOURCE_KEY, parameters, xes_constants.DEFAULT_RESOURCE_KEY)

    t1 = get_dt_from_string(t1)
    t2 = get_dt_from_string(t2)
    log = [x for x in log if t1 <= x[timestamp_key] < t2 and x[resource_key] == r]
    total = len(log)

    return total


def case_completions(log: EventLog, t1: Union[datetime, str], t2: Union[datetime, str], r: str,
                     parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> int:
    """
    The number of cases completed during a given time slot in which a given resource was involved.

    Metric RBI 2.2 in Pika, Anastasiia, et al.
    "Mining resource profiles from event logs." ACM Transactions on Management Information Systems (TMIS) 8.1 (2017): 1-30.

    Parameters
    -----------------
    log
        Event log
    t1
        Left interval
    t2
        Right interval
    r
        Resource

    Returns
    ----------------
    metric
        Value of the metric
    """
    if parameters is None:
        parameters = {}

    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    resource_key = exec_utils.get_param_value(Parameters.RESOURCE_KEY, parameters, xes_constants.DEFAULT_RESOURCE_KEY)
    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, xes_constants.DEFAULT_TRACEID_KEY)

    t1 = get_dt_from_string(t1)
    t2 = get_dt_from_string(t2)

    last_eve = []
    stream = []
    for case in log:
        for i in range(len(case)):
            eve = Event({timestamp_key: case[i][timestamp_key], resource_key: case[i][resource_key],
                         case_id_key: case.attributes[case_id_key]})
            stream.append(eve)
            if i == len(case) - 1:
                last_eve.append(eve)

    last_eve = [x for x in last_eve if t1 <= x[timestamp_key] < t2]
    cases_last = set(x[case_id_key] for x in last_eve)

    stream = [x for x in stream if x[resource_key] == r]
    cases_res = set(x[case_id_key] for x in stream)

    return len(cases_last.intersection(cases_res))


def fraction_case_completions(log: EventLog, t1: Union[datetime, str], t2: Union[datetime, str], r: str,
                              parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> float:
    """
    The fraction of cases completed during a given time slot in which a given resource was involved with respect to the
    total number of cases completed during the time slot.

    Metric RBI 2.3 in Pika, Anastasiia, et al.
    "Mining resource profiles from event logs." ACM Transactions on Management Information Systems (TMIS) 8.1 (2017): 1-30.

    Parameters
    -----------------
    log
        Event log
    t1
        Left interval
    t2
        Right interval
    r
        Resource

    Returns
    ----------------
    metric
        Value of the metric
    """
    if parameters is None:
        parameters = {}

    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    resource_key = exec_utils.get_param_value(Parameters.RESOURCE_KEY, parameters, xes_constants.DEFAULT_RESOURCE_KEY)
    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, xes_constants.DEFAULT_TRACEID_KEY)

    t1 = get_dt_from_string(t1)
    t2 = get_dt_from_string(t2)

    last_eve = []
    stream = []
    for case in log:
        for i in range(len(case)):
            eve = Event({timestamp_key: case[i][timestamp_key], resource_key: case[i][resource_key],
                         case_id_key: case.attributes[case_id_key]})
            stream.append(eve)
            if i == len(case) - 1:
                last_eve.append(eve)

    last_eve = [x for x in last_eve if t1 <= x[timestamp_key] < t2]
    cases_last = set(x[case_id_key] for x in last_eve)

    stream = [x for x in stream if x[resource_key] == r]
    cases_res = set(x[case_id_key] for x in stream)

    q1 = float(len(cases_last.intersection(cases_res)))
    q2 = float(len(cases_last))

    return q1 / q2 if q2 > 0 else 0.0


def __insert_start_from_previous_event(log: EventLog, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> EventLog:
    """
    Inserts the start timestamp of an event set to the completion of the previous event in the case

    Parameters
    ---------------
    log
        interval log

    Returns
    ---------------
    log
        interval Log with the start timestamp for each event
    """
    if parameters is None:
        parameters = {}

    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    start_timestamp_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY, parameters,
                                                     xes_constants.DEFAULT_START_TIMESTAMP_KEY)

    for trace in log:
        for i in range(1, len(trace)):
            trace[i][start_timestamp_key] = trace[i-1][timestamp_key]
        trace[0][start_timestamp_key] = trace[0][timestamp_key]

    return log


def __compute_workload(log: EventLog, resource: Optional[str] = None, activity: Optional[str] = None,
                       parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Dict[Tuple, int]:
    """
    Computes the workload of resources/activities, corresponding to each event a number
    (number of concurring events)

    Parameters
    ---------------
    log
        event log
    resource
        (if provided) Resource on which we want to compute the workload
    activity
        (if provided) Activity on which we want to compute the workload

    Returns
    ---------------
    workload_dict
        Dictionary associating to each event the number of concurring events
    """
    if parameters is None:
        parameters = {}

    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    resource_key = exec_utils.get_param_value(Parameters.RESOURCE_KEY, parameters, xes_constants.DEFAULT_RESOURCE_KEY)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    start_timestamp_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY, parameters, None)

    from pm4py.objects.log.util import sorting
    log = sorting.sort_timestamp(log, timestamp_key)
    from pm4py.objects.log.util import interval_lifecycle
    log = interval_lifecycle.to_interval(log, parameters=parameters)
    if start_timestamp_key is None:
        log = __insert_start_from_previous_event(log, parameters=parameters)
        start_timestamp_key = xes_constants.DEFAULT_START_TIMESTAMP_KEY
    events = converter.apply(log, variant=converter.Variants.TO_EVENT_STREAM, parameters={"deepcopy": False, "include_case_attributes": False})
    if resource is not None:
        events = [x for x in events if x[resource_key] == resource]
    if activity is not None:
        events = [x for x in events if x[activity_key] == activity]
    events = [(x[start_timestamp_key].timestamp(), x[timestamp_key].timestamp(), x[resource_key], x[activity_key]) for x
              in events]
    events = sorted(events)
    from intervaltree import IntervalTree, Interval
    tree = IntervalTree()
    ev_map = {}
    k = 0.000001
    for ev in events:
        tree.add(Interval(ev[0], ev[1] + k))
    for ev in events:
        ev_map[ev] = len(tree[ev[0]:ev[1] + k])
    return ev_map


def average_workload(log: EventLog, t1: Union[datetime, str], t2: Union[datetime, str], r: str,
                     parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> float:
    """
    The average number of activities started by a given resource but not completed at a moment in time.

    Metric RBI 2.4 in Pika, Anastasiia, et al.
    "Mining resource profiles from event logs." ACM Transactions on Management Information Systems (TMIS) 8.1 (2017): 1-30.

    Parameters
    -----------------
    log
        Event log
    t1
        Left interval
    t2
        Right interval
    r
        Resource

    Returns
    ----------------
    metric
        Value of the metric
    """
    if parameters is None:
        parameters = {}

    t2 = get_dt_from_string(t2).timestamp()

    ev_dict = __compute_workload(log, resource=r, parameters=parameters)
    ev_dict = {x: y for x, y in ev_dict.items() if x[0] < t2 and x[1] >= t2}
    num = 0.0
    den = 0.0
    for ev in ev_dict:
        workload = ev_dict[ev]
        duration = ev[1] - ev[0]
        num += workload*duration
        den += duration
    return num/den if den > 0 else 0.0


def multitasking(log: EventLog, t1: Union[datetime, str], t2: Union[datetime, str], r: str,
                 parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> float:
    """
    The fraction of active time during which a given resource is involved in more than one activity with respect
    to the resource's active time.

    Metric RBI 3.1 in Pika, Anastasiia, et al.
    "Mining resource profiles from event logs." ACM Transactions on Management Information Systems (TMIS) 8.1 (2017): 1-30.

    Parameters
    -----------------
    log
        Event log
    t1
        Left interval
    t2
        Right interval
    r
        Resource

    Returns
    ----------------
    metric
        Value of the metric
    """
    if parameters is None:
        parameters = {}

    t1 = get_dt_from_string(t1).timestamp()
    t2 = get_dt_from_string(t2).timestamp()

    ev_dict = __compute_workload(log, resource=r, parameters=parameters)
    ev_dict = {x: y for x, y in ev_dict.items() if x[0] >= t1 and x[1] <= t2}
    num = 0.0
    den = 0.0
    for ev in ev_dict:
        workload = ev_dict[ev]
        duration = ev[1] - ev[0]
        if workload > 1:
            num += duration
        den += duration
    return num/den if den > 0 else 0.0


def average_duration_activity(log: EventLog, t1: Union[datetime, str], t2: Union[datetime, str], r: str, a: str,
                       parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> float:
    """
    The average duration of instances of a given activity completed during a given time slot by a given resource.

    Metric RBI 4.3 in Pika, Anastasiia, et al.
    "Mining resource profiles from event logs." ACM Transactions on Management Information Systems (TMIS) 8.1 (2017): 1-30.

    Parameters
    -----------------
    log
        Event log
    t1
        Left interval
    t2
        Right interval
    r
        Resource
    a
        Activity

    Returns
    ----------------
    metric
        Value of the metric
    """
    if parameters is None:
        parameters = {}

    t1 = get_dt_from_string(t1)
    t2 = get_dt_from_string(t2)

    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    resource_key = exec_utils.get_param_value(Parameters.RESOURCE_KEY, parameters, xes_constants.DEFAULT_RESOURCE_KEY)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    start_timestamp_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY, parameters, None)

    from pm4py.objects.log.util import sorting
    log = sorting.sort_timestamp(log, timestamp_key)
    from pm4py.objects.log.util import interval_lifecycle
    log = interval_lifecycle.to_interval(log, parameters=parameters)
    if start_timestamp_key is None:
        log = __insert_start_from_previous_event(log, parameters=parameters)
        start_timestamp_key = xes_constants.DEFAULT_START_TIMESTAMP_KEY

    log = converter.apply(log, variant=converter.Variants.TO_EVENT_STREAM, parameters={"deepcopy": False, "include_case_attributes": False})
    log = [x for x in log if x[resource_key] == r and x[activity_key] == a and x[timestamp_key] >= t1 and x[timestamp_key] < t2]

    return float(mean(x[timestamp_key].timestamp() - x[start_timestamp_key].timestamp() for x in log))


def average_case_duration(log: EventLog, t1: Union[datetime, str], t2: Union[datetime, str], r: str,
                          parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> float:
    """
    The average duration of cases completed during a given time slot in which a given resource was involved.

    Metric RBI 4.4 in Pika, Anastasiia, et al.
    "Mining resource profiles from event logs." ACM Transactions on Management Information Systems (TMIS) 8.1 (2017): 1-30.

    Parameters
    -----------------
    log
        Event log
    t1
        Left interval
    t2
        Right interval
    r
        Resource

    Returns
    ----------------
    metric
        Value of the metric
    """
    if parameters is None:
        parameters = {}

    resource_key = exec_utils.get_param_value(Parameters.RESOURCE_KEY, parameters, xes_constants.DEFAULT_RESOURCE_KEY)

    from pm4py.algo.filtering.log.attributes import attributes_filter
    parameters_filter = {attributes_filter.Parameters.ATTRIBUTE_KEY: resource_key}
    log = attributes_filter.apply(log, [r], parameters=parameters_filter)

    from pm4py.algo.filtering.log.timestamp import timestamp_filter
    log = timestamp_filter.filter_traces_intersecting(log, t1, t2, parameters=parameters)

    from pm4py.statistics.traces.generic.log import case_statistics
    cd = case_statistics.get_cases_description(log, parameters=parameters).values()
    return mean(x["caseDuration"] for x in cd)


def interaction_two_resources(log: EventLog, t1: Union[datetime, str], t2: Union[datetime, str], r1: str, r2: str,
                              parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> float:
    """
    The number of cases completed during a given time slot in which two given resources were involved.

    Metric RBI 5.1 in Pika, Anastasiia, et al.
    "Mining resource profiles from event logs." ACM Transactions on Management Information Systems (TMIS) 8.1 (2017): 1-30.

    Parameters
    -----------------
    log
        Event log
    t1
        Left interval
    t2
        Right interval
    r1
        Resource 1
    r2
        Resource 2

    Returns
    ----------------
    metric
        Value of the metric
    """
    if parameters is None:
        parameters = {}

    t1 = get_dt_from_string(t1)
    t2 = get_dt_from_string(t2)

    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    resource_key = exec_utils.get_param_value(Parameters.RESOURCE_KEY, parameters, xes_constants.DEFAULT_RESOURCE_KEY)

    from pm4py.algo.filtering.log.attributes import attributes_filter
    parameters_filter = {attributes_filter.Parameters.ATTRIBUTE_KEY: resource_key}
    log = attributes_filter.apply(log, [r1], parameters=parameters_filter)
    log = attributes_filter.apply(log, [r2], parameters=parameters_filter)
    red_log = EventLog()
    for trace in log:
        if trace:
            if t1 <= trace[-1][timestamp_key] < t2:
                red_log.append(trace)
    return len(red_log)


def social_position(log: EventLog, t1_0: Union[datetime, str], t2_0: Union[datetime, str], r: str,
                              parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> float:
    """
    The fraction of resources involved in the same cases with a given resource during a given time slot with
    respect to the total number of resources active during the time slot.

    Metric RBI 5.2 in Pika, Anastasiia, et al.
    "Mining resource profiles from event logs." ACM Transactions on Management Information Systems (TMIS) 8.1 (2017): 1-30.

    Parameters
    -----------------
    df
        Dataframe
    t1_0
        Left interval
    t2_0
        Right interval
    r
        Resource

    Returns
    ----------------
    metric
        Value of the metric
    """
    if parameters is None:
        parameters = {}

    resource_key = exec_utils.get_param_value(Parameters.RESOURCE_KEY, parameters, xes_constants.DEFAULT_RESOURCE_KEY)

    from pm4py.algo.filtering.log.timestamp import timestamp_filter
    log = timestamp_filter.apply_events(log, t1_0, t2_0, parameters=parameters)

    from pm4py.algo.filtering.log.attributes import attributes_filter
    parameters_filter = {attributes_filter.Parameters.ATTRIBUTE_KEY: resource_key}

    filtered_log = attributes_filter.apply(log, [r], parameters=parameters_filter)

    q1 = float(len(filtered_log))
    q2 = float(len(log))

    return q1/q2 if q2 > 0 else 0.0

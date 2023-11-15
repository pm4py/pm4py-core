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
__doc__ = """
The ``pm4py.stats`` module contains the statistics offered in ``pm4py``
"""

from typing import Dict, Union, List, Tuple, Collection, Iterator
from typing import Set, Optional
from collections import Counter

import pandas as pd

from pm4py.objects.log.obj import EventLog, Trace, EventStream
from pm4py.util.pandas_utils import check_is_pandas_dataframe, check_pandas_dataframe_columns, insert_ev_in_tr_index
from pm4py.utils import get_properties, __event_log_deprecation_warning
from pm4py.util import constants
from pm4py.objects.petri_net.obj import PetriNet
from pm4py.objects.process_tree.obj import ProcessTree
import deprecation


def get_start_activities(log: Union[EventLog, pd.DataFrame], activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> Dict[str, int]:
    """
    Returns the start activities from a log object

    :param log: Log object
    :param activity_key: attribute to be used for the activity
    :param timestamp_key: attribute to be used for the timestamp
    :param case_id_key: attribute to be used as case identifier
    :rtype: ``Dict[str, int]``

    .. code-block:: python3

        import pm4py

        start_activities = pm4py.get_start_activities(dataframe, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
    """
    __event_log_deprecation_warning(log)

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
        from pm4py.statistics.start_activities.pandas import get
        return get.get_start_activities(log, parameters=properties)
    else:
        from pm4py.statistics.start_activities.log import get
        return get.get_start_activities(log, parameters=properties)


def get_end_activities(log: Union[EventLog, pd.DataFrame], activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> Dict[str, int]:
    """
    Returns the end activities of a log

    :param log: Log object
    :param activity_key: attribute to be used for the activity
    :param timestamp_key: attribute to be used for the timestamp
    :param case_id_key: attribute to be used as case identifier
    :rtype: ``Dict[str, int]``

    .. code-block:: python3

        import pm4py

        end_activities = pm4py.get_end_activities(dataframe, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
    """
    __event_log_deprecation_warning(log)

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
        from pm4py.statistics.end_activities.pandas import get
        return get.get_end_activities(log, parameters=properties)
    else:
        from pm4py.statistics.end_activities.log import get
        return get.get_end_activities(log, parameters=properties)


def get_event_attributes(log: Union[EventLog, pd.DataFrame]) -> List[str]:
    """
    Returns the attributes at the event level of the log

    :param log: Log object
    :rtype: ``List[str]``

    .. code-block:: python3

        import pm4py

        event_attributes = pm4py.get_event_attributes(dataframe)
    """
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

    :param log: Log object
    :rtype: ``List[str]``

    .. code-block:: python3

        import pm4py

        trace_attributes = pm4py.get_trace_attributes(dataframe)
    """
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
    Returns the values for a specified (event) attribute

    :param log: Log object
    :param attribute: attribute
    :param count_once_per_case: If True, consider only an occurrence of the given attribute value inside a case (if there are multiple events sharing the same attribute value, count only 1 occurrence)
    :param case_id_key: attribute to be used as case identifier
    :rtype: ``Dict[str, int]``

    .. code-block:: python3

        import pm4py

        activities = pm4py.get_event_attribute_values(dataframe, 'concept:name', case_id_key='case:concept:name')
    """
    __event_log_deprecation_warning(log)

    parameters = get_properties(log, case_id_key=case_id_key)
    parameters["keep_once_per_case"] = count_once_per_case
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, case_id_key=case_id_key)
        from pm4py.statistics.attributes.pandas import get
        return get.get_attribute_values(log, attribute, parameters=parameters)
    else:
        from pm4py.statistics.attributes.log import get
        return get.get_attribute_values(log, attribute, parameters=parameters)


def get_trace_attribute_values(log: Union[EventLog, pd.DataFrame], attribute: str, case_id_key: str = "case:concept:name") -> Dict[str, int]:
    """
    Returns the values for a specified trace attribute

    :param log: Log object
    :param attribute: Attribute
    :param case_id_key: attribute to be used as case identifier
    :rtype: ``Dict[str, int]``

    .. code-block:: python3

        import pm4py

        tr_attr_values = pm4py.get_trace_attribute_values(dataframe, 'case:attribute', case_id_key='case:concept:name')
    """
    __event_log_deprecation_warning(log)

    parameters = get_properties(log, case_id_key=case_id_key)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, case_id_key=case_id_key)
        from pm4py.statistics.attributes.pandas import get
        if attribute not in log and constants.CASE_ATTRIBUTE_PREFIX + attribute in log:
            # if "attribute" does not exist as column, but "case:attribute" exists, then use that
            attribute = constants.CASE_ATTRIBUTE_PREFIX + attribute
        ret = get.get_attribute_values(log, attribute, parameters=parameters)
        return ret
    else:
        from pm4py.statistics.attributes.log import get
        ret = get.get_trace_attribute_values(log, attribute, parameters=parameters)

        if not ret:
            # if the provided attribute does not exist, but starts with "case:", try to get the attribute values
            # removing the "case:" at the beginning
            if attribute.startswith(constants.CASE_ATTRIBUTE_PREFIX):
                attribute = attribute.split(constants.CASE_ATTRIBUTE_PREFIX)[-1]
            ret = get.get_trace_attribute_values(log, attribute, parameters=parameters)

        return ret


def get_variants(log: Union[EventLog, pd.DataFrame], activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> Dict[Tuple[str], List[Trace]]:
    """
    Gets the variants from the log

    :param log: Event log
    :param activity_key: attribute to be used for the activity
    :param timestamp_key: attribute to be used for the timestamp
    :param case_id_key: attribute to be used as case identifier
    :rtype: ``Dict[Tuple[str], List[Trace]]``

    .. code-block:: python3

        import pm4py

        variants = pm4py.get_variants(dataframe, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
    """
    return get_variants_as_tuples(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)


def get_variants_as_tuples(log: Union[EventLog, pd.DataFrame], activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> Dict[Tuple[str], List[Trace]]:
    """
    Gets the variants from the log (where the keys are tuples and not strings)

    :param log: Event log
    :param activity_key: attribute to be used for the activity
    :param timestamp_key: attribute to be used for the timestamp
    :param case_id_key: attribute to be used as case identifier
    :rtype: ``Dict[Tuple[str], List[Trace]]``

    .. code-block:: python3

        import pm4py

        variants = pm4py.get_variants_as_tuples(dataframe, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
    """
    __event_log_deprecation_warning(log)

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
        from pm4py.statistics.variants.pandas import get
        return get.get_variants_count(log, parameters=properties)
    else:
        from pm4py.statistics.variants.log import get
        return get.get_variants(log, parameters=properties)


def split_by_process_variant(log: Union[EventLog, pd.DataFrame], activity_key: str = "concept:name",
                             timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name",
                             variant_column: str = "@@variant_column",
                             index_in_trace_column: str = "@@index_in_trace") -> Iterator[
    Tuple[Collection[str], pd.DataFrame]]:
    """
    Splits an event log into sub-dataframes for each process variant.
    The result is an iterator over the variants along with the sub-dataframes.

    :param log: Event log
    :param activity_key: attribute to be used for the activity
    :param timestamp_key: attribute to be used for the timestamp
    :param case_id_key: attribute to be used as case identifier
    :param variant_column: name of the utility column that stores the variant's tuple
    :param index_in_trace_column: name of the utility column that stores the index of the event in the case
    :rtype: ``Iterator[Tuple[Collection[str], pd.DataFrame]]``

    .. code-block:: python3

        import pandas as pd
        import pm4py

        dataframe = pd.read_csv('tests/input_data/receipt.csv')
        dataframe = pm4py.format_dataframe(dataframe)
        for variant, subdf in pm4py.split_by_process_variant(dataframe):
            print(variant)
            print(subdf)
    """
    __event_log_deprecation_warning(log)

    import pm4py
    log = pm4py.convert_to_dataframe(log)
    check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    from pm4py.util import pandas_utils
    log = pandas_utils.insert_ev_in_tr_index(log, case_id=case_id_key, column_name=index_in_trace_column)
    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    from pm4py.objects.log.util import pandas_numpy_variants
    variants_dict, case_variant = pandas_numpy_variants.apply(log, parameters=properties)

    log[variant_column] = log[case_id_key].map(case_variant)

    for variant, filtered_log in log.groupby(variant_column, sort=False):
        yield variant, filtered_log


def get_variants_paths_duration(log: Union[EventLog, pd.DataFrame], activity_key: str = "concept:name",
                                timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name",
                                variant_column: str = "@@variant_column",
                                variant_count: str = "@@variant_count",
                                index_in_trace_column: str = "@@index_in_trace",
                                cumulative_occ_path_column: str = "@@cumulative_occ_path_column",
                                times_agg: str = "mean") -> pd.DataFrame:
    """
    Method that associates to a log object a Pandas dataframe aggregated by variants and positions (inside the variant).
    Each row is associated to different columns:
    - The variant
    - The position (in the variant)
    - The source activity (of the path)
    - The target activity (of the path)
    - An aggregation of the times between the two activities (for example, the mean over all the cases of the same variant)
    - The cumulative occurrences of the path inside the case (for example, the first A->B would be associated to 0,
                                                            and the second A->B would be associated to 1)

    :param log: Event log
    :param activity_key: attribute to be used for the activity
    :param timestamp_key: attribute to be used for the timestamp
    :param case_id_key: attribute to be used as case identifier
    :param variant_column: name of the utility column that stores the variant's tuple
    :param variant_count: name of the utility column that stores the variant's number of occurrences
    :param index_in_trace_column: name of the utility column that stores the index of the event in the case
    :param cumulative_occ_path_column: name of the column that stores the cumulative occurrences of the path inside the case
    :param times_agg: aggregation (mean, median) to be used
    :rtype: ``pd.DataFrame``

    .. code-block:: python3

        import pandas as pd
        import pm4py

        dataframe = pd.read_csv('tests/input_data/receipt.csv')
        dataframe = pm4py.format_dataframe(dataframe)

        var_paths_durs = pm4py.get_variants_paths_duration(dataframe)
        print(var_paths_durs)
    """
    __event_log_deprecation_warning(log)
    check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    list_to_concat = []
    for variant, filtered_log in split_by_process_variant(log, activity_key=activity_key, timestamp_key=timestamp_key,
                                                          case_id_key=case_id_key, variant_column=variant_column,
                                                          index_in_trace_column=index_in_trace_column):
        from pm4py.statistics.eventually_follows.pandas import get as eventually_follows
        dir_follo_dataframe = eventually_follows.get_partial_order_dataframe(filtered_log.copy(), activity_key=activity_key,
                                                                             timestamp_key=timestamp_key,
                                                                             case_id_glue=case_id_key,
                                                                             sort_caseid_required=False,
                                                                             sort_timestamp_along_case_id=False,
                                                                             reduce_dataframe=False)
        dir_follo_dataframe[cumulative_occ_path_column] = dir_follo_dataframe.groupby(
            [case_id_key, activity_key, activity_key + "_2"]).cumcount()
        dir_follo_dataframe = dir_follo_dataframe[
            [index_in_trace_column, constants.DEFAULT_FLOW_TIME, cumulative_occ_path_column]].groupby(
            index_in_trace_column).agg(
            {constants.DEFAULT_FLOW_TIME: times_agg, cumulative_occ_path_column: 'min'}).reset_index()
        dir_follo_dataframe[activity_key] = dir_follo_dataframe[index_in_trace_column].apply(lambda x: variant[x])
        dir_follo_dataframe[activity_key + "_2"] = dir_follo_dataframe[index_in_trace_column].apply(
            lambda x: variant[x + 1])
        dir_follo_dataframe[variant_column] = dir_follo_dataframe[index_in_trace_column].apply(lambda x: variant)
        dir_follo_dataframe[variant_count] = filtered_log[case_id_key].nunique()

        list_to_concat.append(dir_follo_dataframe)

    dataframe = pd.concat(list_to_concat)
    dataframe[index_in_trace_column] = -dataframe[index_in_trace_column]
    dataframe = dataframe.sort_values([variant_count, variant_column, index_in_trace_column], ascending=False)
    dataframe[index_in_trace_column] = -dataframe[index_in_trace_column]

    return dataframe

def get_stochastic_language(*args, **kwargs) -> Dict[List[str], float]:
    """
    Gets the stochastic language from the provided object

    :param args: Pandas dataframe / event log / accepting Petri net / process tree
    :param kwargs: keyword arguments
    :rtype: ``Dict[List[str], float]``

    .. code-block:: python3

        import pm4py

        log = pm4py.read_xes('tests/input_data/running-example.xes')
        language_log = pm4py.get_stochastic_language(log)
        print(language_log)
        net, im, fm = pm4py.read_pnml('tests/input_data/running-example.pnml')
        language_model = pm4py.get_stochastic_language(net, im, fm)
        print(language_model)
    """
    from pm4py.statistics.variants.log import get
    if isinstance(args[0], EventLog) or isinstance(args[0], EventStream) or isinstance(args[0], pd.DataFrame):
        from pm4py.objects.conversion.log import converter as log_converter
        log = log_converter.apply(args[0])
        return get.get_language(log)
    elif isinstance(args[0], PetriNet) or isinstance(args[0], ProcessTree) or isinstance(args[0], dict):
        import pm4py
        log = pm4py.play_out(*args, **kwargs)
        return get.get_language(log)
    else:
        raise Exception("unsupported input")


def get_minimum_self_distances(log: Union[EventLog, pd.DataFrame], activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> Dict[str, int]:
    '''
    This algorithm computes the minimum self-distance for each activity observed in an event log.
    The self distance of a in <a> is infinity, of a in <a,a> is 0, in <a,b,a> is 1, etc.
    The minimum self distance is the minimal observed self distance value in the event log.

    :param log: event log (either pandas.DataFrame, EventLog or EventStream)
    :param activity_key: attribute to be used for the activity
    :param timestamp_key: attribute to be used for the timestamp
    :param case_id_key: attribute to be used as case identifier
    :rtype: ``Dict[str, int]``

    .. code-block:: python3

        import pm4py

        msd = pm4py.get_minimum_self_distances(dataframe, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
    '''
    __event_log_deprecation_warning(log)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    from pm4py.algo.discovery.minimum_self_distance import algorithm as msd_algo
    return msd_algo.apply(log, parameters=properties)


def get_minimum_self_distance_witnesses(log: Union[EventLog, pd.DataFrame], activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> Dict[str, Set[str]]:
    """
    This function derives the minimum self distance witnesses.
    The self distance of a in <a> is infinity, of a in <a,a> is 0, in <a,b,a> is 1, etc.
    The minimum self distance is the minimal observed self distance value in the event log.
    A 'witness' is an activity that witnesses the minimum self distance.
    For example, if the minimum self distance of activity a in some log L is 2, then,
    if trace <a,b,c,a> is in log L, b and c are a witness of a.

    :param log: Event Log to use
    :param activity_key: attribute to be used for the activity
    :param timestamp_key: attribute to be used for the timestamp
    :param case_id_key: attribute to be used as case identifier
    :rtype: ``Dict[str, Set[str]]``

    .. code-block:: python3

        import pm4py

        msd_wit = pm4py.get_minimum_self_distance_witnesses(dataframe, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
    """
    __event_log_deprecation_warning(log)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    from pm4py.algo.discovery.minimum_self_distance import algorithm as msd_algo
    from pm4py.algo.discovery.minimum_self_distance import utils as msdw_algo
    return msdw_algo.derive_msd_witnesses(log, msd_algo.apply(log, parameters=get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)))


def get_case_arrival_average(log: Union[EventLog, pd.DataFrame], activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> float:
    """
    Gets the average difference between the start times of two consecutive cases

    :param log: log object
    :param activity_key: attribute to be used for the activity
    :param timestamp_key: attribute to be used for the timestamp
    :param case_id_key: attribute to be used as case identifier
    :rtype: ``float``

    .. code-block:: python3

        import pm4py

        case_arr_avg = pm4py.get_case_arrival_average(dataframe, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
    """
    __event_log_deprecation_warning(log)

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
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

    :param log: Log object
    :param activity_key: attribute to be used for the activity
    :param timestamp_key: attribute to be used for the timestamp
    :param case_id_key: attribute to be used as case identifier
    :rtype: ``Dict[str, int]``

    .. code-block:: python3

        import pm4py

        rework = pm4py.get_rework_cases_per_activity(dataframe, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
    """
    __event_log_deprecation_warning(log)

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
        from pm4py.statistics.rework.pandas import get as rework_get
        return rework_get.apply(log, parameters=properties)
    else:
        from pm4py.statistics.rework.log import get as rework_get
        return rework_get.apply(log, parameters=properties)


@deprecation.deprecated(deprecated_in="2.3.0", removed_in="3.0.0", details="the get_case_overlap function will be removed in a future release.")
def get_case_overlap(log: Union[EventLog, pd.DataFrame], activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> List[int]:
    """
    Associates to each case in the log the number of cases concurrently open

    :param log: Log object
    :param activity_key: attribute to be used for the activity
    :param timestamp_key: attribute to be used for the timestamp
    :param case_id_key: attribute to be used as case identifier
    :rtype: ``List[int]``

    .. code-block:: python3

        import pm4py

        overlap = pm4py.get_case_overlap(dataframe, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
    """
    __event_log_deprecation_warning(log)

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
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

    :param log: Log object
    :param activity_key: attribute to be used for the activity
    :param timestamp_key: attribute to be used for the timestamp
    :param case_id_key: attribute to be used as case identifier
    :rtype: ``float``

    .. code-block:: python3

        import pm4py

        cycle_time = pm4py.get_cycle_time(dataframe, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
    """
    __event_log_deprecation_warning(log)

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
        from pm4py.statistics.traces.cycle_time.pandas import get as cycle_time
        return cycle_time.apply(log, parameters=properties)
    else:
        from pm4py.statistics.traces.cycle_time.log import get as cycle_time
        return cycle_time.apply(log, parameters=properties)


def get_all_case_durations(log: Union[EventLog, pd.DataFrame], business_hours: bool = False, business_hour_slots=constants.DEFAULT_BUSINESS_HOUR_SLOTS, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> List[float]:
    """
    Gets the durations of the cases in the event log

    :param log: Event log
    :param business_hours: Enables/disables the computation based on the business hours (default: False)
    :param business_hour_slots: work schedule of the company, provided as a list of tuples where each tuple represents one time slot of business hours. One slot i.e. one tuple consists of one start and one end time given in seconds since week start, e.g. [(7 * 60 * 60, 17 * 60 * 60), ((24 + 7) * 60 * 60, (24 + 12) * 60 * 60), ((24 + 13) * 60 * 60, (24 + 17) * 60 * 60),] meaning that business hours are Mondays 07:00 - 17:00 and Tuesdays 07:00 - 12:00 and 13:00 - 17:00
    :param activity_key: attribute to be used for the activity
    :param timestamp_key: attribute to be used for the timestamp
    :param case_id_key: attribute to be used as case identifier
    :rtype: ``List[float]``

    .. code-block:: python3

        import pm4py

        case_durations = pm4py.get_all_case_durations(dataframe, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
    """
    __event_log_deprecation_warning(log)

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    properties["business_hours"] = business_hours
    properties["business_hour_slots"] = business_hour_slots
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
        from pm4py.statistics.traces.generic.pandas import case_statistics
        cd = case_statistics.get_cases_description(log, parameters=properties)
        return sorted([x["caseDuration"] for x in cd.values()])
    else:
        from pm4py.statistics.traces.generic.log import case_statistics
        return case_statistics.get_all_case_durations(log, parameters=properties)


def get_case_duration(log: Union[EventLog, pd.DataFrame], case_id: str, business_hours: bool = False, business_hour_slots=constants.DEFAULT_BUSINESS_HOUR_SLOTS, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: Optional[str] = None) -> float:
    """
    Gets the duration of a specific case

    :param log: Event log
    :param case_id: Case identifier
    :param business_hours: Enables/disables the computation based on the business hours (default: False)
    :param business_hour_slots: work schedule of the company, provided as a list of tuples where each tuple represents one time slot of business hours. One slot i.e. one tuple consists of one start and one end time given in seconds since week start, e.g. [(7 * 60 * 60, 17 * 60 * 60), ((24 + 7) * 60 * 60, (24 + 12) * 60 * 60), ((24 + 13) * 60 * 60, (24 + 17) * 60 * 60),] meaning that business hours are Mondays 07:00 - 17:00 and Tuesdays 07:00 - 12:00 and 13:00 - 17:00
    :param activity_key: attribute to be used for the activity
    :param timestamp_key: attribute to be used for the timestamp
    :param case_id_key: attribute to be used as case identifier
    :rtype: ``float``

    .. code-block:: python3

        import pm4py

        duration = pm4py.get_case_duration(dataframe, 'case 1', activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
    """
    __event_log_deprecation_warning(log)

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    properties["business_hours"] = business_hours
    properties["business_hour_slots"] = business_hour_slots
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
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

    :param log: Event log object / Pandas dataframe
    :param activity: Activity to consider
    :param activity_key: attribute to be used for the activity
    :param timestamp_key: attribute to be used for the timestamp
    :param case_id_key: attribute to be used as case identifier
    :rtype: ``Dict[int, int]``

    .. code-block:: python3

        import pm4py

        act_pos = pm4py.get_activity_position_summary(dataframe, 'Act. A', activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
    """
    __event_log_deprecation_warning(log)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
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

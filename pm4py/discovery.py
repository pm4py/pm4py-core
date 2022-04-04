__doc__ = """
Process Discovery algorithms want to find a suitable process model that describes the order of events/activities that are executed during a process execution.

* Procedural
    * Discovering Directly-Follows Graphs
        * `Frequency DFG`_
        * `Performance DFG`_
    * Discovering Petri nets
        * `Alpha Miner`_
        * `Inductive Miner`_
        * `Heuristics Miner`_
    * `BPMN discovery using the Inductive Miner`_
    * `Process tree discovery using the Inductive Miner`_
    * `Transition system`_
    * `Prefix tree`_
* Declarative
    * `Log skeleton`_
* Time-infused
    * `Temporal profile`_

.. _Frequency DFG: pm4py.html#pm4py.discovery.discover_dfg
.. _Performance DFG: pm4py.html#pm4py.discovery.discover_performance_dfg
.. _Alpha Miner: pm4py.html#pm4py.discovery.discover_petri_net_alpha
.. _Inductive Miner: pm4py.html#pm4py.discovery.discover_petri_net_inductive
.. _Heuristics Miner: pm4py.html#pm4py.discovery.discover_petri_net_heuristics
.. _BPMN discovery using the Inductive Miner: pm4py.html#pm4py.discovery.discover_bpmn_inductive
.. _Process tree discovery using the Inductive Miner: pm4py.html#pm4py.discovery.discover_process_tree_inductive
.. _Transition system: pm4py.html#pm4py.discovery.discover_transition_system
.. _Prefix tree: pm4py.html#pm4py.discovery.discover_prefix_tree
.. _Log skeleton: pm4py.html#pm4py.discovery.discover_log_skeleton
.. _Temporal profile: pm4py.html#pm4py.discovery.discover_temporal_profile
"""

import warnings
from typing import Tuple, Union, List, Dict, Any, Optional

import pandas as pd
from pandas import DataFrame

from pm4py.objects.bpmn.obj import BPMN
from pm4py.objects.heuristics_net.obj import HeuristicsNet
from pm4py.objects.transition_system.obj import TransitionSystem
from pm4py.objects.trie.obj import Trie
from pm4py.objects.log.obj import EventLog
from pm4py.objects.log.obj import EventStream
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.util.pandas_utils import check_is_pandas_dataframe, check_pandas_dataframe_columns
from pm4py.utils import get_properties, xes_constants, __event_log_deprecation_warning
from pm4py.util import constants
import deprecation


def discover_dfg(log: Union[EventLog, pd.DataFrame], activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> Tuple[dict, dict, dict]:
    """
    Discovers a DFG from a log

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
    dfg
        DFG
    start_activities
        Start activities
    end_activities
        End activities
    """
    # Variant that is Pandas native: YES
    # Unit test: YES
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
        from pm4py.util import constants

        from pm4py.algo.discovery.dfg.adapters.pandas.df_statistics import get_dfg_graph
        dfg = get_dfg_graph(log, activity_key=activity_key,
                            timestamp_key=timestamp_key,
                            case_id_glue=case_id_key)
        from pm4py.statistics.start_activities.pandas import get as start_activities_module
        from pm4py.statistics.end_activities.pandas import get as end_activities_module
        start_activities = start_activities_module.get_start_activities(log, parameters=properties)
        end_activities = end_activities_module.get_end_activities(log, parameters=properties)
    else:
        from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
        dfg = dfg_discovery.apply(log, parameters=properties)
        from pm4py.statistics.start_activities.log import get as start_activities_module
        from pm4py.statistics.end_activities.log import get as end_activities_module
        start_activities = start_activities_module.get_start_activities(log, parameters=properties)
        end_activities = end_activities_module.get_end_activities(log, parameters=properties)
    return dfg, start_activities, end_activities


def discover_directly_follows_graph(log: Union[EventLog, pd.DataFrame], activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> Tuple[dict, dict, dict]:
    # Variant that is Pandas native: YES
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")

    return discover_dfg(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)


def discover_performance_dfg(log: Union[EventLog, pd.DataFrame], business_hours: bool = False, worktiming: List[int] = [7, 17], weekends: List[int] = [6, 7], workcalendar=constants.DEFAULT_BUSINESS_HOURS_WORKCALENDAR, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> Tuple[dict, dict, dict]:
    """
    Discovers a performance directly-follows graph from an event log

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
    performance_dfg
        Performance DFG
    start_activities
        Start activities
    end_activities
        End activities
    """
    # Variant that is Pandas native: YES
    # Unit test: YES
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
        from pm4py.util import constants

        from pm4py.algo.discovery.dfg.adapters.pandas.df_statistics import get_dfg_graph
        dfg = get_dfg_graph(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_glue=case_id_key, measure="performance", perf_aggregation_key="all",
                            business_hours=business_hours, worktiming=worktiming, weekends=weekends, workcalendar=workcalendar)
        from pm4py.statistics.start_activities.pandas import get as start_activities_module
        from pm4py.statistics.end_activities.pandas import get as end_activities_module
        start_activities = start_activities_module.get_start_activities(log, parameters=properties)
        end_activities = end_activities_module.get_end_activities(log, parameters=properties)
    else:
        from pm4py.algo.discovery.dfg.variants import performance as dfg_discovery
        properties[dfg_discovery.Parameters.AGGREGATION_MEASURE] = "all"
        properties[dfg_discovery.Parameters.BUSINESS_HOURS] = business_hours
        properties[dfg_discovery.Parameters.WORKTIMING] = worktiming
        properties[dfg_discovery.Parameters.WEEKENDS] = weekends
        dfg = dfg_discovery.apply(log, parameters=properties)
        from pm4py.statistics.start_activities.log import get as start_activities_module
        from pm4py.statistics.end_activities.log import get as end_activities_module
        start_activities = start_activities_module.get_start_activities(log, parameters=properties)
        end_activities = end_activities_module.get_end_activities(log, parameters=properties)
    return dfg, start_activities, end_activities


def discover_petri_net_alpha(log: Union[EventLog, pd.DataFrame], activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> Tuple[PetriNet, Marking, Marking]:
    """
    Discovers a Petri net using the Alpha Miner

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
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    """
    # Variant that is Pandas native: YES
    # Unit test: YES
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    from pm4py.algo.discovery.alpha import algorithm as alpha_miner
    return alpha_miner.apply(log, variant=alpha_miner.Variants.ALPHA_VERSION_CLASSIC, parameters=get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key))


@deprecation.deprecated("2.3.0", "3.0.0", details="this method will be removed in a future release.")
def discover_petri_net_alpha_plus(log: Union[EventLog, pd.DataFrame], activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> Tuple[PetriNet, Marking, Marking]:
    """
    Discovers a Petri net using the Alpha+ algorithm

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
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    """
    # Variant that is Pandas native: NO DEPRECATED
    # Unit test: YES
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    from pm4py.algo.discovery.alpha import algorithm as alpha_miner
    return alpha_miner.apply(log, variant=alpha_miner.Variants.ALPHA_VERSION_PLUS, parameters=get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key))


def discover_petri_net_inductive(log: Union[EventLog, pd.DataFrame], noise_threshold: float = 0.0, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> Tuple[
    PetriNet, Marking, Marking]:
    """
    Discovers a Petri net using the IMDFc algorithm

    Parameters
    --------------
    log
        Event log
    noise_threshold
        Noise threshold (default: 0.0)
    activity_key
        attribute to be used for the activity
    timestamp_key
        attribute to be used for the timestamp
    case_id_key
        attribute to be used as case identifier

    Returns
    --------------
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    """
    # Variant that is Pandas native: NO
    # Unit test: YES
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    pt = discover_process_tree_inductive(log, noise_threshold, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    from pm4py.convert import convert_to_petri_net
    return convert_to_petri_net(pt)


def discover_petri_net_heuristics(log: Union[EventLog, pd.DataFrame], dependency_threshold: float = 0.5,
                                  and_threshold: float = 0.65,
                                  loop_two_threshold: float = 0.5, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> Tuple[PetriNet, Marking, Marking]:
    """
    Discover a Petri net using the Heuristics Miner

    Parameters
    ---------------
    log
        Event log
    dependency_threshold
        Dependency threshold (default: 0.5)
    and_threshold
        AND threshold (default: 0.65)
    loop_two_threshold
        Loop two threshold (default: 0.5)
    activity_key
        attribute to be used for the activity
    timestamp_key
        attribute to be used for the timestamp
    case_id_key
        attribute to be used as case identifier

    Returns
    --------------
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    """
    # Variant that is Pandas native: YES
    # Unit test: YES
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    from pm4py.algo.discovery.heuristics.variants import classic as heuristics_miner
    heu_parameters = heuristics_miner.Parameters
    parameters = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    parameters[heu_parameters.DEPENDENCY_THRESH] = dependency_threshold
    parameters[heu_parameters.AND_MEASURE_THRESH] = and_threshold
    parameters[heu_parameters.LOOP_LENGTH_TWO_THRESH] = loop_two_threshold

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
        return heuristics_miner.apply_pandas(log, parameters=parameters)
    else:
        return heuristics_miner.apply(log, parameters=parameters)


def discover_process_tree_inductive(log: Union[EventLog, pd.DataFrame], noise_threshold: float = 0.0, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> ProcessTree:
    """
    Discovers a process tree using the IM algorithm

    Parameters
    --------------
    log
        Event log
    noise_threshold
        Noise threshold (default: 0.0)
    activity_key
        attribute to be used for the activity
    timestamp_key
        attribute to be used for the timestamp
    case_id_key
        attribute to be used as case identifier

    Returns
    --------------
    process_tree
        Process tree object
    """
    # Variant that is Pandas native: NO
    # Unit test: YES
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    from pm4py.algo.discovery.inductive import algorithm as inductive_miner
    parameters = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    parameters[inductive_miner.Variants.IM_CLEAN.value.Parameters.NOISE_THRESHOLD] = noise_threshold
    return inductive_miner.apply_tree(log, variant=inductive_miner.Variants.IM_CLEAN, parameters=parameters)


def discover_heuristics_net(log: Union[EventLog, pd.DataFrame], dependency_threshold: float = 0.5,
                            and_threshold: float = 0.65,
                            loop_two_threshold: float = 0.5, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> HeuristicsNet:
    """
    Discovers an heuristics net

    Parameters
    ---------------
    log
        Event log
    dependency_threshold
        Dependency threshold (default: 0.5)
    and_threshold
        AND threshold (default: 0.65)
    loop_two_threshold
        Loop two threshold (default: 0.5)
    activity_key
        attribute to be used for the activity
    timestamp_key
        attribute to be used for the timestamp
    case_id_key
        attribute to be used as case identifier

    Returns
    --------------
    heu_net
        Heuristics net
    """
    # Variant that is Pandas native: YES
    # Unit test: YES
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    from pm4py.algo.discovery.heuristics.variants import classic as heuristics_miner
    heu_parameters = heuristics_miner.Parameters
    parameters = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    parameters[heu_parameters.DEPENDENCY_THRESH] = dependency_threshold
    parameters[heu_parameters.AND_MEASURE_THRESH] = and_threshold
    parameters[heu_parameters.LOOP_LENGTH_TWO_THRESH] = loop_two_threshold

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
        return heuristics_miner.apply_heu_pandas(log, parameters=parameters)
    else:
        return heuristics_miner.apply_heu(log, parameters=parameters)


def derive_minimum_self_distance(log: Union[DataFrame, EventLog, EventStream], activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> Dict[str, int]:
    '''
        This algorithm computes the minimum self-distance for each activity observed in an event log.
        The self distance of a in <a> is infinity, of a in <a,a> is 0, in <a,b,a> is 1, etc.
        The activity key 'concept:name' is used.


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
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    from pm4py.algo.discovery.minimum_self_distance import algorithm as msd
    return msd.apply(log, parameters=get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key))


def discover_footprints(*args: Union[EventLog, Tuple[PetriNet, Marking, Marking], ProcessTree]) -> Union[
    List[Dict[str, Any]], Dict[str, Any]]:
    """
    Discovers the footprints out of the provided event log / pocess model

    Parameters
    --------------
    args
        Event log / process model
    """
    # Variant that is Pandas native: YES
    # Unit test: YES
    from pm4py.algo.discovery.footprints import algorithm as fp_discovery
    return fp_discovery.apply(*args)


def discover_eventually_follows_graph(log: Union[EventLog, pd.DataFrame], activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> Dict[Tuple[str, str], int]:
    """
    Gets the eventually follows graph from a log object

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
    eventually_follows_graph
        Dictionary of tuples of activities that eventually follows each other; along with the number of occurrences
    """
    # Variant that is Pandas native: YES
    # Unit test: YES
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
        from pm4py.statistics.eventually_follows.pandas import get
        return get.apply(log, parameters=properties)
    else:
        from pm4py.statistics.eventually_follows.log import get
        return get.apply(log, parameters=properties)


def discover_bpmn_inductive(log: Union[EventLog, pd.DataFrame], noise_threshold: float = 0.0, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> BPMN:
    """
        Discovers a BPMN using the Inductive Miner algorithm

        Parameters
        --------------
        log
            Event log
        noise_threshold
            Noise threshold (default: 0.0)
        activity_key
            attribute to be used for the activity
        timestamp_key
            attribute to be used for the timestamp
        case_id_key
            attribute to be used as case identifier

        Returns
        --------------
        bpmn_diagram
            BPMN diagram
        """
    # Variant that is Pandas native: NO
    # Unit test: YES
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    pt = discover_process_tree_inductive(log, noise_threshold, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    from pm4py.convert import convert_to_bpmn
    return convert_to_bpmn(pt)


def discover_transition_system(log: Union[EventLog, pd.DataFrame], direction: str = "forward", window: int = 2, view: str = "sequence", activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> TransitionSystem:
    """
    Discovers a transition system as described in the process mining book

    "Process Mining: Data Science in Action"

    Parameters
    -----------------
    log
        Event log
    direction
        Direction in which the transition system is built (forward, backward)
    window
        Window (2, 3, ...)
    view
        View to use in the construction of the states (sequence, set, multiset)
    activity_key
        attribute to be used for the activity
    timestamp_key
        attribute to be used for the timestamp
    case_id_key
        attribute to be used as case identifier

    Returns
    -----------------
    transition_system
        Transition system
    """
    # Variant that is Pandas native: YES
    # Unit test: YES
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    properties["direction"] = direction
    properties["window"] = window
    properties["view"] = view

    from pm4py.algo.discovery.transition_system import algorithm as ts_discovery
    return ts_discovery.apply(log, parameters=properties)


def discover_prefix_tree(log: Union[EventLog, pd.DataFrame], activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> Trie:
    """
    Discovers a prefix tree from the provided log object.

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
    prefix_tree
        Prefix tree
    """
    # Variant that is Pandas native: YES
    # Unit test: YES
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    from pm4py.algo.transformation.log_to_trie import algorithm as trie_discovery
    return trie_discovery.apply(log, parameters=properties)


def discover_temporal_profile(log: Union[EventLog, pd.DataFrame], activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> Dict[Tuple[str, str], Tuple[float, float]]:
    """
    Discovers a temporal profile from a log object.

    Implements the approach described in:
    Stertz, Florian, Jürgen Mangler, and Stefanie Rinderle-Ma. "Temporal Conformance Checking at Runtime based on Time-infused Process Models." arXiv preprint arXiv:2008.07262 (2020).

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
    -------------
    dict_agg
        Dictionary containing, for every couple of activities eventually following in at least a case of the log,
        the average and the standard deviation of the difference of the timestamps.

        E.g. if the log has two cases:

        A (timestamp: 1980-01)   B (timestamp: 1980-03)    C (timestamp: 1980-06)
        A (timestamp: 1990-01)   B (timestamp: 1990-02)    D (timestamp: 1990-03)

        The returned dictionary will contain:
        {('A', 'B'): (1.5 months, 0.5 months), ('A', 'C'): (5 months, 0), ('A', 'D'): (2 months, 0)}
    """
    # Variant that is Pandas native: YES
    # Unit test: YES
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    from pm4py.algo.discovery.temporal_profile import algorithm as temporal_profile_discovery
    return temporal_profile_discovery.apply(log, parameters=properties)


def discover_log_skeleton(log: Union[EventLog, pd.DataFrame], noise_threshold: float = 0.0, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> Dict[str, Any]:
    """
    Discovers a log skeleton from an event log.

    A log skeleton is a declarative model which consists of six different constraints:
    - "directly_follows": specifies for some activities some strict bounds on the activities directly-following. For example,
                        'A should be directly followed by B' and 'B should be directly followed by C'.
    - "always_before": specifies that some activities may be executed only if some other activities are executed somewhen before
                        in the history of the case.
                        For example, 'C should always be preceded by A'
    - "always_after": specifies that some activities should always trigger the execution of some other activities
                        in the future history of the case.
                        For example, 'A should always be followed by C'
    - "equivalence": specifies that a given couple of activities should happen with the same number of occurrences inside
                        a case.
                        For example, 'B and C should always happen the same number of times'.
    - "never_together": specifies that a given couple of activities should never happen together in the history of the case.
                        For example, 'there should be no case containing both C and D'.
    - "activ_occurrences": specifies the allowed number of occurrences per activity:
                        E.g. A is allowed to be executed 1 or 2 times, B is allowed to be executed 1 or 2 or 3 or 4 times.

    Reference paper:
    Verbeek, H. M. W., and R. Medeiros de Carvalho. "Log skeletons: A classification approach to process discovery." arXiv preprint arXiv:1806.08247 (2018).

    Parameters
    ------------------
    log
        Event log
    noise_threshold
        Noise threshold, acting as described in the paper.
    activity_key
        attribute to be used for the activity
    timestamp_key
        attribute to be used for the timestamp
    case_id_key
        attribute to be used as case identifier

    Returns
    -----------------
    log_skeleton
        Log skeleton object, expressed as dictionaries of the six constraints (never_together, always_before ...)
        along with the discovered rules.
    """
    # Variant that is Pandas native: YES
    # Unit test: YES
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    properties["noise_threshold"] = noise_threshold

    from pm4py.algo.discovery.log_skeleton import algorithm as log_skeleton_discovery
    return log_skeleton_discovery.apply(log, parameters=properties)


def discover_batches(log: Union[EventLog, pd.DataFrame], merge_distance: int = 15 * 60, min_batch_size: int = 2, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name", resource_key: str = "org:resource") -> List[
    Tuple[Tuple[str, str], int, Dict[str, Any]]]:
    """
    Discover batches from the provided log object

    The following categories of batches are detected:
    - Simultaneous (all the events in the batch have identical start and end timestamps)
    - Batching at start (all the events in the batch have identical start timestamp)
    - Batching at end (all the events in the batch have identical end timestamp)
    - Sequential batching (for all the consecutive events, the end of the first is equal to the start of the second)
    - Concurrent batching (for all the consecutive events that are not sequentially matched)

    The approach has been described in the following paper:
    Martin, N., Swennen, M., Depaire, B., Jans, M., Caris, A., & Vanhoof, K. (2015, December). Batch Processing:
    Definition and Event Log Identification. In SIMPDA (pp. 137-140).

    Parameters
    ------------------
    log
        Log object
    merge_distance
         the maximum time distance between non-overlapping intervals in order for them to be considered belonging to the same batch (default: 15*60   15 minutes)
    min_batch_size
        the minimum number of events for a batch to be considered (default: 2)
    activity_key
        attribute to be used for the activity
    timestamp_key
        attribute to be used for the timestamp
    case_id_key
        attribute to be used as case identifier
    resource_key
        attribute to be used as resource

    Returns
    ------------------
    list_batches
        A (sorted) list containing tuples. Each tuple contain:
        - Index 0: the activity-resource for which at least one batch has been detected
        - Index 1: the number of batches for the given activity-resource
        - Index 2: a list containing all the batches. Each batch is described by:
            # The start timestamp of the batch
            # The complete timestamp of the batch
            # The list of events that are executed in the batch
    """
    # Variant that is Pandas native: YES
    # Unit test: YES
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key, resource_key=resource_key)
    properties["merge_distance"] = merge_distance
    properties["min_batch_size"] = min_batch_size

    from pm4py.algo.discovery.batches import algorithm as batches_discovery
    return batches_discovery.apply(log, parameters=properties)

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
import warnings
from typing import Tuple, Union, List, Dict, Any

import deprecation
import pandas as pd
from pandas import DataFrame

from pm4py.objects.bpmn.obj import BPMN
from pm4py.objects.heuristics_net.obj import HeuristicsNet
from pm4py.objects.log.obj import EventLog
from pm4py.objects.log.obj import EventStream
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.util.pandas_utils import check_is_pandas_dataframe, check_pandas_dataframe_columns
from pm4py.utils import get_properties, xes_constants


def discover_dfg(log: Union[EventLog, pd.DataFrame]) -> Tuple[dict, dict, dict]:
    """
    Discovers a DFG from a log

    Parameters
    --------------
    log
        Event log

    Returns
    --------------
    dfg
        DFG
    start_activities
        Start activities
    end_activities
        End activities
    """
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        from pm4py.util import constants
        properties = get_properties(log)
        from pm4py.algo.discovery.dfg.adapters.pandas.df_statistics import get_dfg_graph
        activity_key = properties[constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in properties else xes_constants.DEFAULT_NAME_KEY
        timestamp_key = properties[constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] if constants.PARAMETER_CONSTANT_TIMESTAMP_KEY in properties else xes_constants.DEFAULT_TIMESTAMP_KEY
        case_id_key = properties[constants.PARAMETER_CONSTANT_CASEID_KEY] if constants.PARAMETER_CONSTANT_CASEID_KEY in properties else constants.CASE_CONCEPT_NAME
        dfg = get_dfg_graph(log, activity_key=activity_key,
                            timestamp_key=timestamp_key,
                            case_id_glue=case_id_key)
        from pm4py.statistics.start_activities.pandas import get as start_activities_module
        from pm4py.statistics.end_activities.pandas import get as end_activities_module
        start_activities = start_activities_module.get_start_activities(log, parameters=properties)
        end_activities = end_activities_module.get_end_activities(log, parameters=properties)
    else:
        from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
        dfg = dfg_discovery.apply(log, parameters=get_properties(log))
        from pm4py.statistics.start_activities.log import get as start_activities_module
        from pm4py.statistics.end_activities.log import get as end_activities_module
        start_activities = start_activities_module.get_start_activities(log, parameters=get_properties(log))
        end_activities = end_activities_module.get_end_activities(log, parameters=get_properties(log))
    return dfg, start_activities, end_activities


def discover_directly_follows_graph(log: Union[EventLog, pd.DataFrame]) -> Tuple[dict, dict, dict]:
    return discover_dfg(log)


def discover_performance_dfg(log: Union[EventLog, pd.DataFrame]) -> Tuple[dict, dict, dict]:
    """
    Discovers a performance directly-follows graph from an event log

    Parameters
    ---------------
    log
        Event log

    Returns
    ---------------
    performance_dfg
        Performance DFG
    start_activities
        Start activities
    end_activities
        End activities
    """
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        from pm4py.util import constants
        properties = get_properties(log)
        from pm4py.algo.discovery.dfg.adapters.pandas.df_statistics import get_dfg_graph
        activity_key = properties[constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in properties else xes_constants.DEFAULT_NAME_KEY
        timestamp_key = properties[constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] if constants.PARAMETER_CONSTANT_TIMESTAMP_KEY in properties else xes_constants.DEFAULT_TIMESTAMP_KEY
        case_id_key = properties[constants.PARAMETER_CONSTANT_CASEID_KEY] if constants.PARAMETER_CONSTANT_CASEID_KEY in properties else constants.CASE_CONCEPT_NAME
        dfg = get_dfg_graph(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_glue=case_id_key, measure="performance")
        from pm4py.statistics.start_activities.pandas import get as start_activities_module
        from pm4py.statistics.end_activities.pandas import get as end_activities_module
        start_activities = start_activities_module.get_start_activities(log, parameters=properties)
        end_activities = end_activities_module.get_end_activities(log, parameters=properties)
    else:
        from pm4py.algo.discovery.dfg.variants import performance as dfg_discovery
        properties = get_properties(log)
        properties[dfg_discovery.Parameters.AGGREGATION_MEASURE] = "all"
        dfg = dfg_discovery.apply(log, parameters=properties)
        from pm4py.statistics.start_activities.log import get as start_activities_module
        from pm4py.statistics.end_activities.log import get as end_activities_module
        start_activities = start_activities_module.get_start_activities(log, parameters=properties)
        end_activities = end_activities_module.get_end_activities(log, parameters=properties)
    return dfg, start_activities, end_activities


def discover_petri_net_alpha(log: Union[EventLog, pd.DataFrame]) -> Tuple[PetriNet, Marking, Marking]:
    """
    Discovers a Petri net using the Alpha Miner

    Parameters
    --------------
    log
        Event log

    Returns
    --------------
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    """
    from pm4py.algo.discovery.alpha import algorithm as alpha_miner
    return alpha_miner.apply(log, variant=alpha_miner.Variants.ALPHA_VERSION_CLASSIC, parameters=get_properties(log))


def discover_petri_net_alpha_plus(log: Union[EventLog, pd.DataFrame]) -> Tuple[PetriNet, Marking, Marking]:
    """
    Discovers a Petri net using the Alpha+ algorithm

    Parameters
    --------------
    log
        Event log

    Returns
    --------------
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    """
    from pm4py.algo.discovery.alpha import algorithm as alpha_miner
    return alpha_miner.apply(log, variant=alpha_miner.Variants.ALPHA_VERSION_PLUS, parameters=get_properties(log))


def discover_petri_net_inductive(log: Union[EventLog, pd.DataFrame], noise_threshold: float = 0.0) -> Tuple[
    PetriNet, Marking, Marking]:
    """
    Discovers a Petri net using the IMDFc algorithm

    Parameters
    --------------
    log
        Event log
    noise_threshold
        Noise threshold (default: 0.0)

    Returns
    --------------
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    """
    pt = discover_process_tree_inductive(log, noise_threshold)
    from pm4py.convert import convert_to_petri_net
    return convert_to_petri_net(pt)


def discover_petri_net_heuristics(log: Union[EventLog, pd.DataFrame], dependency_threshold: float = 0.5,
                                  and_threshold: float = 0.65,
                                  loop_two_threshold: float = 0.5) -> Tuple[PetriNet, Marking, Marking]:
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

    Returns
    --------------
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    """
    from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
    heu_parameters = heuristics_miner.Variants.CLASSIC.value.Parameters
    parameters = get_properties(log)
    parameters[heu_parameters.DEPENDENCY_THRESH] = dependency_threshold
    parameters[heu_parameters.AND_MEASURE_THRESH] = and_threshold
    parameters[heu_parameters.LOOP_LENGTH_TWO_THRESH] = loop_two_threshold

    return heuristics_miner.apply(log, variant=heuristics_miner.Variants.CLASSIC, parameters=parameters)


def discover_process_tree_inductive(log: Union[EventLog, pd.DataFrame], noise_threshold: float = 0.0) -> ProcessTree:
    """
    Discovers a process tree using the IM algorithm

    Parameters
    --------------
    log
        Event log
    noise_threshold
        Noise threshold (default: 0.0)

    Returns
    --------------
    process_tree
        Process tree object
    """
    from pm4py.algo.discovery.inductive import algorithm as inductive_miner
    parameters = get_properties(log)
    parameters[inductive_miner.Variants.IM_CLEAN.value.Parameters.NOISE_THRESHOLD] = noise_threshold
    return inductive_miner.apply_tree(log, variant=inductive_miner.Variants.IM_CLEAN, parameters=parameters)


@deprecation.deprecated(deprecated_in='2.2.2', removed_in='2.4.0',
                        details='discover_tree_inductive is deprecated, use discover_process_tree_inductive')
def discover_tree_inductive(log: Union[EventLog, pd.DataFrame], noise_threshold: float = 0.0) -> ProcessTree:
    warnings.warn('discover_tree_inductive is deprecated, use discover_process_tree_inductive', DeprecationWarning)
    """
    Discovers a process tree using the IMDFc algorithm

    Parameters
    --------------
    log
        Event log
    noise_threshold
        Noise threshold (default: 0.0)

    Returns
    --------------
    process_tree
        Process tree object
    """
    return discover_process_tree_inductive(log, noise_threshold)


def discover_heuristics_net(log: Union[EventLog, pd.DataFrame], dependency_threshold: float = 0.5,
                            and_threshold: float = 0.65,
                            loop_two_threshold: float = 0.5) -> HeuristicsNet:
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

    Returns
    --------------
    heu_net
        Heuristics net
    """
    from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
    heu_parameters = heuristics_miner.Variants.CLASSIC.value.Parameters
    parameters = get_properties(log)
    parameters[heu_parameters.DEPENDENCY_THRESH] = dependency_threshold
    parameters[heu_parameters.AND_MEASURE_THRESH] = and_threshold
    parameters[heu_parameters.LOOP_LENGTH_TWO_THRESH] = loop_two_threshold
    return heuristics_miner.apply_heu(log, variant=heuristics_miner.Variants.CLASSIC, parameters=parameters)


def derive_minimum_self_distance(log: Union[DataFrame, EventLog, EventStream]) -> Dict[str, int]:
    '''
        This algorithm computes the minimum self-distance for each activity observed in an event log.
        The self distance of a in <a> is infinity, of a in <a,a> is 0, in <a,b,a> is 1, etc.
        The activity key 'concept:name' is used.


        Parameters
        ----------
        log
            event log (either pandas.DataFrame, EventLog or EventStream)

        Returns
        -------
            dict mapping an activity to its self-distance, if it exists, otherwise it is not part of the dict.
        '''
    from pm4py.algo.discovery.minimum_self_distance import algorithm as msd
    return msd.apply(log, parameters=get_properties(log))


def discover_footprints(*args: Union[EventLog, Tuple[PetriNet, Marking, Marking], ProcessTree]) -> Union[
    List[Dict[str, Any]], Dict[str, Any]]:
    """
    Discovers the footprints out of the provided event log / pocess model

    Parameters
    --------------
    args
        Event log / process model
    """
    from pm4py.algo.discovery.footprints import algorithm as fp_discovery
    return fp_discovery.apply(*args)


def discover_eventually_follows_graph(log: Union[EventLog, pd.DataFrame]) -> Dict[Tuple[str, str], int]:
    """
    Gets the eventually follows graph from a log object

    Parameters
    ---------------
    log
        Log object

    Returns
    ---------------
    eventually_follows_graph
        Dictionary of tuples of activities that eventually follows each other; along with the number of occurrences
    """
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        from pm4py.statistics.eventually_follows.pandas import get
        return get.apply(log, parameters=get_properties(log))
    else:
        from pm4py.statistics.eventually_follows.log import get
        return get.apply(log, parameters=get_properties(log))


def discover_bpmn_inductive(log: Union[EventLog, pd.DataFrame], noise_threshold: float = 0.0) -> BPMN:
    """
        Discovers a BPMN using the Inductive Miner algorithm

        Parameters
        --------------
        log
            Event log
        noise_threshold
            Noise threshold (default: 0.0)

        Returns
        --------------
        bpmn_diagram
            BPMN diagram
        """
    pt = discover_process_tree_inductive(log, noise_threshold)
    from pm4py.convert import convert_to_bpmn
    return convert_to_bpmn(pt)

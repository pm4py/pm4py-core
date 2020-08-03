import sys
from collections import Counter

import pandas
from pm4py.algo.discovery.dfg.adapters.pandas import df_statistics
from pm4py import util as pmutil
from pm4py.algo.discovery.dfg.versions import native as dfg_inst
from pm4py.algo.discovery.inductive.util import shared_constants
from pm4py.algo.discovery.inductive.util.petri_el_count import Counts
from pm4py.algo.discovery.inductive.versions.dfg.data_structures.subtree import SubtreeDFGBased
from pm4py.algo.discovery.inductive.versions.dfg.util import get_tree_repr_dfg_based
from pm4py.statistics.attributes.log import get as log_attributes_stats
from pm4py.statistics.end_activities.log import get as log_end_act_stats
from pm4py.statistics.start_activities.log import get as log_start_act_stats
from pm4py.statistics.attributes.pandas import get as pd_attributes_stats
from pm4py.statistics.end_activities.pandas import get as pd_end_act_stats
from pm4py.statistics.start_activities.pandas import get as pd_start_act_stats
from pm4py.objects.conversion.process_tree import converter as tree_to_petri
from pm4py.objects.conversion.log import converter as log_conversion
from pm4py.objects.dfg.utils import dfg_utils
from pm4py.util import exec_utils
from pm4py.algo.discovery.inductive.parameters import Parameters
from pm4py.algo.discovery.inductive.util import tree_consistency

sys.setrecursionlimit(shared_constants.REC_LIMIT)


def apply(log, parameters=None):
    """
    Apply the IMDF algorithm to a log obtaining a Petri net along with an initial and final marking

    Parameters
    -----------
    log
        Log
    parameters
        Parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> attribute of the log to use as activity name
            (default concept:name)

    Returns
    -----------
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    """
    if parameters is None:
        parameters = {}
    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, pmutil.constants.CASE_CONCEPT_NAME)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, pmutil.xes_constants.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, pmutil.xes_constants.DEFAULT_TIMESTAMP_KEY)
    if isinstance(log, pandas.core.frame.DataFrame):
        dfg = df_statistics.get_dfg_graph(log, case_id_glue=case_id_glue,
                                          activity_key=activity_key,
                                          timestamp_key=timestamp_key)
        start_activities = pd_start_act_stats.get_start_activities(log, parameters=parameters)
        end_activities = pd_end_act_stats.get_end_activities(log, parameters=parameters)
        activities = pd_attributes_stats.get_attribute_values(log, activity_key, parameters=parameters)
        return apply_dfg(dfg, activities=activities, start_activities=start_activities, end_activities=end_activities, parameters=parameters)
    log = log_conversion.apply(log, parameters, log_conversion.TO_EVENT_LOG)
    tree = apply_tree(log, parameters=parameters)
    net, initial_marking, final_marking = tree_to_petri.apply(tree)
    return net, initial_marking, final_marking


def apply_variants(variants, parameters=None):
    """
    Apply the IMDF algorithm to a dictionary/list/set of variants obtaining a Petri net along with an initial and final marking

    Parameters
    -----------
    variants
        Dictionary/list/set of variants in the log
    parameters
        Parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> attribute of the log to use as activity name
            (default concept:name)

    Returns
    -----------
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    """
    if parameters is None:
        parameters = {}
    dfg, list_act, start_activities, end_activities = dfg_utils.get_dfg_sa_ea_act_from_variants(variants, parameters=parameters)
    return apply_dfg(dfg, parameters=parameters, start_activities=start_activities, end_activities=end_activities, activities=list_act)


def apply_tree_variants(variants, parameters=None):
    """
    Apply the IMDF algorithm to a dictionary/list/set of variants a log obtaining a process tree

    Parameters
    ----------
    variants
        Dictionary/list/set of variants in the log
    parameters
        Parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> attribute of the log to use as activity name
            (default concept:name)

    Returns
    ----------
    tree
        Process tree
    """
    if parameters is None:
        parameters = {}
    dfg, list_act, start_activities, end_activities = dfg_utils.get_dfg_sa_ea_act_from_variants(variants, parameters=parameters)
    return apply_tree_dfg(dfg, parameters=parameters, start_activities=start_activities, end_activities=end_activities, activities=list_act)


def apply_tree(log, parameters=None):
    """
    Apply the IMDF algorithm to a log obtaining a process tree

    Parameters
    ----------
    log
        Log
    parameters
        Parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> attribute of the log to use as activity name
            (default concept:name)

    Returns
    ----------
    tree
        Process tree
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, pmutil.xes_constants.DEFAULT_NAME_KEY)

    # get the DFG
    dfg = [(k, v) for k, v in dfg_inst.apply(log, parameters={
        pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}).items() if v > 0]

    # gets the start activities from the log
    start_activities = log_start_act_stats.get_start_activities(log, parameters=parameters)
    # gets the end activities from the log
    end_activities = log_end_act_stats.get_end_activities(log, parameters=parameters)

    # get the activities in the log
    activities = log_attributes_stats.get_attribute_values(log, activity_key)

    # check if the log contains empty traces
    contains_empty_traces = False
    traces_length = [len(trace) for trace in log]
    if traces_length:
        contains_empty_traces = min([len(trace) for trace in log]) == 0

    return apply_tree_dfg(dfg, parameters=parameters, activities=activities, contains_empty_traces=contains_empty_traces,
                          start_activities=start_activities, end_activities=end_activities)


def apply_dfg(dfg, parameters=None, activities=None, contains_empty_traces=False, start_activities=None,
              end_activities=None):
    """
    Apply the IMDF algorithm to a DFG graph obtaining a Petri net along with an initial and final marking

    Parameters
    -----------
    dfg
        Directly-Follows graph
    parameters
        Parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> attribute of the log to use as activity name
            (default concept:name)
    activities
        Activities of the process (default None)
    contains_empty_traces
        Boolean value that is True if the event log from which the DFG has been extracted contains empty traces
    start_activities
        If provided, the start activities of the log
    end_activities
        If provided, the end activities of the log

    Returns
    -----------
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    """
    if parameters is None:
        parameters = {}

    tree = apply_tree_dfg(dfg, parameters=parameters, activities=activities, contains_empty_traces=contains_empty_traces,
                          start_activities=start_activities, end_activities=end_activities)
    net, initial_marking, final_marking = tree_to_petri.apply(tree)

    return net, initial_marking, final_marking


def apply_tree_dfg(dfg, parameters=None, activities=None, contains_empty_traces=False, start_activities=None,
                   end_activities=None):
    """
    Apply the IMDF algorithm to a DFG graph obtaining a process tree

    Parameters
    ----------
    dfg
        Directly-follows graph
    parameters
        Parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> attribute of the log to use as activity name
            (default concept:name)
    activities
        Activities of the process (default None)
    contains_empty_traces
        Boolean value that is True if the event log from which the DFG has been extracted contains empty traces
    start_activities
        If provided, the start activities of the log
    end_activities
        If provided, the end activities of the log

    Returns
    ----------
    tree
        Process tree
    """
    if parameters is None:
        parameters = {}

    noise_threshold = exec_utils.get_param_value(Parameters.NOISE_THRESHOLD, parameters, 0.0)

    if type(dfg) is Counter or type(dfg) is dict:
        newdfg = []
        for key in dfg:
            value = dfg[key]
            newdfg.append((key, value))
        dfg = newdfg

    c = Counts()
    s = SubtreeDFGBased(dfg, dfg, dfg, activities, c, 0, noise_threshold=noise_threshold,
                        initial_start_activities=start_activities,
                        initial_end_activities=end_activities)

    tree_repr = get_tree_repr_dfg_based.get_repr(s, 0, contains_empty_traces=contains_empty_traces)
    # Ensures consistency to the parent pointers in the process tree
    tree_consistency.fix_parent_pointers(tree_repr)
    # Fixes a 1 child XOR that is added when single-activities flowers are found
    tree_consistency.fix_one_child_xor_flower(tree_repr)

    return tree_repr

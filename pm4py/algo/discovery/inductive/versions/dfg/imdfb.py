import sys
from collections import Counter

from pm4py import util as pmutil
from pm4py.algo.discovery.dfg.versions import native as dfg_inst
from pm4py.algo.discovery.inductive.util import shared_constants
from pm4py.algo.discovery.inductive.util.petri_el_count import Counts
from pm4py.algo.discovery.inductive.versions.dfg.data_structures.subtree_imdfb import SubtreeB
from pm4py.algo.discovery.inductive.versions.dfg.util import get_tree_repr_imdfb
from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.algo.filtering.log.end_activities import end_activities_filter
from pm4py.algo.filtering.log.start_activities import start_activities_filter
from pm4py.objects.conversion.process_tree import factory as tree_to_petri
from pm4py.objects.log.util import xes as xes_util

sys.setrecursionlimit(shared_constants.REC_LIMIT)


def apply(log, parameters):
    """
    Apply the IMDF algorithm to a log obtaining a Petri net along with an initial and final marking

    Parameters
    -----------
    log
        Log
    parameters
        Parameters of the algorithm, including:
            pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY -> attribute of the log to use as activity name
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
    if pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_util.DEFAULT_NAME_KEY
    if pmutil.constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY] = parameters[
            pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY]
    activity_key = parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY]
    # apply the reduction by default only on very small logs
    enable_reduction = parameters["enable_reduction"] if "enable_reduction" in parameters else True

    # get the DFG
    dfg = [(k, v) for k, v in dfg_inst.apply(log, parameters={
        pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}).items() if v > 0]

    # get the activities in the log
    activities = attributes_filter.get_attribute_values(log, activity_key)

    # gets the start activities from the log
    start_activities = list(start_activities_filter.get_start_activities(log, parameters=parameters).keys())
    # gets the end activities from the log
    end_activities = list(end_activities_filter.get_end_activities(log, parameters=parameters).keys())

    # check if the log contains empty traces
    contains_empty_traces = False
    traces_length = [len(trace) for trace in log]
    if traces_length:
        contains_empty_traces = min([len(trace) for trace in log]) == 0

    net, initial_marking, final_marking = apply_dfg(dfg, parameters=parameters, activities=activities,
                                                    contains_empty_traces=contains_empty_traces,
                                                    start_activities=start_activities, end_activities=end_activities)

    """if enable_reduction:
        vis_trans = [x for x in net.transitions if x.label]
        hid_trans = [x for x in net.transitions if x.label is None]
        if vis_trans:
            ratio = len(hid_trans) / len(vis_trans)

            if ratio < 2.0:
                # avoid reducting too much complicated processes
                reduction_parameters = copy(parameters)
                if "is_reduction" not in reduction_parameters:
                    reduction_parameters["is_reduction"] = True
                if "thread_maximum_ex_time" not in reduction_parameters:
                    reduction_parameters["thread_maximum_ex_time"] = shared_constants.RED_MAX_THR_EX_TIME

                # do the replay
                aligned_traces = token_replay.apply(log, net, initial_marking, final_marking,
                                                    parameters=reduction_parameters)

                # apply petri_reduction technique in order to simplify the Petri net
                net = petri_cleaning.petri_reduction_treplay(net, parameters={"aligned_traces": aligned_traces})"""

    return net, initial_marking, final_marking


def apply_tree(log, parameters):
    """
    Apply the IMDF algorithm to a log obtaining a process tree

    Parameters
    ----------
    log
        Log
    parameters
        Parameters of the algorithm, including:
            pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY -> attribute of the log to use as activity name
            (default concept:name)

    Returns
    ----------
    tree
        Process tree
    """
    if parameters is None:
        parameters = {}
    if pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_util.DEFAULT_NAME_KEY
    activity_key = parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY]

    # get the DFG
    dfg = [(k, v) for k, v in dfg_inst.apply(log, parameters={
        pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}).items() if v > 0]

    # gets the start activities from the log
    start_activities = start_activities_filter.get_start_activities(log, parameters=parameters)
    # gets the end activities from the log
    end_activities = end_activities_filter.get_end_activities(log, parameters=parameters)

    # get the activities in the log
    activities = attributes_filter.get_attribute_values(log, activity_key)

    # check if the log contains empty traces
    contains_empty_traces = False
    traces_length = [len(trace) for trace in log]
    if traces_length:
        contains_empty_traces = min([len(trace) for trace in log]) == 0

    return apply_tree_dfg(dfg, parameters, activities=activities, contains_empty_traces=contains_empty_traces,
                          start_activities=start_activities, end_activities=end_activities)


def apply_dfg(dfg, parameters, activities=None, contains_empty_traces=False, start_activities=None,
              end_activities=None):
    """
    Apply the IMDF algorithm to a DFG graph obtaining a Petri net along with an initial and final marking

    Parameters
    -----------
    dfg
        Directly-Follows graph
    parameters
        Parameters of the algorithm, including:
            pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY -> attribute of the log to use as activity name
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
    tree = apply_tree_dfg(dfg, parameters, activities=activities, contains_empty_traces=contains_empty_traces,
                          start_activities=start_activities, end_activities=end_activities)
    net, initial_marking, final_marking = tree_to_petri.apply(tree)

    return net, initial_marking, final_marking


def apply_tree_dfg(dfg, parameters, activities=None, contains_empty_traces=False, start_activities=None,
                   end_activities=None):
    """
    Apply the IMDF algorithm to a DFG graph obtaining a process tree

    Parameters
    ----------
    dfg
        Directly-follows graph
    parameters
        Parameters of the algorithm, including:
            pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY -> attribute of the log to use as activity name
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

    noise_threshold = shared_constants.NOISE_THRESHOLD

    if "noiseThreshold" in parameters:
        noise_threshold = parameters["noiseThreshold"]

    if type(dfg) is Counter or type(dfg) is dict:
        newdfg = []
        for key in dfg:
            value = dfg[key]
            newdfg.append((key, value))
        dfg = newdfg

    c = Counts()
    s = SubtreeB(dfg, dfg, dfg, activities, c, 0, noise_threshold=noise_threshold, start_activities=start_activities,
                 end_activities=end_activities, initial_start_activities=start_activities,
                 initial_end_activities=end_activities)

    tree_repr = get_tree_repr_imdfb.get_repr(s, 0, contains_empty_traces=contains_empty_traces)

    return tree_repr

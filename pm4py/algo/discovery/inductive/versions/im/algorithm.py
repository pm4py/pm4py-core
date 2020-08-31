from pm4py import util as pmutil
from pm4py.algo.discovery.inductive.util.petri_el_count import Counts
from pm4py.algo.discovery.inductive.versions.im.util import get_tree_repr_implain
from pm4py.algo.discovery.inductive.versions.im.data_structures import subtree_plain as subtree
from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.algo.filtering.log.end_activities import end_activities_filter
from pm4py.algo.filtering.log.start_activities import start_activities_filter
from pm4py.algo.discovery.dfg.versions import native as dfg_inst
from pm4py.objects.conversion.process_tree import converter as tree_to_petri
from pm4py.algo.discovery.inductive.parameters import Parameters
from pm4py.util import exec_utils
from pm4py.objects.conversion.log import converter
from pm4py.objects.process_tree import util
from pm4py.objects.log.util import filtering_utils
from pm4py.util import constants, xes_constants
from pm4py.objects.log.log import EventLog, Trace, Event
import pandas as pd
from pm4py.statistics.variants.pandas import get as variants_get
from pm4py.algo.discovery.inductive.util import tree_consistency


def apply(log, parameters=None):
    """
    Apply the IM algorithm to a log obtaining a Petri net along with an initial and final marking

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
    if type(log) is pd.DataFrame:
        vars = variants_get.get_variants_count(log, parameters=parameters)
        return apply_variants(vars, parameters=parameters)
    else:
        log = converter.apply(log, parameters=parameters)
        net, initial_marking, final_marking = tree_to_petri.apply(apply_tree(log, parameters))
        return net, initial_marking, final_marking


def apply_variants(variants, parameters=None):
    """
    Apply the IM algorithm to a dictionary of variants, obtaining a Petri net along with an initial and final marking

    Parameters
    -----------
    variants
        Variants
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
    net, im, fm = tree_to_petri.apply(apply_tree_variants(variants, parameters=parameters))
    return net, im, fm


def apply_tree(log, parameters=None):
    """
    Apply the IM algorithm to a log obtaining a process tree

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
    process_tree
        Process tree
    """
    if parameters is None:
        parameters = {}

    if type(log) is pd.DataFrame:
        vars = variants_get.get_variants_count(log, parameters=parameters)
        return apply_tree_variants(vars, parameters=parameters)
    else:
        activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters,
                                                  pmutil.xes_constants.DEFAULT_NAME_KEY)

        log = converter.apply(log, parameters=parameters)
        # since basic IM is influenced once per variant, it makes sense to keep one trace per variant
        log = filtering_utils.keep_one_trace_per_variant(log, parameters=parameters)
        # keep only the activity attribute (since the others are not used)
        log = filtering_utils.keep_only_one_attribute_per_event(log, activity_key)

        dfg = [(k, v) for k, v in dfg_inst.apply(log, parameters=parameters).items() if v > 0]
        c = Counts()
        activities = attributes_filter.get_attribute_values(log, activity_key)
        start_activities = list(start_activities_filter.get_start_activities(log, parameters=parameters).keys())
        end_activities = list(end_activities_filter.get_end_activities(log, parameters=parameters).keys())
        contains_empty_traces = False
        traces_length = [len(trace) for trace in log]
        if traces_length:
            contains_empty_traces = min([len(trace) for trace in log]) == 0

        recursion_depth = 0
        sub = subtree.make_tree(log, dfg, dfg, dfg, activities, c, recursion_depth, 0.0, start_activities,
                                end_activities,
                                start_activities, end_activities, parameters)

        process_tree = get_tree_repr_implain.get_repr(sub, 0, contains_empty_traces=contains_empty_traces)
        # Ensures consistency to the parent pointers in the process tree
        tree_consistency.fix_parent_pointers(process_tree)
        # Fixes a 1 child XOR that is added when single-activities flowers are found
        tree_consistency.fix_one_child_xor_flower(process_tree)
        # folds the process tree (to simplify it in case fallthroughs/filtering is applied)
        process_tree = util.fold(process_tree)

        return process_tree


def apply_tree_variants(variants, parameters=None):
    """
    Apply the IM algorithm to a dictionary of variants obtaining a process tree

    Parameters
    ----------
    variants
        Variants
    parameters
        Parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> attribute of the log to use as activity name
            (default concept:name)

    Returns
    ----------
    process_tree
        Process tree
    """
    log = EventLog()
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)

    var_keys = list(variants.keys())
    for var in var_keys:
        trace = Trace()
        activities = var.split(constants.DEFAULT_VARIANT_SEP)
        for act in activities:
            trace.append(Event({activity_key: act}))
        log.append(trace)

    return apply_tree(log, parameters=parameters)

from pm4py.objects.process_tree import regex
from pm4py.algo.filtering.log.variants import variants_filter as variants_module
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY
from pm4py.objects.log.util import xes
import re

def apply(log, tree, parameters=None):
    """
    Check the fitness of the log against the process tree

    NB: The conformance check is not yet working with trees containing an AND and/or an OR operator!

    Parameters
    ------------
    log
        Event log
    tree
        Process tree
    parameters
        Parameters of the algorithm, including the activity key

    Returns
    -------------
    list_fitness
        List of booleans values (True whether the case is fit, False otherwise)
    """
    if parameters is None:
        parameters = {}

    variants_idxs = variants_module.get_variants_from_log_trace_idx(log, parameters=parameters)
    one_tr_per_var = []
    variants_list = []
    for index_variant, variant in enumerate(variants_idxs):
        variants_list.append(variant)

    for variant in variants_list:
        one_tr_per_var.append(log[variants_idxs[variant][0]])

    reg, mapping = regex.pt_to_regex(tree)
    reg = re.compile(reg)

    all_trace_fitness = []
    for index, trace in enumerate(one_tr_per_var):
        all_trace_fitness.append(apply_trace(trace, tree, reg=reg, mapping=mapping, parameters=parameters))

    al_idx = {}
    for index_variant, variant in enumerate(variants_idxs):
        for trace_idx in variants_idxs[variant]:
            al_idx[trace_idx] = all_trace_fitness[index_variant]

    f_result = []
    for i in range(len(log)):
        f_result.append(al_idx[i])

    return f_result

def apply_trace(trace, tree, reg=None, mapping=None, parameters=None):
    """
    Check the fitness of the trace against the process tree

    NB: The conformance check is not yet working with trees containing an AND and/or an OR operator!

    Parameters
    ------------
    trace
        Trace
    tree
        Process tree
    parameters
        Parameters of the algorithm, including the activity key

    Returns
    -------------
    boolean
        Boolean (True whether the trace is fit, False otherwise)
    """
    if parameters is None:
        parameters = {}

    activity_key = parameters[PARAMETER_CONSTANT_ACTIVITY_KEY] if PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY

    if reg is None:
        reg, mapping = regex.pt_to_regex(tree)
        reg = re.compile(reg)

    trace_str = "".join([mapping[x[activity_key]] for x in trace if x[activity_key] in mapping])

    match = re.match(reg, trace_str)

    if match is not None:
        stru = str(match)
        if "match='" in stru:
            stru = str(match).split("match='")[1].split("'")[0]
        elif "match=\"" in stru:
            stru = str(match).split("match=\"")[1].split("\"")[0]
        else:
            raise Exception("match not contained in the match")
        if len(stru) == 0:
            return False
        return True
    else:
        return False

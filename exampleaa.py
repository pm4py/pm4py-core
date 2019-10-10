import psutil
import ray

import heapq
import sys
from copy import copy

import numpy as np

import pm4py
from pm4py import util as pm4pyutil
from pm4py.algo.conformance import alignments
from pm4py.objects import petri
from pm4py.objects.petri.importer import pnml as petri_importer
from pm4py.objects.log import log as log_implementation
from pm4py.objects.log.util.xes import DEFAULT_NAME_KEY
from pm4py.objects.petri.synchronous_product import construct_cost_aware
from pm4py.objects.petri.utils import construct_trace_net_cost_aware
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY
from pm4py.util.lp import factory as lp_solver_factory

from pm4py.algo.conformance.alignments.versions.state_equation_a_star import PARAM_TRACE_COST_FUNCTION
from pm4py.algo.conformance.alignments.versions.state_equation_a_star import PARAM_MODEL_COST_FUNCTION
from pm4py.algo.conformance.alignments.versions.state_equation_a_star import PARAM_SYNC_COST_FUNCTION
from pm4py.algo.conformance.alignments.versions.state_equation_a_star import DEFAULT_LP_SOLVER_VARIANT
from pm4py.algo.conformance.alignments.versions.state_equation_a_star import PARAM_ALIGNMENT_RESULT_IS_SYNC_PROD_AWARE
from pm4py.algo.conformance.alignments.versions.state_equation_a_star import PARAM_TRACE_NET_COSTS
from pm4py.algo.conformance.alignments.versions.state_equation_a_star import TRACE_NET_CONSTR_FUNCTION
from pm4py.algo.conformance.alignments.versions.state_equation_a_star import TRACE_NET_COST_AWARE_CONSTR_FUNCTION
from pm4py.algo.conformance.alignments.versions.state_equation_a_star import PARAMETER_VARIANT_DELIMITER
from pm4py.algo.conformance.alignments.versions.state_equation_a_star import DEFAULT_VARIANT_DELIMITER
from pm4py.algo.conformance.alignments.versions.state_equation_a_star import PARAMETERS
from pm4py.algo.conformance.alignments.versions.state_equation_a_star import apply_from_variants_list_petri_string

from pm4py.algo.conformance import alignments as ali
from pm4py.algo.conformance.alignments import factory as align_factory
import math

num_cpus = psutil.cpu_count(logical=False)

ray.init(num_cpus=num_cpus)

@ray.remote
def apply_from_variants_list_ray(var_list, petri_net_string, parameters=None):
    """
    Apply the alignments from the specification of a list of variants in the log

    Parameters
    -------------
    var_list
        List of variants (for each item, the first entry is the variant itself, the second entry may be the number of cases)
    petri_net_string
        String representing the accepting Petri net

    Returns
    --------------
    dictio_alignments
        Dictionary that assigns to each variant its alignment
    """
    if parameters is None:
        parameters = {}

    res = apply_from_variants_list_petri_string(var_list, petri_net_string, parameters=parameters)
    return res


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

def apply_log_ray(log, petri_net, initial_marking, final_marking, parameters=None, version=align_factory.VERSION_STATE_EQUATION_A_STAR):
    if parameters is None:
        parameters = dict()
    activity_key = parameters[
        PARAMETER_CONSTANT_ACTIVITY_KEY] if PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else DEFAULT_NAME_KEY
    model_cost_function = parameters[
        PARAM_MODEL_COST_FUNCTION] if PARAM_MODEL_COST_FUNCTION in parameters else None
    sync_cost_function = parameters[
        PARAM_SYNC_COST_FUNCTION] if PARAM_SYNC_COST_FUNCTION in parameters else None
    if model_cost_function is None or sync_cost_function is None:
        # reset variables value
        model_cost_function = dict()
        sync_cost_function = dict()
        for t in petri_net.transitions:
            if t.label is not None:
                model_cost_function[t] = ali.utils.STD_MODEL_LOG_MOVE_COST
                sync_cost_function[t] = 0
            else:
                model_cost_function[t] = 1

    parameters[pm4py.util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = activity_key
    parameters[
        PARAM_MODEL_COST_FUNCTION] = model_cost_function
    parameters[
        PARAM_SYNC_COST_FUNCTION] = sync_cost_function
    best_worst_cost = align_factory.VERSIONS_COST[version](petri_net, initial_marking, final_marking, parameters=parameters)

    variants_idxs = parameters[align_factory.VARIANTS_IDX] if align_factory.VARIANTS_IDX in parameters else None
    if variants_idxs is None:
        variants_idxs = align_factory.variants_module.get_variants_from_log_trace_idx(log, parameters=parameters)
    variants_list = [[x, len(y)] for x, y in variants_idxs.items()]

    petri_net_string = align_factory.petri_exporter.export_petri_as_string(petri_net, initial_marking, final_marking)

    n = math.ceil(len(variants_list)/num_cpus)

    variants_list_split = list(chunks(variants_list, n))

    results = ray.get([apply_from_variants_list_ray.remote(x, petri_net_string) for x in variants_list_split])

    al_idx = {}
    for index, el in enumerate(variants_list_split):
        for index2, var_item in enumerate(el):
            variant = var_item[0]
            for trace_idx in variants_idxs[variant]:
                al_idx[trace_idx] = results[index][variant]

    alignments = []
    for i in range(len(log)):
        alignments.append(al_idx[i])

    # assign fitness to traces
    for index, align in enumerate(alignments):
        unfitness_upper_part = align['cost'] // ali.utils.STD_MODEL_LOG_MOVE_COST
        if unfitness_upper_part == 0:
            align['fitness'] = 1
        elif (len(log[index]) + best_worst_cost) > 0:
            align['fitness'] = 1 - (
                    (align['cost'] // ali.utils.STD_MODEL_LOG_MOVE_COST) / (len(log[index]) + best_worst_cost))
        else:
            align['fitness'] = 0

    return alignments

if __name__ == "__main__":
    import pm4pycvxopt
    from pm4py.objects.log.importer.xes import factory as xes_importer
    from pm4py.algo.discovery.inductive import factory as inductive_miner
    from pm4py.algo.conformance.alignments import factory as alignments_factory

    log = xes_importer.apply("tests/input_data/running-example.xes")
    net, im, fm = inductive_miner.apply(log)
    import time
    aa = time.time()
    aligned_traces = apply_log_ray(log, net, im, fm)
    bb = time.time()
    print(aligned_traces)
    print(bb-aa)
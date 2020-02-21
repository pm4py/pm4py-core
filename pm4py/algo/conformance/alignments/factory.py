from copy import copy

import pm4py
import sys
from pm4py import util as pmutil
from pm4py.algo.conformance.alignments import versions
from pm4py.objects.petri import align_utils
from pm4py.algo.conformance.alignments.versions.state_equation_a_star import PARAM_MODEL_COST_FUNCTION
from pm4py.algo.conformance.alignments.versions.state_equation_a_star import PARAM_SYNC_COST_FUNCTION
from pm4py.algo.conformance.alignments.versions.state_equation_a_star import PARAM_TRACE_COST_FUNCTION
from pm4py.statistics.variants.log import get as variants_module
from pm4py.objects.conversion.log import factory as log_converter
from pm4py.util import xes_constants as xes_util
from pm4py.util.xes_constants import DEFAULT_NAME_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY
import multiprocessing as mp
from pm4py.objects.petri.exporter.versions import pnml as petri_exporter
from pm4py.objects.petri import check_soundness
import math
import time

VERSION_STATE_EQUATION_A_STAR = 'state_equation_a_star'
VERSION_DIJKSTRA_NO_HEURISTICS = 'dijkstra_no_heuristics'


DEFAULT_VARIANT = VERSION_STATE_EQUATION_A_STAR

VERSIONS = {VERSION_STATE_EQUATION_A_STAR: versions.state_equation_a_star.apply, VERSION_DIJKSTRA_NO_HEURISTICS: versions.dijkstra_no_heuristics.apply}
VERSIONS_COST = {VERSION_STATE_EQUATION_A_STAR: versions.state_equation_a_star.get_best_worst_cost, VERSION_DIJKSTRA_NO_HEURISTICS: versions.dijkstra_no_heuristics.get_best_worst_cost}
VERSIONS_VARIANTS_LIST_MPROCESSING = {VERSION_STATE_EQUATION_A_STAR: versions.state_equation_a_star.apply_from_variants_list_petri_string_mprocessing, VERSION_DIJKSTRA_NO_HEURISTICS: versions.dijkstra_no_heuristics.apply_from_variants_list_petri_string_mprocessing}

VARIANTS_IDX = 'variants_idx'

PARAM_MAX_ALIGN_TIME_TRACE = "max_align_time_trace"
DEFAULT_MAX_ALIGN_TIME_TRACE = sys.maxsize
PARAM_MAX_ALIGN_TIME = "max_align_time"
DEFAULT_MAX_ALIGN_TIME = sys.maxsize

def apply(obj, petri_net, initial_marking, final_marking, parameters=None, version=DEFAULT_VARIANT):
    if parameters is None:
        parameters = {}
    if pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_util.DEFAULT_NAME_KEY
    if pmutil.constants.PARAMETER_CONSTANT_TIMESTAMP_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] = xes_util.DEFAULT_TIMESTAMP_KEY
    if pmutil.constants.PARAMETER_CONSTANT_CASEID_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_CASEID_KEY] = pmutil.constants.CASE_ATTRIBUTE_GLUE
    if isinstance(obj, pm4py.objects.log.log.Trace):
        return apply_trace(obj, petri_net, initial_marking, final_marking, parameters, version)
    else:
        return apply_log(log_converter.apply(obj, parameters, log_converter.TO_EVENT_LOG), petri_net, initial_marking,
                         final_marking, parameters, version)


def apply_trace(trace, petri_net, initial_marking, final_marking, parameters=None,
                version=DEFAULT_VARIANT):
    """
    apply alignments to a trace
    Parameters
    -----------
    trace
        :class:`pm4py.log.log.Trace` trace of events
    petri_net
        :class:`pm4py.objects.petri.petrinet.PetriNet` the model to use for the alignment
    initial_marking
        :class:`pm4py.objects.petri.petrinet.Marking` initial marking of the net
    final_marking
        :class:`pm4py.objects.petri.petrinet.Marking` final marking of the net
    version
        :class:`str` selected variant of the algorithm, possible values: {\'state_equation_a_star\'}
    parameters
        :class:`dict` parameters of the algorithm, for key \'state_equation_a_star\':
            pm4py.util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY -> Attribute in the log that contains the activity
            pm4py.algo.conformance.alignments.versions.state_equation_a_star.PARAM_MODEL_COST_FUNCTION ->
            mapping of each transition in the model to corresponding synchronous costs
            pm4py.algo.conformance.alignments.versions.state_equation_a_star.PARAM_SYNC_COST_FUNCTION ->
            mapping of each transition in the model to corresponding model cost
            pm4py.algo.conformance.alignments.versions.state_equation_a_star.PARAM_TRACE_COST_FUNCTION ->
            mapping of each index of the trace to a positive cost value
    Returns
    -----------
    alignment
        :class:`dict` with keys **alignment**, **cost**, **visited_states**, **queued_states** and
        **traversed_arcs**
        The alignment is a sequence of labels of the form (a,t), (a,>>), or (>>,t)
        representing synchronous/log/model-moves.
    """
    if parameters is None:
        parameters = copy({PARAMETER_CONSTANT_ACTIVITY_KEY: DEFAULT_NAME_KEY})
    if PARAM_TRACE_COST_FUNCTION not in parameters:
        parameters[PARAM_TRACE_COST_FUNCTION] = list(
            map(lambda e: align_utils.STD_MODEL_LOG_MOVE_COST, trace))
    return VERSIONS[version](trace, petri_net, initial_marking, final_marking, parameters)


def apply_log(log, petri_net, initial_marking, final_marking, parameters=None, version=DEFAULT_VARIANT):
    """
    apply alignments to a log
    Parameters
    -----------
    log
        object of the form :class:`pm4py.log.log.EventLog` event log
    petri_net
        :class:`pm4py.objects.petri.petrinet.PetriNet` the model to use for the alignment
    initial_marking
        :class:`pm4py.objects.petri.petrinet.Marking` initial marking of the net
    final_marking
        :class:`pm4py.objects.petri.petrinet.Marking` final marking of the net
    version
        :class:`str` selected variant of the algorithm, possible values: {\'state_equation_a_star\'}
    parameters
        :class:`dict` parameters of the algorithm,
        for key \'state_equation_a_star\':
            pm4py.util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY -> Attribute in the log that contains the activity
            pm4py.algo.conformance.alignments.versions.state_equation_a_star.PARAM_MODEL_COST_FUNCTION ->
            mapping of each transition in the model to corresponding synchronous costs
            pm4py.algo.conformance.alignments.versions.state_equation_a_star.PARAM_SYNC_COST_FUNCTION ->
            mapping of each transition in the model to corresponding model cost
            pm4py.algo.conformance.alignments.versions.state_equation_a_star.PARAM_TRACE_COST_FUNCTION ->
            mapping of each index of the trace to a positive cost value
    Returns
    -----------
    alignment
        :class:`list` of :class:`dict` with keys **alignment**, **cost**, **visited_states**, **queued_states** and
        **traversed_arcs**
        The alignment is a sequence of labels of the form (a,t), (a,>>), or (>>,t)
        representing synchronous/log/model-moves.
    """
    if parameters is None:
        parameters = dict()

    if not check_soundness.check_relaxed_soundness_net_in_fin_marking(petri_net, initial_marking, final_marking):
        raise Exception("trying to apply alignments on a Petri net that is not a relaxed sound net!!")


    start_time = time.time()
    activity_key = parameters[
        PARAMETER_CONSTANT_ACTIVITY_KEY] if PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else DEFAULT_NAME_KEY
    model_cost_function = parameters[
        PARAM_MODEL_COST_FUNCTION] if PARAM_MODEL_COST_FUNCTION in parameters else None
    sync_cost_function = parameters[
        PARAM_SYNC_COST_FUNCTION] if PARAM_SYNC_COST_FUNCTION in parameters else None
    max_align_time = parameters[PARAM_MAX_ALIGN_TIME] if PARAM_MAX_ALIGN_TIME in parameters else DEFAULT_MAX_ALIGN_TIME
    max_align_time_case = parameters[
        PARAM_MAX_ALIGN_TIME_TRACE] if PARAM_MAX_ALIGN_TIME_TRACE in parameters else DEFAULT_MAX_ALIGN_TIME_TRACE

    if model_cost_function is None or sync_cost_function is None:
        # reset variables value
        model_cost_function = dict()
        sync_cost_function = dict()
        for t in petri_net.transitions:
            if t.label is not None:
                model_cost_function[t] = align_utils.STD_MODEL_LOG_MOVE_COST
                sync_cost_function[t] = 0
            else:
                model_cost_function[t] = 1

    parameters[pm4py.util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = activity_key
    parameters[
        PARAM_MODEL_COST_FUNCTION] = model_cost_function
    parameters[
        PARAM_SYNC_COST_FUNCTION] = sync_cost_function
    parameters_best_worst = copy(parameters)
    if PARAM_MAX_ALIGN_TIME_TRACE in parameters_best_worst:
        del parameters_best_worst[PARAM_MAX_ALIGN_TIME_TRACE]

    best_worst_cost = VERSIONS_COST[version](petri_net, initial_marking, final_marking, parameters=parameters_best_worst)

    variants_idxs = parameters[VARIANTS_IDX] if VARIANTS_IDX in parameters else None
    if variants_idxs is None:
        variants_idxs = variants_module.get_variants_from_log_trace_idx(log, parameters=parameters)

    one_tr_per_var = []
    variants_list = []
    for index_variant, variant in enumerate(variants_idxs):
        variants_list.append(variant)

    for variant in variants_list:
        one_tr_per_var.append(log[variants_idxs[variant][0]])

    all_alignments = []
    for trace in one_tr_per_var:
        this_max_align_time = min(max_align_time_case, (max_align_time - (time.time() - start_time))*0.5)
        parameters[PARAM_MAX_ALIGN_TIME_TRACE] = this_max_align_time
        all_alignments.append(apply_trace(trace, petri_net, initial_marking, final_marking, parameters=copy(parameters),
                    version=version))

    al_idx = {}
    for index_variant, variant in enumerate(variants_idxs):
        for trace_idx in variants_idxs[variant]:
            al_idx[trace_idx] = all_alignments[index_variant]

    alignments = []
    for i in range(len(log)):
        alignments.append(al_idx[i])

    # assign fitness to traces
    for index, align in enumerate(alignments):
        if align is not None:
            unfitness_upper_part = align['cost'] // align_utils.STD_MODEL_LOG_MOVE_COST
            if unfitness_upper_part == 0:
                align['fitness'] = 1
            elif (len(log[index]) + best_worst_cost) > 0:
                align['fitness'] = 1 - (
                        (align['cost'] // align_utils.STD_MODEL_LOG_MOVE_COST) / (len(log[index]) + best_worst_cost))
            else:
                align['fitness'] = 0
    return alignments

def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

def apply_log_multiprocessing(log, petri_net, initial_marking, final_marking, parameters=None, version=DEFAULT_VARIANT):
    if parameters is None:
        parameters = dict()

    if not check_soundness.check_relaxed_soundness_net_in_fin_marking(petri_net, initial_marking, final_marking):
        raise Exception("trying to apply alignments on a Petri net that is not a relaxed sound net!!")

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
                model_cost_function[t] = align_utils.STD_MODEL_LOG_MOVE_COST
                sync_cost_function[t] = 0
            else:
                model_cost_function[t] = 1

    parameters[pm4py.util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = activity_key
    parameters[
        PARAM_MODEL_COST_FUNCTION] = model_cost_function
    parameters[
        PARAM_SYNC_COST_FUNCTION] = sync_cost_function
    parameters_best_worst = copy(parameters)
    if PARAM_MAX_ALIGN_TIME_TRACE in parameters_best_worst:
        del parameters_best_worst[PARAM_MAX_ALIGN_TIME_TRACE]

    best_worst_cost = VERSIONS_COST[version](petri_net, initial_marking, final_marking, parameters=parameters_best_worst)

    variants_idxs = parameters[VARIANTS_IDX] if VARIANTS_IDX in parameters else None
    if variants_idxs is None:
        variants_idxs = variants_module.get_variants_from_log_trace_idx(log, parameters=parameters)
    variants_list = [[x, len(y)] for x, y in variants_idxs.items()]

    no_cores = mp.cpu_count()

    petri_net_string = petri_exporter.export_petri_as_string(petri_net, initial_marking, final_marking)

    n = math.ceil(len(variants_list)/no_cores)

    variants_list_split = list(chunks(variants_list, n))

    # Define an output queue
    output = mp.Queue()

    processes = [mp.Process(target=VERSIONS_VARIANTS_LIST_MPROCESSING[version](output, x, petri_net_string, parameters=parameters)) for x in variants_list_split]

    # Run processes
    for p in processes:
        p.start()

    results = []
    for p in processes:
        result = output.get()
        results.append(result)

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
        if align is not None:
            unfitness_upper_part = align['cost'] // align_utils.STD_MODEL_LOG_MOVE_COST
            if unfitness_upper_part == 0:
                align['fitness'] = 1
            elif (len(log[index]) + best_worst_cost) > 0:
                align['fitness'] = 1 - (
                        (align['cost'] // align_utils.STD_MODEL_LOG_MOVE_COST) / (len(log[index]) + best_worst_cost))
            else:
                align['fitness'] = 0

    return alignments



from copy import copy

import pm4py
from pm4py.algo.conformance.alignments import versions
from pm4py.objects.petri import align_utils
from pm4py.statistics.variants.log import get as variants_module
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.util.xes_constants import DEFAULT_NAME_KEY
from pm4py.objects.petri import check_soundness
import time
from pm4py.util import exec_utils
from enum import Enum
import sys
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY


class Variants(Enum):
    VERSION_STATE_EQUATION_A_STAR = versions.state_equation_a_star
    VERSION_DIJKSTRA_NO_HEURISTICS = versions.dijkstra_no_heuristics
    VERSION_DIJKSTRA_LESS_MEMORY = versions.dijkstra_less_memory
    VERSION_STATE_EQUATION_LESS_MEMORY = versions.state_equation_less_memory


class Parameters(Enum):
    PARAM_TRACE_COST_FUNCTION = 'trace_cost_function'
    PARAM_MODEL_COST_FUNCTION = 'model_cost_function'
    PARAM_SYNC_COST_FUNCTION = 'sync_cost_function'
    PARAM_ALIGNMENT_RESULT_IS_SYNC_PROD_AWARE = 'ret_tuple_as_trans_desc'
    PARAM_TRACE_NET_COSTS = "trace_net_costs"
    TRACE_NET_CONSTR_FUNCTION = "trace_net_constr_function"
    TRACE_NET_COST_AWARE_CONSTR_FUNCTION = "trace_net_cost_aware_constr_function"
    PARAM_MAX_ALIGN_TIME_TRACE = "max_align_time_trace"
    PARAM_MAX_ALIGN_TIME = "max_align_time"
    PARAMETER_VARIANT_DELIMITER = "variant_delimiter"
    ACTIVITY_KEY = PARAMETER_CONSTANT_ACTIVITY_KEY
    VARIANTS_IDX = "variants_idx"


DEFAULT_VARIANT = Variants.VERSION_STATE_EQUATION_LESS_MEMORY
VERSION_STATE_EQUATION_A_STAR = Variants.VERSION_STATE_EQUATION_A_STAR
VERSION_DIJKSTRA_NO_HEURISTICS = Variants.VERSION_DIJKSTRA_NO_HEURISTICS
VERSION_DIJKSTRA_LESS_MEMORY = Variants.VERSION_DIJKSTRA_LESS_MEMORY

VERSIONS = {Variants.VERSION_DIJKSTRA_NO_HEURISTICS, Variants.VERSION_DIJKSTRA_NO_HEURISTICS,
            Variants.VERSION_DIJKSTRA_LESS_MEMORY}


def apply(obj, petri_net, initial_marking, final_marking, parameters=None, variant=DEFAULT_VARIANT):
    if parameters is None:
        parameters = {}
    if isinstance(obj, pm4py.objects.log.log.Trace):
        return apply_trace(obj, petri_net, initial_marking, final_marking, parameters=parameters, variant=variant)
    else:
        return apply_log(log_converter.apply(obj, parameters, log_converter.TO_EVENT_LOG), petri_net, initial_marking,
                         final_marking, parameters=parameters, variant=variant)


def apply_trace(trace, petri_net, initial_marking, final_marking, parameters=None,
                variant=DEFAULT_VARIANT):
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
    variant
        selected variant of the algorithm, possible values: {\'Variants.VERSION_STATE_EQUATION_A_STAR, Variants.VERSION_DIJKSTRA_NO_HEURISTICS \'}
    parameters
        :class:`dict` parameters of the algorithm, for key \'state_equation_a_star\':
            Parameters.ACTIVITY_KEY -> Attribute in the log that contains the activity
            Parameters.PARAM_MODEL_COST_FUNCTION ->
            mapping of each transition in the model to corresponding synchronous costs
            Parameters.PARAM_SYNC_COST_FUNCTION ->
            mapping of each transition in the model to corresponding model cost
            Parameters.PARAM_TRACE_COST_FUNCTION ->
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
    return exec_utils.get_variant(variant).apply(trace, petri_net, initial_marking, final_marking,
                                                 parameters=parameters)


def apply_log(log, petri_net, initial_marking, final_marking, parameters=None, variant=DEFAULT_VARIANT):
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
    variant
        selected variant of the algorithm, possible values: {\'Variants.VERSION_STATE_EQUATION_A_STAR, Variants.VERSION_DIJKSTRA_NO_HEURISTICS \'}
    parameters
        :class:`dict` parameters of the algorithm,

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
    max_align_time = exec_utils.get_param_value(Parameters.PARAM_MAX_ALIGN_TIME, parameters,
                                                sys.maxsize)
    max_align_time_case = exec_utils.get_param_value(Parameters.PARAM_MAX_ALIGN_TIME_TRACE, parameters,
                                                     sys.maxsize)

    parameters_best_worst = copy(parameters)

    best_worst_cost = exec_utils.get_variant(variant).get_best_worst_cost(petri_net, initial_marking, final_marking,
                                                                          parameters=parameters_best_worst)

    variants_idxs = exec_utils.get_param_value(Parameters.VARIANTS_IDX, parameters, None)
    if variants_idxs is None:
        variants_idxs = variants_module.get_variants_from_log_trace_idx(log, parameters=parameters)

    one_tr_per_var = []
    variants_list = []
    for index_variant, var in enumerate(variants_idxs):
        variants_list.append(var)

    for var in variants_list:
        one_tr_per_var.append(log[variants_idxs[var][0]])

    all_alignments = []
    for trace in one_tr_per_var:
        this_max_align_time = min(max_align_time_case, (max_align_time - (time.time() - start_time)) * 0.5)
        parameters[Parameters.PARAM_MAX_ALIGN_TIME_TRACE] = this_max_align_time
        all_alignments.append(apply_trace(trace, petri_net, initial_marking, final_marking, parameters=copy(parameters),
                                          variant=variant))

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

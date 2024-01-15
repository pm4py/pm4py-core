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
from copy import copy

from pm4py.algo.conformance.alignments.petri_net import variants
from pm4py.objects.petri_net.utils import align_utils, check_soundness
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.util.xes_constants import DEFAULT_NAME_KEY, DEFAULT_TRACEID_KEY
from pm4py.objects.log.obj import Trace, Event
import time
from pm4py.util.lp import solver
from pm4py.util import exec_utils
from enum import Enum
import sys
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY, PARAMETER_CONSTANT_CASEID_KEY, CASE_CONCEPT_NAME
import importlib.util
from typing import Optional, Dict, Any, Union
from pm4py.objects.log.obj import EventLog, EventStream, Trace
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.util import typing, constants, pandas_utils
import pandas as pd


class Variants(Enum):
    VERSION_STATE_EQUATION_A_STAR = variants.state_equation_a_star
    VERSION_TWEAKED_STATE_EQUATION_A_STAR = variants.tweaked_state_equation_a_star
    VERSION_DIJKSTRA_NO_HEURISTICS = variants.dijkstra_no_heuristics
    VERSION_DIJKSTRA_LESS_MEMORY = variants.dijkstra_less_memory
    VERSION_DISCOUNTED_A_STAR = variants.discounted_a_star

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
    CASE_ID_KEY = PARAMETER_CONSTANT_CASEID_KEY
    ACTIVITY_KEY = PARAMETER_CONSTANT_ACTIVITY_KEY
    VARIANTS_IDX = "variants_idx"
    SHOW_PROGRESS_BAR = "show_progress_bar"
    CORES = 'cores'
    BEST_WORST_COST_INTERNAL = "best_worst_cost_internal"
    FITNESS_ROUND_DIGITS = "fitness_round_digits"
    SYNCHRONOUS = "synchronous_dijkstra"
    EXPONENT="theta"
    ENABLE_BEST_WORST_COST = "enable_best_worst_cost"


def __variant_mapper(variant):
    if type(variant) is str:
        if variant == "Variants.VERSION_STATE_EQUATION_A_STAR":
            variant = Variants.VERSION_STATE_EQUATION_A_STAR
        elif variant == "Variants.VERSION_TWEAKED_STATE_EQUATION_A_STAR":
            variant = Variants.VERSION_TWEAKED_STATE_EQUATION_A_STAR
        elif variant == "Variants.VERSION_DIJKSTRA_NO_HEURISTICS":
            variant = Variants.VERSION_DIJKSTRA_NO_HEURISTICS
        elif variant == "Variants.VERSION_DIJKSTRA_LESS_MEMORY":
            variant = Variants.VERSION_DIJKSTRA_LESS_MEMORY

    return variant


DEFAULT_VARIANT = Variants.VERSION_DIJKSTRA_LESS_MEMORY
if solver.DEFAULT_LP_SOLVER_VARIANT is not None:
    DEFAULT_VARIANT = __variant_mapper(constants.DEFAULT_ALIGNMENTS_VARIANT)

VERSION_STATE_EQUATION_A_STAR = Variants.VERSION_STATE_EQUATION_A_STAR
VERSION_DIJKSTRA_NO_HEURISTICS = Variants.VERSION_DIJKSTRA_NO_HEURISTICS
VERSION_DIJKSTRA_LESS_MEMORY = Variants.VERSION_DIJKSTRA_LESS_MEMORY

VERSIONS = {Variants.VERSION_DIJKSTRA_NO_HEURISTICS, Variants.VERSION_DIJKSTRA_NO_HEURISTICS,
            Variants.VERSION_DIJKSTRA_LESS_MEMORY}


def apply(obj: Union[EventLog, EventStream, pd.DataFrame, Trace], petri_net: PetriNet, initial_marking: Marking, final_marking: Marking, parameters: Optional[Dict[Any, Any]] = None, variant=DEFAULT_VARIANT) -> Union[typing.AlignmentResult, typing.ListAlignments]:
    if parameters is None:
        parameters = {}
    if isinstance(obj, Trace):
        return apply_trace(obj, petri_net, initial_marking, final_marking, parameters=parameters, variant=variant)
    else:
        return apply_log(obj, petri_net, initial_marking,
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

    variant = __variant_mapper(variant)
    parameters = copy(parameters)

    enable_best_worst_cost = exec_utils.get_param_value(Parameters.ENABLE_BEST_WORST_COST, parameters, True)

    ali = exec_utils.get_variant(variant).apply(trace, petri_net, initial_marking, final_marking,
                                                 parameters=parameters)

    trace_cost_function = exec_utils.get_param_value(Parameters.PARAM_TRACE_COST_FUNCTION, parameters, [])
    # Instead of using the length of the trace, use the sum of the trace cost function
    trace_cost_function_sum = sum(trace_cost_function)

    if enable_best_worst_cost:
        best_worst_cost = exec_utils.get_param_value(Parameters.BEST_WORST_COST_INTERNAL, parameters,
                                                     __get_best_worst_cost(petri_net, initial_marking, final_marking, variant, parameters))

        if ali is not None and best_worst_cost is not None:
            ltrace_bwc = trace_cost_function_sum + best_worst_cost

            fitness_num = ali['cost'] // align_utils.STD_MODEL_LOG_MOVE_COST
            fitness_den = ltrace_bwc // align_utils.STD_MODEL_LOG_MOVE_COST
            fitness = 1 - fitness_num / fitness_den if fitness_den > 0 else 0

            ali["fitness"] = fitness
            # returning also the best worst cost, for log fitness computation
            ali["bwc"] = ltrace_bwc

    return ali


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

    if solver.DEFAULT_LP_SOLVER_VARIANT is not None:
        if not check_soundness.check_easy_soundness_net_in_fin_marking(petri_net, initial_marking, final_marking):
            raise Exception("trying to apply alignments on a Petri net that is not a easy sound net!!")

    enable_best_worst_cost = exec_utils.get_param_value(Parameters.ENABLE_BEST_WORST_COST, parameters, True)

    variant = __variant_mapper(variant)

    start_time = time.time()
    max_align_time = exec_utils.get_param_value(Parameters.PARAM_MAX_ALIGN_TIME, parameters,
                                                sys.maxsize)
    max_align_time_case = exec_utils.get_param_value(Parameters.PARAM_MAX_ALIGN_TIME_TRACE, parameters,
                                                     sys.maxsize)

    variants_idxs, one_tr_per_var = __get_variants_structure(log, parameters)
    progress = __get_progress_bar(len(one_tr_per_var), parameters)

    if enable_best_worst_cost:
        best_worst_cost = __get_best_worst_cost(petri_net, initial_marking, final_marking, variant, parameters)
        parameters[Parameters.BEST_WORST_COST_INTERNAL] = best_worst_cost

    all_alignments = []
    for trace in one_tr_per_var:
        this_max_align_time = min(max_align_time_case, (max_align_time - (time.time() - start_time)) * 0.5)
        parameters[Parameters.PARAM_MAX_ALIGN_TIME_TRACE] = this_max_align_time
        all_alignments.append(apply_trace(trace, petri_net, initial_marking, final_marking, parameters=copy(parameters),
                                          variant=variant))
        if progress is not None:
            progress.update()

    alignments = __form_alignments(variants_idxs, all_alignments)
    __close_progress_bar(progress)

    return alignments


def apply_multiprocessing(log, petri_net, initial_marking, final_marking, parameters=None, variant=DEFAULT_VARIANT):
    """
    Applies the alignments using a process pool (multiprocessing)

    Parameters
    ---------------
    log
        Event log
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    parameters
        Parameters of the algorithm

    Returns
    ----------------
    aligned_traces
        Alignments
    """
    if parameters is None:
        parameters = {}

    import multiprocessing

    variant = __variant_mapper(variant)

    num_cores = exec_utils.get_param_value(Parameters.CORES, parameters, multiprocessing.cpu_count() - 2)

    enable_best_worst_cost = exec_utils.get_param_value(Parameters.ENABLE_BEST_WORST_COST, parameters, True)

    variants_idxs, one_tr_per_var = __get_variants_structure(log, parameters)

    if enable_best_worst_cost:
        best_worst_cost = __get_best_worst_cost(petri_net, initial_marking, final_marking, variant, parameters)
        parameters[Parameters.BEST_WORST_COST_INTERNAL] = best_worst_cost

    all_alignments = []

    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=num_cores) as executor:
        futures = []
        for trace in one_tr_per_var:
            futures.append(executor.submit(apply_trace, trace, petri_net, initial_marking, final_marking, parameters, str(variant)))
        progress = __get_progress_bar(len(one_tr_per_var), parameters)
        if progress is not None:
            alignments_ready = 0
            while alignments_ready != len(futures):
                current = 0
                for index, variant in enumerate(futures):
                    current = current + 1 if futures[index].done() else current
                if current > alignments_ready:
                    for i in range(0, current - alignments_ready):
                        progress.update()
                alignments_ready = current
        for index, variant in enumerate(futures):
            all_alignments.append(futures[index].result())
        __close_progress_bar(progress)

    alignments = __form_alignments(variants_idxs, all_alignments)

    return alignments


def __get_best_worst_cost(petri_net, initial_marking, final_marking, variant, parameters):
    parameters_best_worst = copy(parameters)

    best_worst_cost = exec_utils.get_variant(variant).get_best_worst_cost(petri_net, initial_marking, final_marking,
                                                                          parameters=parameters_best_worst)

    return best_worst_cost


def __get_variants_structure(log, parameters):
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, DEFAULT_NAME_KEY)

    variants_idxs = {}
    one_tr_per_var = []

    if pandas_utils.check_is_pandas_dataframe(log):
        case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME)
        traces = [tuple(x) for x in log.groupby(case_id_key)[activity_key].agg(list).to_dict().values()]
        for idx, trace in enumerate(traces):
            if trace not in variants_idxs:
                variants_idxs[trace] = [idx]
                case = Trace()
                for act in trace:
                    case.append(Event({activity_key: act}))
                one_tr_per_var.append(case)
            else:
                variants_idxs[trace].append(idx)
    else:
        log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)
        for idx, case in enumerate(log):
            trace = tuple(x[activity_key] for x in case)
            if trace not in variants_idxs:
                variants_idxs[trace] = [idx]
                one_tr_per_var.append(case)
            else:
                variants_idxs[trace].append(idx)

    return variants_idxs, one_tr_per_var


def __get_progress_bar(num_variants, parameters):
    show_progress_bar = exec_utils.get_param_value(Parameters.SHOW_PROGRESS_BAR, parameters, constants.SHOW_PROGRESS_BAR)
    progress = None
    if importlib.util.find_spec("tqdm") and show_progress_bar and num_variants > 1:
        from tqdm.auto import tqdm
        progress = tqdm(total=num_variants, desc="aligning log, completed variants :: ")
    return progress


def __form_alignments(variants_idxs, all_alignments):
    al_idx = {}
    for index_variant, variant in enumerate(variants_idxs):
        for trace_idx in variants_idxs[variant]:
            al_idx[trace_idx] = all_alignments[index_variant]

    alignments = []
    for i in range(len(al_idx)):
        alignments.append(al_idx[i])

    return alignments


def __close_progress_bar(progress):
    if progress is not None:
        progress.close()
    del progress


def get_diagnostics_dataframe(log, align_output, parameters=None):
    """
    Gets the diagnostics results of alignments (of a log) in a dataframe

    Parameters
    --------------
    log
        Event log
    align_output
        Output of the alignments

    Returns
    --------------
    dataframe
        Diagnostics dataframe
    """
    if parameters is None:
        parameters = {}

    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, DEFAULT_TRACEID_KEY)

    import pandas as pd

    diagn_stream = []

    for index in range(len(log)):
        case_id = log[index].attributes[case_id_key]

        cost = align_output[index]["cost"]
        fitness = align_output[index]["fitness"]
        is_fit = fitness == 1.0

        diagn_stream.append({"case_id": case_id, "cost": cost, "fitness": fitness, "is_fit": is_fit})

    return pandas_utils.instantiate_dataframe(diagn_stream)

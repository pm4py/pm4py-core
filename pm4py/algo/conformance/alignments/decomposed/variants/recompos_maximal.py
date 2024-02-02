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
import importlib.util
import sys
import time
from copy import copy

from pm4py.algo.conformance.alignments.petri_net.variants import state_equation_a_star
from pm4py.objects.log import obj as log_implementation
from pm4py.objects.log.obj import Trace
from pm4py.objects.log.util.xes import DEFAULT_NAME_KEY
from pm4py.objects.petri_net.utils import align_utils as utils, decomposition as decomp_utils
from pm4py.statistics.variants.log import get as variants_module
from pm4py.util import exec_utils
from pm4py.util import variants_util

from enum import Enum
from pm4py.util import constants, nx_utils

from typing import Optional, Dict, Any, Union
from pm4py.objects.log.obj import EventLog
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.util import typing
from pm4py.objects.conversion.log import converter as log_converter


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    BEST_WORST_COST = 'best_worst_cost'
    PARAM_TRACE_COST_FUNCTION = 'trace_cost_function'
    ICACHE = "icache"
    MCACHE = "mcache"
    PARAM_THRESHOLD_BORDER_AGREEMENT = "thresh_border_agreement"
    PARAMETER_VARIANT_DELIMITER = "variant_delimiter"
    PARAM_MODEL_COST_FUNCTION = 'model_cost_function'
    PARAM_SYNC_COST_FUNCTION = 'sync_cost_function'
    PARAM_TRACE_NET_COSTS = "trace_net_costs"
    PARAM_MAX_ALIGN_TIME = "max_align_time"
    PARAM_MAX_ALIGN_TIME_TRACE = "max_align_time_trace"
    SHOW_PROGRESS_BAR = "show_progress_bar"


def get_best_worst_cost(petri_net, initial_marking, final_marking, parameters=None):
    trace = log_implementation.Trace()

    best_worst, cf = align(trace, petri_net, initial_marking, final_marking, parameters=parameters)

    best_worst_cost = sum(cf[x] for x in best_worst['alignment']) // utils.STD_MODEL_LOG_MOVE_COST if best_worst else 0

    return best_worst_cost


def apply_from_variants_list_petri_string(var_list, petri_net_string, parameters=None):
    if parameters is None:
        parameters = {}

    from pm4py.objects.petri_net.importer.variants import pnml as petri_importer

    petri_net, initial_marking, final_marking = petri_importer.import_petri_from_string(petri_net_string)

    res = apply_from_variants_list(var_list, petri_net, initial_marking, final_marking, parameters=parameters)
    return res


def apply_from_variants_list(var_list, petri_net, initial_marking, final_marking, parameters=None):
    """
    Apply the alignments from the specification of a list of variants in the log

    Parameters
    -------------
    var_list
        List of variants (for each item, the first entry is the variant itself, the second entry may be the number of cases)
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    parameters
        Parameters of the algorithm (same as 'apply' method, plus 'variant_delimiter' that is , by default)

    Returns
    --------------
    dictio_alignments
        Dictionary that assigns to each variant its alignment
    """
    if parameters is None:
        parameters = {}

    log = log_implementation.EventLog()
    dictio_alignments = {}
    for varitem in var_list:
        variant = varitem[0]
        trace = variants_util.variant_to_trace(variant, parameters=parameters)
        log.append(trace)

    alignment = apply(log, petri_net, initial_marking, final_marking)

    for index, varitem in enumerate(var_list):
        variant = varitem[0]
        dictio_alignments[variant] = alignment[index]

    return dictio_alignments


def apply(log: EventLog, net: PetriNet, im: Marking, fm: Marking, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> typing.ListAlignments:
    """
    Apply the recomposition alignment approach
    to a log and a Petri net performing decomposition

    Parameters
    --------------
    log
        Event log
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    parameters
        Parameters of the algorithm

    Returns
    --------------
    aligned_traces
        For each trace, return its alignment
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    best_worst_cost = get_best_worst_cost(net, im, fm, parameters=parameters)
    parameters[Parameters.BEST_WORST_COST] = best_worst_cost

    list_nets = decomp_utils.decompose(net, im, fm)

    return apply_log(log, list_nets, parameters=parameters)


def apply_log(log, list_nets, parameters=None):
    """
    Apply the recomposition alignment approach
    to a log and a decomposed Petri net

    Parameters
    --------------
    log
        Log
    list_nets
        Decomposition
    parameters
        Parameters of the algorithm

    Returns
    --------------
    aligned_traces
        For each trace, return its alignment
    """
    if parameters is None:
        parameters = {}

    show_progress_bar = exec_utils.get_param_value(Parameters.SHOW_PROGRESS_BAR, parameters, constants.SHOW_PROGRESS_BAR)
    icache = exec_utils.get_param_value(Parameters.ICACHE, parameters, dict())
    mcache = exec_utils.get_param_value(Parameters.MCACHE, parameters, dict())

    parameters[Parameters.ICACHE] = icache
    parameters[Parameters.MCACHE] = mcache

    variants_idxs = variants_module.get_variants_from_log_trace_idx(log, parameters=parameters)

    progress = None
    if importlib.util.find_spec("tqdm") and show_progress_bar:
        from tqdm.auto import tqdm
        progress = tqdm(total=len(variants_idxs),
                        desc="aligning log with decomposition/recomposition, completed variants :: ")

    one_tr_per_var = []
    variants_list = []
    for index_variant, variant in enumerate(variants_idxs):
        variants_list.append(variant)
    for variant in variants_list:
        one_tr_per_var.append(log[variants_idxs[variant][0]])
    all_alignments = []
    max_align_time = exec_utils.get_param_value(Parameters.PARAM_MAX_ALIGN_TIME, parameters, sys.maxsize)
    start_time = time.time()
    for index, trace in enumerate(one_tr_per_var):
        this_time = time.time()
        if this_time - start_time <= max_align_time:
            alignment = apply_trace(trace, list_nets, parameters=parameters)
        else:
            alignment = None
        if progress is not None:
            progress.update()
        all_alignments.append(alignment)
    al_idx = {}
    for index_variant, variant in enumerate(variants_idxs):
        for trace_idx in variants_idxs[variant]:
            al_idx[trace_idx] = all_alignments[index_variant]
    alignments = []
    for i in range(len(log)):
        alignments.append(al_idx[i])
    # gracefully close progress bar
    if progress is not None:
        progress.close()
    del progress
    return alignments


def get_acache(cons_nets):
    """
    Calculates the A-Cache of the given decomposition

    Parameters
    --------------
    cons_nets
        List of considered nets

    Returns
    --------------
    acache
        A-Cache
    """
    ret = {}
    for index, el in enumerate(cons_nets):
        for lab in el[0].lvis_labels:
            if lab not in ret:
                ret[lab] = []
            ret[lab].append(index)

    return ret


def get_alres(al):
    """
    Gets a description of the alignment for the border agreement

    Parameters
    --------------
    al
        Alignment

    Returns
    --------------
    alres
        Description of the alignment
    """
    if al is not None:
        ret = {}
        for index, el in enumerate(al["alignment"]):
            if el[1][0] is not None and el[1][0] != ">>":
                if not el[1][0] in ret:
                    ret[el[1][0]] = []

                if el[1][1] is not None and el[1][1] != ">>":
                    ret[el[1][0]].append(0)
                else:
                    ret[el[1][0]].append(1)
        return ret
    return None


def order_nodes_second_round(to_visit, G0):
    """
    Orders the second round of nodes to visit to reconstruct the alignment

    Parameters
    ---------------
    to_visit
        Node to visit
    G0
        Recomposition graph

    Returns
    ---------------
    to_visit
        Sorted list of nodes
    """
    cont_loop = True
    while cont_loop:
        cont_loop = False
        i = 0
        while i < len(to_visit):
            j = i + 1
            must_break = False
            while j < len(to_visit):
                if to_visit[j] != to_visit[i]:
                    edg = [e for e in G0.edges if e[0] == to_visit[j] and e[1] == to_visit[i]]
                    edg2 = [e for e in G0.edges if e[1] == to_visit[i] and e[0] == to_visit[j]]
                    if edg and not edg2:
                        to_visit[i], to_visit[j] = to_visit[j], to_visit[i]
                        must_break = True
                        break
                j = j + 1
            if must_break:
                cont_loop = True
                break
            i = i + 1
    return to_visit


def recompose_alignment(cons_nets, cons_nets_result):
    """
    Alignment recomposition

    Parameters
    ---------------
    cons_nets
        Decomposed Petri net elements
    cons_nets_result
        Result of the alignments on such elements
    parameters
        Parameters of the method

    Returns
    ---------------
    alignment
        Recomposed alignment
    """
    G0 = nx_utils.DiGraph()
    for i in range(len(cons_nets_result)):
        if cons_nets_result[i] is not None:
            G0.add_node(i)
    for i in range(len(cons_nets_result)):
        if cons_nets_result[i] is not None:
            for j in range(len(cons_nets_result)):
                if cons_nets_result[j] is not None:
                    if i != j:
                        if cons_nets_result[i]["alignment"][-1][1] == cons_nets_result[j]["alignment"][0][1]:
                            G0.add_edge(i, j)
    all_available = [i for i in range(len(cons_nets_result)) if cons_nets_result[i] is not None]
    to_visit = [i for i in range(len(cons_nets)) if len(list(cons_nets[i][1])) > 0]
    visited = set()
    overall_ali = []
    count = 0
    while len(to_visit) > 0:
        curr = to_visit.pop(0)
        output_edges = [e for e in G0.edges if e[0] == curr]
        for edge in output_edges:
            to_visit.append(edge[1])
        if count > 0:
            sind = 1
        else:
            sind = 0
        if cons_nets_result[curr] is not None:
            overall_ali = overall_ali + [x for x in cons_nets_result[curr]["alignment"][sind:]]
        visited.add(curr)
        count = count + 1
    to_visit = [x for x in all_available if x not in visited]
    to_visit = order_nodes_second_round(to_visit, G0)
    added = set()
    while len(to_visit) > 0:
        curr = to_visit.pop(0)
        if not curr in visited:
            output_edges = [e for e in G0.edges if e[0] == curr]
            for edge in output_edges:
                to_visit.append(edge[1])
            if count > 0:
                sind = 1
            else:
                sind = 0
            if cons_nets_result[curr] is not None:
                for y in [x for x in cons_nets_result[curr]["alignment"][sind:]]:
                    if not y in added:
                        overall_ali.append(y)
                        added.add(y)
            visited.add(curr)
        count = count + 1
    return overall_ali


def apply_trace(trace, list_nets, parameters=None):
    """
    Align a trace against a decomposition

    Parameters
    --------------
    trace
        Trace
    list_nets
        List of Petri nets (decomposed)
    parameters
        Parameters of the algorithm

    Returns
    --------------
    alignment
        Alignment of the trace
    """
    if parameters is None:
        parameters = {}

    max_align_time_trace = exec_utils.get_param_value(Parameters.PARAM_MAX_ALIGN_TIME_TRACE, parameters, sys.maxsize)
    threshold_border_agreement = exec_utils.get_param_value(Parameters.PARAM_THRESHOLD_BORDER_AGREEMENT, parameters,
                                                            100000000)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, DEFAULT_NAME_KEY)
    icache = exec_utils.get_param_value(Parameters.ICACHE, parameters, dict())
    mcache = exec_utils.get_param_value(Parameters.MCACHE, parameters, dict())
    cons_nets = copy(list_nets)
    acache = get_acache(cons_nets)
    cons_nets_result = []
    cons_nets_alres = []
    cons_nets_costs = []
    max_val_alres = 0
    start_time = time.time()
    i = 0
    while i < len(cons_nets):
        this_time = time.time()
        if this_time - start_time > max_align_time_trace:
            # the alignment did not termine in the provided time
            return None
        net, im, fm = cons_nets[i]
        proj = Trace([x for x in trace if x[activity_key] in net.lvis_labels])
        if len(proj) > 0:
            acti = tuple(x[activity_key] for x in proj)
            tup = (cons_nets[i], acti)
            if tup not in icache:
                al, cf = align(proj, net, im, fm, parameters=parameters)
                alres = get_alres(al)
                icache[tup] = (al, cf, alres)
            al, cf, alres = icache[tup]
            cons_nets_result.append(al)
            cons_nets_alres.append(alres)
            cons_nets_costs.append(cf)
            if this_time - start_time > max_align_time_trace:
                # the alignment did not termine in the provided time
                return None
            max_val_alres = max(max_val_alres, max(z for y in alres.values() for z in y) if alres else 0)
            border_disagreements = 0
            if max_val_alres > 0:
                comp_to_merge = set()
                for act in [x[activity_key] for x in trace if x[activity_key] in net.lvis_labels]:
                    for ind in acache[act]:
                        if ind >= i:
                            break
                        if cons_nets_alres[ind] is None or cons_nets_alres[ind] is None:
                            # the alignment did not termine in the provided time
                            return None
                        if cons_nets_alres[ind][act] != cons_nets_alres[i][act]:
                            for ind2 in acache[act]:
                                comp_to_merge.add(ind2)
                if comp_to_merge:
                    comp_to_merge = sorted(list(comp_to_merge), reverse=True)
                    border_disagreements += len(comp_to_merge)
                    # if the number of border disagreements exceed the specified threshold
                    # then stop iterating on the trace
                    if border_disagreements > threshold_border_agreement:
                        return None
                    comp_to_merge_ids = tuple(list(cons_nets[j][0].t_tuple for j in comp_to_merge))
                    if comp_to_merge_ids not in mcache:
                        mcache[comp_to_merge_ids] = decomp_utils.merge_sublist_nets(
                            [cons_nets[zz] for zz in comp_to_merge])
                    new_comp = mcache[comp_to_merge_ids]
                    cons_nets.append(new_comp)
                    j = 0
                    while j < len(comp_to_merge):
                        z = comp_to_merge[j]
                        if z < i:
                            i = i - 1
                        if z <= i:
                            del cons_nets_result[z]
                            del cons_nets_alres[z]
                            del cons_nets_costs[z]
                        del cons_nets[z]
                        j = j + 1
                    acache = get_acache(cons_nets)
                    continue
        else:
            cons_nets_result.append(None)
            cons_nets_alres.append(None)
            cons_nets_costs.append(None)
        i = i + 1
    if this_time - start_time > max_align_time_trace:
        # the alignment did not termine in the provided time
        return None
    alignment = recompose_alignment(cons_nets, cons_nets_result, )
    overall_cost_dict = {}
    for cf in cons_nets_costs:
        if cf is not None:
            for el in cf:
                overall_cost_dict[el] = cf[el]
    cost = 0
    for el in alignment:
        cost = cost + overall_cost_dict[el]
    alignment = [x[1] for x in alignment]
    if this_time - start_time > max_align_time_trace:
        # the alignment did not termine in the provided time
        return None
    res = {"cost": cost, "alignment": alignment}
    best_worst_cost = exec_utils.get_param_value(Parameters.BEST_WORST_COST, parameters, None)
    if best_worst_cost is not None and len(trace) > 0:
        cost1 = cost // utils.STD_MODEL_LOG_MOVE_COST
        fitness = 1.0 - cost1 / (best_worst_cost + len(trace))
        res["fitness"] = fitness
        res["bwc"] = (best_worst_cost + len(trace)) * utils.STD_MODEL_LOG_MOVE_COST
    
    return res


def align(trace, petri_net, initial_marking, final_marking, parameters=None):
    if parameters is None:
        parameters = {}

    new_parameters = copy(parameters)
    new_parameters[state_equation_a_star.Parameters.RETURN_SYNC_COST_FUNCTION] = True
    new_parameters[state_equation_a_star.Parameters.PARAM_ALIGNMENT_RESULT_IS_SYNC_PROD_AWARE] = True

    aligned_trace, cost_function = state_equation_a_star.apply(trace, petri_net, initial_marking, final_marking,
                                                               parameters=new_parameters)

    cf = {}
    for x in cost_function:
        cf[((x.name[0], x.name[1]), (x.label[0], x.label[1]))] = cost_function[x]

    return aligned_trace, cf

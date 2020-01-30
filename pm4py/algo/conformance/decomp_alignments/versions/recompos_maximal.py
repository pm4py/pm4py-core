from pm4py.objects import petri
from pm4py.objects.log.log import Trace
from pm4py.objects.petri.utils import construct_trace_net_cost_aware, decorate_places_preset_trans, \
    decorate_transitions_prepostset
from pm4py.objects.petri.synchronous_product import construct_cost_aware
from pm4py.objects.log.util.xes import DEFAULT_NAME_KEY
import heapq
from pm4py.objects.petri import align_utils as utils
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY
from pm4py.objects.petri import decomposition as decomp_utils
from pm4py.algo.filtering.log.variants import variants_filter as variants_module
from pm4py import util as pm4pyutil
from copy import copy
import networkx as nx
import sys


PARAM_TRACE_COST_FUNCTION = 'trace_cost_function'
PARAM_MODEL_COST_FUNCTION = 'model_cost_function'
PARAM_SYNC_COST_FUNCTION = 'sync_cost_function'

PARAM_ALIGNMENT_RESULT_IS_SYNC_PROD_AWARE = 'ret_tuple_as_trans_desc'
PARAM_TRACE_NET_COSTS = "trace_net_costs"

TRACE_NET_CONSTR_FUNCTION = "trace_net_constr_function"
TRACE_NET_COST_AWARE_CONSTR_FUNCTION = "trace_net_cost_aware_constr_function"

PARAM_MAX_ALIGN_TIME_TRACE = "max_align_time_trace"
DEFAULT_MAX_ALIGN_TIME_TRACE = sys.maxsize
PARAM_MAX_ALIGN_TIME = "max_align_time"
DEFAULT_MAX_ALIGN_TIME = sys.maxsize

PARAMETER_VARIANT_DELIMITER = "variant_delimiter"
DEFAULT_VARIANT_DELIMITER = ","

ICACHE = "icache"
MCACHE = "mcache"


def apply(log, net, im, fm, parameters=None):
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
    icache = parameters[ICACHE] if ICACHE in parameters else dict()
    mcache = parameters[MCACHE] if MCACHE in parameters else dict()

    parameters[ICACHE] = icache
    parameters[MCACHE] = mcache

    variants_idxs = variants_module.get_variants_from_log_trace_idx(log, parameters=parameters)
    one_tr_per_var = []
    variants_list = []
    for index_variant, variant in enumerate(variants_idxs):
        variants_list.append(variant)
    for variant in variants_list:
        one_tr_per_var.append(log[variants_idxs[variant][0]])
    all_alignments = []
    for trace in one_tr_per_var:
        all_alignments.append(apply_trace(trace, list_nets, parameters=parameters))
    al_idx = {}
    for index_variant, variant in enumerate(variants_idxs):
        for trace_idx in variants_idxs[variant]:
            al_idx[trace_idx] = all_alignments[index_variant]
    alignments = []
    for i in range(len(log)):
        alignments.append(al_idx[i])
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
                edg = [e for e in G0.edges if e[0] == to_visit[j] and e[1] == to_visit[i]]
                if edg:
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

    Returns
    ---------------
    alignment
        Recomposed alignment
    """
    G0 = nx.DiGraph()
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
        overall_ali = overall_ali + [x for x in cons_nets_result[curr]["alignment"][sind:]]
        visited.add(curr)
        count = count + 1
    to_visit = [x for x in all_available if x not in visited]
    to_visit = order_nodes_second_round(to_visit, G0)
    added = set()
    while len(to_visit) > 0:
        curr = to_visit.pop(0)
        output_edges = [e for e in G0.edges if e[0] == curr]
        for edge in output_edges:
            to_visit.append(edge[1])
        if count > 0:
            sind = 1
        else:
            sind = 0
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

    activity_key = DEFAULT_NAME_KEY if parameters is None or PARAMETER_CONSTANT_ACTIVITY_KEY not in parameters else \
        parameters[
            pm4pyutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY]
    icache = parameters[ICACHE] if ICACHE in parameters else dict()
    mcache = parameters[MCACHE] if MCACHE in parameters else dict()
    cons_nets = copy(list_nets)
    acache = get_acache(cons_nets)
    cons_nets_result = []
    cons_nets_alres = []
    cons_nets_costs = []
    max_val_alres = 0
    i = 0
    while i < len(cons_nets):
        net, im, fm = cons_nets[i]
        proj = Trace([x for x in trace if x[activity_key] in net.lvis_labels])
        if len(proj) > 0:
            acti = tuple(x[activity_key] for x in proj)
            tup = (cons_nets[i], acti)
            if tup not in icache:
                al, cf = align(proj, net, im, fm, parameters=parameters)
                cf_new = {}
                for el in cf:
                    cf_new[(el.name, el.label)] = cf[el]
                alres = get_alres(al)
                icache[tup] = (al, cf_new, alres)
            al, cf, alres = icache[tup]
            cons_nets_result.append(al)
            cons_nets_alres.append(alres)
            cons_nets_costs.append(cf)
            max_val_alres = max(max_val_alres, max(z for y in alres.values() for z in y))
            if max_val_alres > 0:
                comp_to_merge = set()
                for act in [x[activity_key] for x in trace if x[activity_key] in net.lvis_labels]:
                    for ind in acache[act]:
                        if ind >= i:
                            break
                        if cons_nets_alres[ind][act] != cons_nets_alres[i][act]:
                            for ind2 in acache[act]:
                                comp_to_merge.add(ind2)
                if comp_to_merge:
                    comp_to_merge = sorted(list(comp_to_merge), reverse=True)
                    comp_to_merge_ids = tuple(list(cons_nets[j][0].t_tuple for j in comp_to_merge))
                    if comp_to_merge_ids not in mcache:
                        mcache[comp_to_merge_ids] = decomp_utils.merge_sublist_nets([cons_nets[zz] for zz in comp_to_merge])
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
    alignment = recompose_alignment(cons_nets, cons_nets_result)
    overall_cost_dict = {}
    for cf in cons_nets_costs:
        if cf is not None:
            for el in cf:
                overall_cost_dict[el] = cf[el]
    cost = 0
    for el in alignment:
        cost = cost + overall_cost_dict[el]
    alignment = [x[1] for x in alignment]
    res = {"cost": cost, "alignment": alignment}
    return res


def align(trace, petri_net, initial_marking, final_marking, parameters=None):
    """
    Align a trace against a Petri net

    Parameters
    -------------
    trace
        Trace
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking

    Returns
    -------------
    alignment
        Alignment
    cost_function
        Cost function
    """
    if parameters is None:
        parameters = {}

    activity_key = DEFAULT_NAME_KEY if parameters is None or PARAMETER_CONSTANT_ACTIVITY_KEY not in parameters else \
        parameters[
            pm4pyutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY]

    trace_net, trace_im, trace_fm = petri.utils.construct_trace_net(trace, activity_key=activity_key)

    return apply_trace_net(petri_net, initial_marking, final_marking, trace_net, trace_im, trace_fm)


def apply_trace_net(petri_net, initial_marking, final_marking, trace_net, trace_im, trace_fm):
    """
    Apply the alignment to a Petri net with initial and final marking,
    providing the trace net

    Parameters
    -------------
    petri_net
        Model
    initial_marking
        IM of the model
    final_marking
        FM of the model
    trace_net
        Trace net
    trace_im
        IM of the trace net
    trace_fm
        FM of the trace net

    Returns
    -------------
    alignment
        Alignment
    cost_function
        Cost function
    """
    sync_prod, sync_initial_marking, sync_final_marking = petri.synchronous_product.construct(trace_net, trace_im,
                                                                                              trace_fm, petri_net,
                                                                                              initial_marking,
                                                                                              final_marking,
                                                                                              utils.SKIP)
    cost_function = utils.construct_standard_cost_function(sync_prod, utils.SKIP)

    return __search(sync_prod, sync_initial_marking, sync_final_marking, cost_function,
                           utils.SKIP), cost_function


def __search(sync_net, ini, fin, cost_function, skip):
    """
    Search function for the decomposed/recomposed alignments

    Parameters
    ------------
    sync_net
        Synchronous Petri net
    ini
        Initial marking
    fin
        Final marking
    cost_function
        Cost function
    skip
        Skip symbol

    Returns
    -------------
    ali
        Alignment (if not None)
    """
    decorate_transitions_prepostset(sync_net)
    decorate_places_preset_trans(sync_net)

    closed = set()

    ini_state = utils.DijkstraSearchTuple(0, ini, None, None, 0)
    open_set = [ini_state]
    heapq.heapify(open_set)
    visited = 0
    queued = 0
    traversed = 0

    trans_empty_preset = set(t for t in sync_net.transitions if len(t.in_arcs) == 0)

    while not len(open_set) == 0:

        curr = heapq.heappop(open_set)

        current_marking = curr.m
        already_closed = current_marking in closed
        if already_closed:
            continue

        if current_marking == fin:
            return utils.__reconstruct_alignment(curr, visited, queued, traversed,
                                                 ret_tuple_as_trans_desc=True)

        closed.add(current_marking)
        visited += 1

        possible_enabling_transitions = copy(trans_empty_preset)
        for p in current_marking:
            for t in p.ass_trans:
                possible_enabling_transitions.add(t)

        enabled_trans = [t for t in possible_enabling_transitions if t.sub_marking <= current_marking]

        trans_to_visit_with_cost = [(t, cost_function[t]) for t in enabled_trans if not (
                t is not None and utils.__is_log_move(t, skip) and utils.__is_model_move(t, skip))]

        for t, cost in trans_to_visit_with_cost:
            traversed += 1
            new_marking = utils.add_markings(current_marking, t.add_marking)

            if new_marking in closed:
                continue

            queued += 1

            tp = utils.DijkstraSearchTuple(curr.g + cost, new_marking, curr, t, curr.l + 1)

            heapq.heappush(open_set, tp)

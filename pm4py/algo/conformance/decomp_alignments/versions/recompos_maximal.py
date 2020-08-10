from pm4py.objects.log.log import Trace
from pm4py.objects.log import log as log_implementation
from pm4py.objects.log.util.xes import DEFAULT_NAME_KEY
from pm4py.objects.petri import align_utils as utils
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY
from pm4py.objects.petri import decomposition as decomp_utils
from pm4py.statistics.variants.log import get as variants_module
from pm4py.objects.petri.importer import pnml as petri_importer
from pm4py import util as pm4pyutil
from copy import copy
from pm4py.algo.conformance.decomp_alignments.parameters import Parameters
from pm4py.util import exec_utils
from pm4py.algo.conformance.alignments.versions import state_equation_less_memory


def get_best_worst_cost(petri_net, initial_marking, final_marking, parameters=None):
    trace = log_implementation.Trace()

    best_worst, cf = align(trace, petri_net, initial_marking, final_marking, parameters=parameters)

    best_worst_cost = sum(cf[x] for x in best_worst['alignment']) // utils.STD_MODEL_LOG_MOVE_COST if best_worst[
        'alignment'] else 0

    return best_worst_cost


def apply_from_variants_list_petri_string(var_list, petri_net_string, parameters=None):
    if parameters is None:
        parameters = {}

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
    activity_key = DEFAULT_NAME_KEY if parameters is None or PARAMETER_CONSTANT_ACTIVITY_KEY not in parameters else \
        parameters[
            pm4pyutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY]
    variant_delimiter = exec_utils.get_param_value(Parameters.PARAMETER_VARIANT_DELIMITER, parameters,
                                                   pm4pyutil.constants.DEFAULT_VARIANT_SEP)
    log = log_implementation.EventLog()
    dictio_alignments = {}
    for varitem in var_list:
        variant = varitem[0]
        trace = log_implementation.Trace()
        variant_split = variant.split(variant_delimiter) if type(variant) is str else variant
        for el in variant_split:
            trace.append(log_implementation.Event({activity_key: el}))
            log.append(trace)

    alignment = apply(log, petri_net, initial_marking, final_marking)

    for index, varitem in enumerate(var_list):
        variant = varitem[0]
        dictio_alignments[variant] = alignment[index]

    return dictio_alignments


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
    if parameters is None:
        parameters = {}

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
    icache = exec_utils.get_param_value(Parameters.ICACHE, parameters, dict())
    mcache = exec_utils.get_param_value(Parameters.MCACHE, parameters, dict())

    parameters[Parameters.ICACHE] = icache
    parameters[Parameters.MCACHE] = mcache

    variants_idxs = variants_module.get_variants_from_log_trace_idx(log, parameters=parameters)
    one_tr_per_var = []
    variants_list = []
    for index_variant, variant in enumerate(variants_idxs):
        variants_list.append(variant)
    for variant in variants_list:
        one_tr_per_var.append(log[variants_idxs[variant][0]])
    all_alignments = []
    for index, trace in enumerate(one_tr_per_var):
        alignment = apply_trace(trace, list_nets, parameters=parameters)
        all_alignments.append(alignment)
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
    parameters
        Parameters of the method

    Returns
    ---------------
    alignment
        Recomposed alignment
    """
    import networkx as nx

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
    i = 0
    while i < len(cons_nets):
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
            max_val_alres = max(max_val_alres, max(z for y in alres.values() for z in y))
            border_disagreements = 0
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
    res = {"cost": cost, "alignment": alignment}
    best_worst_cost = exec_utils.get_param_value(Parameters.BEST_WORST_COST, parameters, None)
    if best_worst_cost is not None and len(trace) > 0:
        cost1 = cost // utils.STD_MODEL_LOG_MOVE_COST
        fitness = 1.0 - cost1 / (best_worst_cost + len(trace))
        res["fitness"] = fitness
    return res


def align(trace, petri_net, initial_marking, final_marking, parameters=None):
    if parameters is None:
        parameters = {}

    new_parameters = copy(parameters)
    new_parameters[state_equation_less_memory.Parameters.RETURN_SYNC_COST_FUNCTION] = True
    new_parameters[state_equation_less_memory.Parameters.PARAM_ALIGNMENT_RESULT_IS_SYNC_PROD_AWARE] = True

    aligned_trace, cost_function = state_equation_less_memory.apply(trace, petri_net, initial_marking, final_marking,
                                                                    parameters=new_parameters)

    cf = {}
    for x in cost_function:
        cf[((x.label[0], x.name[1]), (x.label[0], x.label[1]))] = cost_function[x]

    return aligned_trace, cf

import math

from pulp import lpSum, LpVariable, LpProblem, LpMinimize

from pm4py.algo.conformance.tree_alignments.variants.approximated.calculate_a_sa_ea_sets import \
    initialize_a_sa_ea_tau_sets
from pm4py.algo.conformance.tree_alignments.variants.approximated.utilities import calculate_optimal_alignment, \
    concatenate_traces, trace_to_list_of_str, add_fitness_and_cost_info_to_alignments
from pm4py.objects.process_tree.util import get_process_tree_height, process_tree_to_binary_process_tree
from pm4py.objects.petri.align_utils import SKIP
from pm4py.objects.process_tree.process_tree import ProcessTree
from pm4py.objects.log.log import Trace, Event
from pm4py.objects.log.log import EventLog
from typing import Union, Dict, Set, List, Tuple
from pm4py.objects.process_tree.importer.variants import ptml
from pm4py.objects.process_tree.pt_operator import Operator
from pm4py.util.xes_constants import DEFAULT_NAME_KEY
from pm4py.util import exec_utils, constants
from pm4py.statistics.variants.log.get import get_variants_from_log_trace_idx
from pm4py.util.lp import solver
from enum import Enum
import numpy as np


class Parameters(Enum):
    MAX_TRACE_LENGTH = "max_trace_length"
    MAX_PROCESS_TREE_HEIGHT = "max_process_tree_height"
    PARAMETER_VARIANT_DELIMITER = "variant_delimiter"
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY


def apply_from_variants_tree_string(var_list, tree_string, parameters=None):
    """
    Apply the alignments from the specification of a list of variants in the log.
    The tree is specified as a PTML input

    Parameters
    ------------
    var_list
        List of variants (for each item, the first entry is the variant itself, the second entry may be the number of cases)
    tree_string
        PTML string representing the tree
    parameters
        Parameters of the algorithm

        Returns
    --------------
    dictio_alignments
        Dictionary that assigns to each variant its alignment
    """
    if parameters is None:
        parameters = {}

    tree = ptml.import_tree_from_string(tree_string, parameters=parameters)

    res = apply_from_variants_list(var_list, tree, parameters=parameters)
    return res


def apply_from_variants_list(var_list, tree, parameters=None):
    """
    Apply the alignments from the specification of a list of variants in the log

    Parameters
    -------------
    var_list
        List of variants (for each item, the first entry is the variant itself, the second entry may be the number of cases)
    tree
        Process tree
    parameters
        Parameters of the algorithm

    Returns
    --------------
    dictio_alignments
        Dictionary that assigns to each variant its alignment
    """
    if parameters is None:
        parameters = {}

    variant_delimiter = exec_utils.get_param_value(Parameters.PARAMETER_VARIANT_DELIMITER, parameters,
                                                   ",")
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, DEFAULT_NAME_KEY)

    dictio_alignments = {}
    log = EventLog()

    for index, varitem in enumerate(var_list):
        activities = varitem[0].split(variant_delimiter)
        trace = Trace()
        for act in activities:
            trace.append(Event({activity_key: act}))
        log.append(trace)

    alignments = apply(log, tree, parameters=parameters)
    for index, varitem in enumerate(var_list):
        dictio_alignments[varitem[0]] = alignments[index]
    return dictio_alignments


def apply(obj: Union[Trace, EventLog], pt: ProcessTree, parameters=None):
    """
    Returns approximated alignments for a process tree

    Parameters
    --------------
    obj
        Event log or trace (a conversion is done if necessary)
    pt
        Process tree
    parameters
        Parameters of the algorithm

    Returns
    --------------
    alignments
        Approximated alignments
    :param obj:
    :param pt:
    :param parameters:
    :return:
    """
    if parameters is None:
        parameters = {}

    max_trace_length = exec_utils.get_param_value(Parameters.MAX_TRACE_LENGTH, parameters, 1)
    max_process_tree_height = exec_utils.get_param_value(Parameters.MAX_PROCESS_TREE_HEIGHT, parameters, 1)

    return __align(obj, pt, max_trace_length=max_trace_length, max_process_tree_height=max_process_tree_height,
                   parameters=parameters)


def __align(obj: Union[Trace, EventLog], pt: ProcessTree, max_trace_length: int = 1,
            max_process_tree_height: int = 1, parameters=None):
    """
    this function approximates alignments for a given event log or trace and a process tree

    :param obj: event log or single trace
    :param pt: process tree
    :param max_trace_length: specifies when the recursive splitting stops based on the trace's length
    :param max_process_tree_height: specifies when the recursive splitting stops based on the tree's height
    :return:
    """
    assert isinstance(pt, ProcessTree)
    if isinstance(obj, Trace):
        e = EventLog()
        e.append(obj)
        obj = e
    assert isinstance(obj, EventLog)
    pt = process_tree_to_binary_process_tree(pt)
    return __approximate_alignments_for_log(obj, pt, max_trace_length, max_process_tree_height,
                                            parameters=parameters)


def __approximate_alignments_for_log(log: EventLog, pt: ProcessTree, max_tl: int, max_th: int,
                                     parameters=None):
    a_sets, sa_sets, ea_sets, tau_sets = initialize_a_sa_ea_tau_sets(pt)
    variants = get_variants_from_log_trace_idx(log, parameters=parameters)
    inv_corr = {}
    for i, var in enumerate(variants):
        alignment = __approximate_alignment_for_trace(pt, a_sets, sa_sets, ea_sets, tau_sets, log[variants[var][0]],
                                                      max_tl, max_th,
                                                      parameters=parameters)
        alignment = add_fitness_and_cost_info_to_alignments(alignment, pt, log[variants[var][0]])
        for idx in variants[var]:
            inv_corr[idx] = alignment
    alignments = []
    for i in range(len(log)):
        alignments.append(inv_corr[i])
    return alignments


def __approximate_alignment_for_trace(pt: ProcessTree, a_sets: Dict[ProcessTree, Set[str]],
                                      sa_sets: Dict[ProcessTree, Set[str]], ea_sets: Dict[ProcessTree, Set[str]],
                                      tau_flags: Dict[ProcessTree, bool], trace: Trace, max_tl: int,
                                      max_th: int, parameters=None):
    if len(trace) <= max_tl or get_process_tree_height(pt) <= max_th:
        return calculate_optimal_alignment(pt, trace, parameters=parameters)
    else:
        if pt.operator == Operator.SEQUENCE:
            return __approximate_alignment_on_sequence(pt, trace, a_sets, sa_sets, ea_sets, tau_flags, max_tl, max_th,
                                                       parameters=parameters)
        elif pt.operator == Operator.LOOP:
            return __approximate_alignment_on_loop(pt, trace, a_sets, sa_sets, ea_sets, tau_flags, max_tl, max_th,
                                                   parameters=parameters)
        elif pt.operator == Operator.XOR:
            return __approximate_alignment_on_choice(pt, trace, a_sets, sa_sets, ea_sets, tau_flags, max_tl, max_th,
                                                     parameters=parameters)
        elif pt.operator == Operator.PARALLEL:
            return __approximate_alignment_on_parallel(pt, trace, a_sets, sa_sets, ea_sets, tau_flags, max_tl, max_th,
                                                       parameters=parameters)


def __approximate_alignment_on_choice(pt: ProcessTree, trace: Trace, a_sets: Dict[ProcessTree, Set[str]],
                                      sa_sets: Dict[ProcessTree, Set[str]], ea_sets: Dict[ProcessTree, Set[str]],
                                      tau_flags: Dict[ProcessTree, bool], tl: int, th: int,
                                      parameters=None):
    if parameters is None:
        parameters = {}
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, DEFAULT_NAME_KEY)

    assert pt.operator == Operator.XOR
    assert len(trace) > 0

    best_suited_subtree = None
    lowest_mismatches = math.inf
    for subtree in pt.children:
        mismatches = 0
        if len(trace) > 0:
            if trace[0][activity_key] not in sa_sets[subtree]:
                mismatches += 1
            if trace[-1][activity_key] not in ea_sets[subtree]:
                mismatches += 1
            if len(trace) > 2:
                for a in trace[1:-1]:
                    if a[activity_key] not in a_sets[subtree]:
                        mismatches += 1
        else:
            if not tau_flags[subtree] and len(sa_sets[subtree].intersection(ea_sets[subtree])) != 0:
                mismatches += 1
            elif not tau_flags[subtree] and len(sa_sets[subtree].intersection(ea_sets[subtree])) == 0:
                mismatches += 2
        if mismatches < lowest_mismatches:
            best_suited_subtree = subtree
            lowest_mismatches = mismatches
    return __approximate_alignment_for_trace(best_suited_subtree, a_sets, sa_sets, ea_sets, tau_flags, trace, tl, th,
                                             parameters=parameters)


def __approximate_alignment_on_loop(pt: ProcessTree, trace: Trace, a_sets: Dict[ProcessTree, Set[str]],
                                    sa_sets: Dict[ProcessTree, Set[str]], ea_sets: Dict[ProcessTree, Set[str]],
                                    tau_flags: Dict[ProcessTree, bool], tl: int, th: int,
                                    parameters=None):
    if parameters is None:
        parameters = {}
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, DEFAULT_NAME_KEY)

    assert pt.operator == Operator.LOOP
    assert len(pt.children) == 2
    assert len(trace) > 0

    # x_i_j = 1 <=> assigns activity i to subtree j
    x_variables = {}
    # t_i_j = 1 <=> inserts a tau at position i and assigns it to subtree j
    t_variables = {}
    # s_i_j = 1 <=> activity i is a start activity in the current sub-trace assigned to subtree j
    s_variables = {}
    # e_i_j = 1 <=> activity i is an end activity in the current sub-trace assigned to subtree j
    e_variables = {}
    # v_i_j = 1 <=> activity i is neither a start nor end-activity in the current sub-trace assigned to subtree j
    v_variables = {}
    # auxiliary variables
    # p_i_j = 1 <=> previous activity i-1 is assigned to the other subtree or t_1_other-subtree is 1
    p_variables = {}
    # n_i_j = 1 <=> next activity i+1 is assigned to the other subtree or t_1_other-subtree is 1
    n_variables = {}

    t_costs = {}
    s_costs = {}
    e_costs = {}
    v_costs = {}
    all_variables = []

    Aub = []
    Aeq = []
    bub = []
    beq = []

    for i, a in enumerate(trace):
        x_variables[i] = {}
        s_variables[i] = {}
        s_costs[i] = {}
        e_variables[i] = {}
        e_costs[i] = {}
        v_variables[i] = {}
        v_costs[i] = {}
        p_variables[i] = {}
        n_variables[i] = {}
        for j, subtree in enumerate(pt.children):
            all_variables.append('x_' + str(i) + '_' + str(j))
            x_variables[i][j] = len(all_variables)-1
            all_variables.append('s_' + str(i) + '_' + str(j))
            s_variables[i][j] = len(all_variables)-1
            s_costs[i][j] = 0 if a[activity_key] in sa_sets[subtree] else 1
            all_variables.append('e_' + str(i) + '_' + str(j))
            e_variables[i][j] = len(all_variables) - 1
            e_costs[i][j] = 0 if a[activity_key] in ea_sets[subtree] else 1
            all_variables.append('v_' + str(i) + '_' + str(j))
            v_variables[i][j] = len(all_variables)-1
            v_costs[i][j] = 0 if a[activity_key] in a_sets[subtree] else 1
            all_variables.append('p_' + str(i) + '_' + str(j))
            p_variables[i][j] = len(all_variables)-1
            all_variables.append('n_' + str(i) + '_' + str(j))
            n_variables[i][j] = len(all_variables)-1

    for i in range(len(trace) + 1):
        t_variables[i] = {}
        t_costs[i] = {}
        for j, subtree in enumerate(pt.children):
            all_variables.append('t_' + str(i) + '_' + str(j))
            t_variables[i][j] = len(all_variables)-1
            if tau_flags[subtree]:
                t_costs[i][j] = -0.00001  # favour to add a cut if possible over not putting a cut
            else:
                if len(sa_sets[subtree].intersection(ea_sets[subtree])) != 0:
                    t_costs[i][j] = 1
                else:
                    t_costs[i][j] = 2

    c = [0] * len(all_variables)
    for i in range(len(trace)):
        for j in range(len(pt.children)):
            c[s_variables[i][j]] = s_costs[i][j]

    for i in range(len(trace)):
        for j in range(len(pt.children)):
            c[e_variables[i][j]] = e_costs[i][j]

    for i in range(len(trace)):
        for j in range(len(pt.children)):
            c[v_variables[i][j]] = v_costs[i][j]

    for i in range(len(trace) + 1):
        for j in range(len(pt.children)):
            c[t_variables[i][j]] = t_costs[i][j]

    # first tau can never be assigned to the 2nd subtree
    r = [0] * len(all_variables)
    r[t_variables[0][1]] = 1
    Aeq.append(r)
    beq.append(0)

    # last tau can never be assigned to the 2nd subtree
    r = [0] * len(all_variables)
    r[t_variables[len(trace)][1]] = 1
    Aeq.append(r)
    beq.append(0)

    # if first/last tau is not used --> first/last activity is assigned to 1st subtree
    r = [0] * len(all_variables)
    r[t_variables[0][0]] = -1
    r[x_variables[0][0]] = -1
    Aub.append(r)
    bub.append(-1)

    r = [0] * len(all_variables)
    r[t_variables[len(trace)][0]] = -1
    r[x_variables[len(trace) - 1][0]] = -1
    Aub.append(r)
    bub.append(-1)

    for i in range(len(trace)):
        # every activity is assigned to one subtree
        r1 = [0] * len(all_variables)
        # start/end/intermediate-activity at position i can only be assigned to one subtree
        r2 = [0] * len(all_variables)
        r3 = [0] * len(all_variables)
        r4 = [0] * len(all_variables)
        for j in range(len(pt.children)):
            r1[x_variables[i][j]] = 1
            r2[x_variables[i][j]] = 1
            r3[x_variables[i][j]] = 1
            r4[x_variables[i][j]] = 1
        Aeq.append(r1)
        beq.append(1)
        Aub.append(r2)
        Aub.append(r3)
        Aub.append(r4)
        bub.append(1)
        bub.append(1)
        bub.append(1)

    # max one tau is used per index
    for i in range(len(trace) + 1):
        r = [0] * len(all_variables)
        for j in range(2):
            r[t_variables[i][j]] = 1
        Aub.append(r)
        bub.append(1)

    # if tau is used and hence, assigned to a subtree, the surrounding activities are assigned to the other subtree
    for i in range(1, len(trace)):
        # if tau at position i is assigned to 1st subtree, the previous activity is assigned to 2nd subtree
        r1 = [0] * len(all_variables)
        # if tau at position i is assigned to 1st subtree, the previous activity is assigned to 2nd subtree
        r2 = [0] * len(all_variables)
        r1[t_variables[i][0]] = 1
        r1[x_variables[i - 1][1]] = -1
        r2[t_variables[i][1]] = 1
        r2[x_variables[i - 1][0]] = -1
        Aub.append(r1)
        Aub.append(r2)
        bub.append(0)
        bub.append(0)

    for i in range(len(trace)):
        # if tau at position i is assigned to 1st subtree, the next activity is assigned to 2nd subtree
        r1 = [0] * len(all_variables)
        # if tau at position i is assigned to 2nd subtree, the next activity is assigned to 1st subtree
        r2 = [0] * len(all_variables)
        r1[t_variables[i][0]] = 1
        r1[x_variables[i][1]] = -1
        r2[t_variables[i][1]] = 1
        r2[x_variables[i][0]] = -1
        Aub.append(r1)
        Aub.append(r2)
        bub.append(0)
        bub.append(0)

    # if last tau is used and assigned to 1st subtree (assigning it to the 2nd subtree is already forbidden by another
    # constraint) --> last activity must be assigned to 2nd subtree
    r = [0] * len(all_variables)
    r[t_variables[len(trace)][0]] = 1
    r[x_variables[len(trace) - 1][1]] = -1
    Aub.append(r)
    bub.append(0)

    # define auxiliary variables n: n_i_1 = 1 <=> next activity i+1 is assigned to 2nd subtree or t_i+1_2 = 1
    for i in range(len(trace) - 1):
        r1 = [0] * len(all_variables)
        r2 = [0] * len(all_variables)
        r3 = [0] * len(all_variables)
        r4 = [0] * len(all_variables)
        r5 = [0] * len(all_variables)
        r6 = [0] * len(all_variables)

        r1[n_variables[i][0]] = 1
        r1[x_variables[i + 1][1]] = -1
        r1[t_variables[i + 1][1]] = -1
        r2[n_variables[i][0]] = -1
        r2[x_variables[i + 1][1]] = 1
        r3[n_variables[i][0]] = -1
        r3[t_variables[i + 1][1]] = 1
        r4[n_variables[i][1]] = 1
        r4[x_variables[i + 1][0]] = -1
        r4[t_variables[i + 1][0]] = -1
        r5[n_variables[i][1]] = -1
        r5[x_variables[i + 1][0]] = 1
        r6[n_variables[i][1]] = -1
        r6[t_variables[i + 1][0]] = 1
        Aub.append(r1)
        Aub.append(r2)
        Aub.append(r3)
        Aub.append(r4)
        Aub.append(r5)
        Aub.append(r6)
        bub.append(0)
        bub.append(0)
        bub.append(0)
        bub.append(0)
        bub.append(0)
        bub.append(0)

    r = [0] * len(all_variables)
    r[t_variables[len(trace)][1]] = 1
    r[n_variables[len(trace) - 1][0]] = -1
    Aub.append(r)
    bub.append(0)

    r = [0] * len(all_variables)
    r[t_variables[len(trace)][0]] = 1
    r[n_variables[len(trace) - 1][1]] = -1
    Aub.append(r)
    bub.append(0)

    # define e_i_j variables
    for i in range(len(trace)):
        for j in range(2):
            r1 = [0] * len(all_variables)
            r2 = [0] * len(all_variables)
            r3 = [0] * len(all_variables)
            r1[e_variables[i][j]] = 1
            r1[n_variables[i][j]] = -1
            r2[e_variables[i][j]] = 1
            r2[x_variables[i][j]] = -1
            r3[e_variables[i][j]] = -1
            r3[n_variables[i][j]] = 1
            r3[x_variables[i][j]] = 1
            Aub.append(r1)
            Aub.append(r2)
            Aub.append(r3)
            bub.append(0)
            bub.append(0)
            bub.append(1)

    # define auxiliary variables p: p_i_1 = 1 <=> previous activity i-1 is assigned to 2nd subtree or t_i-1_2 = 1
    r1 = [0] * len(all_variables)
    r1[t_variables[0][1]] = 1
    r1[p_variables[0][0]] = -1
    r2 = [0] * len(all_variables)
    r2[p_variables[0][1]] = 1
    r2[t_variables[0][0]] = -1
    Aub.append(r1)
    Aub.append(r2)
    bub.append(0)
    bub.append(0)

    for i in range(1, len(trace)):
        r1 = [0] * len(all_variables)
        r2 = [0] * len(all_variables)
        r3 = [0] * len(all_variables)
        r4 = [0] * len(all_variables)
        r5 = [0] * len(all_variables)
        r6 = [0] * len(all_variables)
        r1[p_variables[i][0]] = 1
        r1[t_variables[i][1]] = -1
        r1[x_variables[i - 1][1]] = -1
        r2[p_variables[i][0]] = -1
        r2[t_variables[i][1]] = 1
        r3[p_variables[i][0]] = -1
        r3[x_variables[i - 1][1]] = 1
        r4[p_variables[i][1]] = -1
        r4[t_variables[i][0]] = 1
        r4[x_variables[i - 1][0]] = 1
        r5[p_variables[i][1]] = -1
        r5[t_variables[i][0]] = 1
        r6[p_variables[i][1]] = -1
        r6[x_variables[i - 1][0]] = 1
        Aub.append(r1)
        Aub.append(r2)
        Aub.append(r3)
        Aub.append(r4)
        Aub.append(r5)
        Aub.append(r6)
        bub.append(0)
        bub.append(0)
        bub.append(0)
        bub.append(0)
        bub.append(0)
        bub.append(0)

    # define s_i_j variables
    for i in range(len(trace)):
        for j in range(2):
            r1 = [0] * len(all_variables)
            r2 = [0] * len(all_variables)
            r3 = [0] * len(all_variables)
            r1[s_variables[i][j]] = -1
            r1[p_variables[i][j]] = 1
            r1[x_variables[i][j]] = 1
            r2[s_variables[i][j]] = 1
            r2[p_variables[i][j]] = -1
            r3[s_variables[i][j]] = 1
            r3[p_variables[i][j]] = -1
            Aub.append(r1)
            Aub.append(r2)
            Aub.append(r3)
            bub.append(1)
            bub.append(0)
            bub.append(0)

    r = [0] * len(all_variables)
    r[t_variables[0][0]] = -1
    r[s_variables[0][0]] = -1
    Aub.append(r)
    bub.append(-1)

    # define v_i_j variables
    for i in range(len(trace)):
        for j in range(2):
            r1 = [0] * len(all_variables)
            r2 = [0] * len(all_variables)
            r3 = [0] * len(all_variables)
            r4 = [0] * len(all_variables)

            r1[v_variables[i][j]] = -1
            r1[s_variables[i][j]] = -1
            r1[e_variables[i][j]] = -1
            r1[x_variables[i][j]] = 1

            r2[v_variables[i][j]] = 1
            r2[x_variables[i][j]] = -1

            r3[v_variables[i][j]] = 1
            r3[e_variables[i][j]] = 1

            r4[v_variables[i][j]] = 1
            r4[s_variables[i][j]] = 1

            Aub.append(r1)
            Aub.append(r2)
            Aub.append(r3)
            Aub.append(r4)

            bub.append(0)
            bub.append(0)
            bub.append(1)
            bub.append(1)

    for idx, v in enumerate(all_variables):
        r = [0] * len(all_variables)
        r[idx] = -1
        Aub.append(r)
        bub.append(0)
        r = [0] * len(all_variables)
        r[idx] = 1
        Aub.append(r)
        bub.append(1)

    Aeq = np.asmatrix(Aeq).astype(np.float64)
    beq = np.asmatrix(beq).transpose().astype(np.float64)
    Aub = np.asmatrix(Aub).astype(np.float64)
    bub = np.asmatrix(bub).transpose().astype(np.float64)
    sol = solver.apply(c, Aub, bub, Aeq, beq)
    points = solver.get_points_from_sol(sol)

    for i in t_variables:
        for j in t_variables[i]:
            t_variables[i][j] = True if points[t_variables[i][j]] == 1.0 else False
    for i in x_variables:
        for j in x_variables[i]:
            x_variables[i][j] = True if points[x_variables[i][j]] == 1.0 else False

    alignments_to_calculate: List[Tuple[ProcessTree, Trace]] = []
    sub_trace = Trace()
    current_subtree_idx = 0
    for i in range(len(trace)):
        for j in range(2):
            if t_variables[i][j]:
                if i == 0:
                    # first tau can be only assigned to first subtree
                    assert j == 0
                    alignments_to_calculate.append((pt.children[j], Trace()))
                    current_subtree_idx = 1
                else:
                    alignments_to_calculate.append((pt.children[current_subtree_idx], sub_trace))
                    alignments_to_calculate.append((pt.children[j], Trace()))
                    sub_trace = Trace()
        for j in range(2):
            if x_variables[i][j]:
                if j == current_subtree_idx:
                    sub_trace.append(trace[i])
                else:
                    alignments_to_calculate.append((pt.children[current_subtree_idx], sub_trace))
                    sub_trace = Trace()
                    sub_trace.append(trace[i])
                    current_subtree_idx = j
    if len(sub_trace) > 0:
        alignments_to_calculate.append((pt.children[current_subtree_idx], sub_trace))
    if t_variables[len(trace)][0]:
        alignments_to_calculate.append((pt.children[0], Trace()))

    res = []
    for subtree, sub_trace in alignments_to_calculate:
        res.extend(
            __approximate_alignment_for_trace(subtree, a_sets, sa_sets, ea_sets, tau_flags, sub_trace, tl, th,
                                              parameters=parameters))
    return res


def __approximate_alignment_on_sequence(pt: ProcessTree, trace: Trace, a_sets: Dict[ProcessTree, Set[str]],
                                        sa_sets: Dict[ProcessTree, Set[str]], ea_sets: Dict[ProcessTree, Set[str]],
                                        tau_flags: Dict[ProcessTree, bool], tl: int, th: int,
                                        parameters=None):
    if parameters is None:
        parameters = {}
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, DEFAULT_NAME_KEY)

    assert pt.operator == Operator.SEQUENCE
    assert len(pt.children) > 0
    assert len(trace) > 0

    ilp = LpProblem(sense=LpMinimize)

    # x_i_j = 1 <=> assigns activity i to subtree j
    x_variables: Dict[int, Dict[int, LpVariable]] = {}

    # s_i_j = 1 <=> activity i is a start activity in the current sub-trace assigned to subtree j
    s_variables: Dict[int, Dict[int, LpVariable]] = {}

    # e_i_j = 1 <=> activity i is an end activity in the current sub-trace assigned to subtree j
    e_variables: Dict[int, Dict[int, LpVariable]] = {}

    # auxiliary u_j <=> u_j=1 if an activity is assigned to subtree j
    u_variables: Dict[int, LpVariable] = {}

    # v_i_j = 1 <=> activity i is neither a start nor end-activity in the current sub-trace assigned to subtree j
    v_variables: Dict[int, Dict[int, LpVariable]] = {}

    s_costs = {}
    e_costs = {}
    u_costs = {}
    v_costs = {}

    # trace <a_0,...,a_n>
    for i, a in enumerate(trace):
        x_variables[i] = {}
        s_variables[i] = {}
        s_costs[i] = {}
        e_variables[i] = {}
        e_costs[i] = {}
        v_variables[i] = {}
        v_costs[i] = {}

        for j, subtree in enumerate(pt.children):
            x_variables[i][j] = LpVariable('x_' + str(i) + '_' + str(j), cat='Binary')

            s_variables[i][j] = LpVariable('s_' + str(i) + '_' + str(j), cat='Binary')
            s_costs[i][j] = 0 if a[activity_key] in sa_sets[subtree] else 1

            e_variables[i][j] = LpVariable('e_' + str(i) + '_' + str(j), cat='Binary')
            e_costs[i][j] = 0 if a[activity_key] in ea_sets[subtree] else 1

            v_variables[i][j] = LpVariable('v_' + str(i) + '_' + str(j), cat='Binary')
            v_costs[i][j] = 0 if a[activity_key] in a_sets[subtree] else 1

    for j in range(len(pt.children)):
        u_variables[j] = LpVariable('u_' + str(j), cat='Binary')
        # define costs to not assign anything to subtree j
        if tau_flags[pt.children[j]]:
            u_costs[j] = 0
        elif sa_sets[pt.children[j]] & ea_sets[pt.children[j]]:
            # intersection of start-activities and end-activities is not empty
            u_costs[j] = 1
        else:
            # intersection of start-activities and end-activities is empty
            u_costs[j] = 2

    # objective function
    ilp += lpSum(
        [v_variables[i][j] * v_costs[i][j] for i in range(len(trace)) for j in range(len(pt.children))] +
        [s_variables[i][j] * s_costs[i][j] for i in range(len(trace)) for j in range(len(pt.children))] +
        [e_variables[i][j] * e_costs[i][j] for i in range(len(trace)) for j in range(len(pt.children))] +
        [1 - u_variables[j] * u_costs[j] for j in range(len(pt.children))]), "objective_function"

    # constraints
    for i in range(len(trace)):
        # every activity is assigned to one subtree
        ilp += lpSum([x_variables[i][j] * 1 for j in range(len(pt.children))]) == 1

    for j in range(len(pt.children)):
        # first activity is start activity
        ilp += x_variables[0][j] <= s_variables[0][j]
        # last activity is end-activity
        ilp += x_variables[len(trace) - 1][j] <= e_variables[len(trace) - 1][j]

    # define s_i_j variables
    for i in range(1, len(trace)):
        for j in range(len(pt.children)):
            ilp += s_variables[i][j] >= x_variables[i][j] + 1 - x_variables[i - 1][j] - 1
            ilp += s_variables[i][j] <= x_variables[i][j]
            ilp += s_variables[i][j] <= 1 - x_variables[i - 1][j]
    for i in range(len(trace)):
        # activity can be only for one subtree a start-activity
        ilp += lpSum(s_variables[i][j] for j in range(len(pt.children))) <= 1

    # define e_i_j variables
    for i in range(len(trace) - 1):
        for j in range(len(pt.children)):
            ilp += e_variables[i][j] >= x_variables[i][j] + 1 - x_variables[i + 1][j] - 1
            ilp += e_variables[i][j] <= x_variables[i][j]
            ilp += e_variables[i][j] <= 1 - x_variables[i + 1][j]
    for i in range(len(trace)):
        # activity can be only for one subtree an end-activity
        ilp += lpSum(e_variables[i][j] for j in range(len(pt.children))) <= 1

    # constraint - preserving sequence when assigning activities to subtrees
    for i in range(len(trace) - 1):
        for j in range(len(pt.children)):
            ilp += lpSum(x_variables[i + 1][k] for k in range(j, len(pt.children))) >= x_variables[i][j]

    for j in range(len(pt.children)):
        for i in range(len(trace)):
            # define u_j variables
            ilp += u_variables[j] >= x_variables[i][j]

        # if u_j variable = 1 ==> a start activity must exist
        ilp += u_variables[j] <= lpSum(s_variables[i][j] for i in range(len(trace)))
        # if u_j variable = 1 ==> an end activity must exist
        ilp += u_variables[j] <= lpSum(e_variables[i][j] for i in range(len(trace)))

    # define v_i_j variables
    for i in range(len(trace)):
        for j in range(2):
            ilp += v_variables[i][j] >= 1 - s_variables[i][j] + 1 - e_variables[i][j] + x_variables[i][j] - 2
            ilp += v_variables[i][j] <= x_variables[i][j]
            ilp += v_variables[i][j] <= 1 - e_variables[i][j]
            ilp += v_variables[i][j] <= 1 - s_variables[i][j]

    status = ilp.solve()
    assert status == 1

    alignments_to_calculate: List[Tuple[ProcessTree, Trace]] = []
    for j in range(len(pt.children)):
        sub_trace = Trace()
        for i in range(len(trace)):
            if x_variables[i][j].varValue == 1:
                sub_trace.append(trace[i])
        alignments_to_calculate.append((pt.children[j], sub_trace))
    # calculate and compose alignments
    res = []
    for subtree, sub_trace in alignments_to_calculate:
        res.extend(
            __approximate_alignment_for_trace(subtree, a_sets, sa_sets, ea_sets, tau_flags, sub_trace, tl, th,
                                              parameters=parameters))
    return res


def __approximate_alignment_on_parallel(pt: ProcessTree, trace: Trace, a_sets: Dict[ProcessTree, Set[str]],
                                        sa_sets: Dict[ProcessTree, Set[str]], ea_sets: Dict[ProcessTree, Set[str]],
                                        tau_flags: Dict[ProcessTree, bool], tl: int, th: int,
                                        parameters=None):
    if parameters is None:
        parameters = {}
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, DEFAULT_NAME_KEY)

    assert pt.operator == Operator.PARALLEL
    assert len(pt.children) > 0
    assert len(trace) > 0

    ilp = LpProblem(sense=LpMinimize)

    # x_i_j = 1 <=> assigns activity i to subtree j
    x_variables: Dict[int, Dict[int, LpVariable]] = {}

    # s_i_j = 1 <=> activity i is a start activity in the current sub-trace assigned to subtree j
    s_variables: Dict[int, Dict[int, LpVariable]] = {}

    # e_i_j = 1 <=> activity i is an end activity in the current sub-trace assigned to subtree j
    e_variables: Dict[int, Dict[int, LpVariable]] = {}

    # auxiliary u_j <=> u_j=1 if an activity is assigned to subtree j
    u_variables: Dict[int, LpVariable] = {}

    # v_i_j = 1 <=> activity i is neither a start nor end-activity in the current sub-trace assigned to subtree j
    v_variables: Dict[int, Dict[int, LpVariable]] = {}

    s_costs = {}
    e_costs = {}
    u_costs = {}
    v_costs = {}

    for i, a in enumerate(trace):
        x_variables[i] = {}
        s_variables[i] = {}
        s_costs[i] = {}
        e_variables[i] = {}
        e_costs[i] = {}
        v_variables[i] = {}
        v_costs[i] = {}

        for j, subtree in enumerate(pt.children):
            x_variables[i][j] = LpVariable('x_' + str(i) + '_' + str(j), cat='Binary')

            s_variables[i][j] = LpVariable('s_' + str(i) + '_' + str(j), cat='Binary')
            s_costs[i][j] = 0 if a[activity_key] in sa_sets[subtree] else 1

            e_variables[i][j] = LpVariable('e_' + str(i) + '_' + str(j), cat='Binary')
            e_costs[i][j] = 0 if a[activity_key] in ea_sets[subtree] else 1

            v_variables[i][j] = LpVariable('v_' + str(i) + '_' + str(j), cat='Binary')
            v_costs[i][j] = 0 if a[activity_key] in a_sets[subtree] else 1

    for j in range(len(pt.children)):
        u_variables[j] = LpVariable('u_' + str(j), cat='Binary')
        # define costs to not assign anything to subtree j
        if tau_flags[pt.children[j]]:
            u_costs[j] = 0
        elif sa_sets[pt.children[j]] & ea_sets[pt.children[j]]:
            # intersection of start-activities and end-activities is not empty
            u_costs[j] = 1
        else:
            # intersection of start-activities and end-activities is empty
            u_costs[j] = 2

    # objective function
    ilp += lpSum(
        [v_variables[i][j] * v_costs[i][j] for i in range(len(trace)) for j in range(len(pt.children))] +
        [s_variables[i][j] * s_costs[i][j] for i in range(len(trace)) for j in range(len(pt.children))] +
        [e_variables[i][j] * e_costs[i][j] for i in range(len(trace)) for j in range(len(pt.children))] +
        [1 - u_variables[j] * u_costs[j] for j in range(len(pt.children))]), "objective_function"

    # constraints
    for i in range(len(trace)):
        # every activity is assigned to one subtree
        ilp += lpSum([x_variables[i][j] * 1 for j in range(len(pt.children))]) == 1

    for j in range(len(pt.children)):
        # first activity is a start activity
        ilp += x_variables[0][j] <= s_variables[0][j]
        # last activity is an end-activity
        ilp += x_variables[len(trace) - 1][j] <= e_variables[len(trace) - 1][j]

    # define s_i_j variables
    for i in range(len(trace)):
        for j in range(len(pt.children)):
            ilp += s_variables[i][j] <= x_variables[i][j]
            for k in range(i):
                ilp += s_variables[i][j] <= 1 - x_variables[k][j]
        # activity can be only a start-activity for one subtree
        ilp += lpSum(s_variables[i][j] for j in range(len(pt.children))) <= 1

    # define e_i_j variables
    for i in range(len(trace)):
        for j in range(len(pt.children)):
            ilp += e_variables[i][j] <= x_variables[i][j]
            for k in range(i + 1, len(trace)):
                ilp += e_variables[i][j] <= 1 - x_variables[k][j]
        # activity can be only an end-activity for one subtree
        ilp += lpSum(e_variables[i][j] for j in range(len(pt.children))) <= 1

    for j in range(len(pt.children)):
        for i in range(len(trace)):
            # define u_j variables
            ilp += u_variables[j] >= x_variables[i][j]
        # if u_j variable = 1 ==> a start activity must exist
        ilp += u_variables[j] <= lpSum(s_variables[i][j] for i in range(len(trace)))
        # if u_j variable = 1 ==> an end activity must exist
        ilp += u_variables[j] <= lpSum(e_variables[i][j] for i in range(len(trace)))

    # define v_i_j variables
    for i in range(len(trace)):
        for j in range(2):
            ilp += v_variables[i][j] >= 1 - s_variables[i][j] + 1 - e_variables[i][j] + x_variables[i][j] - 2
            ilp += v_variables[i][j] <= x_variables[i][j]
            ilp += v_variables[i][j] <= 1 - e_variables[i][j]
            ilp += v_variables[i][j] <= 1 - s_variables[i][j]

    status = ilp.solve()
    assert status == 1

    # trace_parts list contains trace parts mapped onto the determined subtree
    trace_parts: List[Tuple[ProcessTree, Trace]] = []
    last_subtree: ProcessTree = None
    for i in range(len(trace)):
        for j in range(len(pt.children)):
            subtree = pt.children[j]
            if x_variables[i][j].varValue == 1:
                if last_subtree and subtree == last_subtree:
                    trace_parts[-1][1].append(trace[i])
                else:
                    assert last_subtree is None or subtree != last_subtree
                    t = Trace()
                    t.append(trace[i])
                    trace_parts.append((subtree, t))
                    last_subtree = subtree
                continue

    # calculate an alignment for each subtree
    alignments_per_subtree: Dict[ProcessTree] = {}
    for j in range(len(pt.children)):
        subtree: ProcessTree = pt.children[j]
        sub_trace = Trace()
        for trace_part in trace_parts:
            if subtree == trace_part[0]:
                sub_trace = concatenate_traces(sub_trace, trace_part[1])
        alignments_per_subtree[subtree] = __approximate_alignment_for_trace(subtree, a_sets, sa_sets, ea_sets,
                                                                            tau_flags, sub_trace, tl, th,
                                                                            parameters=parameters)
    # compose alignments from subtree alignments
    res = []
    for trace_part in trace_parts:
        activities_to_cover = trace_to_list_of_str(trace_part[1])
        activities_covered_so_far = []
        alignment = alignments_per_subtree[trace_part[0]]
        while activities_to_cover != activities_covered_so_far:
            move = alignment.pop(0)
            res.append(move)
            # if the alignment move is NOT a model move add activity to activities_covered_so_far
            if move[0] != SKIP:
                activities_covered_so_far.append(move[0])
    # add possible remaining alignment moves to resulting alignment, the order does not matter (parallel operator)
    for subtree in alignments_per_subtree:
        if len(alignments_per_subtree[subtree]) > 0:
            res.extend(alignments_per_subtree[subtree])
    return res

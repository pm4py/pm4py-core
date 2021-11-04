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
import math

from pm4py.algo.conformance.alignments.process_tree.variants.approximated.calculate_a_sa_ea_sets import initialize_a_sa_ea_tau_sets
from pm4py.algo.conformance.alignments.process_tree.variants.approximated.utilities import calculate_optimal_alignment, concatenate_traces, trace_to_list_of_str, add_fitness_and_cost_info_to_alignments, AlignmentNoneException, EfficientTree
from pm4py.objects.process_tree.utils.generic import get_process_tree_height, process_tree_to_binary_process_tree
from pm4py.objects.petri_net.utils.align_utils import SKIP
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.objects.log.obj import Trace
from pm4py.objects.log.obj import EventLog
from typing import Union, Dict, Set, List, Tuple
from pm4py.objects.process_tree.obj import Operator
from pm4py.util.xes_constants import DEFAULT_NAME_KEY
from pm4py.util import exec_utils, constants
from pm4py.statistics.variants.log.get import get_variants_from_log_trace_idx
from enum import Enum
import sys
import time
from pm4py.util import variants_util


class Parameters(Enum):
    MAX_TRACE_LENGTH = "max_trace_length"
    MAX_PROCESS_TREE_HEIGHT = "max_process_tree_height"
    PARAMETER_VARIANT_DELIMITER = "variant_delimiter"
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    PARAM_MAX_ALIGN_TIME_TRACE = "max_align_time_trace"
    PARAM_MAX_ALIGN_TIME = "max_align_time"


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

    from pm4py.objects.process_tree.importer.variants import ptml

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

    dictio_alignments = {}
    log = EventLog()

    for index, varitem in enumerate(var_list):
        trace = variants_util.variant_to_trace(varitem[0], parameters=parameters)
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
    pt = EfficientTree(pt)
    
    return __approximate_alignments_for_log(obj, pt, max_trace_length, max_process_tree_height,
                                            parameters=parameters)


def __approximate_alignments_for_log(log: EventLog, pt: ProcessTree, max_tl: int, max_th: int,
                                     parameters=None):
    if parameters is None:
        parameters = {}

    a_sets, sa_sets, ea_sets, tau_sets = initialize_a_sa_ea_tau_sets(pt)
    variants = get_variants_from_log_trace_idx(log, parameters=parameters)
    inv_corr = {}

    max_align_time = exec_utils.get_param_value(Parameters.PARAM_MAX_ALIGN_TIME, parameters,
                                                sys.maxsize)
    log_alignment_start_time = time.time()

    for i, var in enumerate(variants):
        this_time = time.time()

        if this_time - log_alignment_start_time <= max_align_time:
            parameters["trace_alignment_start_time"] = this_time
            alignment = __approximate_alignment_for_trace(pt, a_sets, sa_sets, ea_sets, tau_sets, log[variants[var][0]],
                                                          max_tl, max_th,
                                                          parameters=parameters)
            alignment = add_fitness_and_cost_info_to_alignments(alignment, pt, log[variants[var][0]], parameters=parameters)
        else:
            alignment = None

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
    if parameters is None:
        parameters = {}

    max_align_time_trace = exec_utils.get_param_value(Parameters.PARAM_MAX_ALIGN_TIME_TRACE, parameters,
                                                      sys.maxsize)

    start_time = parameters["trace_alignment_start_time"]
    current_time = time.time()

    if current_time - start_time > max_align_time_trace:
        # the alignment of the trace did not terminate in an useful time
        return None

    try:
        if len(trace) <= max_tl or get_process_tree_height(pt) <= max_th:
            return calculate_optimal_alignment(pt, trace, parameters=parameters)
        else:
            if pt.operator == Operator.SEQUENCE:
                return __approximate_alignment_on_sequence(pt, trace, a_sets, sa_sets, ea_sets, tau_flags, max_tl,
                                                           max_th,
                                                           parameters=parameters)
            elif pt.operator == Operator.LOOP:
                return __approximate_alignment_on_loop(pt, trace, a_sets, sa_sets, ea_sets, tau_flags, max_tl, max_th,
                                                       parameters=parameters)
            elif pt.operator == Operator.XOR:
                return __approximate_alignment_on_choice(pt, trace, a_sets, sa_sets, ea_sets, tau_flags, max_tl, max_th,
                                                         parameters=parameters)
            elif pt.operator == Operator.PARALLEL:
                return __approximate_alignment_on_parallel(pt, trace, a_sets, sa_sets, ea_sets, tau_flags, max_tl,
                                                           max_th,
                                                           parameters=parameters)
    except AlignmentNoneException:
        # alignment did not terminate correctly. return None
        return None


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

    from pulp import lpSum, LpVariable, LpProblem, LpMinimize

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, DEFAULT_NAME_KEY)

    assert pt.operator == Operator.LOOP
    assert len(pt.children) == 2
    assert len(trace) > 0

    ilp = LpProblem(sense=LpMinimize)

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
            x_variables[i][j] = LpVariable('x_' + str(i) + '_' + str(j), cat='Binary')

            s_variables[i][j] = LpVariable('s_' + str(i) + '_' + str(j), cat='Binary')
            s_costs[i][j] = 0 if a[activity_key] in sa_sets[subtree] else 1

            e_variables[i][j] = LpVariable('e_' + str(i) + '_' + str(j), cat='Binary')
            e_costs[i][j] = 0 if a[activity_key] in ea_sets[subtree] else 1

            v_variables[i][j] = LpVariable('v_' + str(i) + '_' + str(j), cat='Binary')
            v_costs[i][j] = 0 if a[activity_key] in a_sets[subtree] else 1

            p_variables[i][j] = LpVariable('p_' + str(i) + '_' + str(j), cat='Binary')
            n_variables[i][j] = LpVariable('n_' + str(i) + '_' + str(j), cat='Binary')

    for i in range(len(trace) + 1):
        t_variables[i] = {}
        t_costs[i] = {}
        for j, subtree in enumerate(pt.children):
            t_variables[i][j] = LpVariable('t_' + str(i) + '_' + str(j), cat='Binary')
            if tau_flags[subtree]:
                t_costs[i][j] = -0.00001  # favour to add a cut if possible over not putting a cut
            else:
                if len(sa_sets[subtree].intersection(ea_sets[subtree])) != 0:
                    t_costs[i][j] = 1
                else:
                    t_costs[i][j] = 2

    # objective function
    ilp += lpSum(
        [s_variables[i][j] * s_costs[i][j] for i in range(len(trace)) for j in range(len(pt.children))] +
        [e_variables[i][j] * e_costs[i][j] for i in range(len(trace)) for j in range(len(pt.children))] +
        [v_variables[i][j] * v_costs[i][j] for i in range(len(trace)) for j in range(len(pt.children))] +
        [t_variables[i][j] * t_costs[i][j] for i in range(len(trace) + 1) for j in
         range(len(pt.children))]), "objective_function"

    # constraints
    # universe j                        {0,1}
    # universe i for t_i_j variables    {0,...,len(trace)}
    # universe i else                   {0,...,len(trace)-1}

    # first tau can never be assigned to the 2nd subtree
    ilp += t_variables[0][1] == 0

    # last tau can never be assigned to the 2nd subtree
    ilp += t_variables[len(trace)][1] == 0

    # if first/last tau is not used --> first/last activity is assigned to 1st subtree
    ilp += 1 - t_variables[0][0] <= x_variables[0][0]
    ilp += 1 - t_variables[len(trace)][0] <= x_variables[len(trace) - 1][0]

    for i in range(len(trace)):
        # every activity is assigned to one subtree
        ilp += lpSum([x_variables[i][j] * 1 for j in range(len(pt.children))]) == 1

        # start/end/intermediate-activity at position i can only be assigned to one subtree
        ilp += lpSum([s_variables[i][j] * 1 for j in range(len(pt.children))]) <= 1
        ilp += lpSum([e_variables[i][j] * 1 for j in range(len(pt.children))]) <= 1
        ilp += lpSum([v_variables[i][j] * 1 for j in range(len(pt.children))]) <= 1

    for i in range(len(trace) + 1):
        # max one tau is used per index
        ilp += lpSum([t_variables[i][j] for j in range(2)]) <= 1

    # if tau is used and hence, assigned to a subtree, the surrounding activities are assigned to the other subtree
    for i in range(1, len(trace)):
        # if tau at position i is assigned to 1st subtree, the previous activity is assigned to 2nd subtree
        ilp += t_variables[i][0] <= x_variables[i - 1][1]
        # if tau at position i is assigned to 1st subtree, the previous activity is assigned to 2nd subtree
        ilp += t_variables[i][1] <= x_variables[i - 1][0]
    for i in range(len(trace)):
        # if tau at position i is assigned to 1st subtree, the next activity is assigned to 2nd subtree
        ilp += t_variables[i][0] <= x_variables[i][1]
        # if tau at position i is assigned to 2nd subtree, the next activity is assigned to 1st subtree
        ilp += t_variables[i][1] <= x_variables[i][0]
    # if last tau is used and assigned to 1st subtree (assigning it to the 2nd subtree is already forbidden by another
    # constraint) --> last activity must be assigned to 2nd subtree
    ilp += t_variables[len(trace)][0] <= x_variables[len(trace) - 1][1]

    # define auxiliary variables n: n_i_1 = 1 <=> next activity i+1 is assigned to 2nd subtree or t_i+1_2 = 1
    for i in range(len(trace) - 1):
        ilp += n_variables[i][0] <= x_variables[i + 1][1] + t_variables[i + 1][1]
        ilp += n_variables[i][0] >= x_variables[i + 1][1]
        ilp += n_variables[i][0] >= t_variables[i + 1][1]

        ilp += n_variables[i][1] <= x_variables[i + 1][0] + t_variables[i + 1][0]
        ilp += n_variables[i][1] >= x_variables[i + 1][0]
        ilp += n_variables[i][1] >= t_variables[i + 1][0]

    ilp += t_variables[len(trace)][1] <= n_variables[len(trace) - 1][0]
    ilp += t_variables[len(trace)][0] <= n_variables[len(trace) - 1][1]

    # define e_i_j variables
    for i in range(len(trace)):
        for j in range(2):
            ilp += e_variables[i][j] <= n_variables[i][j]
            ilp += e_variables[i][j] <= x_variables[i][j]
            ilp += e_variables[i][j] >= n_variables[i][j] + x_variables[i][j] - 1

    # define auxiliary variables p: p_i_1 = 1 <=> previous activity i-1 is assigned to 2nd subtree or t_i-1_2 = 1
    ilp += t_variables[0][1] <= p_variables[0][0]
    ilp += p_variables[0][1] <= t_variables[0][0]

    for i in range(1, len(trace)):
        ilp += p_variables[i][0] <= t_variables[i][1] + x_variables[i - 1][1]
        ilp += p_variables[i][0] >= t_variables[i][1]
        ilp += p_variables[i][0] >= x_variables[i - 1][1]

        ilp += p_variables[i][1] <= t_variables[i][0] + x_variables[i - 1][0]
        ilp += p_variables[i][1] >= t_variables[i][0]
        ilp += p_variables[i][1] >= x_variables[i - 1][0]

    # define s_i_j variables
    for i in range(len(trace)):
        for j in range(2):
            ilp += s_variables[i][j] >= p_variables[i][j] + x_variables[i][j] - 1
            ilp += s_variables[i][j] <= p_variables[i][j]
            ilp += s_variables[i][j] <= p_variables[i][j]
    ilp += 1 - t_variables[0][0] <= s_variables[0][0]

    # define v_i_j variables
    for i in range(len(trace)):
        for j in range(2):
            ilp += v_variables[i][j] >= 1 - s_variables[i][j] + 1 - e_variables[i][j] + x_variables[i][j] - 2
            ilp += v_variables[i][j] <= x_variables[i][j]
            ilp += v_variables[i][j] <= 1 - e_variables[i][j]
            ilp += v_variables[i][j] <= 1 - s_variables[i][j]

    status = ilp.solve()
    assert status == 1

    alignments_to_calculate = []
    sub_trace = Trace()
    current_subtree_idx = 0
    for i in range(len(trace)):
        for j in range(2):
            if t_variables[i][j].varValue:
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
            if x_variables[i][j].varValue:
                if j == current_subtree_idx:
                    sub_trace.append(trace[i])
                else:
                    alignments_to_calculate.append((pt.children[current_subtree_idx], sub_trace))
                    sub_trace = Trace()
                    sub_trace.append(trace[i])
                    current_subtree_idx = j
    if len(sub_trace) > 0:
        alignments_to_calculate.append((pt.children[current_subtree_idx], sub_trace))
    if t_variables[len(trace)][0].varValue:
        alignments_to_calculate.append((pt.children[0], Trace()))

    res = []
    for subtree, sub_trace in alignments_to_calculate:
        align_result = __approximate_alignment_for_trace(subtree, a_sets, sa_sets, ea_sets, tau_flags, sub_trace, tl, th,
                                              parameters=parameters)
        if align_result is None:
            # the alignment did not terminate correctly.
            return None
        res.extend(align_result)
    return res


def __approximate_alignment_on_sequence(pt: ProcessTree, trace: Trace, a_sets: Dict[ProcessTree, Set[str]],
                                        sa_sets: Dict[ProcessTree, Set[str]], ea_sets: Dict[ProcessTree, Set[str]],
                                        tau_flags: Dict[ProcessTree, bool], tl: int, th: int,
                                        parameters=None):
    if parameters is None:
        parameters = {}

    from pulp import lpSum, LpVariable, LpProblem, LpMinimize

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, DEFAULT_NAME_KEY)

    assert pt.operator == Operator.SEQUENCE
    assert len(pt.children) > 0
    assert len(trace) > 0

    ilp = LpProblem(sense=LpMinimize)

    # x_i_j = 1 <=> assigns activity i to subtree j
    x_variables = {}

    # s_i_j = 1 <=> activity i is a start activity in the current sub-trace assigned to subtree j
    s_variables = {}

    # e_i_j = 1 <=> activity i is an end activity in the current sub-trace assigned to subtree j
    e_variables = {}

    # auxiliary u_j <=> u_j=1 if an activity is assigned to subtree j
    u_variables = {}

    # v_i_j = 1 <=> activity i is neither a start nor end-activity in the current sub-trace assigned to subtree j
    v_variables = {}

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
        [(1 - u_variables[j]) * u_costs[j] for j in range(len(pt.children))]), "objective_function"

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

    alignments_to_calculate = []
    for j in range(len(pt.children)):
        sub_trace = Trace()
        for i in range(len(trace)):
            if x_variables[i][j].varValue == 1:
                sub_trace.append(trace[i])
        alignments_to_calculate.append((pt.children[j], sub_trace))
    # calculate and compose alignments
    res = []
    for subtree, sub_trace in alignments_to_calculate:
        align_result = __approximate_alignment_for_trace(subtree, a_sets, sa_sets, ea_sets, tau_flags, sub_trace, tl, th,
                                              parameters=parameters)
        if align_result is None:
            # the alignment did not terminate correctly.
            return None
        res.extend(align_result)
    return res


def __approximate_alignment_on_parallel(pt: ProcessTree, trace: Trace, a_sets: Dict[ProcessTree, Set[str]],
                                        sa_sets: Dict[ProcessTree, Set[str]], ea_sets: Dict[ProcessTree, Set[str]],
                                        tau_flags: Dict[ProcessTree, bool], tl: int, th: int,
                                        parameters=None):
    if parameters is None:
        parameters = {}

    from pulp import lpSum, LpVariable, LpProblem, LpMinimize

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, DEFAULT_NAME_KEY)

    assert pt.operator == Operator.PARALLEL
    assert len(pt.children) > 0
    assert len(trace) > 0

    ilp = LpProblem(sense=LpMinimize)

    # x_i_j = 1 <=> assigns activity i to subtree j
    x_variables = {}

    # s_i_j = 1 <=> activity i is a start activity in the current sub-trace assigned to subtree j
    s_variables = {}

    # e_i_j = 1 <=> activity i is an end activity in the current sub-trace assigned to subtree j
    e_variables = {}

    # auxiliary u_j <=> u_j=1 if an activity is assigned to subtree j
    u_variables = {}

    # v_i_j = 1 <=> activity i is neither a start nor end-activity in the current sub-trace assigned to subtree j
    v_variables = {}

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
        [(1 - u_variables[j]) * u_costs[j] for j in range(len(pt.children))]), "objective_function"

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
    trace_parts = []
    last_subtree = None
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
    alignments_per_subtree = {}
    for j in range(len(pt.children)):
        subtree = pt.children[j]
        sub_trace = Trace()
        for trace_part in trace_parts:
            if subtree == trace_part[0]:
                sub_trace = concatenate_traces(sub_trace, trace_part[1])
        align_result = __approximate_alignment_for_trace(subtree, a_sets, sa_sets, ea_sets,
                                                                            tau_flags, sub_trace, tl, th,
                                                                            parameters=parameters)
        if align_result is None:
            # the alignment did not terminate correctly.
            return None
        alignments_per_subtree[subtree] = align_result
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

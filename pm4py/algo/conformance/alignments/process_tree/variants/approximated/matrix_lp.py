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
from pm4py.util.lp import solver
from enum import Enum
import numpy as np
from copy import copy
import sys
import time
from pm4py.util import variants_util

TOL = 0.1 ** 6


class Parameters(Enum):
    MAX_TRACE_LENGTH = "max_trace_length"
    MAX_PROCESS_TREE_HEIGHT = "max_process_tree_height"
    PARAMETER_VARIANT_DELIMITER = "variant_delimiter"
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    PARAM_MAX_ALIGN_TIME_TRACE = "max_align_time_trace"
    PARAM_MAX_ALIGN_TIME = "max_align_time"
    SUBTREE_ALIGN_CACHE = "subtree_align_cache"


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

    parameters[Parameters.SUBTREE_ALIGN_CACHE] = {}

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

    var_keys_with_trace_length = list((x, len(log[y[0]])) for x, y in variants.items())
    var_keys_with_trace_length = sorted(var_keys_with_trace_length, key=lambda x: x[1])
    var_keys = [x[0] for x in var_keys_with_trace_length]

    for i, var in enumerate(var_keys):
        this_time = time.time()

        if this_time - log_alignment_start_time <= max_align_time:
            parameters["trace_alignment_start_time"] = this_time
            alignment = __approximate_alignment_for_trace(pt, a_sets, sa_sets, ea_sets, tau_sets, log[variants[var][0]],
                                                          max_tl, max_th,
                                                          parameters=parameters)
            alignment = add_fitness_and_cost_info_to_alignments(alignment, pt, log[variants[var][0]],
                                                                parameters=parameters)
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
    subtree_align_cache = exec_utils.get_param_value(Parameters.SUBTREE_ALIGN_CACHE, parameters, {})
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, DEFAULT_NAME_KEY)

    start_time = parameters["trace_alignment_start_time"]
    current_time = time.time()

    trace_activities = tuple([x[activity_key] for x in trace])

    id_pt = id(pt)

    # if the combination process tree-trace is in the cache
    # use the cache to avoid further computations
    if (id_pt, trace_activities) in subtree_align_cache:
        return copy(subtree_align_cache[(id_pt, trace_activities)])

    if current_time - start_time > max_align_time_trace:
        # the alignment of the trace did not terminate in an useful time
        subtree_align_cache[(id_pt, trace_activities)] = None
        return None

    try:
        if len(trace) <= max_tl or get_process_tree_height(pt) <= max_th:
            aligned_trace = calculate_optimal_alignment(pt, trace, parameters=parameters)
            subtree_align_cache[(id_pt, trace_activities)] = copy(aligned_trace)
            return aligned_trace
        else:
            if pt.operator == Operator.SEQUENCE:
                aligned_trace = __approximate_alignment_on_sequence(pt, trace, a_sets, sa_sets, ea_sets, tau_flags,
                                                                    max_tl,
                                                                    max_th,
                                                                    parameters=parameters)
                subtree_align_cache[(id_pt, trace_activities)] = copy(aligned_trace)
                return aligned_trace
            elif pt.operator == Operator.LOOP:
                aligned_trace = __approximate_alignment_on_loop(pt, trace, a_sets, sa_sets, ea_sets, tau_flags, max_tl,
                                                                max_th,
                                                                parameters=parameters)
                subtree_align_cache[(id_pt, trace_activities)] = copy(aligned_trace)
                return aligned_trace
            elif pt.operator == Operator.XOR:
                aligned_trace = __approximate_alignment_on_choice(pt, trace, a_sets, sa_sets, ea_sets, tau_flags,
                                                                  max_tl, max_th,
                                                                  parameters=parameters)
                subtree_align_cache[(id_pt, trace_activities)] = copy(aligned_trace)
                return aligned_trace
            elif pt.operator == Operator.PARALLEL:
                aligned_trace = __approximate_alignment_on_parallel(pt, trace, a_sets, sa_sets, ea_sets, tau_flags,
                                                                    max_tl,
                                                                    max_th,
                                                                    parameters=parameters)
                subtree_align_cache[(id_pt, trace_activities)] = copy(aligned_trace)
                return aligned_trace
    except AlignmentNoneException:
        # alignment did not terminate correctly. return None
        subtree_align_cache[(id_pt, trace_activities)] = None
        return None
    except IndexError:
        # alignment did not terminate correctly. return None
        subtree_align_cache[(id_pt, trace_activities)] = None
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
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, DEFAULT_NAME_KEY)

    assert pt.operator == Operator.LOOP
    assert len(pt.children) == 2
    assert len(trace) > 0

    # x_i_j = 1 <=> assigns activity i to subtree j
    x__variables = {}
    # t_i_j = 1 <=> inserts a tau at position i and assigns it to subtree j
    t__variables = {}
    # s_i_j = 1 <=> activity i is a start activity in the current sub-trace assigned to subtree j
    s__variables = {}
    # e_i_j = 1 <=> activity i is an end activity in the current sub-trace assigned to subtree j
    e__variables = {}
    # v_i_j = 1 <=> activity i is neither a start nor end-activity in the current sub-trace assigned to subtree j
    v__variables = {}
    # auxiliary variables
    # p_i_j = 1 <=> previous activity i-1 is assigned to the other subtree or t_1_other-subtree is 1
    p__variables = {}
    # n_i_j = 1 <=> next activity i+1 is assigned to the other subtree or t_1_other-subtree is 1
    n__variables = {}

    t__costs = {}
    s__costs = {}
    e__costs = {}
    v__costs = {}
    all_variables = []

    Aub = []
    Aeq = []
    bub = []
    beq = []

    for i, a in enumerate(trace):
        x__variables[i] = {}
        s__variables[i] = {}
        s__costs[i] = {}
        e__variables[i] = {}
        e__costs[i] = {}
        v__variables[i] = {}
        v__costs[i] = {}
        p__variables[i] = {}
        n__variables[i] = {}
        for j, subtree in enumerate(pt.children):
            all_variables.append('x_' + str(i) + '_' + str(j))
            x__variables[i][j] = len(all_variables) - 1
            all_variables.append('s_' + str(i) + '_' + str(j))
            s__variables[i][j] = len(all_variables) - 1
            s__costs[i][j] = 0 if a[activity_key] in sa_sets[subtree] else 1
            all_variables.append('e_' + str(i) + '_' + str(j))
            e__variables[i][j] = len(all_variables) - 1
            e__costs[i][j] = 0 if a[activity_key] in ea_sets[subtree] else 1
            all_variables.append('v_' + str(i) + '_' + str(j))
            v__variables[i][j] = len(all_variables) - 1
            v__costs[i][j] = 0 if a[activity_key] in a_sets[subtree] else 1
            all_variables.append('p_' + str(i) + '_' + str(j))
            p__variables[i][j] = len(all_variables) - 1
            all_variables.append('n_' + str(i) + '_' + str(j))
            n__variables[i][j] = len(all_variables) - 1

    for i in range(len(trace) + 1):
        t__variables[i] = {}
        t__costs[i] = {}
        for j, subtree in enumerate(pt.children):
            all_variables.append('t_' + str(i) + '_' + str(j))
            t__variables[i][j] = len(all_variables) - 1
            if tau_flags[subtree]:
                t__costs[i][j] = -0.00001  # favour to add a cut if possible over not putting a cut
            else:
                if len(sa_sets[subtree].intersection(ea_sets[subtree])) != 0:
                    t__costs[i][j] = 1
                else:
                    t__costs[i][j] = 2

    c = [0] * len(all_variables)
    for i in range(len(trace)):
        for j in range(len(pt.children)):
            c[s__variables[i][j]] = s__costs[i][j]

    for i in range(len(trace)):
        for j in range(len(pt.children)):
            c[e__variables[i][j]] = e__costs[i][j]

    for i in range(len(trace)):
        for j in range(len(pt.children)):
            c[v__variables[i][j]] = v__costs[i][j]

    for i in range(len(trace) + 1):
        for j in range(len(pt.children)):
            c[t__variables[i][j]] = t__costs[i][j]

    # first tau can never be assigned to the 2nd subtree
    r = [0] * len(all_variables)
    r[t__variables[0][1]] = 1
    Aeq.append(r)
    beq.append(0)

    # last tau can never be assigned to the 2nd subtree
    r = [0] * len(all_variables)
    r[t__variables[len(trace)][1]] = 1
    Aeq.append(r)
    beq.append(0)

    # if first/last tau is not used --> first/last activity is assigned to 1st subtree
    r = [0] * len(all_variables)
    r[t__variables[0][0]] = -1
    r[x__variables[0][0]] = -1
    Aub.append(r)
    bub.append(-1)

    r = [0] * len(all_variables)
    r[t__variables[len(trace)][0]] = -1
    r[x__variables[len(trace) - 1][0]] = -1
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
            r1[x__variables[i][j]] = 1
            r2[x__variables[i][j]] = 1
            r3[x__variables[i][j]] = 1
            r4[x__variables[i][j]] = 1
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
            r[t__variables[i][j]] = 1
        Aub.append(r)
        bub.append(1)

    # if tau is used and hence, assigned to a subtree, the surrounding activities are assigned to the other subtree
    for i in range(1, len(trace)):
        # if tau at position i is assigned to 1st subtree, the previous activity is assigned to 2nd subtree
        r1 = [0] * len(all_variables)
        # if tau at position i is assigned to 1st subtree, the previous activity is assigned to 2nd subtree
        r2 = [0] * len(all_variables)
        r1[t__variables[i][0]] = 1
        r1[x__variables[i - 1][1]] = -1
        r2[t__variables[i][1]] = 1
        r2[x__variables[i - 1][0]] = -1
        Aub.append(r1)
        Aub.append(r2)
        bub.append(0)
        bub.append(0)

    for i in range(len(trace)):
        # if tau at position i is assigned to 1st subtree, the next activity is assigned to 2nd subtree
        r1 = [0] * len(all_variables)
        # if tau at position i is assigned to 2nd subtree, the next activity is assigned to 1st subtree
        r2 = [0] * len(all_variables)
        r1[t__variables[i][0]] = 1
        r1[x__variables[i][1]] = -1
        r2[t__variables[i][1]] = 1
        r2[x__variables[i][0]] = -1
        Aub.append(r1)
        Aub.append(r2)
        bub.append(0)
        bub.append(0)

    # if last tau is used and assigned to 1st subtree (assigning it to the 2nd subtree is already forbidden by another
    # constraint) --> last activity must be assigned to 2nd subtree
    r = [0] * len(all_variables)
    r[t__variables[len(trace)][0]] = 1
    r[x__variables[len(trace) - 1][1]] = -1
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

        r1[n__variables[i][0]] = 1
        r1[x__variables[i + 1][1]] = -1
        r1[t__variables[i + 1][1]] = -1
        r2[n__variables[i][0]] = -1
        r2[x__variables[i + 1][1]] = 1
        r3[n__variables[i][0]] = -1
        r3[t__variables[i + 1][1]] = 1
        r4[n__variables[i][1]] = 1
        r4[x__variables[i + 1][0]] = -1
        r4[t__variables[i + 1][0]] = -1
        r5[n__variables[i][1]] = -1
        r5[x__variables[i + 1][0]] = 1
        r6[n__variables[i][1]] = -1
        r6[t__variables[i + 1][0]] = 1
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
    r[t__variables[len(trace)][1]] = 1
    r[n__variables[len(trace) - 1][0]] = -1
    Aub.append(r)
    bub.append(0)

    r = [0] * len(all_variables)
    r[t__variables[len(trace)][0]] = 1
    r[n__variables[len(trace) - 1][1]] = -1
    Aub.append(r)
    bub.append(0)

    # define e_i_j variables
    for i in range(len(trace)):
        for j in range(2):
            r1 = [0] * len(all_variables)
            r2 = [0] * len(all_variables)
            r3 = [0] * len(all_variables)
            r1[e__variables[i][j]] = 1
            r1[n__variables[i][j]] = -1
            r2[e__variables[i][j]] = 1
            r2[x__variables[i][j]] = -1
            r3[e__variables[i][j]] = -1
            r3[n__variables[i][j]] = 1
            r3[x__variables[i][j]] = 1
            Aub.append(r1)
            Aub.append(r2)
            Aub.append(r3)
            bub.append(0)
            bub.append(0)
            bub.append(1)

    # define auxiliary variables p: p_i_1 = 1 <=> previous activity i-1 is assigned to 2nd subtree or t_i-1_2 = 1
    r1 = [0] * len(all_variables)
    r1[t__variables[0][1]] = 1
    r1[p__variables[0][0]] = -1
    r2 = [0] * len(all_variables)
    r2[p__variables[0][1]] = 1
    r2[t__variables[0][0]] = -1
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
        r1[p__variables[i][0]] = 1
        r1[t__variables[i][1]] = -1
        r1[x__variables[i - 1][1]] = -1
        r2[p__variables[i][0]] = -1
        r2[t__variables[i][1]] = 1
        r3[p__variables[i][0]] = -1
        r3[x__variables[i - 1][1]] = 1
        r4[p__variables[i][1]] = -1
        r4[t__variables[i][0]] = 1
        r4[x__variables[i - 1][0]] = 1
        r5[p__variables[i][1]] = -1
        r5[t__variables[i][0]] = 1
        r6[p__variables[i][1]] = -1
        r6[x__variables[i - 1][0]] = 1
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
            r1[s__variables[i][j]] = -1
            r1[p__variables[i][j]] = 1
            r1[x__variables[i][j]] = 1
            r2[s__variables[i][j]] = 1
            r2[p__variables[i][j]] = -1
            r3[s__variables[i][j]] = 1
            r3[p__variables[i][j]] = -1
            Aub.append(r1)
            Aub.append(r2)
            Aub.append(r3)
            bub.append(1)
            bub.append(0)
            bub.append(0)

    r = [0] * len(all_variables)
    r[t__variables[0][0]] = -1
    r[s__variables[0][0]] = -1
    Aub.append(r)
    bub.append(-1)

    # define v_i_j variables
    for i in range(len(trace)):
        for j in range(2):
            r1 = [0] * len(all_variables)
            r2 = [0] * len(all_variables)
            r3 = [0] * len(all_variables)
            r4 = [0] * len(all_variables)

            r1[v__variables[i][j]] = -1
            r1[s__variables[i][j]] = -1
            r1[e__variables[i][j]] = -1
            r1[x__variables[i][j]] = 1

            r2[v__variables[i][j]] = 1
            r2[x__variables[i][j]] = -1

            r3[v__variables[i][j]] = 1
            r3[e__variables[i][j]] = 1

            r4[v__variables[i][j]] = 1
            r4[s__variables[i][j]] = 1

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

    points = __ilp_solve(c, Aub, bub, Aeq, beq)

    for i in t__variables:
        for j in t__variables[i]:
            t__variables[i][j] = True if points[t__variables[i][j]] == 1 else False
    for i in x__variables:
        for j in x__variables[i]:
            x__variables[i][j] = True if points[x__variables[i][j]] == 1 else False

    t_variables = t__variables
    x_variables = x__variables

    alignments_to_calculate = []
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
        align_result = __approximate_alignment_for_trace(subtree, a_sets, sa_sets, ea_sets, tau_flags, sub_trace, tl,
                                                         th,
                                                         parameters=parameters)
        if align_result is None:
            # the alignment did not terminate correctly
            return None
        res.extend(align_result)
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

    # x_i_j = 1 <=> assigns activity i to subtree j
    x__variables = {}

    # s_i_j = 1 <=> activity i is a start activity in the current sub-trace assigned to subtree j
    s__variables = {}

    # e_i_j = 1 <=> activity i is an end activity in the current sub-trace assigned to subtree j
    e__variables = {}

    # auxiliary u_j <=> u_j=1 if an activity is assigned to subtree j
    u__variables = {}

    # v_i_j = 1 <=> activity i is neither a start nor end-activity in the current sub-trace assigned to subtree j
    v__variables = {}

    s__costs = {}
    e__costs = {}
    u__costs = {}
    v__costs = {}

    all_variables = []

    for i, a in enumerate(trace):
        x__variables[i] = {}
        s__variables[i] = {}
        s__costs[i] = {}
        e__variables[i] = {}
        e__costs[i] = {}
        v__variables[i] = {}
        v__costs[i] = {}

        for j, subtree in enumerate(pt.children):
            all_variables.append('x_' + str(i) + '_' + str(j))
            x__variables[i][j] = len(all_variables) - 1
            all_variables.append('s_' + str(i) + '_' + str(j))
            s__variables[i][j] = len(all_variables) - 1
            all_variables.append('e_' + str(i) + '_' + str(j))
            e__variables[i][j] = len(all_variables) - 1
            all_variables.append('v_' + str(i) + '_' + str(j))
            v__variables[i][j] = len(all_variables) - 1
            s__costs[i][j] = 0 if a[activity_key] in sa_sets[subtree] else 1
            e__costs[i][j] = 0 if a[activity_key] in ea_sets[subtree] else 1
            v__costs[i][j] = 0 if a[activity_key] in a_sets[subtree] else 1

    for j in range(len(pt.children)):
        all_variables.append('u_' + str(j))
        u__variables[j] = len(all_variables) - 1
        # define costs to not assign anything to subtree j
        if tau_flags[pt.children[j]]:
            u__costs[j] = 0
        elif sa_sets[pt.children[j]] & ea_sets[pt.children[j]]:
            # intersection of start-activities and end-activities is not empty
            u__costs[j] = 1
        else:
            # intersection of start-activities and end-activities is empty
            u__costs[j] = 2

    # objective function
    c = [0] * len(all_variables)
    for i in range(len(trace)):
        for j in range(len(pt.children)):
            c[v__variables[i][j]] = v__costs[i][j]
    for i in range(len(trace)):
        for j in range(len(pt.children)):
            c[s__variables[i][j]] = s__costs[i][j]
    for i in range(len(trace)):
        for j in range(len(pt.children)):
            c[e__variables[i][j]] = e__costs[i][j]
    for j in range(len(pt.children)):
        c[u__variables[j]] = -u__costs[j]
    Aub = []
    bub = []
    Aeq = []
    beq = []

    # every activity is assigned to one subtree
    for i in range(len(trace)):
        r = [0] * len(all_variables)
        for j in range(len(pt.children)):
            r[x__variables[i][j]] = 1
        Aeq.append(r)
        beq.append(1)

    for j in range(len(pt.children)):
        r1 = [0] * len(all_variables)
        r2 = [0] * len(all_variables)
        # first activity is start activity
        r1[x__variables[0][j]] = 1
        r1[s__variables[0][j]] = -1
        # last activity is an end activity
        r2[x__variables[len(trace) - 1][j]] = 1
        r2[e__variables[len(trace) - 1][j]] = -1
        Aub.append(r1)
        Aub.append(r2)
        bub.append(0)
        bub.append(0)

    # define s_i_j variables
    for i in range(1, len(trace)):
        for j in range(len(pt.children)):
            r1 = [0] * len(all_variables)
            r2 = [0] * len(all_variables)
            r3 = [0] * len(all_variables)
            r1[s__variables[i][j]] = -1
            r1[x__variables[i][j]] = 1
            r1[x__variables[i - 1][j]] = -1
            r2[s__variables[i][j]] = 1
            r2[x__variables[i][j]] = -1
            r3[s__variables[i][j]] = 1
            r3[x__variables[i - 1][j]] = 1
            Aub.append(r1)
            Aub.append(r2)
            Aub.append(r3)
            bub.append(0)
            bub.append(0)
            bub.append(1)

    for i in range(len(trace)):
        r = [0] * len(all_variables)
        for j in range(len(pt.children)):
            r[s__variables[i][j]] = 1
        Aub.append(r)
        bub.append(1)

    # define e_i_j variables
    for i in range(len(trace) - 1):
        for j in range(len(pt.children)):
            r1 = [0] * len(all_variables)
            r2 = [0] * len(all_variables)
            r3 = [0] * len(all_variables)
            r1[e__variables[i][j]] = -1
            r1[x__variables[i][j]] = 1
            r1[x__variables[i + 1][j]] = -1
            r2[e__variables[i][j]] = 1
            r2[x__variables[i][j]] = -1
            r3[e__variables[i][j]] = 1
            r3[x__variables[i + 1][j]] = 1
            Aub.append(r1)
            Aub.append(r2)
            Aub.append(r3)
            bub.append(0)
            bub.append(0)
            bub.append(1)
    for i in range(len(trace)):
        # activity can be only for one subtree an end-activity
        r = [0] * len(all_variables)
        for j in range(len(pt.children)):
            r[e__variables[i][j]] = 1
        Aub.append(r)
        bub.append(1)

    # constraint - preserving sequence when assigning activities to subtrees
    for i in range(len(trace) - 1):
        for j in range(len(pt.children)):
            r = [0] * len(all_variables)
            for k in range(j, len(pt.children)):
                r[x__variables[i + 1][k]] = -1
            r[x__variables[i][j]] = 1
            Aub.append(r)
            bub.append(0)

    # define u_j variables
    for j in range(len(pt.children)):
        for i in range(len(trace)):
            r = [0] * len(all_variables)
            r[u__variables[j]] = -1
            r[x__variables[i][j]] = 1
            Aub.append(r)
            bub.append(0)
        r1 = [0] * len(all_variables)
        r2 = [0] * len(all_variables)
        r1[u__variables[j]] = 1
        r2[u__variables[j]] = 1

        for i in range(len(trace)):
            r1[s__variables[i][j]] = -1
            r2[e__variables[i][j]] = -1
        Aub.append(r1)
        Aub.append(r2)
        bub.append(0)
        bub.append(0)

    # define v_i_j variables
    for i in range(len(trace)):
        for j in range(2):
            r1 = [0] * len(all_variables)
            r2 = [0] * len(all_variables)
            r3 = [0] * len(all_variables)
            r4 = [0] * len(all_variables)

            r1[v__variables[i][j]] = -1
            r1[s__variables[i][j]] = -1
            r1[e__variables[i][j]] = -1
            r1[x__variables[i][j]] = 1

            r2[v__variables[i][j]] = 1
            r2[x__variables[i][j]] = -1

            r3[v__variables[i][j]] = 1
            r3[e__variables[i][j]] = 1

            r4[v__variables[i][j]] = 1
            r4[s__variables[i][j]] = 1

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

    points = __ilp_solve(c, Aub, bub, Aeq, beq)

    for i in x__variables:
        for j in x__variables[i]:
            x__variables[i][j] = True if points[x__variables[i][j]] == 1 else False

    x_variables = x__variables

    alignments_to_calculate = []
    for j in range(len(pt.children)):
        sub_trace = Trace()
        for i in range(len(trace)):
            if x_variables[i][j] == 1:
                sub_trace.append(trace[i])
        alignments_to_calculate.append((pt.children[j], sub_trace))
    # calculate and compose alignments
    res = []
    for subtree, sub_trace in alignments_to_calculate:
        align_result = __approximate_alignment_for_trace(subtree, a_sets, sa_sets, ea_sets, tau_flags, sub_trace, tl,
                                                         th,
                                                         parameters=parameters)
        if align_result is None:
            # the alignment did not terminate correctly
            return None
        res.extend(align_result)

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

    x__variables = {}
    s__variables = {}
    e__variables = {}
    u__variables = {}
    v__variables = {}

    s__costs = {}
    e__costs = {}
    u__costs = {}
    v__costs = {}
    all_variables = []

    for i, a in enumerate(trace):
        x__variables[i] = {}
        s__variables[i] = {}
        s__costs[i] = {}
        e__variables[i] = {}
        e__costs[i] = {}
        v__variables[i] = {}
        v__costs[i] = {}

        for j, subtree in enumerate(pt.children):
            all_variables.append('x_' + str(i) + '_' + str(j))
            x__variables[i][j] = len(all_variables) - 1
            all_variables.append('s_' + str(i) + '_' + str(j))
            s__variables[i][j] = len(all_variables) - 1
            all_variables.append('e_' + str(i) + '_' + str(j))
            e__variables[i][j] = len(all_variables) - 1
            all_variables.append('v_' + str(i) + '_' + str(j))
            v__variables[i][j] = len(all_variables) - 1
            s__costs[i][j] = 0 if a[activity_key] in sa_sets[subtree] else 1
            e__costs[i][j] = 0 if a[activity_key] in ea_sets[subtree] else 1
            v__costs[i][j] = 0 if a[activity_key] in a_sets[subtree] else 1

    for j in range(len(pt.children)):
        all_variables.append('u_' + str(j))
        u__variables[j] = len(all_variables) - 1
        # define costs to not assign anything to subtree j
        if tau_flags[pt.children[j]]:
            u__costs[j] = 0
        elif sa_sets[pt.children[j]] & ea_sets[pt.children[j]]:
            # intersection of start-activities and end-activities is not empty
            u__costs[j] = 1
        else:
            # intersection of start-activities and end-activities is empty
            u__costs[j] = 2

    c = [0] * len(all_variables)
    for i in range(len(trace)):
        for j in range(len(pt.children)):
            c[v__variables[i][j]] = v__costs[i][j]
            c[s__variables[i][j]] = s__costs[i][j]
            c[e__variables[i][j]] = e__costs[i][j]
    for j in range(len(pt.children)):
        c[u__variables[j]] = -u__costs[j]
    Aub = []
    bub = []
    Aeq = []
    beq = []

    for i in range(len(trace)):
        r = [0] * len(all_variables)
        for j in range(len(pt.children)):
            r[x__variables[i][j]] = 1
        Aeq.append(r)
        beq.append(1)

    for j in range(len(pt.children)):
        r1 = [0] * len(all_variables)
        r2 = [0] * len(all_variables)

        # first activity is a start activity
        r1[x__variables[0][j]] = 1
        r1[s__variables[0][j]] = -1
        # last activity is an end-activity
        r2[x__variables[len(trace) - 1][j]] = 1
        r2[e__variables[len(trace) - 1][j]] = -1

        Aub.append(r1)
        Aub.append(r2)
        bub.append(0)
        bub.append(0)

    # define s_i_j variables
    for i in range(len(trace)):
        for j in range(len(pt.children)):
            r = [0] * len(all_variables)
            r[s__variables[i][j]] = 1
            r[x__variables[i][j]] = -1
            Aub.append(r)
            bub.append(0)
            for k in range(i):
                r = [0] * len(all_variables)
                r[s__variables[i][j]] = 1
                r[x__variables[k][j]] = 1
                Aub.append(r)
                bub.append(1)
        r = [0] * len(all_variables)
        for j in range(len(pt.children)):
            r[s__variables[i][j]] = 1
        Aub.append(r)
        bub.append(1)

    # define e_i_j variables
    for i in range(len(trace)):
        for j in range(len(pt.children)):
            r = [0] * len(all_variables)
            r[e__variables[i][j]] = 1
            r[x__variables[i][j]] = -1
            Aub.append(r)
            bub.append(0)
            for k in range(i + 1, len(trace)):
                r = [0] * len(all_variables)
                r[e__variables[i][j]] = 1
                r[x__variables[k][j]] = 1
                Aub.append(r)
                bub.append(1)
        # activity can be only an end-activity for one subtree
        r = [0] * len(all_variables)
        for j in range(len(pt.children)):
            r[e__variables[i][j]] = 1
        Aub.append(r)
        bub.append(1)

    for j in range(len(pt.children)):
        r2 = [0] * len(all_variables)
        r3 = [0] * len(all_variables)

        r2[u__variables[j]] = 1
        r3[u__variables[j]] = 1
        for i in range(len(trace)):
            r1 = [0] * len(all_variables)

            # define u_j variables
            r1[u__variables[j]] = -1
            r1[x__variables[i][j]] = 1
            Aub.append(r1)
            bub.append(0)

            # if u_j variable = 1 ==> a start activity must exist
            r2[s__variables[i][j]] = -1
            # if u_j variable = 1 ==> an end activity must exist
            r3[e__variables[i][j]] = -1

        Aub.append(r2)
        bub.append(0)
        Aub.append(r3)
        bub.append(0)

    # define v_i_j variables
    for i in range(len(trace)):
        for j in range(2):
            r1 = [0] * len(all_variables)
            r2 = [0] * len(all_variables)
            r3 = [0] * len(all_variables)
            r4 = [0] * len(all_variables)

            r1[v__variables[i][j]] = -1
            r1[s__variables[i][j]] = -1
            r1[e__variables[i][j]] = -1
            r1[x__variables[i][j]] = 1

            r2[v__variables[i][j]] = 1
            r2[x__variables[i][j]] = -1

            r3[v__variables[i][j]] = 1
            r3[e__variables[i][j]] = 1

            r4[v__variables[i][j]] = 1
            r4[s__variables[i][j]] = 1

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

    points = __ilp_solve(c, Aub, bub, Aeq, beq)

    for i in x__variables:
        for j in x__variables[i]:
            x__variables[i][j] = True if points[x__variables[i][j]] == 1 else False

    x_variables = x__variables

    # trace_parts list contains trace parts mapped onto the determined subtree
    trace_parts = []
    last_subtree = None
    for i in range(len(trace)):
        for j in range(len(pt.children)):
            subtree = pt.children[j]
            if x_variables[i][j]:
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


def __ilp_solve(c, Aub, bub, Aeq, beq):
    Aeq = np.asmatrix(Aeq).astype(np.float64)
    beq = np.asmatrix(beq).transpose().astype(np.float64)
    Aub = np.asmatrix(Aub).astype(np.float64)
    bub = np.asmatrix(bub).transpose().astype(np.float64)

    if "cvxopt" in solver.DEFAULT_LP_SOLVER_VARIANT:
        # does this part only if cvxopt is imported
        from cvxopt import matrix
        c = matrix([x * 1.0 for x in c])
        Aeq = matrix(Aeq)
        beq = matrix(beq)
        Aub = matrix(Aub)
        bub = matrix(bub)

        # tries to solve the problem with LP solving
        # (faster)
        # if it produces a vector which elements are different from 0 or 1
        # then use the ILP solver
        sol = solver.apply(c, Aub, bub, Aeq, beq, variant="cvxopt_solver_custom_align")
        points = solver.get_points_from_sol(sol, variant="cvxopt_solver_custom_align")
        condition_points = True
        for x in points:
            if x > TOL or x < 1 - TOL:
                continue
            condition_points = False
            break
        # there is at least one point in the solution that is not integer.
        # in that case, it is better to apply the ILP solver instead of just rounding the points
        if condition_points is False:
            sol = solver.apply(c, Aub, bub, Aeq, beq, variant="cvxopt_solver_custom_align_ilp")
            points = solver.get_points_from_sol(sol, variant="cvxopt_solver_custom_align_ilp")
        # round the points to the nearest integer (0 or 1).
        # if the ILP solver is called, these are already integer
        points = [round(x) for x in points]
    else:
        # calls other linear solvers (pulp, ortools) with REQUIRE_ILP set to True
        sol = solver.apply(c, Aub, bub, Aeq, beq, variant=solver.DEFAULT_LP_SOLVER_VARIANT,
                           parameters={solver.Parameters.REQUIRE_ILP: True})
        points = solver.get_points_from_sol(sol, variant=solver.DEFAULT_LP_SOLVER_VARIANT)

    return points

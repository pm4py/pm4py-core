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
from enum import Enum
from typing import Set, List

from pm4py.algo.conformance.alignments.petri_net.algorithm import Parameters as AlignParameters
from pm4py.algo.conformance.alignments.petri_net.algorithm import Variants
from pm4py.algo.conformance.alignments.petri_net.algorithm import apply as get_alignment
from pm4py.algo.conformance.alignments.petri_net.variants.state_equation_a_star import get_best_worst_cost
from pm4py.objects.conversion.process_tree import converter as pt_converter
from pm4py.objects.log.obj import Trace, Event
from pm4py.objects.petri_net.utils.align_utils import SKIP, STD_MODEL_LOG_MOVE_COST
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.util import exec_utils
from pm4py.util.xes_constants import DEFAULT_NAME_KEY


class Parameters(Enum):
    CLASSIC_ALIGNMENTS_VARIANT = "classic_alignments_variant"
    CONVERSION_VERSION = "petri_conversion_version"


class AlignmentNoneException(Exception):
    # exception that is raise when the alignment is None
    # (failed due to time constraints)
    pass


class EfficientTree(ProcessTree):
    # extend the parent class to replace the __eq__ and __hash__ method
    def __init__(self, tree):
        i = 0
        while i < len(tree.children):
            tree.children[i] = EfficientTree(tree.children[i])
            tree.children[i].parent = self
            i = i + 1
        ProcessTree.__init__(self, operator=tree.operator, parent=tree.parent, children=tree.children, label=tree.label)

    def __eq__(self, other):
        return id(self) == id(other)

    def __hash__(self):
        return id(self)


def concatenate_traces(t1: Trace, t2: Trace) -> Trace:
    for e in t2:
        t1.append(e)
    return t1


def trace_to_list_of_str(t: Trace) -> List[str]:
    return [e[DEFAULT_NAME_KEY] for e in t]


def list_of_str_to_trace(activities: List[str]) -> Trace:
    t = Trace()
    for a in activities:
        e = Event()
        e["concept:name"] = a
        t.append(e)
    return t


def get_activity_labels_from_trace(trace: Trace) -> Set[str]:
    labels = set()
    for a in trace:
        labels.add(a[DEFAULT_NAME_KEY])
    return labels


def apply_standard_cost_function_to_alignment(align: List) -> int:
    res = 0
    if align is not None:
        # do not add the moves, if the alignment did not succeed
        # due to time constraints
        for move in align:
            if move[0] == SKIP and move[1] is not None:
                # visible model move
                res += 1
            elif move[0] != SKIP and move[1] == SKIP:
                # log move
                res += 1
    return res


def empty_sequence_accepted(pt: ProcessTree) -> bool:
    alignment = calculate_optimal_alignment(pt, Trace())
    return alignment["cost"] < STD_MODEL_LOG_MOVE_COST


def calculate_optimal_alignment(pt: ProcessTree, trace: Trace, parameters=None):
    if parameters is None:
        parameters = {}
    align_variant = exec_utils.get_param_value(Parameters.CLASSIC_ALIGNMENTS_VARIANT, parameters,
                                               Variants.VERSION_STATE_EQUATION_A_STAR)
    conversion_version = exec_utils.get_param_value(Parameters.CONVERSION_VERSION, parameters,
                                                    pt_converter.Variants.TO_PETRI_NET_TRANSITION_BORDERED)

    parent = pt.parent
    pt.parent = None
    net, im, fm = pt_converter.apply(pt, variant=conversion_version)

    # in this way, also the other parameters are passed to alignments
    alignment_parameters = copy(parameters)
    alignment_parameters[AlignParameters.PARAM_ALIGNMENT_RESULT_IS_SYNC_PROD_AWARE] = True

    alignment = get_alignment(trace, net, im, fm, variant=align_variant,
                              parameters=alignment_parameters)

    pt.parent = parent
    res = []

    # if the alignment has terminated prematurely due to time constraints, raise an Exception
    if alignment is None:
        raise AlignmentNoneException("alignment terminated prematurely")

    if conversion_version == pt_converter.Variants.TO_PETRI_NET_TRANSITION_BORDERED or conversion_version == pt_converter.Variants.TO_PETRI_NET_TRANSITION_BORDERED.value:
        # remove invisible model moves from alignment steps that do not belong to a silent model move in the process tree
        # this is possible only if the TO_PETRI_NET_TRANSITION_BORDERED variant is used
        for a in alignment["alignment"]:
            if not (a[0][0] == SKIP and not a[0][1].isdigit()):
                res.append(a[1])
    else:
        for a in alignment["alignment"]:
            res.append(a[1])

    return res


def add_fitness_and_cost_info_to_alignments(alignment: List, pt: ProcessTree, trace: Trace, parameters=None) -> List:
    if parameters is None:
        parameters = {}

    def calculate_get_best_worst_cost(tree: ProcessTree, conversion_version) -> int:
        net, im, fm = pt_converter.apply(tree, variant=conversion_version)
        return get_best_worst_cost(net, im, fm)

    conversion_version = exec_utils.get_param_value(Parameters.CONVERSION_VERSION, parameters,
                                                    pt_converter.Variants.TO_PETRI_NET_TRANSITION_BORDERED)
    if alignment is not None:
        # if the alignment is not None, return a nice dictionary with the alignment of the trace
        cost = apply_standard_cost_function_to_alignment(alignment)
        if cost == 0:
            fitness = 1
        else:
            fitness = 1 - cost / (len(trace) + calculate_get_best_worst_cost(pt, conversion_version))
        res = {"alignment": alignment,
               "cost": cost,
               "fitness": fitness}
    else:
        # otherwise, return None
        return None

    return res

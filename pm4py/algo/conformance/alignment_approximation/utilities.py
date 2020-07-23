from pm4py.algo.conformance.alignments.algorithm import apply as get_alignment
from pm4py.algo.conformance.alignments.algorithm import Variants
from pm4py.objects.conversion.process_tree.factory import apply as convert_pt_to_petri_net
from pm4py.objects.log.log import Trace, Event
from pm4py.objects.process_tree.process_tree import ProcessTree
from pm4py.objects.process_tree.util import is_leaf
from typing import Set, List
from pm4py.util.xes_constants import DEFAULT_NAME_KEY
from pm4py.objects.petri.align_utils import SKIP, STD_MODEL_LOG_MOVE_COST


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


def get_process_tree_height(pt: ProcessTree) -> int:
    """
    calculates from the given node the max height downwards
    :param pt: process tree node
    :return: height
    """
    if is_leaf(pt):
        return 1
    else:
        return 1 + max([get_process_tree_height(x) for x in pt.children])


def get_number_leaf_nodes(pt: ProcessTree) -> int:
    if is_leaf(pt):
        return 1
    else:
        res = 0
        for c in pt.children:
            res += get_number_leaf_nodes(c)
        return res


def get_number_nodes(pt: ProcessTree) -> int:
    res = 1
    for c in pt.children:
        res += get_number_nodes(c)
    return res


def get_number_inner_nodes(pt: ProcessTree) -> int:
    if is_leaf(pt):
        return 0
    else:
        res = 1
        for c in pt.children:
            res += get_number_inner_nodes(c)
        return res


def get_activity_labels_from_trace(trace: Trace) -> Set[str]:
    labels = set()
    for a in trace:
        labels.add(a[DEFAULT_NAME_KEY])
    return labels


def get_costs_from_alignment(align) -> int:
    res = 0
    for move in align:
        if move[0] == SKIP and move[1] is not None:
            # visible model move
            res += 1
        elif move[0] != SKIP and move[1] == SKIP:
            # log move
            res += 1
    return res


def empty_sequence_accepted(pt: ProcessTree) -> bool:
    alignment = __calculate_optimal_alignment(pt, Trace(), variant=Variants.VERSION_STATE_EQUATION_A_STAR)
    return alignment["cost"] < STD_MODEL_LOG_MOVE_COST


def process_tree_to_binary_process_tree(pt: ProcessTree) -> ProcessTree:
    if len(pt.children) > 2:
        new_subtree = ProcessTree()
        new_subtree.operator = pt.operator
        new_subtree.children = pt.children[1:]
        pt.children = pt.children[:1]
        pt.children.append(new_subtree)
    for c in pt.children:
        process_tree_to_binary_process_tree(c)
    return pt


def __calculate_optimal_alignment(pt: ProcessTree, trace: Trace, variant=Variants.VERSION_STATE_EQUATION_A_STAR):
    net, im, fm = convert_pt_to_petri_net(pt)
    return get_alignment(trace, net, im, fm, variant=variant)

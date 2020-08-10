from typing import Set
from pm4py.objects.process_tree.process_tree import ProcessTree
from pm4py.objects.process_tree.util import is_leaf, is_tau_leaf
from pm4py.objects.process_tree.pt_operator import Operator


def __get_activity_set(pt: ProcessTree, a_set=None) -> Set[str]:
    if a_set is None:
        a_set = set()
    if is_leaf(pt):
        a_set.add(pt.label)
    else:
        for c in pt.children:
            __get_activity_set(c, a_set)
    return a_set


def __get_start_activity_set_binary_tree(pt: ProcessTree, sa_set=None) -> Set[str]:
    assert pt.children is None or len(pt.children) <= 2
    if sa_set is None:
        sa_set = set()
    if is_leaf(pt) and not is_tau_leaf(pt):
        sa_set.add(pt.label)
    elif not is_tau_leaf(pt):
        assert len(pt.children) == 2
        tau_in_language_sub_pt_1 = __check_empty_sequence_accepted(pt.children[0])

        if pt.operator == Operator.SEQUENCE:
            if not tau_in_language_sub_pt_1:
                return __get_start_activity_set_binary_tree(pt.children[0], sa_set)
            else:
                for c in pt.children:
                    sa_set.union(__get_start_activity_set_binary_tree(c, sa_set))
        elif pt.operator == Operator.PARALLEL or pt.operator == Operator.XOR:
            for c in pt.children:
                sa_set.union(__get_start_activity_set_binary_tree(c, sa_set))
        elif pt.operator == Operator.LOOP:
            if not tau_in_language_sub_pt_1:
                return __get_start_activity_set_binary_tree(pt.children[0], sa_set)
            else:
                for c in pt.children:
                    sa_set.union(__get_start_activity_set_binary_tree(c, sa_set))
    return sa_set


def __get_end_activity_set_binary_tree(pt: ProcessTree, ea_set=None) -> Set[str]:
    assert pt.children is None or len(pt.children) <= 2
    if ea_set is None:
        ea_set = set()
    if is_leaf(pt) and not is_tau_leaf(pt):
        ea_set.add(pt.label)
    elif not is_tau_leaf(pt):
        assert len(pt.children) == 2
        tau_in_language_sub_pt_1 = __check_empty_sequence_accepted(pt.children[0])
        tau_in_language_sub_pt_2 = __check_empty_sequence_accepted(pt.children[1])

        if pt.operator == Operator.SEQUENCE:
            if not tau_in_language_sub_pt_2:
                return __get_end_activity_set_binary_tree(pt.children[1], ea_set)
            else:
                for c in pt.children:
                    ea_set.union(__get_end_activity_set_binary_tree(c, ea_set))
        elif pt.operator == Operator.PARALLEL or pt.operator == Operator.XOR:
            for c in pt.children:
                ea_set.union(__get_end_activity_set_binary_tree(c, ea_set))
        elif pt.operator == Operator.LOOP:
            if not tau_in_language_sub_pt_1:
                return __get_end_activity_set_binary_tree(pt.children[0], ea_set)
            else:
                for c in pt.children:
                    ea_set.union(__get_end_activity_set_binary_tree(c, ea_set))
    return ea_set


def __check_empty_sequence_accepted(pt: ProcessTree) -> bool:
    if is_leaf(pt):
        if is_tau_leaf(pt):
            return True
        else:
            return False
    else:
        assert len(pt.children) == 2
        if pt.operator == Operator.SEQUENCE or pt.operator == Operator.PARALLEL:
            return __check_empty_sequence_accepted(pt.children[0]) and __check_empty_sequence_accepted(pt.children[1])
        elif pt.operator == Operator.XOR:
            return __check_empty_sequence_accepted(pt.children[0]) or __check_empty_sequence_accepted(pt.children[1])
        else:
            assert pt.operator == Operator.LOOP
            return __check_empty_sequence_accepted(pt.children[0])


def initialize_a_sa_ea_tau_sets(pt: ProcessTree, a_sets=None, sa_sets=None, ea_sets=None, tau_sets=None):
    if a_sets is None:
        a_sets = {}
    if sa_sets is None:
        sa_sets = {}
    if ea_sets is None:
        ea_sets = {}
    if tau_sets is None:
        tau_sets = {}

    a_sets[pt] = __get_activity_set(pt)
    sa_sets[pt] = __get_start_activity_set_binary_tree(pt)
    ea_sets[pt] = __get_end_activity_set_binary_tree(pt)
    tau_sets[pt] = __check_empty_sequence_accepted(pt)

    for c in pt.children:
        a_sets, sa_sets, ea_sets, tau_sets = initialize_a_sa_ea_tau_sets(c, a_sets=a_sets, sa_sets=sa_sets,
                                                                         ea_sets=ea_sets, tau_sets=tau_sets)
    return a_sets, sa_sets, ea_sets, tau_sets

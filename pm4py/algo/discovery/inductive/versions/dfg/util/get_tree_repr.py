from pm4py.algo.discovery.dfg.utils.dfg_utils import get_activities_self_loop
from pm4py.algo.discovery.inductive.versions.dfg.util.check_skip_trans import verify_skip_transition_necessity, \
    verify_skip_for_parallel_cut
from pm4py.objects.process_tree import tree_constants
from pm4py.objects.process_tree.process_tree import ProcessTree, PTTransition


def get_transition(counts, label):
    """
    Create a node (transition) with the specified label in the process tree
    """
    counts.inc_no_visible()
    return PTTransition(label, label)


def get_new_hidden_trans(counts, type_trans="unknown"):
    """
    Create a hidden node (transition) in the process tree
    """
    counts.inc_no_hidden()
    return PTTransition(type_trans + '_' + str(counts.num_hidden), None)


def check_loop_need(spec_tree_struct):
    """
    Check whether a forced loop transitions shall be added

    Parameters
    -----------
    spec_tree_struct
        Internal tree structure (after application of Inductive Miner)

    Returns
    -----------
    need_loop_on_subtree
        Checks if the loop on the subtree is needed
    """
    self_loop_activities = set(get_activities_self_loop(spec_tree_struct.initial_dfg))
    self_loop_activities = self_loop_activities.intersection(set(spec_tree_struct.activities))

    need_loop_on_subtree = len(self_loop_activities) > 0

    return need_loop_on_subtree


def get_repr(spec_tree_struct, rec_depth, counts, must_add_skip=False, contains_empty_traces=False):
    """
    Get the representation of a process tree

    Parameters
    -----------
    spec_tree_struct
        Internal tree structure (after application of Inductive Miner)
    rec_depth
        Current recursion depth
    counts
        Count object (keep track of the number of nodes (transitions) added to the tree
    must_add_skip
        Boolean value that indicate if we are forced to add the skip
    contains_empty_traces
        Boolean value that is True if the event log from which the DFG has been extracted contains empty traces

    Returns
    -----------
    final_tree_repr
        Representation of the tree (could be printed, transformed, viewed)
    """
    need_loop_on_subtree = check_loop_need(spec_tree_struct)

    final_tree_repr = ProcessTree()
    final_tree_repr.rec_depth = rec_depth

    if contains_empty_traces and rec_depth == 0:
        rec_depth = rec_depth + 1

    child_tree = ProcessTree()
    if spec_tree_struct.detected_cut == "flower" or (
            spec_tree_struct.detected_cut == "base_concurrent" and need_loop_on_subtree):
        final_tree_repr.set_operator(tree_constants.LOOP_OPERATOR)
        child_tree = ProcessTree()
        child_tree.set_operator(tree_constants.EXCLUSIVE_OPERATOR)
        rec_depth = rec_depth + 1
        child_tree.rec_depth = rec_depth
        final_tree_repr.add_subtree(child_tree)
    elif spec_tree_struct.detected_cut == "base_concurrent":
        final_tree_repr.set_operator(tree_constants.EXCLUSIVE_OPERATOR)
        child_tree = final_tree_repr
    elif spec_tree_struct.detected_cut == "sequential":
        final_tree_repr.set_operator(tree_constants.SEQUENTIAL_OPERATOR)
        child_tree = final_tree_repr
    elif spec_tree_struct.detected_cut == "loopCut":
        final_tree_repr.set_operator(tree_constants.LOOP_OPERATOR)
        child_tree = final_tree_repr
    elif spec_tree_struct.detected_cut == "concurrent":
        final_tree_repr.set_operator(tree_constants.EXCLUSIVE_OPERATOR)
        child_tree = final_tree_repr
    elif spec_tree_struct.detected_cut == "parallel":
        final_tree_repr.set_operator(tree_constants.PARALLEL_OPERATOR)
        child_tree = final_tree_repr

    if spec_tree_struct.detected_cut == "base_concurrent" or spec_tree_struct.detected_cut == "flower":
        for act in spec_tree_struct.activities:
            child_tree.add_transition(get_transition(counts, act))
        if verify_skip_transition_necessity(must_add_skip, spec_tree_struct.initial_dfg,
                                            spec_tree_struct.activities) and counts.num_visible_trans > 0:
            # add skip transition
            child_tree.add_transition(get_new_hidden_trans(counts, type_trans="skip"))
    if spec_tree_struct.detected_cut == "sequential" or spec_tree_struct.detected_cut == "loopCut":
        for ch in spec_tree_struct.children:
            child, counts = get_repr(ch, rec_depth + 1, counts,
                                      must_add_skip=verify_skip_transition_necessity(False,
                                                                                     ch.initial_dfg,
                                                                                     ch.activities))
            child_tree.add_subtree(child)
    if spec_tree_struct.detected_cut == "parallel":
        m_add_skip = verify_skip_for_parallel_cut(spec_tree_struct.dfg, spec_tree_struct.children)
        for child in spec_tree_struct.children:
            m_add_skip_final = verify_skip_transition_necessity(m_add_skip, spec_tree_struct.dfg,
                                                                spec_tree_struct.activities)
            child_final, counts = get_repr(child, rec_depth + 1, counts, must_add_skip=m_add_skip_final)
            child_tree.add_subtree(child_final)
    if spec_tree_struct.detected_cut == "concurrent":
        for child in spec_tree_struct.children:
            m_add_skip_final = verify_skip_transition_necessity(False, spec_tree_struct.dfg,
                                                                spec_tree_struct.activities)
            child_final, counts = get_repr(child, rec_depth + 1, counts, must_add_skip=m_add_skip_final)
            child_tree.add_subtree(child_final)

    if contains_empty_traces and rec_depth == 1:
        master_tree_repr = ProcessTree()
        master_tree_repr.rec_depth = 0
        master_tree_repr.set_operator(tree_constants.EXCLUSIVE_OPERATOR)
        master_tree_repr.add_transition(get_new_hidden_trans(counts, type_trans="skip"))
        master_tree_repr.add_subtree(final_tree_repr)

        return master_tree_repr, counts

    return final_tree_repr, counts

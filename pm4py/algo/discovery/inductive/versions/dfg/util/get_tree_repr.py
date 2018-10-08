import pm4py
from pm4py.algo.discovery.inductive.data_structures.process_tree import ProcessTree, PT_Transition
from pm4py.algo.discovery.inductive.versions.dfg.util.check_skip_trans import verify_skip_transition_necessity, verify_skip_for_parallel_cut
from pm4py.algo.discovery.inductive.data_structures import tree_constants

def get_transition(counts, label):
    """
    Create a transitions with the specified label in the Petri net
    """
    counts.inc_no_visible()
    return PT_Transition(label, label)


def get_new_hidden_trans(counts, type="unknown"):
    """
    Create a new hidden transition in the Petri net
    """
    counts.inc_no_hidden()
    return PT_Transition(type + '_' + str(counts.num_hidden), None)


def get_repr(spec_tree_struct, rec_depth, counts, must_add_skip=False):
    final_tree_repr = ProcessTree()
    final_tree_repr.rec_depth = rec_depth

    if spec_tree_struct.detected_cut == "base_concurrent":
        final_tree_repr.operator = tree_constants.EXCLUSIVE_OPERATOR
        child_tree = final_tree_repr
    elif spec_tree_struct.detected_cut == "flower":
        final_tree_repr.operator = tree_constants.LOOP_OPERATOR
        child_tree = ProcessTree()
        child_tree.operator = tree_constants.EXCLUSIVE_OPERATOR
        rec_depth = rec_depth + 1
        child_tree.rec_depth = rec_depth
        final_tree_repr.add_subtree(child_tree)
    elif spec_tree_struct.detected_cut == "sequential":
        final_tree_repr.operator = tree_constants.SEQUENTIAL_OPERATOR
        child_tree = final_tree_repr
    elif spec_tree_struct.detected_cut == "loopCut":
        final_tree_repr.operator = tree_constants.LOOP_OPERATOR
        child_tree = ProcessTree()
        child_tree.operator = tree_constants.SEQUENTIAL_OPERATOR
        rec_depth = rec_depth + 1
        child_tree.rec_depth = rec_depth
        final_tree_repr.add_subtree(child_tree)
    elif spec_tree_struct.detected_cut == "concurrent":
        final_tree_repr.operator = tree_constants.EXCLUSIVE_OPERATOR
        child_tree = final_tree_repr
    elif spec_tree_struct.detected_cut == "parallel":
        final_tree_repr.operator = tree_constants.PARALLEL_OPERATOR
        child_tree = final_tree_repr
    if spec_tree_struct.detected_cut == "base_concurrent" or spec_tree_struct.detected_cut == "flower":
        for act in spec_tree_struct.activities:
            child_tree.add_transition(get_transition(counts, act))
        if verify_skip_transition_necessity(must_add_skip, spec_tree_struct.initial_dfg,
                                            spec_tree_struct.activities) and counts.num_visible_trans > 0:
            # add skip transition
            child_tree.add_transition(get_new_hidden_trans(counts, type="skip"))
    if spec_tree_struct.detected_cut == "sequential" or spec_tree_struct.detected_cut == "loopCut":
        child0, counts = get_repr(spec_tree_struct.children[0], rec_depth + 1, counts,
                                  must_add_skip=verify_skip_transition_necessity(False,
                                                                                          spec_tree_struct.initial_dfg,
                                                                                          spec_tree_struct.activities))
        child1, counts = get_repr(spec_tree_struct.children[1], rec_depth + 1, counts,
                                  must_add_skip=verify_skip_transition_necessity(False,
                                                                                          spec_tree_struct.initial_dfg,
                                                                                          spec_tree_struct.activities))
        child_tree.add_subtree(child0)
        child_tree.add_subtree(child1)
    if spec_tree_struct.detected_cut == "parallel":
        mAddSkip = verify_skip_for_parallel_cut(spec_tree_struct.dfg, spec_tree_struct.children)
        for child in spec_tree_struct.children:
            mAddSkipFinal = verify_skip_transition_necessity(mAddSkip, spec_tree_struct.dfg, spec_tree_struct.activities)
            child_final, counts = get_repr(child, rec_depth + 1, counts, must_add_skip=mAddSkipFinal)
            child_tree.add_subtree(child_final)
    if spec_tree_struct.detected_cut == "concurrent":
        for child in spec_tree_struct.children:
            mAddSkipFinal = verify_skip_transition_necessity(False, spec_tree_struct.dfg, spec_tree_struct.activities)
            child_final, counts = get_repr(child, rec_depth + 1, counts, must_add_skip=mAddSkipFinal)
            child_tree.add_subtree(child_final)

    return final_tree_repr, counts

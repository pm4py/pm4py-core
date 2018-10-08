from pm4py.algo.discovery.inductive.data_structures.process_tree import ProcessTree
from pm4py.algo.discovery.inductive.versions.dfg.util.check_skip_trans import verify_skip_transition_necessity

def get_repr(spec_tree_struct, final_tree_repr, recDepth, counts, must_add_skip=False, must_add_loop=False):
    if final_tree_repr is None:
        final_tree_repr = ProcessTree()

    if spec_tree_struct.detected_cut == "base_concurrent":
        final_tree_repr.operator = "X"
        final_tree_repr.base_case = True
    elif spec_tree_struct.detected_cut == "flower":
        final_tree_repr.operator = "↩(X"
        final_tree_repr.flower = True
        final_tree_repr.base_case = True
    elif spec_tree_struct.detected_cut == "sequential":
        final_tree_repr.operator = "->"
    elif spec_tree_struct.detected_cut == "loopCut":
        final_tree_repr.operator = "↩"
    elif spec_tree_struct.detected_cut == "concurrent":
        final_tree_repr.operator = "X"
    elif spec_tree_struct.detected_cut == "parallel":
        final_tree_repr.operator = "+"

    if spec_tree_struct.detected_cut == "base_concurrent" or spec_tree_struct.detected_cut == "flower":
        for act in spec_tree_struct.activities:
            final_tree_repr.add_transition(act, act)

    return final_tree_repr, counts
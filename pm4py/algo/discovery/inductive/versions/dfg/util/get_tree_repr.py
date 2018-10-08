from pm4py.algo.discovery.inductive.data_structures.process_tree import ProcessTree

def get_list_trans_representation_of_tree(spec_tree_struct, final_tree_repr, recDepth, counts, must_add_skip=False, must_add_loop=False):
    if final_tree_repr is None:
        final_tree_repr = ProcessTree()



    return final_tree_repr, counts
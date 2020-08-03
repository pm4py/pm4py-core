from pm4py.objects.process_tree.pt_operator import Operator


def fix_parent_pointers(pt):
    """
    Ensures consistency to the parent pointers in the process tree

    Parameters
    --------------
    pt
        Process tree
    """
    for child in pt.children:
        child.parent = pt
        if child.children:
            fix_parent_pointers(child)


def fix_one_child_xor_flower(tree):
    """
    Fixes a 1 child XOR that is added when single-activities flowers are found

    Parameters
    --------------
    tree
        Process tree
    """
    if tree.parent is not None and tree.operator is Operator.XOR and len(tree.children) == 1:
        for child in tree.children:
            child.parent = tree.parent
            tree.parent.children.append(child)
            del tree.parent.children[tree.parent.children.index(tree)]
    else:
        for child in tree.children:
            fix_one_child_xor_flower(child)

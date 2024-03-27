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
import copy
import hashlib
from typing import Optional, List, Dict, Tuple

from pm4py.objects.process_tree import obj as pt
from pm4py.objects.process_tree import obj as pt_op
from pm4py.objects.process_tree import state as pt_st
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.util import constants


def fold(tree):
    '''
    This method reduces a process tree by merging nodes of the form N(N(a,b),c) into N(a,b,c), i.e., where
    N = || or X. For example X(X(a,b),c) == X(a,b,c).
    Furthermore, meaningless parts, e.g., internal nodes without children, or, operators with one child are removed
    as well.

    :param tree:
    :return:
    '''
    tree = copy.deepcopy(tree)
    tree = _fold(tree)
    root = tree
    while root.parent is None and len(tree.children) == 1:
        root = tree.children[0]
        root.parent = None
        tree.children.clear()
        del tree
        tree = root

    tree_str = str(tree)
    tree = reduce_tau_leafs(tree)
    tau_leafs_red_tree_str = str(tree)

    if len(tau_leafs_red_tree_str) != len(tree_str):
        tree = fold(tree)
        tree_str = str(tree)

    tree2 = _fold(tree)
    tree2_str = str(tree2)

    if len(tree2_str) != len(tree_str):
        tree = fold(tree2)

    return tree


def _fold(tree):
    tree = reduce_tau_leafs(tree)

    if len(tree.children) > 0:
        tree.children = list(map(lambda c: _fold(c), tree.children))
        tree.children = list(filter(lambda c: c is not None, tree.children))

        if len(tree.children) == 0:
            tree.parent = None
            tree.children = None
            return None
        elif len(tree.children) == 1:
            child = tree.children[0]
            child.parent = tree.parent
            tree.parent = None
            tree.children = None
            return child

        if tree.operator in [pt_op.Operator.SEQUENCE, pt_op.Operator.PARALLEL]:
            i = 0
            while i < len(tree.children):
                child = tree.children[i]
                if child.operator is None and child.label is None:
                    del tree.children[i]
                    continue
                i = i + 1
            if len(tree.children) == 0:
                tree.operator = None

        if tree.operator in [pt_op.Operator.SEQUENCE, pt_op.Operator.XOR, pt_op.Operator.PARALLEL]:
            chlds = [c for c in tree.children]
            for c in chlds:
                if c.operator == tree.operator:
                    i = tree.children.index(c)
                    tree.children[i:i] = c.children
                    for cc in c.children:
                        cc.parent = tree
                    tree.children.remove(c)
                    c.children.clear()
                    c.parent = None
    return tree


def reduce_tau_leafs(tree):
    '''
    This method reduces tau leaves that are not meaningful. For example tree ->(a,\tau,b) is reduced to ->(a,b).
    In some cases this results in constructs such as ->(a), i.e., a sequence with a single child. Such constructs
    are not further reduced.

    :param tree:
    :return:
    '''
    if len(tree.children) > 0:
        for c in tree.children:
            reduce_tau_leafs(c)
        silents = 0
        for c in tree.children:
            if is_tau_leaf(c):
                silents += 1
        if silents > 0:
            if len(tree.children) == silents:
                # all children are tau, keep one (might be folded later)
                if tree.operator in [pt_op.Operator.SEQUENCE, pt_op.Operator.PARALLEL, pt_op.Operator.XOR,
                                     pt_op.Operator.OR]:
                    # remove all but one, later reductions might need the fact that skipping is possible
                    while silents > 1:
                        cc = tree.children
                        for c in cc:
                            if is_tau_leaf(c):
                                c.parent = None
                                tree.children.remove(c)
                                silents -= 1
                                break
                elif tree.operator == pt_op.Operator.LOOP and len(tree.children) == 2:
                    # remove all loop is redundant
                    cc = tree.children
                    for c in cc:
                        if is_tau_leaf(c):
                            c.parent = None
                            tree.children.remove(c)
            else:
                # at least one non-tau child
                if tree.operator in [pt_op.Operator.SEQUENCE, pt_op.Operator.PARALLEL]:
                    # remove all, they are redundant for these operators
                    cc = tree.children
                    for c in cc:
                        if is_tau_leaf(c):
                            c.parent = None
                            tree.children.remove(c)
                elif tree.operator in [pt_op.Operator.XOR, pt_op.Operator.OR]:
                    # keep one, we should be able to skip
                    while silents > 1:
                        cc = tree.children
                        for c in cc:
                            if is_tau_leaf(c):
                                c.parent = None
                                tree.children.remove(c)
                                silents -= 1
                                break
    return tree


def is_tau_leaf(tree):
    return is_leaf(tree) and tree.label is None


def is_leaf(tree):
    return (tree.children is None or len(tree.children) == 0) and tree.operator is None


def project_execution_sequence_to_leafs(execution_sequence):
    """
    Project an execution sequence to the set of leafs
    of the tree.

    Parameters
    ------------
    execution_sequence
        Execution sequence on the process tree

    Returns
    ------------
    list_leafs
        Leafs nodes of the process tree
    """
    return list(map(lambda x: x[0],
                    filter(lambda x: (x[1] is pt_st.State.OPEN and len(x[0].children) == 0), execution_sequence)))


def project_execution_sequence_to_labels(execution_sequence):
    """
    Project an execution sequence to a set of labels

    Parameters
    ------------
    execution_sequence
        Execution sequence on the process tree

    Returns
    ------------
    list_labels
        List of labels contained in the process tree
    """
    return list(map(lambda x: x.label,
                    filter(lambda x: x.label is not None, project_execution_sequence_to_leafs(execution_sequence))))


def parse(string_rep):
    """
    Parse a string provided by the user to a process tree
    (initialization method)

    Parameters
    ------------
    string_rep
        String representation of the process tree

    Returns
    ------------
    node
        Process tree object
    """
    depth_cache = dict()
    depth = 0
    return parse_recursive(string_rep, depth_cache, depth)


def parse_recursive(string_rep, depth_cache, depth):
    """
    Parse a string provided by the user to a process tree
    (recursive method)

    Parameters
    ------------
    string_rep
        String representation of the process tree
    depth_cache
        Depth cache of the algorithm
    depth
        Current step depth

    Returns
    -----------
    node
        Process tree object
    """
    string_rep = string_rep.strip().replace("\r", "").replace("\n", " ")
    node = None
    operator = None
    if string_rep.startswith(pt_op.Operator.LOOP.value):
        operator = pt_op.Operator.LOOP
        string_rep = string_rep[len(pt_op.Operator.LOOP.value):]
    elif string_rep.startswith(pt_op.Operator.PARALLEL.value):
        operator = pt_op.Operator.PARALLEL
        string_rep = string_rep[len(pt_op.Operator.PARALLEL.value):]
    elif string_rep.startswith(pt_op.Operator.XOR.value):
        operator = pt_op.Operator.XOR
        string_rep = string_rep[len(pt_op.Operator.XOR.value):]
    elif string_rep.startswith(pt_op.Operator.OR.value):
        operator = pt_op.Operator.OR
        string_rep = string_rep[len(pt_op.Operator.OR.value):]
    elif string_rep.startswith(pt_op.Operator.SEQUENCE.value):
        operator = pt_op.Operator.SEQUENCE
        string_rep = string_rep[len(pt_op.Operator.SEQUENCE.value):]
    elif string_rep.startswith(pt_op.Operator.INTERLEAVING.value):
        operator = pt_op.Operator.INTERLEAVING
        string_rep = string_rep[len(pt_op.Operator.INTERLEAVING.value):]
    if operator is not None:
        parent = None if depth == 0 else depth_cache[depth - 1]
        node = pt.ProcessTree(operator=operator, parent=parent)
        depth_cache[depth] = node
        if parent is not None:
            parent.children.append(node)
        depth += 1
        string_rep = string_rep.strip()
        assert (string_rep[0] == '(')
        parse_recursive(string_rep[1:], depth_cache, depth)
    else:
        label = None
        if string_rep.startswith('\''):
            string_rep = string_rep[1:]
            escape_ext = string_rep.find('\'')
            label = string_rep[0:escape_ext]
            string_rep = string_rep[escape_ext + 1:]
        else:
            assert (string_rep.startswith('tau') or string_rep.startswith('τ') or string_rep.startswith(u'\u03c4'))
            if string_rep.startswith('tau'):
                string_rep = string_rep[len('tau'):]
            elif string_rep.startswith('τ'):
                string_rep = string_rep[len('τ'):]
            elif string_rep.startswith(u'\u03c4'):
                string_rep = string_rep[len(u'\u03c4'):]
        parent = None if depth == 0 else depth_cache[depth - 1]
        node = pt.ProcessTree(operator=operator, parent=parent, label=label)
        if parent is not None:
            parent.children.append(node)

        while string_rep.strip().startswith(')'):
            depth -= 1
            string_rep = (string_rep.strip())[1:]
        if len(string_rep.strip()) > 0:
            parse_recursive((string_rep.strip())[1:], depth_cache, depth)
    return node


def tree_sort(tree):
    """
    Sort a tree in such way that the order of the nodes
    in AND/XOR children is always the same.
    This is a recursive function

    Parameters
    --------------
    tree
        Process tree
    """
    tree.labels_hash_sum = 0
    for child in tree.children:
        tree_sort(child)
        tree.labels_hash_sum += child.labels_hash_sum
    if tree.label is not None:
        # this assures that among different executions, the same string gets always the same hash
        this_hash = int(hashlib.md5(str(tree.label).encode(constants.DEFAULT_ENCODING)).hexdigest(), 16)
        tree.labels_hash_sum += this_hash
    if tree.operator is pt_op.Operator.PARALLEL or tree.operator is pt_op.Operator.XOR:
        tree.children = sorted(tree.children, key=lambda x: x.labels_hash_sum)


def structurally_language_equal(tree1, tree2):
    '''
    this function checks if two given process trees are structurally equal, modulo, shuffling of children (if allowed),
    i.e., in the parallel, or and xor operators, the order does not matter.

    :param tree1:
    :param tree2:
    :return:
    '''
    if tree1.label is not None:
        return True if tree2.label == tree1.label else False
    elif len(tree1.children) == 0:
        return tree2.label is None and len(tree2.children) == 0
    else:
        if tree1.operator == tree2.operator:
            if len(tree1.children) != len(tree2.children):
                return False
            if tree1.operator in [pt_op.Operator.SEQUENCE, pt_op.Operator.LOOP]:
                for i in range(len(tree1.children)):
                    if not structurally_language_equal(tree1.children[i], tree2.children[i]):
                        return False
                return True
            elif tree1.operator in [pt_op.Operator.PARALLEL, pt_op.Operator.XOR, pt_op.Operator.OR]:
                matches = list(range(len(tree1.children)))
                for i in range(len(tree1.children)):
                    mm = [m for m in matches]
                    for j in mm:
                        if structurally_language_equal(tree1.children[i], tree2.children[j]):
                            matches.remove(j)
                            break
                return True if len(matches) == 0 else False
        else:
            return False


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


def process_tree_to_binary_process_tree(tree: ProcessTree) -> ProcessTree:
    if len(tree.children) > 2:
        left_tree = tree.children[0]

        right_tree_op = tree.operator
        if tree.operator == pt_op.Operator.LOOP:
            right_tree_op = pt_op.Operator.XOR

        right_tree = ProcessTree(operator=right_tree_op, parent=tree,
                                 children=tree.children[1:])
        for child in right_tree.children:
            child.parent = right_tree

        tree.children = [left_tree, right_tree]

    for child in tree.children:
        process_tree_to_binary_process_tree(child)

    return tree


def common_ancestor(t1: ProcessTree, t2: ProcessTree) -> Optional[ProcessTree]:
    parents = set()
    parent = t1.parent
    while parent is not None:
        parents.add(parent)
        parent = parent.parent
    parent = t2.parent
    while parent is not None:
        if parent in parents:
            return parent
        parent = parent.parent
    return None


def get_ancestors_until(t: ProcessTree, until: ProcessTree, include_until: bool = True) -> Optional[List[ProcessTree]]:
    ancestors = list()
    if t == until:
        return ancestors
    parent = t.parent
    while parent != until:
        ancestors.append(parent)
        parent = parent.parent
        if parent is None:
            return None
    if include_until:
        ancestors.append(until)
    return ancestors


def get_leaves(t: ProcessTree, leaves=None):
    leaves = leaves if leaves is not None else set()
    if len(t.children) == 0:
        leaves.add(t)
    else:
        for c in t.children:
            leaves = get_leaves(c, leaves)
    return leaves


def get_leaves_as_tuples(t: ProcessTree, leaves=None):
    leaves = leaves if leaves is not None else set()
    if len(t.children) == 0:
        leaves.add((id(t), t))
    else:
        for c in t.children:
            leaves = get_leaves_as_tuples(c, leaves)
    return leaves


def is_operator(tree: ProcessTree, operator: pt_op.Operator) -> bool:
    return tree is not None and tree.operator is not None and tree.operator == operator


def is_any_operator_of(tree: ProcessTree, operators: List[pt_op.Operator]) -> bool:
    return tree is not None and tree.operator is not None and tree.operator in operators


def is_in_state(tree: ProcessTree, target_state: ProcessTree.OperatorState,
                tree_state: Dict[Tuple[int, ProcessTree], ProcessTree.OperatorState]) -> bool:
    return tree is not None and (id(tree), tree) in tree_state and tree_state[(id(tree), tree)] == target_state


def is_root(tree: ProcessTree) -> bool:
    return tree.parent is None

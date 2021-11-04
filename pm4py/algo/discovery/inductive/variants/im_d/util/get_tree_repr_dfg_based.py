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
from pm4py.objects.dfg.utils.dfg_utils import get_activities_self_loop
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.objects.process_tree.obj import Operator


def get_transition(label):
    """
    Create a node (transition) with the specified label in the process tree
    """
    return ProcessTree(operator=None, label=label)


def get_new_hidden_trans():
    """
    Create a hidden node (transition) in the process tree
    """
    return ProcessTree(operator=None, label=None)


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


def get_repr(spec_tree_struct, rec_depth, contains_empty_traces=False):
    """
    Get the representation of a process tree

    Parameters
    -----------
    spec_tree_struct
        Internal tree structure (after application of Inductive Miner)
    rec_depth
        Current recursion depth
    contains_empty_traces
        Boolean value that is True if the event log from which the DFG has been extracted contains empty traces

    Returns
    -----------
    final_tree_repr
        Representation of the tree (could be printed, transformed, viewed)
    """

    need_loop_on_subtree = check_loop_need(spec_tree_struct)

    if contains_empty_traces and rec_depth == 0:
        rec_depth = rec_depth + 1

    child_tree = None
    if spec_tree_struct.detected_cut == "flower" or (
            spec_tree_struct.detected_cut == "base_xor" and need_loop_on_subtree):
        final_tree_repr = ProcessTree(operator=Operator.LOOP)
        child_tree = ProcessTree(operator=Operator.XOR)
        child_tree_redo = ProcessTree(label=None)
        #child_tree_exit = ProcessTree(label=None)
        final_tree_repr.children.append(child_tree)
        final_tree_repr.children.append(child_tree_redo)
        #final_tree_repr.children.append(child_tree_exit)
        child_tree.parent = final_tree_repr
        child_tree_redo.parent = final_tree_repr
        #child_tree_exit.parent = final_tree_repr
    elif spec_tree_struct.detected_cut == "base_xor":
        if len(spec_tree_struct.activities) > 1 or spec_tree_struct.must_insert_skip:
            final_tree_repr = ProcessTree(operator=Operator.XOR)
            child_tree = final_tree_repr
        else:
            final_tree_repr = ProcessTree(operator=None, label=None)
    elif spec_tree_struct.detected_cut == "sequential":
        if spec_tree_struct.need_loop_on_subtree:
            final_tree_repr = ProcessTree(operator=Operator.LOOP)
            child_tree = ProcessTree(operator=Operator.SEQUENCE)
            child_tree.parent = final_tree_repr
            final_tree_repr.children.append(child_tree)
            child = ProcessTree()
            final_tree_repr.children.append(child)
            child.parent = final_tree_repr
        else:
            final_tree_repr = ProcessTree(operator=Operator.SEQUENCE)
            child_tree = final_tree_repr
    elif spec_tree_struct.detected_cut == "loopCut":
        final_tree_repr = ProcessTree(operator=Operator.LOOP)
        child_tree = final_tree_repr
    elif spec_tree_struct.detected_cut == "xor":
        final_tree_repr = ProcessTree(operator=Operator.XOR)
        child_tree = final_tree_repr
    elif spec_tree_struct.detected_cut == "parallel":
        final_tree_repr = ProcessTree(operator=Operator.PARALLEL)
        child_tree = final_tree_repr

    if spec_tree_struct.detected_cut == "base_xor" or spec_tree_struct.detected_cut == "flower":
        for act in spec_tree_struct.activities:
            if child_tree is None:
                new_vis_trans = get_transition(act)
                child_tree = new_vis_trans
                final_tree_repr = child_tree
            else:
                new_vis_trans = get_transition(act)
                child_tree.children.append(new_vis_trans)
                new_vis_trans.parent = child_tree
    if spec_tree_struct.detected_cut == "sequential" or spec_tree_struct.detected_cut == "loopCut":
        for ch in spec_tree_struct.children:
            child = get_repr(ch, rec_depth + 1)
            child_tree.children.append(child)
            child.parent = child_tree

        if spec_tree_struct.detected_cut == "loopCut" and len(spec_tree_struct.children) < 2:
            while len(spec_tree_struct.children) < 2:
                child = ProcessTree()
                child_tree.children.append(child)
                child.parent = child_tree
                spec_tree_struct.children.append(ProcessTree(operator=None, label=None, parent=spec_tree_struct))

    if spec_tree_struct.detected_cut == "parallel":
        for child in spec_tree_struct.children:
            child_final = get_repr(child, rec_depth + 1)
            child_tree.children.append(child_final)
            child_final.parent = child_tree

    if spec_tree_struct.detected_cut == "xor":
        for child in spec_tree_struct.children:
            child_final = get_repr(child, rec_depth + 1)
            child_tree.children.append(child_final)
            child_final.parent = child_tree

    if spec_tree_struct.must_insert_skip:
        skip = get_new_hidden_trans()
        if spec_tree_struct.detected_cut == "base_xor":
            child_tree.children.append(skip)
            skip.parent = child_tree
        else:
            master_tree_repr = ProcessTree(operator=Operator.XOR)
            master_tree_repr.children.append(final_tree_repr)
            final_tree_repr.parent = master_tree_repr

            master_tree_repr.children.append(skip)
            skip.parent = master_tree_repr

            return master_tree_repr

    if contains_empty_traces and rec_depth == 1:
        master_tree_repr = ProcessTree(operator=Operator.XOR)
        master_tree_repr.children.append(final_tree_repr)
        final_tree_repr.parent = master_tree_repr

        skip_transition = ProcessTree()

        master_tree_repr.children.append(skip_transition)
        skip_transition.parent = master_tree_repr

        return master_tree_repr

    return final_tree_repr

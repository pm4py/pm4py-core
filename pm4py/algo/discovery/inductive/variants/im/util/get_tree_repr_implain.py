from pm4py.algo.discovery.dfg.utils.dfg_utils import get_activities_self_loop
from pm4py.objects.process_tree.process_tree import ProcessTree
from pm4py.objects.process_tree.pt_operator import Operator
from pm4py.util import exec_utils, xes_constants
from pm4py.algo.discovery.inductive.parameters import Parameters


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

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, spec_tree_struct.parameters,
                                              xes_constants.DEFAULT_NAME_KEY)

    base_cases = ('empty_log', 'single_activity')
    cut = ('concurrent', 'sequential', 'parallel', 'loopCut')
    # note that the activity_once_per_trace is not included here, as it is can be dealt with as a parallel cut
    fall_throughs = ('empty_trace', 'strict_tau_loop', 'tau_loop', 'flower')

    # if a cut was detected in the current subtree:
    if spec_tree_struct.detected_cut in cut:
        if spec_tree_struct.detected_cut == "sequential":
            final_tree_repr = ProcessTree(operator=Operator.SEQUENCE)
        elif spec_tree_struct.detected_cut == "loopCut":
            final_tree_repr = ProcessTree(operator=Operator.LOOP)
        elif spec_tree_struct.detected_cut == "concurrent":
            final_tree_repr = ProcessTree(operator=Operator.XOR)
        elif spec_tree_struct.detected_cut == "parallel":
            final_tree_repr = ProcessTree(operator=Operator.PARALLEL)


        if not (spec_tree_struct.detected_cut == "loopCut" and len(spec_tree_struct.children) >= 3):
            for ch in spec_tree_struct.children:
                # get the representation of the current child (from children in the subtree-structure):
                child = get_repr(ch, rec_depth + 1)
                # add connection from child_tree to child_final and the other way around:
                final_tree_repr.children.append(child)
                child.parent = final_tree_repr
        
        else:
            child = get_repr(spec_tree_struct.children[0], rec_depth + 1)
            final_tree_repr.children.append(child)
            child.parent = final_tree_repr

            redo_child = ProcessTree(operator=Operator.XOR)
            for ch in spec_tree_struct.children[1:]:
                child = get_repr(ch, rec_depth + 1)
                redo_child.children.append(child)
                child.parent = redo_child
            
            final_tree_repr.children.append(redo_child)
            redo_child.parent = final_tree_repr

        if spec_tree_struct.detected_cut == "loopCut" and len(spec_tree_struct.children) < 3:
            while len(spec_tree_struct.children) < 2:
                child = ProcessTree()
                final_tree_repr.children.append(child)
                child.parent = final_tree_repr
                spec_tree_struct.children.append(None)
        


    if spec_tree_struct.detected_cut in base_cases:
        # in the base case of an empty log, we only return a silent transition
        if spec_tree_struct.detected_cut == "empty_log":
            return ProcessTree(operator=None, label=None)
        # in the base case of a single activity, we return a tree consisting of the single activity
        elif spec_tree_struct.detected_cut == "single_activity":
            act_a = spec_tree_struct.log[0][0][activity_key]
            return ProcessTree(operator=None, label=act_a)

    if spec_tree_struct.detected_cut in fall_throughs:
        if spec_tree_struct.detected_cut == "empty_trace":
            # should return XOR(tau, IM(L') )
            final_tree_repr = ProcessTree(operator=Operator.XOR)
            final_tree_repr.children.append(ProcessTree(operator=None, label=None))
            # iterate through all children of the current node
            for ch in spec_tree_struct.children:
                child = get_repr(ch, rec_depth + 1)
                final_tree_repr.children.append(child)
                child.parent = final_tree_repr

        elif spec_tree_struct.detected_cut == "strict_tau_loop" or spec_tree_struct.detected_cut == "tau_loop":
            # should return LOOP( IM(L'), tau)
            final_tree_repr = ProcessTree(operator=Operator.LOOP)
            # iterate through all children of the current node
            if spec_tree_struct.children:
                for ch in spec_tree_struct.children:
                    child = get_repr(ch, rec_depth + 1)
                    final_tree_repr.children.append(child)
                    child.parent = final_tree_repr
            else:
                for ch in spec_tree_struct.activities:
                    child = get_transition(ch)
                    final_tree_repr.append(child)
                    child.parent = final_tree_repr

            # add a silent tau transition as last child of the current node
            final_tree_repr.children.append(ProcessTree(operator=None, label=None))

        elif spec_tree_struct.detected_cut == "flower":
            # should return something like LOOP(XOR(a,b,c,d,...), tau)
            final_tree_repr = ProcessTree(operator=Operator.LOOP)
            xor_child = ProcessTree(operator=Operator.XOR, parent=final_tree_repr)
            # append all the activities in the current subtree to the XOR part to allow for any behaviour
            for ch in spec_tree_struct.activities:
                child = get_transition(ch)
                xor_child.children.append(child)
                child.parent = xor_child
            final_tree_repr.children.append(xor_child)
            # now add the tau to the children to get the wanted output
            final_tree_repr.children.append(ProcessTree(operator=None, label=None))

    return final_tree_repr

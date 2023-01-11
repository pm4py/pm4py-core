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
import time
import uuid

from pm4py.objects.petri_net.obj import Marking
from pm4py.objects.petri_net.obj import PetriNet
from pm4py.objects.petri_net.utils.petri_utils import remove_transition, add_arc_from_to, remove_place
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.objects.process_tree.obj import Operator
from pm4py.objects.petri_net.utils import reduction


class Counts(object):
    """
    Shared variables among executions
    """

    def __init__(self):
        """
        Constructor
        """
        self.num_places = 0
        self.num_hidden = 0
        self.num_visible_trans = 0
        self.dict_skips = {}
        self.dict_loops = {}

    def inc_places(self):
        """
        Increase the number of places
        """
        self.num_places = self.num_places + 1

    def inc_no_hidden(self):
        """
        Increase the number of hidden transitions
        """
        self.num_hidden = self.num_hidden + 1

    def inc_no_visible(self):
        """
        Increase the number of visible transitions
        """
        self.num_visible_trans = self.num_visible_trans + 1


def clean_duplicate_transitions(net):
    """
    Clean duplicate transitions in a Petri net

    Parameters
    ------------
    net
        Petri net

    Returns
    ------------
    net
        Cleaned Petri net
    """
    transitions = list(net.transitions)
    already_visited_combo = set()
    for i in range(0, len(transitions)):
        trans = transitions[i]
        if trans.label is None:
            in_arcs = trans.in_arcs
            out_arcs = trans.out_arcs
            to_delete = False
            for in_arc in in_arcs:
                in_place = in_arc.source
                for out_arc in out_arcs:
                    out_place = out_arc.target
                    combo = in_place.name + " " + out_place.name
                    if combo in already_visited_combo:
                        to_delete = True
                        break
                    already_visited_combo.add(combo)
            if to_delete:
                net = remove_transition(net, trans)
    return net


def get_new_place(counts):
    """
    Create a new place in the Petri net
    """
    counts.inc_places()
    return PetriNet.Place('p_' + str(counts.num_places))


def get_new_hidden_trans(counts, type_trans="unknown"):
    """
    Create a new hidden transition in the Petri net
    """
    counts.inc_no_hidden()
    return PetriNet.Transition(type_trans + '_' + str(counts.num_hidden), None)


def get_transition(counts, label):
    """
    Create a transitions with the specified label in the Petri net
    """
    counts.inc_no_visible()
    return PetriNet.Transition(str(uuid.uuid4()), label)


def get_first_terminal_child_transitions(tree):
    """
    Gets the list of transitions belonging to the first terminal child node of the current tree

    Parameters
    ----------
    tree
        Process tree

    Returns
    ---------
    transitions_list
        List of transitions belonging to the first terminal child node
    """
    if tree.children:
        if tree.children[0].operator:
            return get_first_terminal_child_transitions(tree.children[0])
        else:
            if tree.children[0].children:
                return tree.children[0].children
            else:
                return [tree.children[0]]
    return []


def get_last_terminal_child_transitions(tree):
    """
    Gets the list of transitions belonging to the last terminal child node of the current tree

    Parameters
    ----------
    tree
        Process tree

    Returns
    ---------
    transitions_list
        List of transitions belonging to the first terminal child node
    """
    if tree.children:
        if tree.children[-1].operator:
            return get_last_terminal_child_transitions(tree.children[-1])
        else:
            if tree.children[-1].children:
                return tree.children[-1].children
            else:
                return [tree.children[-1]]
    return []


def check_loop_to_first_operator(tree):
    """
    Checks if loop to first operator

    Parameters
    ------------
    tree
        Process tree

    Returns
    ------------
    boolean
        Check if no loop to the first operator
    """
    if tree.operator == Operator.LOOP:
        return True
    if tree.children:
        if tree.children[0].operator == Operator.LOOP:
            return True
        else:
            return check_loop_to_first_operator(tree.children[0])
    return tree.operator == Operator.LOOP


def check_loop_to_last_operator(tree):
    """
    Checks if loop to last operator

    Parameters
    -------------
    tree
        Process tree

    Returns
    -------------
    boolean
        Check if no loop to the last operator
    """
    if tree.operator == Operator.LOOP:
        return True
    if tree.children:
        if tree.children[-1].operator == Operator.LOOP:
            return True
        else:
            return check_loop_to_last_operator(tree.children[-1])
    return tree.operator == Operator.LOOP


def check_initial_loop(tree):
    """
    Check if the tree, on-the-left, starts with a loop

    Parameters
    ----------
    tree
        Process tree

    Returns
    ----------
    boolean
        True if it starts with an initial loop
    """
    if tree.children:
        if tree.children[0].operator:
            if tree.children[0].operator == Operator.LOOP:
                return True
            else:
                return check_terminal_loop(tree.children[0])
    return False


def check_terminal_loop(tree):
    """
    Check if the tree, on-the-right, ends with a loop

    Parameters
    ----------
    tree
        Process tree

    Returns
    -----------
    boolean
        True if it ends with a terminal loop
    """
    if tree.children:
        if tree.children[-1].operator:
            if tree.children[-1].operator == Operator.LOOP:
                return True
            else:
                return check_terminal_loop(tree.children[-1])
    return False


def check_tau_mandatory_at_initial_marking(tree):
    """
    When a conversion to a Petri net is operated, check if is mandatory to add a hidden transition
    at initial marking

    Parameters
    ----------
    tree
        Process tree

    Returns
    ----------
    boolean
        Boolean that is true if it is mandatory to add a hidden transition connecting the initial marking
        to the rest of the process
    """
    condition1 = check_initial_loop(tree)
    terminal_transitions = get_first_terminal_child_transitions(tree)
    condition2 = len(terminal_transitions) > 1
    condition3 = check_loop_to_first_operator(tree)
    condition4 = tree.operator == Operator.XOR or tree.operator == Operator.PARALLEL

    return condition1 or condition2 or condition3 or condition4


def check_tau_mandatory_at_final_marking(tree):
    """
    When a conversion to a Petri net is operated, check if is mandatory to add a hidden transition
    at final marking

    Returns
    ----------
    boolean
        Boolean that is true if it is mandatory to add a hidden transition connecting
        the rest of the process to the final marking
    """
    condition1 = check_terminal_loop(tree)
    terminal_transitions = get_last_terminal_child_transitions(tree)
    condition2 = len(terminal_transitions) > 1
    condition3 = check_loop_to_last_operator(tree)
    condition4 = tree.operator == Operator.XOR or tree.operator == Operator.PARALLEL

    return condition1 or condition2 or condition3 or condition4


def recursively_add_tree(parent_tree, tree, net, initial_entity_subtree, final_entity_subtree, counts, rec_depth,
                         force_add_skip=False):
    """
    Recursively add the subtrees to the Petri net

    Parameters
    -----------
    parent_tree
        Parent tree
    tree
        Current subtree
    net
        Petri net
    initial_entity_subtree
        Initial entity (place/transition) that should be attached from the subtree
    final_entity_subtree
        Final entity (place/transition) that should be attached from the subtree
    counts
        Counts object (keeps the number of places, transitions and hidden transitions)
    rec_depth
        Recursion depth of the current iteration
    force_add_skip
        Boolean value that tells if the addition of a skip is mandatory

    Returns
    ----------
    net
        Updated Petri net
    counts
        Updated counts object (keeps the number of places, transitions and hidden transitions)
    final_place
        Last place added in this recursion
    """
    if type(initial_entity_subtree) is PetriNet.Transition:
        initial_place = get_new_place(counts)
        net.places.add(initial_place)
        add_arc_from_to(initial_entity_subtree, initial_place, net)
    else:
        initial_place = initial_entity_subtree
    if final_entity_subtree is not None and type(final_entity_subtree) is PetriNet.Place:
        final_place = final_entity_subtree
    else:
        final_place = get_new_place(counts)
        net.places.add(final_place)
        if final_entity_subtree is not None and type(final_entity_subtree) is PetriNet.Transition:
            add_arc_from_to(final_place, final_entity_subtree, net)
    tree_childs = [child for child in tree.children]

    if force_add_skip:
        invisible = get_new_hidden_trans(counts, type_trans="skip")
        add_arc_from_to(initial_place, invisible, net)
        add_arc_from_to(invisible, final_place, net)

    if tree.operator is None:
        trans = tree
        if trans.label is None:
            petri_trans = get_new_hidden_trans(counts, type_trans="skip")
        else:
            petri_trans = get_transition(counts, trans.label)
        net.transitions.add(petri_trans)
        add_arc_from_to(initial_place, petri_trans, net)
        add_arc_from_to(petri_trans, final_place, net)

    if tree.operator == Operator.XOR:
        for subtree in tree_childs:
            net, counts, intermediate_place = recursively_add_tree(tree, subtree, net, initial_place, final_place,
                                                                   counts,
                                                                   rec_depth + 1)
    elif tree.operator == Operator.OR:
        new_initial_trans = get_new_hidden_trans(counts, type_trans="tauSplit")
        net.transitions.add(new_initial_trans)
        add_arc_from_to(initial_place, new_initial_trans, net)
        new_final_trans = get_new_hidden_trans(counts, type_trans="tauJoin")
        net.transitions.add(new_final_trans)
        add_arc_from_to(new_final_trans, final_place, net)
        terminal_place = get_new_place(counts)
        net.places.add(terminal_place)
        add_arc_from_to(terminal_place, new_final_trans, net)
        first_place = get_new_place(counts)
        net.places.add(first_place)
        add_arc_from_to(new_initial_trans, first_place, net)

        for subtree in tree_childs:
            subtree_init_place = get_new_place(counts)
            net.places.add(subtree_init_place)
            add_arc_from_to(new_initial_trans, subtree_init_place, net)
            subtree_start_place = get_new_place(counts)
            net.places.add(subtree_start_place)
            subtree_end_place = get_new_place(counts)
            net.places.add(subtree_end_place)
            trans_start = get_new_hidden_trans(counts, type_trans="inclusiveStart")
            trans_later = get_new_hidden_trans(counts, type_trans="inclusiveLater")
            trans_skip = get_new_hidden_trans(counts, type_trans="inclusiveSkip")
            net.transitions.add(trans_start)
            net.transitions.add(trans_later)
            net.transitions.add(trans_skip)
            add_arc_from_to(first_place, trans_start, net)
            add_arc_from_to(subtree_init_place, trans_start, net)
            add_arc_from_to(trans_start, subtree_start_place, net)
            add_arc_from_to(trans_start, terminal_place, net)

            add_arc_from_to(terminal_place, trans_later, net)
            add_arc_from_to(subtree_init_place, trans_later, net)
            add_arc_from_to(trans_later, subtree_start_place, net)
            add_arc_from_to(trans_later, terminal_place, net)

            add_arc_from_to(terminal_place, trans_skip, net)
            add_arc_from_to(subtree_init_place, trans_skip, net)
            add_arc_from_to(trans_skip, terminal_place, net)
            add_arc_from_to(trans_skip, subtree_end_place, net)

            add_arc_from_to(subtree_end_place, new_final_trans, net)

            net, counts, intermediate_place = recursively_add_tree(tree, subtree, net, subtree_start_place,
                                                                   subtree_end_place,
                                                                   counts,
                                                                   rec_depth + 1)

    elif tree.operator == Operator.PARALLEL:
        new_initial_trans = get_new_hidden_trans(counts, type_trans="tauSplit")
        net.transitions.add(new_initial_trans)
        add_arc_from_to(initial_place, new_initial_trans, net)
        new_final_trans = get_new_hidden_trans(counts, type_trans="tauJoin")
        net.transitions.add(new_final_trans)
        add_arc_from_to(new_final_trans, final_place, net)

        for subtree in tree_childs:
            net, counts, intermediate_place = recursively_add_tree(tree, subtree, net, new_initial_trans,
                                                                   new_final_trans,
                                                                   counts,
                                                                   rec_depth + 1)

    elif tree.operator == Operator.INTERLEAVING:
        new_initial_trans = get_new_hidden_trans(counts, type_trans="tauSplit")
        net.transitions.add(new_initial_trans)
        add_arc_from_to(initial_place, new_initial_trans, net)
        new_final_trans = get_new_hidden_trans(counts, type_trans="tauJoin")
        net.transitions.add(new_final_trans)
        add_arc_from_to(new_final_trans, final_place, net)

        control_place = get_new_place(counts)
        net.places.add(control_place)

        add_arc_from_to(new_initial_trans, control_place, net)
        add_arc_from_to(control_place, new_final_trans, net)

        for subtree in tree_childs:
            placeI = get_new_place(counts)
            net.places.add(placeI)
            iTrans = get_new_hidden_trans(counts, type_trans="iTrans")
            net.transitions.add(iTrans)
            placeF = get_new_place(counts)
            net.places.add(placeF)
            fTrans = get_new_hidden_trans(counts, type_trans="fTrans")
            net.transitions.add(fTrans)

            add_arc_from_to(new_initial_trans, placeI, net)
            add_arc_from_to(placeI, iTrans, net)
            add_arc_from_to(fTrans, placeF, net)
            add_arc_from_to(placeF, new_final_trans, net)

            add_arc_from_to(control_place, iTrans, net)
            add_arc_from_to(fTrans, control_place, net)

            net, counts, intermediate_place = recursively_add_tree(tree, subtree, net, iTrans,
                                                                   fTrans,
                                                                   counts,
                                                                   rec_depth + 1)

    elif tree.operator == Operator.SEQUENCE:
        intermediate_place = initial_place
        for i in range(len(tree_childs)):
            final_connection_place = None
            if i == len(tree_childs) - 1:
                final_connection_place = final_place
            net, counts, intermediate_place = recursively_add_tree(tree, tree_childs[i], net, intermediate_place,
                                                                   final_connection_place, counts,
                                                                   rec_depth + 1)
    elif tree.operator == Operator.LOOP:
        # if not parent_tree.operator == Operator.SEQUENCE:
        new_initial_place = get_new_place(counts)
        net.places.add(new_initial_place)
        init_loop_trans = get_new_hidden_trans(counts, type_trans="init_loop")
        net.transitions.add(init_loop_trans)
        add_arc_from_to(initial_place, init_loop_trans, net)
        add_arc_from_to(init_loop_trans, new_initial_place, net)
        initial_place = new_initial_place
        loop_trans = get_new_hidden_trans(counts, type_trans="loop")
        net.transitions.add(loop_trans)
        if len(tree_childs) == 1:
            net, counts, intermediate_place = recursively_add_tree(tree, tree_childs[0], net, initial_place,
                                                                   final_place,
                                                                   counts,
                                                                   rec_depth + 1)
            add_arc_from_to(final_place, loop_trans, net)
            add_arc_from_to(loop_trans, initial_place, net)
        else:
            net, counts, int1 = recursively_add_tree(tree, tree_childs[0], net, initial_place,
                                                     None, counts,
                                                     rec_depth + 1)
            int2 = None
            for i in range(1, len(tree_childs)):
                net, counts, int2 = recursively_add_tree(tree, tree_childs[i], net, int1,
                                                         int2, counts,
                                                         rec_depth + 1)

            net, counts, int3 = recursively_add_tree(tree, ProcessTree(), net, int1,
                                                     final_place, counts,
                                                     rec_depth + 1)

            looping_place = int2

            add_arc_from_to(looping_place, loop_trans, net)
            add_arc_from_to(loop_trans, initial_place, net)

    return net, counts, final_place


def apply(tree, parameters=None):
    """
    Apply from Process Tree to Petri net

    Parameters
    -----------
    tree
        Process tree
    parameters
        Parameters of the algorithm

    Returns
    -----------
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    """
    if parameters is None:
        parameters = {}
    del parameters

    counts = Counts()
    net = PetriNet('imdf_net_' + str(time.time()))
    initial_marking = Marking()
    final_marking = Marking()
    source = get_new_place(counts)
    source.name = "source"
    sink = get_new_place(counts)
    sink.name = "sink"
    net.places.add(source)
    net.places.add(sink)
    initial_marking[source] = 1
    final_marking[sink] = 1
    initial_mandatory = check_tau_mandatory_at_initial_marking(tree)
    final_mandatory = check_tau_mandatory_at_final_marking(tree)
    if initial_mandatory:
        initial_place = get_new_place(counts)
        net.places.add(initial_place)
        tau_initial = get_new_hidden_trans(counts, type_trans="tau")
        net.transitions.add(tau_initial)
        add_arc_from_to(source, tau_initial, net)
        add_arc_from_to(tau_initial, initial_place, net)
    else:
        initial_place = source
    if final_mandatory:
        final_place = get_new_place(counts)
        net.places.add(final_place)
        tau_final = get_new_hidden_trans(counts, type_trans="tau")
        net.transitions.add(tau_final)
        add_arc_from_to(final_place, tau_final, net)
        add_arc_from_to(tau_final, sink, net)
    else:
        final_place = sink

    net, counts, last_added_place = recursively_add_tree(tree, tree, net, initial_place, final_place, counts, 0)

    reduction.apply_simple_reduction(net)

    places = list(net.places)
    for place in places:
        if len(place.out_arcs) == 0 and not place in final_marking:
            remove_place(net, place)
        if len(place.in_arcs) == 0 and not place in initial_marking:
            remove_place(net, place)

    return net, initial_marking, final_marking

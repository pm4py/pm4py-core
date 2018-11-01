import time

from pm4py.algo.discovery.inductive.util import petri_cleaning
from pm4py.algo.discovery.inductive.util.petri_el_count import Counts
from pm4py.algo.discovery.inductive.versions.dfg.util.petri_el_add import get_new_place, get_new_hidden_trans, \
    get_transition
from pm4py.objects import petri
from pm4py.objects.petri.petrinet import Marking
from pm4py.objects.petri.petrinet import PetriNet
from pm4py.objects.process_tree import process_tree, tree_constants


def recursively_add_tree(tree, net, initial_entity_subtree, final_entity_subtree, counts, rec_depth,
                         force_add_skip=False):
    """
    Recursively add the subtrees to the Petri net

    Parameters
    -----------
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
        petri.utils.add_arc_from_to(initial_entity_subtree, initial_place, net)
    else:
        initial_place = initial_entity_subtree
    if final_entity_subtree is not None and type(final_entity_subtree) is PetriNet.Place:
        final_place = final_entity_subtree
    else:
        final_place = get_new_place(counts)
        net.places.add(final_place)
        if final_entity_subtree is not None and type(final_entity_subtree) is PetriNet.Transition:
            petri.utils.add_arc_from_to(final_place, final_entity_subtree, net)
    tree_subtrees = [child for child in tree.children if type(child) is process_tree.ProcessTree]
    tree_transitions = [child for child in tree.children if type(child) is process_tree.PTTransition]

    for trans in tree_transitions:
        if trans.label is None:
            petri_trans = get_new_hidden_trans(counts, type_trans="skip")
        else:
            petri_trans = get_transition(counts, trans.label)
        net.transitions.add(petri_trans)
        petri.utils.add_arc_from_to(initial_place, petri_trans, net)
        petri.utils.add_arc_from_to(petri_trans, final_place, net)

    if tree.operator == tree_constants.EXCLUSIVE_OPERATOR:
        for subtree in tree_subtrees:
            net, counts, intermediate_place = recursively_add_tree(subtree, net, initial_place, final_place, counts,
                                                                   rec_depth + 1, force_add_skip=force_add_skip)
    elif tree.operator == tree_constants.PARALLEL_OPERATOR:
        new_initial_trans = get_new_hidden_trans(counts, type_trans="tauSplit")
        net.transitions.add(new_initial_trans)
        petri.utils.add_arc_from_to(initial_place, new_initial_trans, net)
        new_final_trans = get_new_hidden_trans(counts, type_trans="tauJoin")
        net.transitions.add(new_final_trans)
        petri.utils.add_arc_from_to(new_final_trans, final_place, net)

        for subtree in tree_subtrees:
            net, counts, intermediate_place = recursively_add_tree(subtree, net, new_initial_trans, new_final_trans,
                                                                   counts,
                                                                   rec_depth + 1, force_add_skip=force_add_skip)
    elif tree.operator == tree_constants.SEQUENTIAL_OPERATOR:
        intermediate_place = initial_place
        for i in range(len(tree_subtrees)):
            final_connection_place = None
            if i == len(tree_subtrees)-1:
                final_connection_place = final_place
            net, counts, intermediate_place = recursively_add_tree(tree_subtrees[i], net, intermediate_place, final_connection_place, counts,
                                                                   rec_depth + 1, force_add_skip=force_add_skip)
    elif tree.operator == tree_constants.LOOP_OPERATOR:
        loop_trans = get_new_hidden_trans(counts, type_trans="loop")
        net.transitions.add(loop_trans)
        petri.utils.add_arc_from_to(final_place, loop_trans, net)
        petri.utils.add_arc_from_to(loop_trans, initial_place, net)

        if len(tree_subtrees) == 1:
            net, counts, intermediate_place = recursively_add_tree(tree_subtrees[0], net, initial_place, final_place,
                                                                   counts,
                                                                   rec_depth + 1, force_add_skip=True)
        else:
            intermediate_place = initial_place
            for i in range(len(tree_subtrees)):
                final_connection_place = None
                if i == len(tree_subtrees) - 1:
                    final_connection_place = final_place
                net, counts, intermediate_place = recursively_add_tree(tree_subtrees[i], net, intermediate_place,
                                                                       final_connection_place, counts,
                                                                       rec_depth + 1, force_add_skip=True)
    if force_add_skip and tree_transitions:
        skip_trans = get_new_hidden_trans(counts, type_trans="skip")
        net.transitions.add(skip_trans)
        petri.utils.add_arc_from_to(initial_place, skip_trans, net)
        petri.utils.add_arc_from_to(skip_trans, final_place, net)

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
    net = petri.petrinet.PetriNet('imdf_net_' + str(time.time()))
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
    initial_mandatory = tree.check_tau_mandatory_at_initial_marking()
    final_mandatory = tree.check_tau_mandatory_at_final_marking()
    if initial_mandatory:
        initial_place = get_new_place(counts)
        net.places.add(initial_place)
        tau_initial = get_new_hidden_trans(counts, type_trans="tau")
        net.transitions.add(tau_initial)
        petri.utils.add_arc_from_to(source, tau_initial, net)
        petri.utils.add_arc_from_to(tau_initial, initial_place, net)
    else:
        initial_place = source
    if final_mandatory:
        final_place = get_new_place(counts)
        net.places.add(final_place)
        tau_final = get_new_hidden_trans(counts, type_trans="tau")
        net.transitions.add(tau_final)
        petri.utils.add_arc_from_to(final_place, tau_final, net)
        petri.utils.add_arc_from_to(tau_final, sink, net)
    else:
        final_place = sink

    net, counts, last_added_place = recursively_add_tree(tree, net, initial_place, final_place, counts, 0)

    net = petri_cleaning.clean_duplicate_transitions(net)

    return net, initial_marking, final_marking

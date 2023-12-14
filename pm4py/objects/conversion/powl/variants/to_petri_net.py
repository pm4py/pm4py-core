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
from itertools import product

import pm4py.objects.conversion.process_tree.variants.to_petri_net as pt_to_pn
from pm4py.objects.petri_net.obj import Marking
from pm4py.objects.petri_net.obj import PetriNet
from pm4py.objects.petri_net.utils.petri_utils import add_arc_from_to, remove_place
from pm4py.objects.powl.obj import Transition, SilentTransition, StrictPartialOrder, OperatorPOWL, FrequentTransition
from pm4py.objects.petri_net.utils import reduction
from pm4py.objects.process_tree.obj import Operator


def recursively_add_tree(powl, net, initial_entity_subtree, final_entity_subtree, counts, rec_depth,
                         force_add_skip=False):
    """
    Recursively add the submodels to the Petri net

    Parameters
    -----------
    powl
        POWL model
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

    if force_add_skip:
        invisible = get_new_hidden_trans(counts, type_trans="skip")
        add_arc_from_to(initial_place, invisible, net)
        add_arc_from_to(invisible, final_place, net)

    if isinstance(powl, Transition):
        if isinstance(powl, SilentTransition):
            petri_trans = get_new_hidden_trans(counts, type_trans="skip")
        elif isinstance(powl, FrequentTransition):
            petri_trans = get_transition(counts, powl.label, powl.activity, powl.skippable, powl.selfloop)
        else:
            petri_trans = get_transition(counts, powl.label, powl.label)
        net.transitions.add(petri_trans)
        add_arc_from_to(initial_place, petri_trans, net)
        add_arc_from_to(petri_trans, final_place, net)

    elif isinstance(powl, OperatorPOWL):
        tree_children = powl.children
        if powl.operator == Operator.XOR:
            for subtree in tree_children:
                net, counts, intermediate_place = recursively_add_tree(subtree, net, initial_place,
                                                                       final_place,
                                                                       counts,
                                                                       rec_depth + 1)
        elif powl.operator == Operator.LOOP:
            new_initial_place = get_new_place(counts)
            net.places.add(new_initial_place)
            init_loop_trans = get_new_hidden_trans(counts, type_trans="init_loop")
            net.transitions.add(init_loop_trans)
            add_arc_from_to(initial_place, init_loop_trans, net)
            add_arc_from_to(init_loop_trans, new_initial_place, net)
            initial_place = new_initial_place
            loop_trans = get_new_hidden_trans(counts, type_trans="loop")
            net.transitions.add(loop_trans)

            exit_node = SilentTransition()
            do = tree_children[0]
            redo = tree_children[1]

            net, counts, int1 = recursively_add_tree(do, net, initial_place,
                                                     None, counts,
                                                     rec_depth + 1)
            net, counts, int2 = recursively_add_tree(redo, net, int1,
                                                     None, counts,
                                                     rec_depth + 1)
            net, counts, int3 = recursively_add_tree(exit_node, net, int1,
                                                     final_place, counts,
                                                     rec_depth + 1)

            looping_place = int2

            add_arc_from_to(looping_place, loop_trans, net)
            add_arc_from_to(loop_trans, initial_place, net)

    elif isinstance(powl, StrictPartialOrder):
        transitive_reduction = powl.order.get_transitive_reduction()
        tree_children = list(powl.children)
        tau_split = get_new_hidden_trans(counts, type_trans="tauSplit")
        net.transitions.add(tau_split)
        add_arc_from_to(initial_place, tau_split, net)
        tau_join = get_new_hidden_trans(counts, type_trans="tauJoin")
        net.transitions.add(tau_join)
        add_arc_from_to(tau_join, final_place, net)

        init_trans = []
        final_trans = []
        start_nodes = transitive_reduction.get_start_nodes()
        end_nodes = transitive_reduction.get_end_nodes()
        for subtree in tree_children:
            i_trans = get_new_hidden_trans(counts, type_trans="init_par")
            net.transitions.add(i_trans)
            if subtree in start_nodes:
                i_place = get_new_place(counts)
                net.places.add(i_place)
                add_arc_from_to(tau_split, i_place, net)

                add_arc_from_to(i_place, i_trans, net)

            f_trans = get_new_hidden_trans(counts, type_trans="final_par")
            net.transitions.add(f_trans)
            if subtree in end_nodes:
                f_place = get_new_place(counts)
                net.places.add(f_place)
                add_arc_from_to(f_trans, f_place, net)
                add_arc_from_to(f_place, tau_join, net)

            net, counts, intermediate_place = recursively_add_tree(subtree,
                                                                   net,
                                                                   i_trans,
                                                                   f_trans,
                                                                   counts,
                                                                   rec_depth + 1)
            init_trans.append(i_trans)
            final_trans.append(f_trans)

        n = range(len(tree_children))
        for i, j in product(n, n):
            if transitive_reduction.is_edge_id(i, j):
                new_place = get_new_place(counts)
                net.places.add(new_place)
                add_arc_from_to(final_trans[i], new_place, net)
                add_arc_from_to(new_place, init_trans[j], net)

    return net, counts, final_place


def apply(powl, parameters=None):
    """
    Apply from POWL model to Petri net

    Parameters
    -----------
    powl
        POWL model
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

    counts = pt_to_pn.Counts()
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
    initial_mandatory = True  # check_tau_mandatory_at_initial_marking(powl)
    final_mandatory = True  # check_tau_mandatory_at_final_marking(powl)
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

    net, counts, last_added_place = recursively_add_tree(powl, net, initial_place, final_place, counts, 0)

    reduction.apply_simple_reduction(net)

    places = list(net.places)
    for place in places:
        if len(place.out_arcs) == 0 and place not in final_marking:
            remove_place(net, place)
        if len(place.in_arcs) == 0 and place not in initial_marking:
            remove_place(net, place)

    return net, initial_marking, final_marking


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


def get_transition(counts, label, activity, skippable=False, selfloop=False):
    """
    Create a transitions with the specified label in the Petri net
    """
    counts.inc_no_visible()
    return PetriNet.Transition(str(uuid.uuid4()), label, properties={"activity": activity,
                                                                     "skippable": skippable,
                                                                     "selfloop": selfloop})

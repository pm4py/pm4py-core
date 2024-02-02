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
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.petri_net.utils.petri_utils import add_arc_from_to, remove_transition
from pm4py.util import nx_utils


def remove_rendundant_invisible_transitions(net):
    """
    Remove redundant transitions from Petri net

    Parameters
    -----------
    net
        Petri net

    Returns
    -----------
    net
        Cleaned net
    """
    trans = [x for x in list(net.transitions) if not x.label]
    i = 0
    while i < len(trans):
        if trans[i] in net.transitions:
            preset_i = set(x.source for x in trans[i].in_arcs)
            postset_i = set(x.target for x in trans[i].out_arcs)
            j = 0
            while j < len(trans):
                if not j == i:
                    preset_j = set(x.source for x in trans[j].in_arcs)
                    postset_j = set(x.target for x in trans[j].out_arcs)
                    if len(preset_j) == len(preset_i) and len(postset_j) < len(postset_i):
                        if len(preset_j.intersection(preset_i)) == len(preset_j) and len(
                                postset_j.intersection(postset_i)) == len(postset_j):
                            remove_transition(net, trans[j])
                            del trans[j]
                            continue
                j = j + 1
            i = i + 1
    return net


def find_bindings(and_measures):
    """
    Find the bindings given the AND measures

    Parameters
    -------------
    and_measures
        AND measures

    Returns
    -------------
    bindings
        Bindings
    """
    G = nx_utils.Graph()
    allocated_nodes = set()
    for n1 in list(and_measures.keys()):
        if n1 not in allocated_nodes:
            allocated_nodes.add(n1)
            G.add_node(n1)
        for n2 in list(and_measures[n1].keys()):
            if n2 not in allocated_nodes:
                allocated_nodes.add(n2)
                G.add_node(n1)
            G.add_edge(n1, n2)
    ret = list(nx_utils.find_cliques(G))
    return ret


def apply(heu_net, parameters=None):
    """
    Converts an Heuristics Net to a Petri net

    Parameters
    --------------
    heu_net
        Heuristics net
    parameters
        Possible parameters of the algorithm

    Returns
    --------------
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    """
    if parameters is None:
        parameters = {}
    net = PetriNet("")
    im = Marking()
    fm = Marking()
    source_places = []
    sink_places = []
    hid_trans_count = 0
    for index, sa_list in enumerate(heu_net.start_activities):
        source = PetriNet.Place("source" + str(index))
        source_places.append(source)
        net.places.add(source)
        im[source] = 1
    for index, ea_list in enumerate(heu_net.end_activities):
        sink = PetriNet.Place("sink" + str(index))
        sink_places.append(sink)
        net.places.add(sink)
        fm[sink] = 1
    act_trans = {}
    who_is_entering = {}
    who_is_exiting = {}
    for act1_name in heu_net.nodes:
        act1 = heu_net.nodes[act1_name]
        if act1_name not in act_trans:
            act_trans[act1_name] = PetriNet.Transition(act1_name, act1_name)
            net.transitions.add(act_trans[act1_name])
            who_is_entering[act1_name] = set()
            who_is_exiting[act1_name] = set()
            for index, sa_list in enumerate(heu_net.start_activities):
                if act1_name in sa_list:
                    who_is_entering[act1_name].add((None, index))
            for index, ea_list in enumerate(heu_net.end_activities):
                if act1_name in ea_list:
                    who_is_exiting[act1_name].add((None, index))
        for act2 in act1.output_connections:
            act2_name = act2.node_name
            if act2_name not in act_trans:
                act_trans[act2_name] = PetriNet.Transition(act2_name, act2_name)
                net.transitions.add(act_trans[act2_name])
                who_is_entering[act2_name] = set()
                who_is_exiting[act2_name] = set()
                for index, sa_list in enumerate(heu_net.start_activities):
                    if act2_name in sa_list:
                        who_is_entering[act2_name].add((None, index))
                for index, ea_list in enumerate(heu_net.end_activities):
                    if act2_name in ea_list:
                        who_is_exiting[act2_name].add((None, index))
            who_is_entering[act2_name].add((act1_name, None))
            who_is_exiting[act1_name].add((act2_name, None))
    places_entering = {}
    for act1 in who_is_entering:
        cliques = find_bindings(heu_net.nodes[act1].and_measures_in)
        places_entering[act1] = {}
        entering_activities = list(who_is_entering[act1])
        entering_activities_wo_source = sorted([x for x in entering_activities if x[0] is not None], key=lambda x: x[0])
        entering_activities_only_source = [x for x in entering_activities if x[0] is None]
        if entering_activities_wo_source:
            master_place = PetriNet.Place("pre_" + act1)
            net.places.add(master_place)
            add_arc_from_to(master_place, act_trans[act1], net)
            if len(entering_activities) == 1:
                places_entering[act1][entering_activities[0]] = master_place
            else:
                for index, act in enumerate(entering_activities_wo_source):
                    if act[0] in heu_net.nodes[act1].and_measures_in:
                        z = 0
                        while z < len(cliques):
                            if act[0] in cliques[z]:
                                hid_trans_count = hid_trans_count + 1
                                hid_trans = PetriNet.Transition("hid_" + str(hid_trans_count), None)
                                net.transitions.add(hid_trans)
                                add_arc_from_to(hid_trans, master_place, net)
                                for act2 in cliques[z]:
                                    if (act2, None) not in places_entering[act1]:
                                        s_place = PetriNet.Place("splace_in_" + act1 + "_" + act2 + "_" + str(index))
                                        net.places.add(s_place)
                                        places_entering[act1][(act2, None)] = s_place
                                    add_arc_from_to(places_entering[act1][(act2, None)], hid_trans, net)
                                del cliques[z]
                                continue
                            z = z + 1
                        pass
                    elif act not in places_entering[act1]:
                        hid_trans_count = hid_trans_count + 1
                        hid_trans = PetriNet.Transition("hid_" + str(hid_trans_count), None)
                        net.transitions.add(hid_trans)
                        add_arc_from_to(hid_trans, master_place, net)
                        if act not in places_entering[act1]:
                            s_place = PetriNet.Place("splace_in_" + act1 + "_" + str(index))
                            net.places.add(s_place)
                            places_entering[act1][act] = s_place
                        add_arc_from_to(places_entering[act1][act], hid_trans, net)
        for el in entering_activities_only_source:
            if len(entering_activities) == 1:
                add_arc_from_to(source_places[el[1]], act_trans[act1], net)
            else:
                hid_trans_count = hid_trans_count + 1
                hid_trans = PetriNet.Transition("hid_" + str(hid_trans_count), None)
                net.transitions.add(hid_trans)
                add_arc_from_to(source_places[el[1]], hid_trans, net)
                add_arc_from_to(hid_trans, master_place, net)
    for act1 in who_is_exiting:
        cliques = find_bindings(heu_net.nodes[act1].and_measures_out)
        exiting_activities = list(who_is_exiting[act1])
        exiting_activities_wo_sink = sorted([x for x in exiting_activities if x[0] is not None], key=lambda x: x[0])
        exiting_activities_only_sink = [x for x in exiting_activities if x[0] is None]
        if exiting_activities_wo_sink:
            if len(exiting_activities) == 1 and len(exiting_activities_wo_sink) == 1:
                ex_act = exiting_activities_wo_sink[0]
                if (act1, None) in places_entering[ex_act[0]]:
                    add_arc_from_to(act_trans[act1], places_entering[ex_act[0]][(act1, None)], net)
            else:
                int_place = PetriNet.Place("intplace_" + str(act1))
                net.places.add(int_place)
                add_arc_from_to(act_trans[act1], int_place, net)
                for ex_act in exiting_activities_wo_sink:
                    if (act1, None) in places_entering[ex_act[0]]:
                        if ex_act[0] in heu_net.nodes[act1].and_measures_out:
                            z = 0
                            while z < len(cliques):
                                if ex_act[0] in cliques[z]:
                                    hid_trans_count = hid_trans_count + 1
                                    hid_trans = PetriNet.Transition("hid_" + str(hid_trans_count), None)
                                    net.transitions.add(hid_trans)
                                    add_arc_from_to(int_place, hid_trans, net)
                                    for act in cliques[z]:
                                        add_arc_from_to(hid_trans, places_entering[act][(act1, None)], net)
                                    del cliques[z]
                                    continue
                                z = z + 1
                        else:
                            hid_trans_count = hid_trans_count + 1
                            hid_trans = PetriNet.Transition("hid_" + str(hid_trans_count), None)
                            net.transitions.add(hid_trans)
                            add_arc_from_to(int_place, hid_trans, net)
                            add_arc_from_to(hid_trans, places_entering[ex_act[0]][(act1, None)], net)
        for el in exiting_activities_only_sink:
            if len(exiting_activities) == 1:
                add_arc_from_to(act_trans[act1], sink_places[el[1]], net)
            else:
                hid_trans_count = hid_trans_count + 1
                hid_trans = PetriNet.Transition("hid_" + str(hid_trans_count), None)
                net.transitions.add(hid_trans)
                add_arc_from_to(int_place, hid_trans, net)
                add_arc_from_to(hid_trans, sink_places[el[1]], net)
    net = remove_rendundant_invisible_transitions(net)
    from pm4py.objects.petri_net.utils import reduction
    reduction.apply_simple_reduction(net)
    return net, im, fm

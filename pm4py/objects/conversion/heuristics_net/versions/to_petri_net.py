from pm4py.objects.petri.petrinet import PetriNet, Marking
from pm4py.objects.petri.utils import add_arc_from_to


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
                target_hidden_trans = {}
                for index, act in enumerate(entering_activities_wo_source):
                    if act[0] not in target_hidden_trans:
                        hid_trans_count = hid_trans_count + 1
                        hid_trans = PetriNet.Transition("hid_" + str(hid_trans_count), None)
                        net.transitions.add(hid_trans)
                        target_hidden_trans[act] = hid_trans
                        add_arc_from_to(hid_trans, master_place, net)
                    else:
                        hid_trans = target_hidden_trans[act[0]]
                    s_place = PetriNet.Place("splace_in_" + act1 + "_" + str(index))
                    net.places.add(s_place)
                    add_arc_from_to(s_place, hid_trans, net)
                    places_entering[act1][act] = s_place
                    if act[0] in heu_net.nodes[act1].and_measures_in:
                        for and_act in heu_net.nodes[act1].and_measures_in[act[0]]:
                            target_hidden_trans[and_act] = hid_trans
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
    return net, im, fm

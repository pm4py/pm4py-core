from pm4py.objects.petri.check_soundness import check_petri_wfnet_and_soundness
from pm4py.objects.petri.petrinet import PetriNet
from pm4py.objects.petri.utils import add_arc_from_to


def get_s_components_from_petri(net, im, fm, ini_net_places=None, ini_net_transitions=None, curr_s_comp=None,
                                rec_depth=0, adv_idx=0, list_s_components=None):
    if list_s_components is None:
        list_s_components = []
    if ini_net_places is None:
        ini_net_places = {}
        for place in net.places:
            ini_net_places[place.name] = place

    if ini_net_transitions is None:
        ini_net_transitions = {}
        for trans in net.transitions:
            ini_net_transitions[trans.name] = trans

    if rec_depth == 0:
        if not check_petri_wfnet_and_soundness(net):
            return list_s_components
    if curr_s_comp is None:
        curr_s_comp = PetriNet()
        for place in im:
            curr_s_comp.places.add(PetriNet.Place(place.name))

    something_changed = True
    while something_changed:
        something_changed = False
        this_comp_arcs = [arc.source.name + "@@@" + arc.target.name for arc in curr_s_comp.arcs]
        this_comp_places_names = [place.name for place in curr_s_comp.places]
        this_comp_trans_names = [trans.name for trans in curr_s_comp.transitions]
        if adv_idx % 2 == 0:
            places_wo_right_conn = [place for place in curr_s_comp.places if not place.out_arcs]
            for p in places_wo_right_conn:
                corr_p = ini_net_places[p.name]
                corr_p_out_trans = [arc.target for arc in corr_p.out_arcs]
                corr_p_out_trans = [trans for trans in corr_p_out_trans if trans.name not in this_comp_trans_names]
                corr_p_out_arcs = [arc.source.name + "@@@" + arc.target.name for arc in corr_p.out_arcs]
                corr_p_out_arcs = [arc for arc in corr_p_out_arcs if arc not in this_comp_arcs]
                for trans in corr_p_out_trans:
                    curr_s_comp.transitions.add(PetriNet.Transition(trans.name, trans.label))

                this_comp_transitions = {trans.name: trans for trans in curr_s_comp.transitions}
                for arc in corr_p_out_arcs:
                    add_arc_from_to(p, this_comp_transitions[arc.split("@@@")[1]], curr_s_comp)
                    something_changed = True

        else:
            trans_wo_right_conn = [trans for trans in curr_s_comp.transitions if not trans.out_arcs]
            for t in trans_wo_right_conn:
                corr_t = ini_net_transitions[t.name]
                corr_t_out_places = [arc.target for arc in corr_t.out_arcs]
                corr_t_out_places = [place for place in corr_t_out_places if place.name not in this_comp_places_names]
                corr_t_out_arcs = [arc.source.name + "@@@" + arc.target.name for arc in corr_t.out_arcs]
                corr_t_out_arcs = [arc for arc in corr_t_out_arcs if arc not in this_comp_arcs]
                for place in corr_t_out_places:
                    curr_s_comp.places.add(PetriNet.Place(place.name))

                this_comp_places = {place.name: place for place in curr_s_comp.places}
                for arc in corr_t_out_arcs:
                    add_arc_from_to(t, this_comp_places[arc.split("@@@")[1]], curr_s_comp)
                    something_changed = True

        adv_idx = adv_idx + 1

    list_s_components.append(curr_s_comp)
    return list_s_components

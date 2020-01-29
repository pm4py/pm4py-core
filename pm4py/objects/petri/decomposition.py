import networkx as nx
from pm4py.objects.petri.petrinet import PetriNet, Marking
from pm4py.objects.petri.utils import add_arc_from_to
import hashlib


def get_graph_components(places, inv_trans, trans_dup_label, tmap):
    G = nx.Graph()
    for x in places:
        G.add_node(x)
    for x in inv_trans:
        G.add_node(x)
    for x in trans_dup_label:
        G.add_node(x)
    for x in trans_dup_label:
        i = 0
        while i < len(tmap[x])-1:
            j = i + 1
            while j < len(tmap[x]):
                G.add_edge(tmap[x][i].name, tmap[x][j].name)
                j = j + 1
    all_inserted_val = set(places.values()).union(inv_trans.values()).union(trans_dup_label.values())
    for v1 in all_inserted_val:
        for arc in v1.out_arcs:
            v2 = arc.target
            if v2 in all_inserted_val:
                G.add_edge(v1.name, v2.name)
    conn_comp = list(nx.algorithms.components.connected_components(G))
    return conn_comp


def decompose(net, im, fm):
    places = {x.name: x for x in net.places}
    inv_trans = {x.name: x for x in net.transitions if x.label is None}
    tmap = {}
    for t in net.transitions:
        if t.label is not None:
            if t.label not in tmap:
                tmap[t.label] = []
            tmap[t.label].append(t)
    trans_dup_label = {x.name: x for x in net.transitions if x.label is not None and len(tmap[x.label]) > 1}
    trans_labels = {x.name: x.label for x in net.transitions}
    conn_comp = get_graph_components(places, inv_trans, trans_dup_label, tmap)
    list_nets = []
    for cmp in conn_comp:
        net_new = PetriNet("")
        im_new = Marking()
        fm_new = Marking()
        lmap = {}
        for el in cmp:
            if el in places:
                lmap[el] = PetriNet.Place(el)
                net_new.places.add(lmap[el])
            elif el in inv_trans:
                lmap[el] = PetriNet.Transition(el, None)
                net_new.transitions.add(lmap[el])
            else:
                lmap[el] = PetriNet.Transition(el, trans_labels[el])
                net_new.transitions.add(lmap[el])
        for el in cmp:
            if el in places:
                old_place = places[el]
                for arc in old_place.in_arcs:
                    st = arc.source
                    if st.name not in lmap:
                        lmap[st.name] = PetriNet.Transition(st.name, trans_labels[st.name])
                        net_new.transitions.add(lmap[st.name])
                    add_arc_from_to(lmap[st.name], lmap[el], net_new)
                for arc in old_place.out_arcs:
                    st = arc.target
                    if st.name not in lmap:
                        lmap[st.name] = PetriNet.Transition(st.name, trans_labels[st.name])
                        net_new.transitions.add(lmap[st.name])
                    add_arc_from_to(lmap[el], lmap[st.name], net_new)
                if old_place in im:
                    im_new[lmap[el]] = im[old_place]
                if old_place in fm:
                    fm_new[lmap[el]] = fm[old_place]
        lvis_labels = sorted([t.label for t in net_new.transitions if t.label is not None])
        t_tuple = tuple(sorted(list(int(hashlib.md5(t.name.encode('utf-8')).hexdigest(), 16) for t in net_new.transitions)))
        net_new.lvis_labels = lvis_labels
        net_new.t_tuple = t_tuple

        list_nets.append((net_new, im_new, fm_new))
    return list_nets

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
import hashlib

from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.petri_net.utils.petri_utils import add_arc_from_to
from pm4py.util import constants, nx_utils


def get_graph_components(places, inv_trans, trans_dup_label, tmap):
    G = nx_utils.Graph()
    for x in places:
        G.add_node(x)
    for x in inv_trans:
        G.add_node(x)
    for x in trans_dup_label:
        G.add_node(x)
    for x in trans_dup_label:
        i = 0
        while i < len(tmap[x]) - 1:
            j = i + 1
            while j < len(tmap[x]):
                G.add_edge(tmap[x][i].label, tmap[x][j].label)
                j = j + 1
            i = i + 1
    all_inserted_val = set(places.values()).union(inv_trans.values()).union(trans_dup_label.values())
    for v1 in all_inserted_val:
        for arc in v1.out_arcs:
            v2 = arc.target
            if v2 in all_inserted_val:
                G.add_edge(v1.name, v2.name)
    conn_comp = list(nx_utils.connected_components(G))
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
    trans_dup_label = {x.label: x for x in net.transitions if x.label is not None and len(tmap[x.label]) > 1}
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
            elif el in trans_labels:
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
        t_tuple = tuple(
            sorted(list(int(hashlib.md5(t.name.encode(constants.DEFAULT_ENCODING)).hexdigest(), 16) for t in
                        net_new.transitions)))
        net_new.lvis_labels = lvis_labels
        net_new.t_tuple = t_tuple

        if len(net_new.places) > 0 or len(net_new.transitions) > 0:
            list_nets.append((net_new, im_new, fm_new))

    return list_nets


def merge_comp(comp1, comp2):
    net = PetriNet("")
    im = Marking()
    fm = Marking()
    places = {}
    trans = {}

    for pl in comp1[0].places:
        places[pl.name] = PetriNet.Place(pl.name)
        net.places.add(places[pl.name])
        if pl in comp1[1]:
            im[places[pl.name]] = comp1[1][pl]
        if pl in comp1[2]:
            fm[places[pl.name]] = comp1[2][pl]

    for pl in comp2[0].places:
        places[pl.name] = PetriNet.Place(pl.name)
        net.places.add(places[pl.name])
        if pl in comp2[1]:
            im[places[pl.name]] = comp2[1][pl]
        if pl in comp2[2]:
            fm[places[pl.name]] = comp2[2][pl]

    for tr in comp1[0].transitions:
        trans[tr.name] = PetriNet.Transition(tr.name, tr.label)
        net.transitions.add(trans[tr.name])

    for tr in comp2[0].transitions:
        if not tr.name in trans:
            trans[tr.name] = PetriNet.Transition(tr.name, tr.label)
            net.transitions.add(trans[tr.name])

    for arc in comp1[0].arcs:
        if type(arc.source) is PetriNet.Place:
            add_arc_from_to(places[arc.source.name], trans[arc.target.name], net)
        else:
            add_arc_from_to(trans[arc.source.name], places[arc.target.name], net)

    for arc in comp2[0].arcs:
        if type(arc.source) is PetriNet.Place:
            add_arc_from_to(places[arc.source.name], trans[arc.target.name], net)
        else:
            add_arc_from_to(trans[arc.source.name], places[arc.target.name], net)

    lvis_labels = sorted([t.label for t in net.transitions if t.label is not None])
    t_tuple = tuple(sorted(
        list(int(hashlib.md5(t.name.encode(constants.DEFAULT_ENCODING)).hexdigest(), 16) for t in net.transitions)))
    net.lvis_labels = lvis_labels
    net.t_tuple = t_tuple

    return (net, im, fm)


def merge_sublist_nets(list_nets):
    while len(list_nets) > 1:
        list_nets.append(merge_comp(list_nets[0], list_nets[1]))
        list_nets.pop(0)
        list_nets.pop(0)

    return list_nets[0]

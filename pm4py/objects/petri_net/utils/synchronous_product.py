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
from pm4py.objects.petri_net.utils.petri_utils import add_arc_from_to
from pm4py.objects.petri_net import properties


def construct(pn1, im1, fm1, pn2, im2, fm2, skip):
    """
    Constructs the synchronous product net of two given Petri nets.


    :param pn1: Petri net 1
    :param im1: Initial marking of Petri net 1
    :param fm1: Final marking of Petri net 1
    :param pn2: Petri net 2
    :param im2: Initial marking of Petri net 2
    :param fm2: Final marking of Petri net 2
    :param skip: Symbol to be used as skip

    Returns
    -------
    :return: Synchronous product net and associated marking labels are of the form (a,>>)
    """
    sync_net = PetriNet('synchronous_product_net of %s and %s' % (pn1.name, pn2.name))
    t1_map, p1_map = __copy_into(pn1, sync_net, True, skip)
    t2_map, p2_map = __copy_into(pn2, sync_net, False, skip)

    for t1 in pn1.transitions:
        for t2 in pn2.transitions:
            if t1.label == t2.label:
                sync = PetriNet.Transition((t1.name, t2.name), (t1.label, t2.label))
                sync_net.transitions.add(sync)
                # copy the properties of the transitions inside the transition of the sync net
                for p1 in t1.properties:
                    sync.properties[p1] = t1.properties[p1]
                for p2 in t2.properties:
                    sync.properties[p2] = t2.properties[p2]
                for a in t1.in_arcs:
                    add_arc_from_to(p1_map[a.source], sync, sync_net)
                for a in t2.in_arcs:
                    add_arc_from_to(p2_map[a.source], sync, sync_net)
                for a in t1.out_arcs:
                    add_arc_from_to(sync, p1_map[a.target], sync_net)
                for a in t2.out_arcs:
                    add_arc_from_to(sync, p2_map[a.target], sync_net)

    sync_im = Marking()
    sync_fm = Marking()
    for p in im1:
        sync_im[p1_map[p]] = im1[p]
    for p in im2:
        sync_im[p2_map[p]] = im2[p]
    for p in fm1:
        sync_fm[p1_map[p]] = fm1[p]
    for p in fm2:
        sync_fm[p2_map[p]] = fm2[p]

    # update 06/02/2021: to distinguish the sync nets that are output of this method, put a property in the sync net
    sync_net.properties[properties.IS_SYNC_NET] = True

    return sync_net, sync_im, sync_fm


def construct_cost_aware(pn1, im1, fm1, pn2, im2, fm2, skip, pn1_costs, pn2_costs, sync_costs):
    """
    Constructs the synchronous product net of two given Petri nets.


    :param pn1: Petri net 1
    :param im1: Initial marking of Petri net 1
    :param fm1: Final marking of Petri net 1
    :param pn2: Petri net 2
    :param im2: Initial marking of Petri net 2
    :param fm2: Final marking of Petri net 2
    :param skip: Symbol to be used as skip
    :param pn1_costs: dictionary mapping transitions of pn1 to corresponding costs
    :param pn2_costs: dictionary mapping transitions of pn2 to corresponding costs
    :param pn1_costs: dictionary mapping pairs of transitions in pn1 and pn2 to costs
    :param sync_costs: Costs of sync moves

    Returns
    -------
    :return: Synchronous product net and associated marking labels are of the form (a,>>)
    """
    sync_net = PetriNet('synchronous_product_net of %s and %s' % (pn1.name, pn2.name))
    t1_map, p1_map = __copy_into(pn1, sync_net, True, skip)
    t2_map, p2_map = __copy_into(pn2, sync_net, False, skip)
    costs = dict()

    for t1 in pn1.transitions:
        costs[t1_map[t1]] = pn1_costs[t1]
    for t2 in pn2.transitions:
        costs[t2_map[t2]] = pn2_costs[t2]

    for t1 in pn1.transitions:
        for t2 in pn2.transitions:
            if t1.label == t2.label:
                sync = PetriNet.Transition((t1.name, t2.name), (t1.label, t2.label))
                sync_net.transitions.add(sync)
                costs[sync] = sync_costs[(t1, t2)]
                # copy the properties of the transitions inside the transition of the sync net
                for p1 in t1.properties:
                    sync.properties[p1] = t1.properties[p1]
                for p2 in t2.properties:
                    sync.properties[p2] = t2.properties[p2]
                for a in t1.in_arcs:
                    add_arc_from_to(p1_map[a.source], sync, sync_net)
                for a in t2.in_arcs:
                    add_arc_from_to(p2_map[a.source], sync, sync_net)
                for a in t1.out_arcs:
                    add_arc_from_to(sync, p1_map[a.target], sync_net)
                for a in t2.out_arcs:
                    add_arc_from_to(sync, p2_map[a.target], sync_net)

    sync_im = Marking()
    sync_fm = Marking()
    for p in im1:
        sync_im[p1_map[p]] = im1[p]
    for p in im2:
        sync_im[p2_map[p]] = im2[p]
    for p in fm1:
        sync_fm[p1_map[p]] = fm1[p]
    for p in fm2:
        sync_fm[p2_map[p]] = fm2[p]

    # update 06/02/2021: to distinguish the sync nets that are output of this method, put a property in the sync net
    sync_net.properties[properties.IS_SYNC_NET] = True

    return sync_net, sync_im, sync_fm, costs


def __copy_into(source_net, target_net, upper, skip):
    t_map = {}
    p_map = {}
    for t in source_net.transitions:
        name = (t.name, skip) if upper else (skip, t.name)
        label = (t.label, skip) if upper else (skip, t.label)
        t_map[t] = PetriNet.Transition(name, label)
        if properties.TRACE_NET_TRANS_INDEX in t.properties:
            # 16/02/2021: copy the index property from the transition of the trace net
            t_map[t].properties[properties.TRACE_NET_TRANS_INDEX] = t.properties[properties.TRACE_NET_TRANS_INDEX]
        target_net.transitions.add(t_map[t])

    for p in source_net.places:
        name = (p.name, skip) if upper else (skip, p.name)
        p_map[p] = PetriNet.Place(name)
        if properties.TRACE_NET_PLACE_INDEX in p.properties:
            # 16/02/2021: copy the index property from the place of the trace net
            p_map[p].properties[properties.TRACE_NET_PLACE_INDEX] = p.properties[properties.TRACE_NET_PLACE_INDEX]
        target_net.places.add(p_map[p])

    for t in source_net.transitions:
        for a in t.in_arcs:
            add_arc_from_to(p_map[a.source], t_map[t], target_net)
        for a in t.out_arcs:
            add_arc_from_to(t_map[t], p_map[a.target], target_net)

    return t_map, p_map

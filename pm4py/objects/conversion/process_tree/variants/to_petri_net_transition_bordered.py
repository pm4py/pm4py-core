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
from pm4py.objects.petri_net import obj
from pm4py.objects.petri_net.utils import petri_utils as pn_util
from pm4py.objects.process_tree.obj import Operator as pt_opt


def apply(tree, parameters=None):
    '''
    Only supports loops with 2 children!
    :param tree:
    :return:
    '''
    net = obj.PetriNet(name=str(tree))
    if len(tree.children) == 0:
        pn_util.add_transition(net, label=tree.label, name=str(id(tree)))
    else:
        sub_nets = list()
        for c in tree.children:
            sub_net, ini, fin = apply(c)
            sub_nets.append(sub_net)
        pn_util.merge(net, sub_nets)
        switch = {
            pt_opt.SEQUENCE: construct_sequence_pattern,
            pt_opt.XOR: construct_xor_pattern,
            pt_opt.PARALLEL: construct_and_pattern,
            pt_opt.LOOP: construct_loop_pattern
        }
        net, ini, fin = switch[tree.operator](net, sub_nets)
    if tree.parent is None:
        p_ini = pn_util.add_place(net)
        p_fin = pn_util.add_place(net)
        pn_util.add_arc_from_to(p_ini, _get_src_transition(net), net)
        pn_util.add_arc_from_to(_get_sink_transition(net), p_fin, net)
        return net, obj.Marking({p_ini: 1}), obj.Marking({p_fin: 1})
    return net, obj.Marking(), obj.Marking()


def _get_src_transition(sub_net):
    for t in sub_net.transitions:
        if len(pn_util.pre_set(t)) == 0:
            return t
    return None


def _get_sink_transition(sub_net):
    for t in sub_net.transitions:
        if len(pn_util.post_set(t)) == 0:
            return t
    return None


def _add_src_sink_transitions(net, p_s, p_t):
    src = pn_util.add_transition(net)
    pn_util.add_arc_from_to(src, p_s, net)
    sink = pn_util.add_transition(net)
    pn_util.add_arc_from_to(p_t, sink, net)
    return net, obj.Marking(), obj.Marking()


def construct_sequence_pattern(net, sub_nets):
    places = [None] * (len(sub_nets) + 1)
    for i in range(len(sub_nets) + 1):
        places[i] = pn_util.add_place(net)
    for i in range(len(sub_nets)):
        pn_util.add_arc_from_to(places[i], _get_src_transition(sub_nets[i]), net)
        pn_util.add_arc_from_to(_get_sink_transition(sub_nets[i]), places[i + 1], net)
    src = pn_util.add_transition(net)
    pn_util.add_arc_from_to(src, places[0], net)
    sink = pn_util.add_transition(net)
    pn_util.add_arc_from_to(places[len(places) - 1], sink, net)
    return net, obj.Marking(), obj.Marking()


def construct_xor_pattern(net, sub_nets):
    p_s = pn_util.add_place(net)
    p_o = pn_util.add_place(net)
    for n in sub_nets:
        pn_util.add_arc_from_to(p_s, _get_src_transition(n), net)
        pn_util.add_arc_from_to(_get_sink_transition(n), p_o, net)
    return _add_src_sink_transitions(net, p_s, p_o)


def construct_and_pattern(net, sub_nets):
    p_s = [None] * len(sub_nets)
    p_t = [None] * len(sub_nets)
    for i in range(len(sub_nets)):
        p_s[i] = pn_util.add_place(net)
        p_t[i] = pn_util.add_place(net)
        pn_util.add_arc_from_to(p_s[i], _get_src_transition(sub_nets[i]), net)
        pn_util.add_arc_from_to(_get_sink_transition(sub_nets[i]), p_t[i], net)
    src = pn_util.add_transition(net)
    for p in p_s:
        pn_util.add_arc_from_to(src, p, net)
    sink = pn_util.add_transition(net)
    for p in p_t:
        pn_util.add_arc_from_to(p, sink, net)
    return net, obj.Marking(), obj.Marking()


def construct_loop_pattern(net, sub_nets):
    assert (len(sub_nets) == 2)
    p_s = pn_util.add_place(net)
    p_t = pn_util.add_place(net)
    pn_util.add_arc_from_to(p_s, _get_src_transition(sub_nets[0]), net)
    pn_util.add_arc_from_to(p_t, _get_src_transition(sub_nets[1]), net)
    pn_util.add_arc_from_to(_get_sink_transition(sub_nets[0]), p_t, net)
    pn_util.add_arc_from_to(_get_sink_transition(sub_nets[1]), p_s, net)
    net, ini, fin = _add_src_sink_transitions(net, p_s, p_t)
    return net, obj.Marking(), obj.Marking()

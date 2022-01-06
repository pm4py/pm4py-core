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
from pm4py.objects.petri_net.utils.petri_utils import remove_arc, remove_transition, remove_place, add_arc_from_to, pre_set, post_set, get_arc_type
from pm4py.objects.petri_net import properties
import itertools
from itertools import combinations, chain


def reduce_single_entry_transitions(net):
    """
    Reduces the number of the single entry transitions in the Petri net

    Parameters
    ----------------
    net
        Petri net
    """
    cont = True
    while cont:
        cont = False
        single_entry_transitions = [t for t in net.transitions if t.label is None and len(t.in_arcs) == 1]
        for i in range(len(single_entry_transitions)):
            t = single_entry_transitions[i]
            source_place = list(t.in_arcs)[0].source
            target_places = [a.target for a in t.out_arcs]
            if len(source_place.in_arcs) == 1 and len(source_place.out_arcs) == 1:
                source_transition = list(source_place.in_arcs)[0].source
                remove_transition(net, t)
                remove_place(net, source_place)
                for p in target_places:
                    add_arc_from_to(source_transition, p, net)
                cont = True
                break
    return net


def reduce_single_exit_transitions(net):
    """
    Reduces the number of the single exit transitions in the Petri net

    Parameters
    --------------
    net
        Petri net
    """
    cont = True
    while cont:
        cont = False
        single_exit_transitions = [t for t in net.transitions if t.label is None and len(t.out_arcs) == 1]
        for i in range(len(single_exit_transitions)):
            t = single_exit_transitions[i]
            target_place = list(t.out_arcs)[0].target
            source_places = [a.source for a in t.in_arcs]
            if len(target_place.in_arcs) == 1 and len(target_place.out_arcs) == 1:
                target_transition = list(target_place.out_arcs)[0].target
                remove_transition(net, t)
                remove_place(net, target_place)
                for p in source_places:
                    add_arc_from_to(p, target_transition, net)
                cont = True
                break
    return net


def apply_simple_reduction(net):
    """
    Apply a simple reduction to the Petri net

    Parameters
    --------------
    net
        Petri net
    """
    reduce_single_entry_transitions(net)
    reduce_single_exit_transitions(net)
    return net


def apply_fst_rule(net):
    """
    Apply the Fusion of Series Transitions (FST) rule

    Parameters
    --------------
    net
        Reset Inhibitor net
    """
    cont = True
    while cont:
        cont = False
        for p, t, u in itertools.product(net.places, net.transitions, net.transitions):
            if (len(list(p.in_arcs)) == 1 and list(p.in_arcs)[0].source == t) and \
                    (len(list(p.out_arcs)) == 1 and list(p.out_arcs)[0].target == u) and \
                    (len(list(u.in_arcs)) == 1 and list(u.in_arcs)[0].source == p) and \
                    (len(post_set(t).intersection(post_set(u))) == 0) and \
                    (set().union(*[post_set(place, properties.INHIBITOR_ARC) for place in post_set(u)]) == post_set(p,
                                                                                                                      properties.INHIBITOR_ARC)) and \
                    (set().union(*[post_set(place, properties.RESET_ARC) for place in post_set(u)]) == post_set(p,
                                                                                                                  properties.RESET_ARC)) and \
                    (len(pre_set(u, properties.RESET_ARC)) == 0 and len(pre_set(u, properties.INHIBITOR_ARC)) == 0):
                if u.label == None:
                    remove_place(net, p)
                    for target in post_set(u):
                        add_arc_from_to(t, target, net)
                    remove_transition(net, u)
                    cont = True
                    break

    return net


def apply_fsp_rule(net, im=None, fm=None):
    """
    Apply the Fusion of Series Places (FSP) rule

    Parameters
    --------------
    net
        Reset Inhibitor net
    """
    if im is None:
        im = {}
    if fm is None:
        fm = {}
    cont = True
    while cont:
        cont = False
        for p, q, t in itertools.product(net.places, net.places, net.transitions):
            if t.label == None:  # only silent transitions may be removed either way
                if (len(t.in_arcs) == 1 and list(t.in_arcs)[0].source == p) and \
                        (len(t.out_arcs) == 1 and list(t.out_arcs)[0].target == q) and \
                        (len(post_set(p)) == 1 and list(post_set(p))[0] == t) and \
                        (len(pre_set(p).intersection(pre_set(q))) == 0) and \
                        (post_set(p, properties.RESET_ARC) == post_set(q, properties.RESET_ARC)) and \
                        (post_set(p, properties.INHIBITOR_ARC) == post_set(q, properties.INHIBITOR_ARC)) and \
                        (len(pre_set(t, properties.RESET_ARC)) == 0 and len(
                            pre_set(t, properties.INHIBITOR_ARC)) == 0):
                    # remove place p and transition t
                    remove_transition(net, t)
                    for source in pre_set(p):
                        add_arc_from_to(source, q, net)
                    remove_place(net, p)
                    if p in im:
                        del im[p]
                        im[q] = 1
                    cont = True
                    break

    return net, im, fm


def apply_fpt_rule(net):
    """
    Apply the Fusion of Parallel Transitions (FPT) rule

    Parameters
    --------------
    net
        Reset Inhibitor net
    """
    cont = True
    while cont:
        cont = False
        for V in power_set([transition for transition in net.transitions if transition.label == None], 2):
            condition = True
            for x, y in itertools.product(V, V):
                if x != y:
                    if not ((pre_set(x) == pre_set(y)) and \
                            (post_set(x) == post_set(y)) and \
                            (pre_set(x, properties.RESET_ARC) == pre_set(y, properties.RESET_ARC)) and \
                            (pre_set(x, properties.INHIBITOR_ARC) == pre_set(y, properties.INHIBITOR_ARC))):
                        condition = False
                        break
            # V is a valid candidate
            if condition:
                # remove transitions except the first one
                for t in V[1:]:
                    remove_transition(net, t)
                cont = True
                break
    return net


def apply_fpp_rule(net, im=None):
    """
    Apply the Fusion of Parallel Places (FPP) rule

    Parameters
    --------------
    net
        Reset Inhibitor net
    """
    if im is None:
        im = {}
    cont = True
    while cont:
        cont = False
        for Q in power_set(net.places, 2):
            condition = True
            for x, y in itertools.product(Q, Q):
                if x != y:
                    if not ((pre_set(x) == pre_set(y)) and \
                            (post_set(x) == post_set(y)) and \
                            (post_set(x, properties.RESET_ARC) == post_set(y, properties.RESET_ARC)) and \
                            (post_set(x, properties.INHIBITOR_ARC) == post_set(y, properties.INHIBITOR_ARC))):
                        condition = False
                        break

            for x in Q:
                if x in im:
                    for y in Q:
                        if y in im and im[x] > im[y]:
                            if not (len(post_set(x, properties.INHIBITOR_ARC)) == 0):
                                condition = False
                                break
                    else:
                        continue
                    break
            # Q is a valid candidate
            if condition:
                # remove places except the first one
                for p in Q[1:]:
                    remove_place(net, p)
                cont = True
                break
    return net


def apply_elt_rule(net):
    """
    Apply the Elimination of Self-Loop Transitions (ELT) rule

    Parameters
    --------------
    net
        Reset Inhibitor net
    """
    cont = True
    while cont:
        cont = False
        for p, t in itertools.product(net.places, [t for t in net.transitions if t.label == None]):
            if (len(list(t.in_arcs)) == 1 and list(t.in_arcs)[0].source == p) and \
                    (len(list(t.out_arcs)) == 1 and list(t.out_arcs)[0].target == p) and \
                    (len(list(p.in_arcs)) >= 2) and \
                    (len(pre_set(t, properties.RESET_ARC)) == 0 and len(pre_set(t, properties.INHIBITOR_ARC)) == 0):
                remove_transition(net, t)
                cont = True
                break

    return net


def apply_elp_rule(net, im=None):
    """
    Apply the Elimination of Self-Loop Places (ELP) rule

    Parameters
    --------------
    net
        Reset Inhibitor net
    """
    if im is None:
        im = {}
    cont = True
    while cont:
        cont = False
        for p in [place for place in net.places]:
            if (set([arc.target for arc in p.out_arcs]).issubset(set([arc.source for arc in p.in_arcs]))) and \
                    (p in im and im[p] >= 1) and \
                    (post_set(p, properties.RESET_ARC).union(set([arc.target for arc in p.out_arcs])) == set(
                        [arc.source for arc in p.in_arcs])) and \
                    (len(post_set(p, properties.INHIBITOR_ARC)) == 0):
                remove_place(net, p)
                cont = True
                break

    return net


def apply_a_rule(net):
    """
    Apply the Abstraction (A) rule

    Parameters
    --------------
    net
        Reset Inhibitor net
    """
    cont = True
    while cont:
        cont = False
        for Q, U in itertools.product(power_set(net.places, 1), power_set(net.transitions, 1)):
            for s, t in itertools.product([s for s in net.places if s not in Q],
                                          [t for t in net.transitions if (t not in U) and (t.label == None)]):
                if ((pre_set(t) == {s}) and \
                    (post_set(s) == {t}) and \
                    (pre_set(s) == set(U)) and \
                    (post_set(t) == set(Q)) and \
                    (len(set(itertools.product(pre_set(s), post_set(t))).intersection(
                        set([(arc.source, arc.target) for arc in net.arcs if
                             get_arc_type(arc) is None])))) == 0) and \
                        (len(pre_set(t, properties.RESET_ARC)) == 0) and \
                        (len(pre_set(t, properties.INHIBITOR_ARC)) == 0):

                    # check conditions on Q
                    condition = True
                    for q in Q:
                        if not ((post_set(s, properties.RESET_ARC) == post_set(q, properties.RESET_ARC)) and \
                                (post_set(s, properties.INHIBITOR_ARC) == post_set(q, properties.INHIBITOR_ARC))):
                            condition = False
                            break
                    # Q is a valid candidate
                    if condition:
                        for u in U:
                            for q in Q:
                                add_arc_from_to(u, q, net)
                        remove_place(net, s)
                        remove_transition(net, t)
                        cont = True
                        break
    return net


def apply_r_rule(net):
    """
    Apply the Reset Reduction (R) rule

    Parameters
    --------------
    net
        Reset Inhibitor net
    """
    cont = True
    while cont:
        cont = False
        for p, t in itertools.product(net.places, net.transitions):
            if p in pre_set(t, properties.RESET_ARC).intersection(pre_set(t, properties.INHIBITOR_ARC)):
                for arc in [arc for arc in net.arcs]:
                    if arc.source == p and arc.target == t and arc.arc_type == properties.RESET_ARC:
                        remove_arc(net, arc)
                cont = True
                break

    return net


def power_set(iterable, min=0):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(min, len(s) + 1))


def apply_reset_inhibitor_net_reduction(net, im=None, fm=None):
    """
    Apply a thorough reduction to the Reset Inhibitor net

    Parameters
    --------------
    net
        Reset Inhibitor net
    """
    if im is None:
        im = {}
    if fm is None:
        fm = {}
    apply_fst_rule(net)
    apply_fsp_rule(net, im, fm)
    # (FPT) rule is exponential to model size
    # apply_fpt_rule(net)
    # (FPP) rule is exponential to model size
    # apply_fpp_rule(net, im)
    apply_elt_rule(net)
    apply_elp_rule(net, im)
    # (A) rule is exponential to model size
    # apply_a_rule(net)
    apply_r_rule(net)
    return net, im, fm

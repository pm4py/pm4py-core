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
import datetime
import itertools
import uuid
from copy import deepcopy
from enum import Enum

from pm4py.objects.petri_net.utils import petri_utils as pn_util
from pm4py.objects.petri_net.obj import PetriNet
from pm4py.objects.process_tree import obj as pt_operator
from pm4py.objects.process_tree.utils import generic as pt_util
from pm4py.objects.process_tree.utils.generic import tree_sort
from pm4py.util import exec_utils

TRANSITION_PREFIX = str(uuid.uuid4())


class Parameters(Enum):
    DEBUG = "debug"
    FOLD = "fold"


def generate_label_for_transition(t):
    return 'tau' if t.label is None else '\'' + t.label + '\'' if not t.name.startswith(
        TRANSITION_PREFIX) else t.label


def generate_new_binary_transition(t1, t2, operator, net):
    t = PetriNet.Transition(TRANSITION_PREFIX + str(datetime.datetime.now()))
    t.label = str(operator) + '(' + generate_label_for_transition(
        t1) + ', ' + generate_label_for_transition(t2) + ')'
    return t


def loop_requirement(t1, t2):
    if t1 == t2:
        return False
    for p in pn_util.pre_set(t2):
        if len(pn_util.pre_set(p)) != 1:  # check that the preset of the t2 preset has one entry
            return False
        if t1 not in pn_util.pre_set(p):  # check that t1 is the unique way to mark the preset of t2
            return False
    for p in pn_util.post_set(t2):
        if len(pn_util.post_set(p)) != 1:
            return False
        if t1 not in pn_util.post_set(p):
            return False
    for p in pn_util.pre_set(t1):
        if len(pn_util.post_set(p)) != 1:
            return False
        if t1 not in pn_util.post_set(p):
            return False
        if t2 not in pn_util.pre_set(p):  # t2 has to enable t1!
            return False
    for p in pn_util.post_set(t1):
        if len(pn_util.pre_set(p)) != 1:  # check that the preset of the t2 preset has one entry
            return False
        if t1 not in pn_util.pre_set(p):  # check that t1 is the unique way to mark the preset of t2
            return False
        if t2 not in pn_util.post_set(p):
            return False
    return True


def binary_loop_detection(net):
    c1 = None
    c2 = None
    for t1, t2 in itertools.product(net.transitions, net.transitions):
        if loop_requirement(t1, t2):
            c1 = t1
            c2 = t2
            break
    if c1 is not None and c2 is not None:
        t = generate_new_binary_transition(c1, c2, pt_operator.Operator.LOOP, net)
        net.transitions.add(t)
        # reduce
        for a in c1.in_arcs:
            pn_util.add_arc_from_to(a.source, t, net)
        for a in c1.out_arcs:
            pn_util.add_arc_from_to(t, a.target, net)
        pn_util.remove_transition(net, c1)
        pn_util.remove_transition(net, c2)
        return net
    return None


def concurrent_requirement(t1, t2):
    if t1 == t2:  # check if transitions different
        return False
    if len(pn_util.pre_set(t1)) == 0 or len(pn_util.post_set(t1)) == 0 or len(pn_util.pre_set(t2)) == 0 or len(
            pn_util.post_set(t2)) == 0:  # not possible in WF-net, just checking...
        return False
    pre_pre = set()
    post_post = set()
    for p in pn_util.pre_set(t1):  # check if t1 is unique post of its preset
        pre_pre = set.union(pre_pre, pn_util.pre_set(p))
        if len(pn_util.post_set(p)) > 1 or t1 not in pn_util.post_set(p):
            return False
    for p in pn_util.post_set(t1):  # check if t1 is unique pre of its postset
        post_post = set.union(post_post, pn_util.post_set(p))
        if len(pn_util.pre_set(p)) > 1 or t1 not in pn_util.pre_set(p):
            return False
    for p in pn_util.pre_set(t2):  # check if t2 is unique post of its preset
        pre_pre = set.union(pre_pre, pn_util.pre_set(p))
        if len(pn_util.post_set(p)) > 1 or t2 not in pn_util.post_set(p):
            return False
    for p in pn_util.post_set(t2):  # check if t2 is unique pre of its postset
        post_post = set.union(post_post, pn_util.post_set(p))
        if len(pn_util.pre_set(p)) > 1 or t2 not in pn_util.pre_set(p):
            return False
    for p in set.union(pn_util.pre_set(t1), pn_util.pre_set(t2)):  # check if presets synchronize
        for t in pre_pre:
            if t not in pn_util.pre_set(p):
                return False
    for p in set.union(pn_util.post_set(t1), pn_util.post_set(t2)):  # check if postsets synchronize
        for t in post_post:
            if t not in pn_util.post_set(p):
                return False
    return True


def binary_concurrency_detection(net):
    c1 = None
    c2 = None
    for t1, t2 in itertools.product(net.transitions, net.transitions):
        if concurrent_requirement(t1, t2):
            c1 = t1
            c2 = t2
            break
    if c1 is not None and c2 is not None:
        t = generate_new_binary_transition(c1, c2, pt_operator.Operator.PARALLEL, net)
        net.transitions.add(t)
        # reduce
        for a in c1.in_arcs:
            pn_util.add_arc_from_to(a.source, t, net)
        for a in c1.out_arcs:
            pn_util.add_arc_from_to(t, a.target, net)
        for a in c2.in_arcs:
            pn_util.add_arc_from_to(a.source, t, net)
        for a in c2.out_arcs:
            pn_util.add_arc_from_to(t, a.target, net)
        pn_util.remove_transition(net, c1)
        pn_util.remove_transition(net, c2)
        return net
    return None


def choice_requirement(t1, t2):
    return t1 != t2 and pn_util.pre_set(t1) == pn_util.pre_set(t2) and pn_util.post_set(t1) == pn_util.post_set(
        t2) and len(pn_util.pre_set(t1)) > 0 and len(
        pn_util.post_set(t1)) > 0


def binary_choice_detection(net):
    c1 = None
    c2 = None
    for t1, t2 in itertools.product(net.transitions, net.transitions):
        if choice_requirement(t1, t2):
            c1 = t1
            c2 = t2
            break
    if c1 is not None and c2 is not None:
        t = generate_new_binary_transition(c1, c2, pt_operator.Operator.XOR, net)
        net.transitions.add(t)
        for a in c1.in_arcs:
            pn_util.add_arc_from_to(a.source, t, net)
        for a in c2.out_arcs:
            pn_util.add_arc_from_to(t, a.target, net)
        pn_util.remove_transition(net, c1)
        pn_util.remove_transition(net, c2)
        return net
    return None


def sequence_requirement(t1, t2):
    if t1 == t2:
        return False
    if len(pn_util.pre_set(t2)) == 0:
        return False
    for p in pn_util.post_set(t1):
        if len(pn_util.pre_set(p)) != 1 or len(pn_util.post_set(p)) != 1:
            return False
        if t1 not in pn_util.pre_set(p):
            return False
        if t2 not in pn_util.post_set(p):
            return False
    for p in pn_util.pre_set(t2):
        if len(pn_util.pre_set(p)) != 1 or len(pn_util.post_set(p)) != 1:
            return False
        if t1 not in pn_util.pre_set(p):
            return False
        if t2 not in pn_util.post_set(p):  # redundant check, just to be sure...
            return False
    return True


def binary_sequence_detection(net):
    c1 = None
    c2 = None
    for t1, t2 in itertools.product(net.transitions, net.transitions):
        if sequence_requirement(t1, t2):
            c1 = t1
            c2 = t2
            break
    if c1 is not None and c2 is not None:
        t = generate_new_binary_transition(c1, c2, pt_operator.Operator.SEQUENCE, net)
        net.transitions.add(t)
        for a in c1.in_arcs:
            pn_util.add_arc_from_to(a.source, t, net)
        for a in c2.out_arcs:
            pn_util.add_arc_from_to(t, a.target, net)
        for p in pn_util.post_set(c1):
            pn_util.remove_place(net, p)
        pn_util.remove_transition(net, c1)
        pn_util.remove_transition(net, c2)
        return net
    return None


def group_blocks_in_net(net, parameters=None):
    """
    Groups the blocks in the Petri net

    Parameters
    --------------
    net
        Petri net
    parameters
        Parameters of the algorithm

    Returns
    --------------
    grouped_net
        Petri net (blocks are grouped according to the algorithm)
    """
    if parameters is None:
        parameters = {}

    from pm4py.algo.analysis.workflow_net import algorithm as wf_eval

    if not wf_eval.apply(net):
        raise ValueError('The Petri net provided is not a WF-net')

    net = deepcopy(net)

    while len(net.transitions) > 1:
        if binary_choice_detection(net) is not None:
            continue
        elif binary_sequence_detection(net) is not None:
            continue
        elif binary_concurrency_detection(net) is not None:
            continue
        elif binary_loop_detection(net) is not None:
            continue
        else:
            break

    return net


def apply(net, im, fm, parameters=None):
    """
    Transforms a WF-net to a process tree

    Parameters
    -------------
    net
        Petri net
    im
        Initial marking
    fm
        Final marking

    Returns
    -------------
    tree
        Process tree
    """
    if parameters is None:
        parameters = {}

    debug = exec_utils.get_param_value(Parameters.DEBUG, parameters, False)
    fold = exec_utils.get_param_value(Parameters.FOLD, parameters, True)

    grouped_net = group_blocks_in_net(net, parameters=parameters)

    if len(grouped_net.transitions) == 1:
        pt_str = list(grouped_net.transitions)[0].label
        pt = pt_operator.ProcessTree(operator=None, label=pt_str)
        ret = pt_util.fold(pt) if fold else pt
        tree_sort(ret)
        return ret
    else:
        if debug:
            from pm4py.visualization.petri_net import visualizer as pn_viz
            pn_viz.view(pn_viz.apply(grouped_net, parameters={"format": "svg"}))
        raise ValueError('Parsing of WF-net Failed')

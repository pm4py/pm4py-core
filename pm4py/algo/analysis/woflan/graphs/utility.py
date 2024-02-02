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
import numpy as np
from pm4py.util import nx_utils


def compute_incidence_matrix(net):
    """
    Given a Petri Net, the incidence matrix is computed. An incidence matrix has n rows (places) and m columns
    (transitions).
    :param net: Petri Net object
    :return: Incidence matrix
    """
    n = len(net.transitions)
    m = len(net.places)
    C = np.zeros((m, n))
    i = 0
    transition_list = sorted(list(net.transitions), key=lambda x: x.name)
    place_list = sorted(list(net.places), key=lambda x: x.name)
    while i < n:
        t = transition_list[i]
        for in_arc in t.in_arcs:
            # arcs that go to transition
            C[place_list.index(in_arc.source), i] -= (1*in_arc.weight)
        for out_arc in t.out_arcs:
            # arcs that lead away from transition
            C[place_list.index(out_arc.target), i] += (1*out_arc.weight)
        i += 1
    return C


def split_incidence_matrix(matrix, net):
    """
    We split the incidence matrix columnwise to get the firing information for each transition
    :param matrix: incidence matrix
    :param net: Petri Net
    :return: Dictionary, whereby the key is an np array that contains the firing information and the value is the name
    of the transition
    """
    transition_dict = {}
    lst_transitions = sorted(list(net.transitions), key=lambda x: x.name)
    i = 0
    while i < len(net.transitions):
        transition_dict[lst_transitions[i]] = np.hsplit(np.transpose(matrix), 1)[0][i]
        i += 1
    return transition_dict

def compute_firing_requirement(net):
    place_list=sorted(list(net.places), key=lambda x: x.name)
    transition_dict={}
    for transition in net.transitions:
        temp_array=np.zeros(len(place_list))
        for arc in transition.in_arcs:
            temp_array[place_list.index(arc.source)] -=1*arc.weight
        transition_dict[transition]=temp_array
    return transition_dict

def enabled_markings(firing_dict, req_dict,marking):
    enabled_transitions = []
    for transition, requirment in req_dict.items():
        if all(np.greater_equal(marking, requirment.copy()*-1)):
            enabled_transitions.append(transition)
    new_markings = []
    for transition in enabled_transitions:
        new_marking = marking + firing_dict[transition]
        new_markings.append((new_marking, transition))
    return new_markings

def convert_marking(net, marking, original_net=None):
    """
    Takes an marking as input and converts it into an Numpy Array
    :param net: PM4Py Petri Net object
    :param marking: Marking that should be converted
    :param original_net: PM4Py Petri Net object without short-circuited transition
    :return: Numpy array representation
    """
    #marking_list=list(el.name for el in marking.keys())
    #
    marking_list = sorted([el.name for el in marking.keys()])
    place_list = sorted(list(el.name for el in net.places))

    mark = np.zeros(len(place_list))
    for index, value in enumerate(mark):
        if place_list[index] in marking_list:
            #TODO: Is setting the value to 1 ok in this case?
            mark[index]=1
    return mark

def check_for_dead_tasks(net, graph):
    """
    We compute a list of dead tasks. A dead task is a task which does not appear in the Minimal Coverability Graph
    :param net: Petri Net representation of PM4Py
    :param graph: Minimal coverability graph. NetworkX MultiDiGraph object.
    :return: list of dead tasks
    """
    tasks=[]
    lst_transitions = sorted(list(net.transitions), key=lambda x: x.name)
    for transition in lst_transitions:
        if transition.label != None:
            tasks.append(transition)
    for node,targets in graph.edges()._adjdict.items():
        for target_node,activties in targets.items():
            for option,activity in activties.items():
                if activity['transition'] in tasks:
                    tasks.remove(activity['transition'])
    return tasks

def check_for_improper_conditions(mcg):
    """
    An improper condition is a state in the minimum-coverability graph with an possible infinite amount of tokens
    :param mcg: networkx object (minimal coverability graph)
    :return: True, if there are no improper conditions; false otherwise
    """
    improper_states=[]
    for node in mcg.nodes:
        if np.inf in mcg.nodes[node]['marking']:
            improper_states.append(node)
    return improper_states

def check_for_substates(mcg):
    """
    Checks if a substate exists in a given mcg
    :param mcg: Minimal coverability graph (networkx object)
    :return: True, if there exist no substate; False otherwise
    """
    for node in mcg.nodes:
        reachable_states = nx_utils.descendants(mcg, node)
        for state in reachable_states:
            if all(np.less(mcg.nodes[node]['marking'],mcg.nodes[state]['marking'])):
                return False
    return True

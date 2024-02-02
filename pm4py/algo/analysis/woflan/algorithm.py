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
from pm4py.util import exec_utils, nx_utils
from enum import Enum
from pm4py.objects.petri_net.utils import petri_utils
import copy
import numpy as np

# Importing for place invariants related stuff (s-components, uniform and weighted place invariants)
from pm4py.algo.analysis.woflan.place_invariants.place_invariants import compute_place_invariants
from pm4py.algo.analysis.woflan.place_invariants.utility import transform_basis
from pm4py.algo.analysis.woflan.place_invariants.s_component import compute_s_components
from pm4py.algo.analysis.woflan.place_invariants.s_component import compute_uncovered_places_in_component
from pm4py.algo.analysis.woflan.place_invariants.utility import \
    compute_uncovered_places as compute_uncovered_place_in_invariants

# Importing to discover not-well handled pairs
from pm4py.algo.analysis.woflan.not_well_handled_pairs.not_well_handled_pairs import \
    apply as compute_not_well_handled_pairs

# Minimal Coverability Graph
from pm4py.algo.analysis.woflan.graphs.minimal_coverability_graph.minimal_coverability_graph import \
    apply as minimal_coverability_graph
from pm4py.algo.analysis.woflan.graphs.utility import check_for_dead_tasks
from pm4py.algo.analysis.woflan.graphs.utility import check_for_improper_conditions
from pm4py.algo.analysis.woflan.graphs.utility import check_for_substates
from pm4py.algo.analysis.woflan.graphs.utility import convert_marking

# Restricted coverability graph
from pm4py.algo.analysis.woflan.graphs.restricted_coverability_graph.restricted_coverability_graph import \
    construct_tree as restricted_coverability_tree

# reachability Graph Creation
from pm4py.algo.analysis.woflan.graphs.reachability_graph.reachability_graph import apply as reachability_graph

from typing import Optional, Dict, Any, Union
from pm4py.objects.petri_net.obj import PetriNet, Marking


class Parameters(Enum):
    RETURN_ASAP_WHEN_NOT_SOUND = "return_asap_when_not_sound"
    PRINT_DIAGNOSTICS = "print_diagnostics"
    RETURN_DIAGNOSTICS = "return_diagnostics"


class Outputs(Enum):
    S_C_NET = "s_c_net"
    PLACE_INVARIANTS = "place_invariants"
    UNIFORM_PLACE_INVARIANTS = "uniform_place_invariants"
    S_COMPONENTS = "s_components"
    UNCOVERED_PLACES_S_COMPONENT = "uncovered_places_s_component"
    NOT_WELL_HANDLED_PAIRS = "not_well_handled_pairs"
    LEFT = "left"
    UNCOVERED_PLACES_UNIFORM = "uncovered_places_uniform"
    WEIGHTED_PLACE_INVARIANTS = "weighted_place_invariants"
    UNCOVERED_PLACES_WEIGHTED = "uncovered_places_weighted"
    MCG = "mcg"
    DEAD_TASKS = "dead_tasks"
    R_G_S_C = "r_g_s_c"
    R_G = "r_g"
    LOCKING_SCENARIOS = "locking_scenarios"
    RESTRICTED_COVERABILITY_TREE = "restricted_coverability_tree"
    DIAGNOSTIC_MESSAGES = "diagnostic_messages"


class woflan:
    def __init__(self, net, initial_marking, final_marking, print_diagnostics=False):
        self.net = net
        self.initial_marking = initial_marking
        self.final_marking = final_marking
        self.print_diagnostics = print_diagnostics
        self.s_c_net = None
        self.place_invariants = None
        self.uniform_place_invariants = None
        self.s_components = None
        self.uncovered_places_s_component = None
        self.not_well_handled_pairs = None
        self.left = None
        self.uncovered_places_uniform = None
        self.weighted_place_invariants = None
        self.uncovered_places_weighted = None
        self.mcg = None
        self.dead_tasks = None
        self.r_g_s_c = None
        self.r_g = None
        self.locking_scenarios = None
        self.restricted_coverability_tree = None
        self.diagnostic_messages = list()

    def set_s_c_net(self, s_c_net):
        self.s_c_net = s_c_net

    def set_place_invariants(self, invariants):
        self.place_invariants = invariants

    def set_uniform_place_invariants(self, invariants):
        self.uniform_place_invariants = invariants

    def set_s_components(self, s_components):
        self.s_components = s_components

    def set_uncovered_places_s_component(self, uncovered_places):
        self.uncovered_places_s_component = uncovered_places

    def set_not_well_handled_pairs(self, not_well_handled_pairs):
        self.not_well_handled_pairs = not_well_handled_pairs

    def set_left(self, left):
        self.left = left

    def set_uncovered_places_uniform(self, places):
        self.uncovered_places_uniform = places

    def set_weighted_place_invariants(self, invariants):
        self.weighted_place_invariants = invariants

    def set_uncovered_places_weighted(self, places):
        self.uncovered_places_weighted = places

    def set_mcg(self, mcg):
        self.mcg = mcg

    def set_dead_tasks(self, dead_tasks):
        self.dead_tasks = dead_tasks

    def set_r_g_s_c(self, r_g):
        self.r_g_s_c = r_g

    def set_r_g(self, r_g):
        self.r_g = r_g

    def set_locking_scenarios(self, scenarios):
        self.locking_scenarios = scenarios

    def set_restricted_coverability_tree(self, graph):
        self.restricted_coverability_tree = graph

    def get_net(self):
        return self.net

    def get_initial_marking(self):
        return self.initial_marking

    def get_final_marking(self):
        return self.final_marking

    def get_s_c_net(self):
        return self.s_c_net

    def get_place_invariants(self):
        return self.place_invariants

    def get_uniform_place_invariants(self):
        return self.uniform_place_invariants

    def get_s_components(self):
        return self.s_components

    def get_uncovered_places_s_component(self):
        return self.uncovered_places_s_component

    def get_not_well_handled_pairs(self):
        return self.not_well_handled_pairs

    def get_left(self):
        return self.left

    def get_uncovered_places_uniform(self):
        return self.uncovered_places_uniform

    def get_weighted_place_invariants(self):
        return self.weighted_place_invariants

    def get_uncovered_places_weighted(self):
        return self.uncovered_places_weighted

    def get_mcg(self):
        return self.mcg

    def get_dead_tasks(self):
        return self.dead_tasks

    def get_r_g_s_c(self):
        return self.r_g_s_c

    def get_r_g(self):
        return self.r_g

    def get_locking_scenarios(self):
        return self.locking_scenarios

    def get_restricted_coverability_tree(self):
        return self.restricted_coverability_tree

    def get_output(self):
        """
        Returns a dictionary representation of the
        entities that are calculated during WOFLAN
        """
        ret = {}
        if self.s_c_net is not None:
            ret[Outputs.S_C_NET.value] = self.s_c_net
        if self.place_invariants is not None:
            ret[Outputs.PLACE_INVARIANTS.value] = self.place_invariants
        if self.uniform_place_invariants is not None:
            ret[Outputs.UNIFORM_PLACE_INVARIANTS.value] = self.uniform_place_invariants
        if self.s_components is not None:
            ret[Outputs.S_COMPONENTS.value] = self.s_components
        if self.uncovered_places_s_component is not None:
            ret[Outputs.UNCOVERED_PLACES_S_COMPONENT.value] = self.uncovered_places_s_component
        if self.not_well_handled_pairs is not None:
            ret[Outputs.NOT_WELL_HANDLED_PAIRS.value] = self.not_well_handled_pairs
        if self.left is not None:
            ret[Outputs.LEFT.value] = self.left
        if self.uncovered_places_uniform is not None:
            ret[Outputs.UNCOVERED_PLACES_UNIFORM.value] = self.uncovered_places_uniform
        if self.weighted_place_invariants is not None:
            ret[Outputs.WEIGHTED_PLACE_INVARIANTS.value] = self.weighted_place_invariants
        if self.uncovered_places_weighted is not None:
            ret[Outputs.UNCOVERED_PLACES_WEIGHTED.value] = self.uncovered_places_weighted
        if self.mcg is not None:
            ret[Outputs.MCG.value] = self.mcg
        if self.dead_tasks is not None:
            ret[Outputs.DEAD_TASKS.value] = self.dead_tasks
        if self.r_g_s_c is not None:
            ret[Outputs.R_G_S_C.value] = self.r_g_s_c
        if self.r_g is not None:
            ret[Outputs.R_G] = self.r_g
        if self.locking_scenarios is not None:
            ret[Outputs.LOCKING_SCENARIOS] = self.locking_scenarios
        if self.restricted_coverability_tree is not None:
            ret[Outputs.RESTRICTED_COVERABILITY_TREE] = self.restricted_coverability_tree
        ret[Outputs.DIAGNOSTIC_MESSAGES] = self.diagnostic_messages
        return ret


def short_circuit_petri_net(net, print_diagnostics=False):
    """
    Fist, sink and source place are identified. Then, a transition from source to sink is added to short-circuited
    the given petri net. If there is no unique source and sink place, an error gets returned
    :param net: Petri net that is going to be short circuited
    :return:
    """
    s_c_net = copy.deepcopy(net)
    no_source_places = 0
    no_sink_places = 0
    sink = None
    source = None
    for place in s_c_net.places:
        if len(place.in_arcs) == 0:
            source = place
            no_source_places += 1
        if len(place.out_arcs) == 0:
            sink = place
            no_sink_places += 1
    if (sink is not None) and (source is not None) and no_source_places == 1 and no_sink_places == 1:
        # If there is one unique source and sink place, short circuit Petri Net is constructed
        t_1 = PetriNet.Transition("short_circuited_transition", "short_circuited_transition")
        s_c_net.transitions.add(t_1)
        # add arcs in short-circuited net
        petri_utils.add_arc_from_to(sink, t_1, s_c_net)
        petri_utils.add_arc_from_to(t_1, source, s_c_net)
        return s_c_net, []
    else:
        if sink is None:
            if print_diagnostics:
                print("There is no sink place.")
            return None, ["There is no sink place."]
        elif source is None:
            if print_diagnostics:
                print("There is no source place.")
            return None, ["There is no source place."]
        elif no_source_places > 1:
            if print_diagnostics:
                print("There is more than one source place.")
            return None, ["There is more than one source place."]
        elif no_sink_places > 1:
            if print_diagnostics:
                print("There is more than one sink place.")
            return None, ["There is more than one sink place."]


def step_1(woflan_object, return_asap_when_unsound=False):
    """
    In the first step, we check if the input is given correct. We check if net is an PM4Py Petri Net representation
    and if the exist a correct entry for the initial and final marking.
    :param woflan_object: Object that contains all necessary information
    :return: Proceed with step 2 if ok; else False
    """

    def check_if_marking_in_net(marking, net):
        """
        Checks if the marked place exists in the Petri Net and if there is only one i_m and f_m
        :param marking: Marking of Petri Net
        :param net: PM4Py representation of Petri Net
        :return: Boolean. True if marking can exists; False if not.
        """
        for place in marking:
            if place in net.places:
                return True
        return False

    if isinstance(woflan_object.get_net(), PetriNet):
        if len(woflan_object.get_initial_marking()) != 1 or len(woflan_object.get_final_marking()) != 1:
            woflan_object.diagnostic_messages.append('There is more than one initial or final marking.')
            if woflan_object.print_diagnostics:
                print('There is more than one initial or final marking.')
            return False
        if check_if_marking_in_net(woflan_object.get_initial_marking(), woflan_object.get_net()):
            if check_if_marking_in_net(woflan_object.get_final_marking(), woflan_object.get_net()):
                woflan_object.diagnostic_messages.append('Input is ok.')
                if woflan_object.print_diagnostics:
                    print('Input is ok.')
                return step_2(woflan_object, return_asap_when_unsound=return_asap_when_unsound)
    woflan_object.diagnostic_messages.append('The Petri Net is not PM4Py Petri Net represenatation.')
    if woflan_object.print_diagnostics:
        print('The Petri Net is not PM4Py Petri Net represenatation.')
    return False


def step_2(woflan_object, return_asap_when_unsound=False):
    """
    This method checks if a given Petri net is a workflow net. First, the Petri Net gets short-circuited
    (connect start and end place with a tau-transition. Second, the Petri Net gets converted into a networkx graph.
    Finally, it is tested if the resulting graph is a strongly connected component.
    :param woflan_object: Woflan objet containing all information
    :return: Bool=True if net is a WF-Net
    """

    def transform_petri_net_into_regular_graph(still_need_to_discover):
        """
        Ths method transforms a list of places and transitions into a networkx graph
        :param still_need_to_discover: set of places and transition that are not fully added to graph
        :return:
        """
        G = nx_utils.DiGraph()
        while len(still_need_to_discover) > 0:
            element = still_need_to_discover.pop()
            G.add_node(element.name)
            for in_arc in element.in_arcs:
                G.add_node(in_arc.source.name)
                G.add_edge(in_arc.source.name, element.name)
            for out_arc in element.out_arcs:
                G.add_node(out_arc.target.name)
                G.add_edge(element.name, out_arc.target.name)
        return G

    s_c_net, diagnostic_messages = short_circuit_petri_net(woflan_object.get_net(),
                                                           print_diagnostics=woflan_object.print_diagnostics)
    woflan_object.set_s_c_net(s_c_net)
    woflan_object.diagnostic_messages += diagnostic_messages
    if woflan_object.get_s_c_net() == None:
        return False
    to_discover = woflan_object.get_s_c_net().places | woflan_object.get_s_c_net().transitions
    graph = transform_petri_net_into_regular_graph(to_discover)
    if not nx_utils.is_strongly_connected(graph):
        woflan_object.diagnostic_messages.append('Petri Net is a not a worflow net.')
        if woflan_object.print_diagnostics:
            print('Petri Net is a not a worflow net.')
        return False
    else:
        woflan_object.diagnostic_messages.append('Petri Net is a workflow net.')
        if woflan_object.print_diagnostics:
            print('Petri Net is a workflow net.')
        return step_3(woflan_object, return_asap_when_unsound=return_asap_when_unsound)


def step_3(woflan_object, return_asap_when_unsound=False):
    woflan_object.set_place_invariants(compute_place_invariants(woflan_object.get_s_c_net()))
    woflan_object.set_uniform_place_invariants(transform_basis(woflan_object.get_place_invariants(), style='uniform'))
    woflan_object.set_s_components(
        compute_s_components(woflan_object.get_s_c_net(), woflan_object.get_uniform_place_invariants()))
    woflan_object.set_uncovered_places_s_component(
        compute_uncovered_places_in_component(woflan_object.get_s_components(), woflan_object.get_s_c_net()))
    if len(woflan_object.get_uncovered_places_s_component()) == 0:
        woflan_object.set_left(True)
        woflan_object.diagnostic_messages.append('Every place is covered by s-components.')
        if woflan_object.print_diagnostics:
            print('Every place is covered by s-components.')
        return step_10(woflan_object, return_asap_when_unsound=return_asap_when_unsound)
    else:
        woflan_object.diagnostic_messages.append('The following places are not covered by an s-component: {}.'.format(
                woflan_object.get_uncovered_places_s_component()))
        if woflan_object.print_diagnostics:
            print('The following places are not covered by an s-component: {}.'.format(
                woflan_object.get_uncovered_places_s_component()))
        if return_asap_when_unsound:
            return False
        return step_4(woflan_object, return_asap_when_unsound=return_asap_when_unsound)


def step_4(woflan_object, return_asap_when_unsound=False):
    woflan_object.set_not_well_handled_pairs(compute_not_well_handled_pairs(woflan_object.get_s_c_net()))
    if len(woflan_object.get_not_well_handled_pairs()) == 0:
        woflan_object.diagnostic_messages.append('Petri Net is unsound.')
        if woflan_object.print_diagnostics:
            print('Petri Net is unsound.')
        woflan_object.set_left(False)
        if return_asap_when_unsound:
            return False
        return step_5(woflan_object, return_asap_when_unsound=return_asap_when_unsound)
    else:
        woflan_object.diagnostic_messages.append('Not well-handled pairs are: {}.'.format(
            woflan_object.get_not_well_handled_pairs()))
        if woflan_object.print_diagnostics:
            print('Not well-handled pairs are: {}.'.format(woflan_object.get_not_well_handled_pairs()))
        woflan_object.set_left(True)
        return step_5(woflan_object, return_asap_when_unsound=return_asap_when_unsound)


def step_5(woflan_object, return_asap_when_unsound=False):
    woflan_object.set_uncovered_places_uniform(
        compute_uncovered_place_in_invariants(woflan_object.get_uniform_place_invariants(),
                                              woflan_object.get_s_c_net()))
    if len(woflan_object.get_uncovered_places_uniform()) == 0:
        woflan_object.diagnostic_messages.append('There are no uncovered places in uniform invariants.')
        if woflan_object.print_diagnostics:
            print('There are no uncovered places in uniform invariants.')
        return step_10(woflan_object, return_asap_when_unsound=return_asap_when_unsound)
    else:
        woflan_object.diagnostic_messages.append('The following places are uncovered in uniform invariants: {}'.format(
            woflan_object.get_uncovered_places_uniform()))
        if woflan_object.print_diagnostics:
            print('The following places are uncovered in uniform invariants: {}'.format(
                woflan_object.get_uncovered_places_uniform()))
        return step_6(woflan_object, return_asap_when_unsound=return_asap_when_unsound)


def step_6(woflan_object, return_asap_when_unsound=False):
    woflan_object.set_weighted_place_invariants(transform_basis(woflan_object.get_place_invariants(), style='weighted'))
    woflan_object.set_uncovered_places_weighted(
        compute_uncovered_place_in_invariants(woflan_object.get_weighted_place_invariants(),
                                              woflan_object.get_s_c_net()))
    if len(woflan_object.get_uncovered_places_weighted()) == 0:
        woflan_object.diagnostic_messages.append('There are no uncovered places in weighted invariants.')
        if woflan_object.print_diagnostics:
            print('There are no uncovered places in weighted invariants.')
        return step_10(woflan_object, return_asap_when_unsound=return_asap_when_unsound)
    else:
        woflan_object.diagnostic_messages.append('The following places are uncovered in weighted invariants: {}'.format(
            woflan_object.get_uncovered_places_weighted()))
        if woflan_object.print_diagnostics:
            print('The following places are uncovered in weighted invariants: {}'.format(
                woflan_object.get_uncovered_places_weighted()))
        return step_7(woflan_object, return_asap_when_unsound=return_asap_when_unsound)


def step_7(woflan_object, return_asap_when_unsound=False):
    woflan_object.set_mcg(minimal_coverability_graph(woflan_object.get_s_c_net(), woflan_object.get_initial_marking(),
                                                     woflan_object.get_net()))
    if len(check_for_improper_conditions(woflan_object.get_mcg())) == 0:
        woflan_object.diagnostic_messages.append('No improper coditions.')
        if woflan_object.print_diagnostics:
            print('No improper conditions.')
        if woflan_object.get_left == True:
            return step_8(woflan_object, return_asap_when_unsound=return_asap_when_unsound)
        else:
            return step_10(woflan_object, return_asap_when_unsound=return_asap_when_unsound)
    else:
        woflan_object.diagnostic_messages.append('Improper WPD. The following are the improper conditions: {}.'.format(
            check_for_improper_conditions(woflan_object.get_mcg())))
        if woflan_object.print_diagnostics:
            print('Improper WPD. The following are the improper conditions: {}.'.format(
                check_for_improper_conditions(woflan_object.get_mcg())))
        if return_asap_when_unsound:
            return False
        return step_9(woflan_object, return_asap_when_unsound=return_asap_when_unsound)


def step_8(woflan_object, return_asap_when_unsound=False):
    if check_for_substates(woflan_object.get_mcg()):
        return step_10(woflan_object, return_asap_when_unsound=return_asap_when_unsound)
    else:
        return step_10(woflan_object, return_asap_when_unsound=return_asap_when_unsound)


def step_9(woflan_object, return_asap_when_unsound=False):
    woflan_object.diagnostic_messages.append('The following sequences are unbounded: {}'.format(
        compute_unbounded_sequences(woflan_object)))
    if woflan_object.print_diagnostics:
        print('The following sequences are unbounded: {}'.format(compute_unbounded_sequences(woflan_object)))
    return False


def step_10(woflan_object, return_asap_when_unsound=False):
    if woflan_object.get_mcg() == None:
        woflan_object.set_mcg(
            minimal_coverability_graph(woflan_object.get_s_c_net(), woflan_object.get_initial_marking(),
                                       woflan_object.get_net()))
    woflan_object.set_dead_tasks(check_for_dead_tasks(woflan_object.get_s_c_net(), woflan_object.get_mcg()))
    if len(woflan_object.get_dead_tasks()) == 0:
        woflan_object.diagnostic_messages.append('There are no dead tasks.')
        if woflan_object.print_diagnostics:
            print('There are no dead tasks.')
        if woflan_object.get_left() == True:
            return step_11(woflan_object, return_asap_when_unsound=return_asap_when_unsound)
        else:
            if return_asap_when_unsound:
                return False
            return step_12(woflan_object, return_asap_when_unsound=return_asap_when_unsound)
    else:
        woflan_object.diagnostic_messages.append('The following tasks are dead: {}'.format(
            woflan_object.get_dead_tasks()))
        if woflan_object.print_diagnostics:
            print('The following tasks are dead: {}'.format(woflan_object.get_dead_tasks()))
        return False


def step_11(woflan_object, return_asap_when_unsound=False):
    woflan_object.set_r_g_s_c(
        reachability_graph(woflan_object.get_s_c_net(), woflan_object.get_initial_marking(), woflan_object.get_net()))
    if nx_utils.is_strongly_connected(woflan_object.get_r_g_s_c()):
        woflan_object.diagnostic_messages.append('All tasks are live.')
        if woflan_object.print_diagnostics:
            print('All tasks are live.')
        return True
    else:
        if return_asap_when_unsound:
            return False
        return step_13(woflan_object, return_asap_when_unsound=return_asap_when_unsound)


def step_12(woflan_object, return_asap_when_unsound=False):
    woflan_object.set_r_g_s_c(
        reachability_graph(woflan_object.get_s_c_net(), woflan_object.get_initial_marking(), woflan_object.get_net()))
    woflan_object.diagnostic_messages.append('There are non-live tasks.')
    if woflan_object.print_diagnostics:
        print('There are non-live tasks.')
    if return_asap_when_unsound:
        return False
    return step_13(woflan_object, return_asap_when_unsound=return_asap_when_unsound)


def step_13(woflan_object, return_asap_when_unsound=False):
    woflan_object.set_locking_scenarios(compute_non_live_sequences(woflan_object))
    woflan_object.diagnostic_messages.append('The following sequences lead to deadlocks: {}.'.format(
        woflan_object.get_locking_scenarios()))
    if woflan_object.print_diagnostics:
        print('The following sequences lead to deadlocks: {}.'.format(woflan_object.get_locking_scenarios()))
    return False


def apply(net: PetriNet, i_m: Marking, f_m: Marking, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Union[bool, Any]:
    """
    Apply the Woflan Soundness check. Trough this process, different steps are executed.
    :param net: Petri Net representation of PM4Py
    :param i_m: initial marking of given Net. Marking object of PM4Py
    :param f_m: final marking of given Net. Marking object of PM4Py
    :return: True, if net is sound; False otherwise.
    """
    if parameters is None:
        parameters = {}
    return_asap_when_unsound = exec_utils.get_param_value(Parameters.RETURN_ASAP_WHEN_NOT_SOUND, parameters, False)
    print_diagnostics = exec_utils.get_param_value(Parameters.PRINT_DIAGNOSTICS, parameters, True)
    return_diagnostics = exec_utils.get_param_value(Parameters.RETURN_DIAGNOSTICS, parameters, False)

    woflan_object = woflan(net, i_m, f_m, print_diagnostics=print_diagnostics)
    step_1_res = step_1(woflan_object, return_asap_when_unsound=return_asap_when_unsound)

    if return_diagnostics:
        return step_1_res, woflan_object.get_output()

    return step_1_res


def compute_non_live_sequences(woflan_object):
    """
    We want to compute the sequences of transitions which lead to deadlocks.
    To do this, we first compute a reachbility graph (possible, since we know that the Petri Net is bounded) and then we
    convert it to a spanning tree. Afterwards, we compute the paths which lead to nodes from which the final marking cannot
    be reached. Note: We are searching for the shortest sequence. After the first red node, all successors are also red.
    Therefore, we do not have to consider them.
    :param woflan_object: Object that contains the necessary information
    :return: List of sequence of transitions, each sequence is a list
    """
    woflan_object.set_r_g(reachability_graph(woflan_object.get_net(), woflan_object.get_initial_marking()))
    f_m = convert_marking(woflan_object.get_net(), woflan_object.get_final_marking())
    sucessfull_terminate_state = None
    for node in woflan_object.get_r_g().nodes:
        if all(np.equal(woflan_object.get_r_g().nodes[node]['marking'], f_m)):
            sucessfull_terminate_state = node
            break
    # red nodes are those from which the final marking is not reachable
    red_nodes = []
    for node in woflan_object.get_r_g().nodes:
        if not nx_utils.has_path(woflan_object.get_r_g(), node, sucessfull_terminate_state):
            red_nodes.append(node)
    # Compute directed spanning tree
    spanning_tree = nx_utils.Edmonds(woflan_object.get_r_g()).find_optimum()
    queue = set()
    paths = {}
    # root node
    queue.add(0)
    paths[0] = []
    processed_nodes = set()
    red_paths = []
    while len(queue) > 0:
        v = queue.pop()
        for node in spanning_tree.neighbors(v):
            if node not in paths and node not in processed_nodes:
                paths[node] = paths[v].copy()
                # we can use directly 0 here, since we are working on a spanning tree and there should be no more edges to a node
                paths[node].append(woflan_object.get_r_g().get_edge_data(v, node)[0]['transition'])
                if node not in red_nodes:
                    queue.add(node)
                else:
                    red_paths.append(paths[node])
        processed_nodes.add(v)
    return red_paths


def compute_unbounded_sequences(woflan_object):
    """
    We compute the sequences which lead to an infinite amount of tokens. To do this, we compute a restricted coverability tree.
    The tree works similar to the graph, despite we consider tree characteristics during the construction.
    :param woflan_object: Woflan object that contains all needed information.
    :return: List of unbounded sequences, each sequence is a list of transitions
    """

    def check_for_markings_larger_than_final_marking(graph, f_m):
        markings = []
        for node in graph.nodes:
            if all(np.greater_equal(graph.nodes[node]['marking'], f_m)):
                markings.append(node)
        return markings

    woflan_object.set_restricted_coverability_tree(
        restricted_coverability_tree(woflan_object.get_net(), woflan_object.get_initial_marking()))
    f_m = convert_marking(woflan_object.get_net(), woflan_object.get_final_marking())
    infinite_markings = []
    for node in woflan_object.get_restricted_coverability_tree().nodes:
        if np.inf in woflan_object.get_restricted_coverability_tree().nodes[node]['marking']:
            infinite_markings.append(node)
    larger_markings = check_for_markings_larger_than_final_marking(woflan_object.get_restricted_coverability_tree(),
                                                                   f_m)
    green_markings = []
    for node in woflan_object.get_restricted_coverability_tree().nodes:
        add_to_green = True
        for marking in infinite_markings:
            if nx_utils.has_path(woflan_object.get_restricted_coverability_tree(), node, marking):
                add_to_green = False
        for marking in larger_markings:
            if nx_utils.has_path(woflan_object.get_restricted_coverability_tree(), node, marking):
                add_to_green = False
        if add_to_green:
            green_markings.append(node)
    red_markings = []
    for node in woflan_object.get_restricted_coverability_tree().nodes:
        add_to_red = True
        for node_green in green_markings:
            if nx_utils.has_path(woflan_object.get_restricted_coverability_tree(), node, node_green):
                add_to_red = False
                break
        if add_to_red:
            red_markings.append(node)
    # Make the path as short as possible. If we reach a red state, we stop and do not go further in the "red zone".
    queue = set()
    queue.add(0)
    paths = {}
    paths[0] = []
    paths_to_red = []
    while len(queue) > 0:
        v = queue.pop()
        successors = woflan_object.get_restricted_coverability_tree().successors(v)
        for suc in successors:
            paths[suc] = paths[v].copy()
            paths[suc].append(woflan_object.get_restricted_coverability_tree().get_edge_data(v, suc)['transition'])
            if suc in red_markings:
                paths_to_red.append(paths[suc])
            else:
                queue.add(suc)
    return paths_to_red

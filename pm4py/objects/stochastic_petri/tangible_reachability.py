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
from pm4py.objects.petri_net.utils.reachability_graph import construct_reachability_graph
from pm4py.objects.conversion.log import converter as log_converter


def get_tangible_reachability_from_log_net_im_fm(log, net, im, fm, parameters=None):
    """
    Gets the tangible reachability graph from a log and an accepting Petri net

    Parameters
    ---------------
    log
        Event log
    net
        Petri net
    im
        Initial marking
    fm
        Final marking

    Returns
    ------------
    reachab_graph
        Reachability graph
    tangible_reach_graph
        Tangible reachability graph
    stochastic_info
        Stochastic information
    """
    if parameters is None:
        parameters = {}

    from pm4py.algo.simulation.montecarlo.utils import replay
    stochastic_info = replay.get_map_from_log_and_net(log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters), net, im, fm,
                                                      parameters=parameters)

    reachability_graph, tangible_reachability_graph = get_tangible_reachability_from_net_im_sinfo(net, im,
                                                                                                  stochastic_info,
                                                                                                  parameters=parameters)

    return reachability_graph, tangible_reachability_graph, stochastic_info


def get_tangible_reachability_from_net_im_sinfo(net, im, stochastic_info, parameters=None):
    """
    Gets the tangible reacahbility graph from a Petri net, an initial marking and a stochastic map

    Parameters
    -------------
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    stochastic_info
        Stochastic information

    Returns
    ------------
    reachab_graph
        Reachability graph
    tangible_reach_graph
        Tangible reachability graph
    """
    if parameters is None:
        parameters = {}
    reachab_graph = construct_reachability_graph(net, im, use_trans_name=True)
    tang_reach_graph = get_tangible_reachability_from_reachability(reachab_graph, stochastic_info)

    return reachab_graph, tang_reach_graph


def get_tangible_reachability_from_reachability(reach_graph, stochastic_info):
    """
    Gets the tangible reachability graph from the reachability graph and the stochastic transition map

    Parameters
    ------------
    reach_graph
        Reachability graph
    stochastic_info
        Stochastic information

    Returns
    ------------
    tangible_reach_graph
        Tangible reachability graph
    """
    timed_transitions = []
    for trans in stochastic_info.keys():
        random_variable = stochastic_info[trans]
        transition_type = random_variable.get_transition_type()
        if transition_type == "TIMED":
            timed_transitions.append(trans.name)
    states_reach = list(reach_graph.states)
    for s in states_reach:
        state_outgoing_trans = list(s.outgoing)
        state_ingoing_trans = list(s.incoming)
        timed_trans_outgoing = [x for x in state_outgoing_trans if x.name in timed_transitions]
        if not len(state_outgoing_trans) == len(timed_trans_outgoing):
            for t in state_outgoing_trans:
                reach_graph.transitions.remove(t)
                t.from_state.outgoing.remove(t)
                t.to_state.incoming.remove(t)
            for t in state_ingoing_trans:
                reach_graph.transitions.remove(t)
                t.from_state.outgoing.remove(t)
                t.to_state.incoming.remove(t)
            reach_graph.states.remove(s)
    states_reach = list(reach_graph.states)
    for s in states_reach:
        if len(s.incoming) == 0 and len(s.outgoing) == 0:
            reach_graph.states.remove(s)

    return reach_graph

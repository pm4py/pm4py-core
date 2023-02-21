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
import copy
from pm4py.objects.bpmn.util.bpmn_utils import *
from pm4py.objects.bpmn.obj import BPMN
from itertools import combinations, chain
import operator


def is_enabled(node, bpmn, m):
    if node not in bpmn.get_nodes():
        return False
    elif isinstance(node, (
            BPMN.ParallelGateway,
            BPMN.InclusiveGateway)) and node.get_gateway_direction() == BPMN.Gateway.Direction.CONVERGING:
        if m[node] < len(node.get_in_arcs()):
            return False
    else:
        if m[node] < 1:
            return False
    return True


def execute(node, bpmn, m):
    if not is_enabled(node, bpmn, m):
        return None

    return weak_execute(node, m)


def try_to_execute(node, bpmn, m):
    if not is_enabled(node, bpmn, m):
        return None
    else:
        return execute(node, bpmn, m)


def add_vector(a, b):
    return list(map(operator.add, a, b))


def sub_vector(a, b):
    return list(map(operator.sub, a, b))


def power_set(iterable, min=1):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(min, len(s) + 1))


def weak_execute(node, m, bpmn_graph):
    """
    Execute a transition even if it is not fully enabled
    Returns multiple possible markings if the node is a gate
    """

    # this first if is a workaround. env events inside subprocesses will be handled explicitly
    # tokens flow out to the first element outside the subprocess. the activated boundary events become deactivated
    if isinstance(node,
                  (BPMN.NormalEndEvent, BPMN.TerminateEndEvent)) and node.get_process() != bpmn_graph.get_process_id():
        m_out = copy.copy(m)
        # reset marking at current node
        del m_out[node]

        sub_process_node = get_node_by_id(node.get_process(), bpmn_graph)

        # delete markings inside subprocess and from other enabled message transitions
        for key in get_all_nodes_inside_process(node.get_process(), bpmn_graph):
            if key in m_out:
                del m_out[key]
        for key in get_boundary_events_of_activity(node.get_process(), bpmn_graph):
            if key in m_out and key != node:
                del m_out[key]

        # add marking at outgoing flow
        if len(sub_process_node.get_out_arcs()) > 0:
            target_node = sub_process_node.get_out_arcs()[0].target
            execute_token_flow(target_node, m_out, bpmn_graph)

        return [m_out]

    elif isinstance(node, (BPMN.Event, BPMN.Activity)) or (
            isinstance(node, BPMN.Gateway) and node.get_gateway_direction() == BPMN.Gateway.Direction.CONVERGING):
        m_out = copy.copy(m)
        # reset marking at current node
        del m_out[node]

        # add marking at outgoing flow
        if len(node.get_out_arcs()) > 0:
            target_node = node.get_out_arcs()[0].target
            execute_token_flow(target_node, m_out, bpmn_graph)

        # external subprocess cancellation
        if isinstance(node, BPMN.MessageBoundaryEvent):
            # delete markings inside subprocess and from other enabled message transitions
            for key in get_all_nodes_inside_process(node.get_activity(), bpmn_graph):
                if key in m_out:
                    del m_out[key]
            for key in get_boundary_events_of_activity(node.get_activity(), bpmn_graph):
                if key in m_out and key != node:
                    del m_out[key]

        return [m_out]

    elif isinstance(node, BPMN.Gateway):
        m_outs = []
        if node.get_gateway_direction() == BPMN.Gateway.Direction.DIVERGING:
            if isinstance(node, BPMN.ParallelGateway):
                m_out = copy.copy(m)
                del m_out[node]
                for out_flow in node.get_out_arcs():
                    execute_token_flow(out_flow.target, m_out, bpmn_graph)
                m_outs.append(m_out)
            elif isinstance(node, BPMN.ExclusiveGateway):
                for out_flow in node.get_out_arcs():
                    m_out = copy.copy(m)
                    del m_out[node]
                    execute_token_flow(out_flow.target, m_out, bpmn_graph)
                    m_outs.append(m_out)
            elif isinstance(node, BPMN.InclusiveGateway):
                for out_flows in power_set(node.get_out_arcs()):
                    for out_flow in out_flows:
                        m_out = copy.copy(m)
                        del m_out[node]
                        execute_token_flow(out_flow.target, m_out, bpmn_graph)
                        m_outs.append(m_out)
        return m_outs


def execute_token_flow(target, marking, bpmn_graph):
    # next node is a subprocess --> add tokens in its start events
    if isinstance(target, BPMN.SubProcess):
        start_events = get_start_events_of_subprocess(target.get_id(), bpmn_graph)
        for start_event in start_events:
            marking[start_event] += 1
        # handle external boundary events
        for boundary_event in get_external_boundary_events_of_activity(target.get_id(), bpmn_graph):
            marking[boundary_event] += 1
    elif isinstance(target, BPMN.EndEvent):
        # end event globally
        if target.get_process() == bpmn_graph.get_process_id():
            if isinstance(target, BPMN.TerminateEndEvent):
                keys_to_delete = [key for key in marking if key != target]
                for key in keys_to_delete:
                    del marking[key]
            marking[target] += 1
        # end event is inside subprocess
        else:
            sub_process_node = get_node_by_id(target.get_process(), bpmn_graph)
            # end event is connected to boundary transition
            for boundary_event in get_boundary_events_of_activity(sub_process_node.get_id(), bpmn_graph):
                if boundary_event.name == target.name:  # TODO: also type of event could be checked, e.g. error end and boundary event
                    # add token to boundary event
                    marking[boundary_event] += 1
                    # reset all tokens inside subprocess and on other boundary events
                    for key in get_all_nodes_inside_process(target.get_process(), bpmn_graph):
                        if key in marking:
                            del marking[key]
                    for key in get_boundary_events_of_activity(sub_process_node.get_id(), bpmn_graph):
                        if key in marking and key != boundary_event:
                            del marking[key]
                    return
            # internal subprocess termination event
            if isinstance(target, BPMN.TerminateEndEvent):
                keys_to_delete = [key for key in marking if key != target and \
                                  key in get_all_nodes_inside_process(target.get_process(),
                                                                      bpmn_graph) + get_boundary_events_of_activity(
                    sub_process_node.get_id(), bpmn_graph)]
                for key in keys_to_delete:
                    del marking[key]
                # add marking at outgoing flow
                if len(sub_process_node.get_out_arcs()) > 0:
                    target_node = sub_process_node.get_out_arcs()[0].target
                    execute_token_flow(target_node, marking, bpmn_graph)
                    return
            marking[
                target] += 1  # instead add token to end event, workaround to make sure that you can fire a message event even after the last event inside subprocess
    # just normal token flow to next node
    else:
        marking[target] += 1


def enabled_nodes(bpmn, m):
    """
    Returns a set of enabled transitions in a Petri net and given marking

    Parameters
    ----------
    :param pn: Petri net
    :param m: marking of the pn

    Returns
    -------
    :return: set of enabled transitions
    """
    enabled = set()
    for node in bpmn.get_nodes():
        if is_enabled(node, bpmn, m):
            enabled.add(node)
            if isinstance(node,
                          BPMN.EndEvent) and node.get_process() == bpmn.get_process_id():  # if there is a token in an end event, we are done and there is no enabled node anymore
                return set()
    return enabled

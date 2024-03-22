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

from pm4py.objects.process_tree.obj import Operator


class Counts(object):
    """
    Shared variables among executions
    """

    def __init__(self):
        """
        Constructor
        """
        self.num_xor_gateways = 0
        self.num_para_gateways = 0
        self.num_tau_trans = 0
        self.tau_trans = []

    def inc_xor_gateways(self):
        """
        Increase the number of xor gateways (split + join)
        """
        self.num_xor_gateways += 1

    def inc_tau_trans(self):
        """
        Increase the number of tau transitions
        """
        self.num_tau_trans += 1

    def inc_para_gateways(self):
        """
        Increase the number of xor gateways (split + join)
        """
        self.num_para_gateways += 1

    def append_tau(self, tau_id):
        self.tau_trans.append(tau_id)


def add_task(bpmn, counts, label):
    """
    Create a task with the specified label in the BPMN
    """
    from pm4py.objects.bpmn.obj import BPMN
    task = BPMN.Task(name=label)
    bpmn.add_node(task)
    return bpmn, task, counts


def add_tau_task(bpmn, counts):
    """
    Create a task with the specified label in the BPMN
    """
    from pm4py.objects.bpmn.obj import BPMN
    counts.inc_tau_trans()
    tau_name = "tau_" + str(counts.num_tau_trans)
    tau_task = BPMN.Task(name=tau_name)
    bpmn.add_node(tau_task)
    counts.append_tau(tau_task)
    return bpmn, tau_task, counts


def add_xor_gateway(bpmn, counts):
    from pm4py.objects.bpmn.obj import BPMN
    counts.inc_xor_gateways()
    split_name = "xor_" + str(counts.num_xor_gateways) + "_split"
    join_name = "xor_" + str(counts.num_xor_gateways) + "_join"

    split = BPMN.ExclusiveGateway(name="", gateway_direction=BPMN.Gateway.Direction.DIVERGING)
    join = BPMN.ExclusiveGateway(name="", gateway_direction=BPMN.Gateway.Direction.CONVERGING)
    bpmn.add_node(split)
    bpmn.add_node(join)

    return bpmn, split, join, counts


def add_parallel_gateway(bpmn, counts):
    from pm4py.objects.bpmn.obj import BPMN
    counts.inc_para_gateways()
    split_name = "parallel_" + str(counts.num_para_gateways) + "_split"
    join_name = "parallel_" + str(counts.num_para_gateways) + "_join"

    split = BPMN.ParallelGateway(name="", gateway_direction=BPMN.Gateway.Direction.DIVERGING)
    join = BPMN.ParallelGateway(name="", gateway_direction=BPMN.Gateway.Direction.CONVERGING)
    bpmn.add_node(split)
    bpmn.add_node(join)
    return bpmn, split, join, counts


def add_inclusive_gateway(bpmn, counts):
    from pm4py.objects.bpmn.obj import BPMN
    counts.inc_para_gateways()
    split_name = "parallel_" + str(counts.num_para_gateways) + "_split"
    join_name = "parallel_" + str(counts.num_para_gateways) + "_join"

    split = BPMN.InclusiveGateway(name="", gateway_direction=BPMN.Gateway.Direction.DIVERGING)
    join = BPMN.InclusiveGateway(name="", gateway_direction=BPMN.Gateway.Direction.CONVERGING)
    bpmn.add_node(split)
    bpmn.add_node(join)
    return bpmn, split, join, counts


def recursively_add_tree(parent_tree, tree, bpmn, initial_event, final_event, counts, rec_depth):
    from pm4py.objects.bpmn.obj import BPMN
    tree_childs = [child for child in tree.children]
    initial_connector = None
    final_connector = None

    if tree.operator is None:
        trans = tree
        if trans.label is None:
            bpmn, task, counts = add_tau_task(bpmn, counts)
            bpmn.add_flow(BPMN.SequenceFlow(initial_event, task))
            bpmn.add_flow(BPMN.SequenceFlow(task, final_event))
            initial_connector = task
            final_connector = task
        else:
            bpmn, task, counts = add_task(bpmn, counts, trans.label)
            bpmn.add_flow(BPMN.SequenceFlow(initial_event, task))
            bpmn.add_flow(BPMN.SequenceFlow(task, final_event))
            initial_connector = task
            final_connector = task

    elif tree.operator == Operator.XOR:
        bpmn, split_gateway, join_gateway, counts = add_xor_gateway(bpmn, counts)
        for subtree in tree_childs:
            bpmn, counts, x, y = recursively_add_tree(tree, subtree, bpmn, split_gateway, join_gateway,
                                                      counts,
                                                      rec_depth + 1)
        bpmn.add_flow(BPMN.SequenceFlow(initial_event, split_gateway))
        bpmn.add_flow(BPMN.SequenceFlow(join_gateway, final_event))
        initial_connector = split_gateway
        final_connector = join_gateway

    elif tree.operator == Operator.PARALLEL:
        bpmn, split_gateway, join_gateway, counts = add_parallel_gateway(bpmn, counts)
        for subtree in tree_childs:
            bpmn, counts, x, y = recursively_add_tree(tree, subtree, bpmn, split_gateway, join_gateway,
                                                      counts,
                                                      rec_depth + 1)
        bpmn.add_flow(BPMN.SequenceFlow(initial_event, split_gateway))
        bpmn.add_flow(BPMN.SequenceFlow(join_gateway, final_event))
        initial_connector = split_gateway
        final_connector = join_gateway

    elif tree.operator == Operator.OR:
        bpmn, split_gateway, join_gateway, counts = add_inclusive_gateway(bpmn, counts)
        for subtree in tree_childs:
            bpmn, counts, x, y = recursively_add_tree(tree, subtree, bpmn, split_gateway, join_gateway,
                                                      counts,
                                                      rec_depth + 1)
        bpmn.add_flow(BPMN.SequenceFlow(initial_event, split_gateway))
        bpmn.add_flow(BPMN.SequenceFlow(join_gateway, final_event))
        initial_connector = split_gateway
        final_connector = join_gateway

    elif tree.operator == Operator.SEQUENCE:
        initial_intermediate_task = initial_event
        bpmn, final_intermediate_task, counts = add_tau_task(bpmn, counts)
        for i in range(len(tree_childs)):
            bpmn, counts, initial_connect, final_connect = recursively_add_tree(tree, tree_childs[i], bpmn,
                                                                                initial_intermediate_task,
                                                                                final_intermediate_task, counts,
                                                                                rec_depth + 1)
            initial_intermediate_task = final_connect
            if i == 0:
                initial_connector = initial_connect
            if i == len(tree_childs) - 2:
                final_intermediate_task = final_event
            else:
                bpmn, final_intermediate_task, counts = add_tau_task(bpmn, counts)
            final_connector = final_connect

    elif tree.operator == Operator.LOOP:
        do = tree_childs[0]
        bpmn, split, join, counts = add_xor_gateway(bpmn, counts)
        bpmn, counts, i, y = recursively_add_tree(tree, do, bpmn, join, split, counts, rec_depth + 1)
        for redo in tree_childs[1:]:
            bpmn, counts, x, y = recursively_add_tree(tree, redo, bpmn, split, join, counts, rec_depth + 1)
        bpmn.add_flow(BPMN.SequenceFlow(initial_event, join))
        bpmn.add_flow(BPMN.SequenceFlow(split, final_event))
        initial_connector = join
        final_connector = split

    return bpmn, counts, initial_connector, final_connector


def delete_tau_transitions(bpmn, counts):
    from pm4py.objects.bpmn.obj import BPMN
    for tau_tran in counts.tau_trans:
        in_arcs = tau_tran.get_in_arcs()
        out_arcs = tau_tran.get_out_arcs()
        if len(in_arcs) > 1 or len(out_arcs) > 1:
            raise Exception("Tau transition has more than one incoming or outgoing edge!")
        if in_arcs and out_arcs:
            out_flow = out_arcs[0]
            in_flow = in_arcs[0]
            source = in_flow.get_source()
            target = out_flow.get_target()
            bpmn.remove_flow(out_flow)
            bpmn.remove_flow(in_flow)
            bpmn.add_flow(BPMN.SequenceFlow(source, target))
        else:
            for in_flow in copy.copy(in_arcs):
                bpmn.remove_flow(in_flow)
            for out_flow in copy.copy(out_arcs):
                bpmn.remove_flow(out_flow)
        bpmn.remove_node(tau_tran)

    return bpmn


def apply(tree, parameters=None):
    """
    Converts the process tree into a BPMN diagram

    Parameters
    --------------
    tree
        Process tree
    parameters
        Parameters of the algorithm

    Returns
    --------------
    bpmn_graph
        BPMN diagram
    """
    from pm4py.objects.bpmn.obj import BPMN
    counts = Counts()
    bpmn = BPMN()
    start_event = BPMN.StartEvent(name="start", isInterrupting=True)
    end_event = BPMN.NormalEndEvent(name="end")
    bpmn.add_node(start_event)
    bpmn.add_node(end_event)
    bpmn, counts, _, _ = recursively_add_tree(tree, tree, bpmn, start_event, end_event, counts, 0)
    bpmn = delete_tau_transitions(bpmn, counts)

    for node in bpmn.get_nodes():
        node.set_process(bpmn.get_process_id())

    for edge in bpmn.get_flows():
        edge.set_process(bpmn.get_process_id())

    return bpmn

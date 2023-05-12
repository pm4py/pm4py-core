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
import random

from pm4py.objects.log.obj import EventLog, Trace, Event
from pm4py.util import xes_constants as xes
from pm4py.objects.process_tree import obj as pt_opt
from pm4py.objects.process_tree import state as pt_st
from pm4py.objects.process_tree.utils import generic as pt_util
from pm4py.objects.process_tree.obj import ProcessTree

import datetime
from copy import deepcopy


class GenerationTree(ProcessTree):
    # extend the parent class to replace the __eq__ and __hash__ method
    def __init__(self, tree):
        i = 0
        while i < len(tree.children):
            tree.children[i] = GenerationTree(tree.children[i])
            tree.children[i].parent = self
            i = i + 1
        ProcessTree.__init__(self, operator=tree.operator, parent=tree.parent, children=tree.children, label=tree.label)

    def __eq__(self, other):
        # method that is different from default one (different taus must give different ID in log generation!!!!)
        return id(self) == id(other)

    def __hash__(self):
        return id(self)


def generate_log(pt0, no_traces=100):
    """
    Generate a log out of a process tree

    Parameters
    ------------
    pt
        Process tree
    no_traces
        Number of traces contained in the process tree

    Returns
    ------------
    log
        Trace log object
    """
    pt = deepcopy(pt0)
    # different taus must give different ID in log generation!!!!
    # so we cannot use the default process tree class
    # we use this different one!
    pt = GenerationTree(pt)
    log = EventLog()

    # assigns to each event an increased timestamp from 1970
    curr_timestamp = 10000000

    for i in range(no_traces):
        ex_seq = execute(pt)
        ex_seq_labels = pt_util.project_execution_sequence_to_labels(ex_seq)
        trace = Trace()
        trace.attributes[xes.DEFAULT_NAME_KEY] = str(i)
        for label in ex_seq_labels:
            event = Event()
            event[xes.DEFAULT_NAME_KEY] = label
            event[xes.DEFAULT_TIMESTAMP_KEY] = datetime.datetime.fromtimestamp(curr_timestamp)

            trace.append(event)

            curr_timestamp = curr_timestamp + 1

        log.append(trace)

    return log


def execute(pt):
    """
    Execute the process tree, returning an execution sequence

    Parameters
    -----------
    pt
        Process tree

    Returns
    -----------
    exec_sequence
        Execution sequence on the process tree
    """
    enabled, open, closed = set(), set(), set()
    enabled.add(pt)
    # populate_closed(pt.children, closed)
    execution_sequence = list()
    while len(enabled) > 0:
        execute_enabled(enabled, open, closed, execution_sequence)
    return execution_sequence


def populate_closed(nodes, closed):
    """
    Populate all closed nodes of a process tree

    Parameters
    ------------
    nodes
        Considered nodes of the process tree
    closed
        Closed nodes
    """
    closed |= set(nodes)
    for node in nodes:
        populate_closed(node.children, closed)


def execute_enabled(enabled, open, closed, execution_sequence=None):
    """
    Execute an enabled node of the process tree

    Parameters
    -----------
    enabled
        Enabled nodes
    open
        Open nodes
    closed
        Closed nodes
    execution_sequence
        Execution sequence

    Returns
    -----------
    execution_sequence
        Execution sequence
    """
    execution_sequence = list() if execution_sequence is None else execution_sequence
    vertex = random.sample(list(enabled), 1)[0]
    enabled.remove(vertex)
    open.add(vertex)
    execution_sequence.append((vertex, pt_st.State.OPEN))
    if len(vertex.children) > 0:
        if vertex.operator is pt_opt.Operator.LOOP:
            while len(vertex.children) < 3:
                vertex.children.append(ProcessTree(parent=vertex))
        if vertex.operator is pt_opt.Operator.SEQUENCE or vertex.operator is pt_opt.Operator.LOOP:
            c = vertex.children[0]
            enabled.add(c)
            execution_sequence.append((c, pt_st.State.ENABLED))
        elif vertex.operator is pt_opt.Operator.PARALLEL:
            enabled |= set(vertex.children)
            for x in vertex.children:
                if x in closed:
                    closed.remove(x)
            map(lambda c: execution_sequence.append((c, pt_st.State.ENABLED)), vertex.children)
        elif vertex.operator is pt_opt.Operator.XOR:
            vc = vertex.children
            c = vc[random.randint(0, len(vc) - 1)]
            enabled.add(c)
            execution_sequence.append((c, pt_st.State.ENABLED))
        elif vertex.operator is pt_opt.Operator.OR:
            some_children = [c for c in vertex.children if random.random() < 0.5]
            enabled |= set(some_children)
            for x in some_children:
                if x in closed:
                    closed.remove(x)
            map(lambda c: execution_sequence.append((c, pt_st.State.ENABLED)), some_children)
        elif vertex.operator is pt_opt.Operator.INTERLEAVING:
            random.shuffle(vertex.children)
            c = vertex.children[0]
            enabled.add(c)
            execution_sequence.append((c, pt_st.State.ENABLED))
    else:
        close(vertex, enabled, open, closed, execution_sequence)
    return execution_sequence


def close(vertex, enabled, open, closed, execution_sequence):
    """
    Close a given vertex of the process tree

    Parameters
    ------------
    vertex
        Vertex to be closed
    enabled
        Set of enabled nodes
    open
        Set of open nodes
    closed
        Set of closed nodes
    execution_sequence
        Execution sequence on the process tree
    """
    open.remove(vertex)
    closed.add(vertex)
    execution_sequence.append((vertex, pt_st.State.CLOSED))
    process_closed(vertex, enabled, open, closed, execution_sequence)


def process_closed(closed_node, enabled, open, closed, execution_sequence):
    """
    Process a closed node, deciding further operations

    Parameters
    -------------
    closed_node
        Node that shall be closed
    enabled
        Set of enabled nodes
    open
        Set of open nodes
    closed
        Set of closed nodes
    execution_sequence
        Execution sequence on the process tree
    """
    vertex = closed_node.parent
    if vertex is not None and vertex in open:
        if should_close(vertex, closed, closed_node):
            close(vertex, enabled, open, closed, execution_sequence)
        else:
            enable = None
            if vertex.operator is pt_opt.Operator.SEQUENCE or vertex.operator is pt_opt.Operator.INTERLEAVING:
                enable = vertex.children[vertex.children.index(closed_node) + 1]
            elif vertex.operator is pt_opt.Operator.LOOP:
                enable = vertex.children[random.randint(1, 2)] if vertex.children.index(closed_node) == 0 else \
                    vertex.children[0]
            if enable is not None:
                enabled.add(enable)
                execution_sequence.append((enable, pt_st.State.ENABLED))


def should_close(vertex, closed, child):
    """
    Decides if a parent vertex shall be closed based on
    the processed child

    Parameters
    ------------
    vertex
        Vertex of the process tree
    closed
        Set of closed nodes
    child
        Processed child

    Returns
    ------------
    boolean
        Boolean value (the vertex shall be closed)
    """
    if vertex.children is None:
        return True
    elif vertex.operator is pt_opt.Operator.LOOP or vertex.operator is pt_opt.Operator.SEQUENCE or vertex.operator is pt_opt.Operator.INTERLEAVING:
        return vertex.children.index(child) == len(vertex.children) - 1
    elif vertex.operator is pt_opt.Operator.XOR:
        return True
    else:
        return set(vertex.children) <= closed

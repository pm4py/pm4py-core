import random

from pm4py.objects.log.log import EventLog, Trace, Event
from pm4py.objects.log.util import xes
from pm4py.objects.process_tree import pt_operator as pt_opt
from pm4py.objects.process_tree import state as pt_st
from pm4py.objects.process_tree import util as pt_util


def generate_log(pt, no_traces=100):
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
    log = EventLog()

    for i in range(no_traces):
        ex_seq = execute(pt)
        ex_seq_labels = pt_util.project_execution_sequence_to_labels(ex_seq)

        trace = Trace()
        trace.attributes[xes.DEFAULT_NAME_KEY] = str(i)
        for label in ex_seq_labels:
            event = Event()
            event[xes.DEFAULT_NAME_KEY] = label
            trace.append(event)
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
    populate_closed(pt.children, closed)
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
    vertex = random.sample(enabled, 1)[0]
    enabled.remove(vertex)
    open.add(vertex)
    execution_sequence.append((vertex, pt_st.State.OPEN))
    if len(vertex.children) > 0:
        if vertex.operator is pt_opt.Operator.SEQUENCE or vertex.operator is pt_opt.Operator.LOOP:
            c = vertex.children[0]
            enabled.add(c)
            execution_sequence.append((c, pt_st.State.ENABLED))
        elif vertex.operator is pt_opt.Operator.PARALLEL:
            enabled |= set(vertex.children)
            map(lambda c: execution_sequence.append((c, pt_st.State.ENABLED)), vertex.children)
        elif vertex.operator is pt_opt.Operator.XOR:
            vc = vertex.children
            c = vc[random.randint(0, len(vc) - 1)]
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
            if vertex.operator is pt_opt.Operator.SEQUENCE:
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
    elif vertex.operator is pt_opt.Operator.LOOP or vertex.operator is pt_opt.Operator.SEQUENCE:
        return vertex.children.index(child) == len(vertex.children) - 1
    else:
        return set(vertex.children) <= closed

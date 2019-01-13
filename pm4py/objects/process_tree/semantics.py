from pm4py.objects.process_tree import pt_operator as pt_opt
from pm4py.objects.process_tree import state as pt_st
from pm4py.objects.log.log import TraceLog, Trace, Event
from pm4py.objects.process_tree import util as pt_util
from pm4py.objects.log.util import xes
import random

def generate_log(pt, no_traces = 100):
    log = TraceLog()

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
    enabled, open, closed = set(), set(), set()
    enabled.add(pt)
    populate_closed(pt.children, closed)
    execution_sequence = list()
    while len(enabled) > 0:
        execute_enabled(enabled, open, closed, execution_sequence)
    return execution_sequence


def populate_closed(nodes, closed):
    closed |= set(nodes)
    for node in nodes:
        populate_closed(node.children, closed)


def execute_enabled(enabled, open, closed, execution_sequence=None):
    execution_sequence = list() if execution_sequence is None else execution_sequence
    vertex = random.sample(enabled, 1)[0]
    enabled.remove(vertex)
    open.add(vertex)
    execution_sequence.append((vertex, pt_st.State.OPEN))
    if len(vertex.children) > 0:
        if vertex.operator is pt_opt.Operator2.SEQUENCE or vertex.operator is pt_opt.Operator2.LOOP:
            c = vertex.children[0]
            enabled.add(c)
            execution_sequence.append((c, pt_st.State.ENABLED))
        elif vertex.operator is pt_opt.Operator2.PARALLEL:
            enabled |= set(vertex.children)
            map(lambda c: execution_sequence.append((c, pt_st.State.ENABLED)), vertex.children)
        elif vertex.operator is pt_opt.Operator2.XOR:
            vc = vertex.children
            c = vc[random.randint(0, len(vc)-1)]
            enabled.add(c)
            execution_sequence.append((c, pt_st.State.ENABLED))
    else:
        close(vertex, enabled, open, closed, execution_sequence)
    return execution_sequence


def close(vertex, enabled, open, closed, execution_sequence):
    open.remove(vertex)
    closed.add(vertex)
    execution_sequence.append((vertex, pt_st.State.CLOSED))
    process_closed(vertex, enabled, open, closed, execution_sequence)


def process_closed(closed_node, enabled, open, closed, execution_sequence):
    vertex = closed_node.parent
    if vertex is not None and vertex in open:
        if should_close(vertex, closed, closed_node):
            close(vertex, enabled, open, closed, execution_sequence)
        else:
            enable = None
            if vertex.operator is pt_opt.Operator2.SEQUENCE:
                enable = vertex.children[vertex.children.index(closed_node)+1]
            elif vertex.operator is pt_opt.Operator2.LOOP:
                enable = vertex.children[random.randint(1, 2)] if vertex.children.index(closed_node) == 0 else vertex.children[0]
            if enable is not None:
                enabled.add(enable)
                execution_sequence.append((enable, pt_st.State.ENABLED))


def should_close(vertex, closed, child):
    if vertex.children is None:
        return True
    elif vertex.operator is pt_opt.Operator2.LOOP or vertex.operator is pt_opt.Operator2.SEQUENCE:
        return vertex.children.index(child) == len(vertex.children) - 1
    else:
        return set(vertex.children) <= closed

from pm4py.objects.process_tree.pt_operator import Operator
from pm4py.util import exec_utils, constants, xes_constants
from pm4py.objects.log.log import EventLog, Trace, Event
from enum import Enum
import random
import time


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    NO_TRACES = "num_traces"


def apply(tree, parameters=None):
    """
    Gets the top-bottom playout of a process tree

    Parameters
    ---------------
    tree
        Process tree
    parameters
        Parameters of the algorithm, including:
            - Parameters.ACTIVITY_KEY: activity key
            - Parameters.NO_TRACES: number of traces that should be returned

    Returns
    ---------------
    log
        Event log
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    no_traces = exec_utils.get_param_value(Parameters.NO_TRACES, parameters, 1000)

    execution_sequences = get_num_ex_sequences(tree, no_traces)

    log = EventLog()
    for seq in execution_sequences:
        trace = Trace()
        for el in seq:
            if el.label is not None:
                event = Event({activity_key: el.label})
                trace.append(event)
        log.append(trace)

    return log


def get_ex_seq_in_time(tree, ex_time):
    """
    Gets the maximum number of execution sequences, doing the playout,
    in the given amount of time

    Parameters
    ----------------
    tree
        Process tree
    ex_time
        Maximum execution time

    Returns
    ----------------
    ex_sec
        Execution sequences
    """
    ex_sec = []
    aa = time.time()
    while time.time() - aa < ex_time:
        ex_sec.append(tuple(get_ex_seq(tree)))
    return ex_sec


def get_num_ex_sequences(tree, num):
    """
    Gets the specified amount of execution sequences

    Parameters
    ---------------
    tree
        Process tree
    num
        Number of execution sequences

    Returns
    ---------------
    ex_sec
        Execution sequences
    """
    ret = []
    for i in range(num):
        ret.append(tuple(get_ex_seq(tree)))
    return ret


def get_ex_seq(tree):
    """
    Gets a trace from a process tree (top-bottom)

    Parameters
    --------------
    tree
        Process tree

    Returns
    -------------
    ex_seq
        Execution sequence
    """
    if tree.operator is None:
        return [tree]
    elif tree.operator is Operator.XOR:
        child = random.choice(tree.children)
        return get_ex_seq(child)
    elif tree.operator is Operator.SEQUENCE:
        ret = []
        for child in tree.children:
            ret = ret + get_ex_seq(child)
        return ret
    elif tree.operator is Operator.LOOP:
        ret = []
        cont = True
        while cont:
            cont = False
            ret = ret + get_ex_seq(tree.children[0])
            r = random.random()
            if r <= 0.5:
                ret = ret + get_ex_seq(tree.children[1])
                cont = True
        return ret
    elif tree.operator is Operator.PARALLEL:
        ret = []
        children_traces = []
        list_choices = []
        for index, child in enumerate(tree.children):
            trace = get_ex_seq(child)
            children_traces.append(trace)
            list_choices += [index] * len(trace)
        random.shuffle(list_choices)
        for c in list_choices:
            act = children_traces[c].pop(0)
            ret.append(act)
        return ret

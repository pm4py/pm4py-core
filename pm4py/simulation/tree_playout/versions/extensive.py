from pm4py.objects.process_tree import bottomup as bottomup_discovery
from pm4py.util import exec_utils
from pm4py.objects.log.log import EventLog, Trace, Event
from pm4py.objects.process_tree.pt_operator import Operator
from pm4py.util import constants, xes_constants
from enum import Enum
import sys

TRACES = "traces"
SKIPPABLE = "skippable"


class Parameters(Enum):
    MAX_TRACE_LENGTH = "max_trace_length"
    MAX_LOOP_OCC = "max_loop_occ"
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    MAX_LIMIT_NUM_TRACES = "max_limit_num_traces"


def get_playout_leaf(node, playout_dictio, max_trace_length, max_loop_occ, min_rem_dict, max_limit_num_traces):
    """
    Performs the playout of a leaf (activity or invisible), returning the traces  allowed by the tree
    """
    mr = min_rem_dict[node]
    playout_dictio[node] = {TRACES: set()}
    if node.label is None:
        playout_dictio[node][TRACES].add(tuple([]))
    else:
        if max_trace_length - mr >= 1:
            playout_dictio[node][TRACES].add((node.label,))


def get_playout_xor(node, playout_dictio, max_trace_length, max_loop_occ, min_rem_dict, max_limit_num_traces):
    """
    Performs the playout of a XOR node, returning the traces allowed by the tree
    """
    mr = min_rem_dict[node]
    traces = set()
    for n in node.children:
        traces = traces.union(playout_dictio[n][TRACES])
        if len(traces) > max_limit_num_traces:
            break
    playout_dictio[node] = {TRACES: traces}


def get_min_remaining_length(traces):
    """
    Minimum remaining length (for sequential, parallel cut detection)

    Parameters
    --------------
    traces
        Traces
    """
    min_len_traces = []
    min_rem_length = []
    for x in traces:
        if len(x) == 0:
            min_len_traces.append(0)
        else:
            min_len_traces.append(len(x[0]))
        min_rem_length.append(0)
    min_rem_length[-1] = 0
    min_rem_length[-2] = min_len_traces[-1]
    j = len(traces) - 3
    while j >= 0:
        min_rem_length[j] = min_rem_length[j + 1] + min_len_traces[j + 1]
        j = j - 1
    return min_len_traces, min_rem_length


def flatten(x):
    """
    Flattens a list of tuples
    """
    ret = []
    for y in x:
        for z in y:
            ret.append(z)
    return ret


def get_sequential_compositions_children(traces, max_trace_length, mr, max_limit_num_traces):
    """
    Returns alls the possible sequential combinations between
    the children of a tree
    """
    min_len_traces, min_rem_length = get_min_remaining_length(traces)
    curr = list(traces[0])
    i = 1
    while i < len(traces):
        to_visit = []
        j = 0
        while j < len(curr):
            x = curr[j]
            if not type(x) is list:
                x = [x]
            z = 0
            while z < len(traces[i]):
                y = traces[i][z]
                xy = list(x)
                xy.append(y)
                if len(flatten(xy)) + min_rem_length[i] <= max_trace_length - mr:
                    to_visit.append(xy)
                z = z + 1
            j = j + 1
        curr = to_visit
        i = i + 1
    return curr


def get_playout_parallel(node, playout_dictio, max_trace_length, max_loop_occ, min_rem_dict, max_limit_num_traces):
    """
    Performs the playout of an AND node, returning the traces allowed by the tree
    """
    mr = min_rem_dict[node]
    traces = list(sorted(playout_dictio[x][TRACES], key=lambda x: len(x)) for x in node.children)
    sequential_compositions = get_sequential_compositions_children(traces, max_trace_length, mr, max_limit_num_traces)
    final_traces = list()
    for x in sequential_compositions:
        if len(final_traces) >= max_limit_num_traces:
            break
        to_visit = [[[]] + [len(y) for y in x]]
        while len(to_visit) > 0:
            curr = to_visit.pop(0)
            possible_choices = [i - 1 for i in range(1, len(curr)) if curr[i] > 0]
            for j in possible_choices:
                new = list(curr)
                new[0] = list(new[0])
                new[0].append(x[j][len(x[j]) - curr[j + 1]])
                new[j + 1] = new[j + 1] - 1
                to_visit.append(new)
            if not possible_choices:
                final_traces.append(tuple(curr[0]))
                if len(final_traces) >= max_limit_num_traces:
                    break
    playout_dictio[node] = {TRACES: set(final_traces)}


def get_playout_sequence(node, playout_dictio, max_trace_length, max_loop_occ, min_rem_dict, max_limit_num_traces):
    """
    Performs the playout of a sequence node, returning the traces allowed by the tree
    """
    mr = min_rem_dict[node]
    final_traces = list()
    traces = list(sorted(playout_dictio[x][TRACES], key=lambda x: len(x)) for x in node.children)
    sequential_compositions = get_sequential_compositions_children(traces, max_trace_length, mr, max_limit_num_traces)
    for x in sequential_compositions:
        final_traces.append(tuple(flatten(x)))
    for n in node.children:
        del playout_dictio[n][TRACES]
    playout_dictio[node] = {TRACES: set(final_traces)}


def get_playout_loop(node, playout_dictio, max_trace_length, max_loop_occ, min_rem_dict, max_limit_num_traces):
    """
    Performs the playout of a loop node, returning the traces allowed by the tree
    """
    mr = min_rem_dict[node]
    final_traces = list()
    do_traces = sorted(list(playout_dictio[node.children[0]][TRACES]), key=lambda x: len(x))
    redo_traces = sorted(list(playout_dictio[node.children[1]][TRACES]), key=lambda x: len(x))
    min_do_trace = min(len(x) for x in do_traces) if do_traces else 0
    to_visit = list((x, 0, 0) for x in do_traces)
    while to_visit:
        curr = to_visit.pop(0)
        curr_trace = curr[0]
        position = curr[1]
        num_loops = curr[2]
        if position == 0 and len(curr_trace) <= max_trace_length - mr:
            final_traces.append(curr_trace)
            if len(final_traces) > max_limit_num_traces:
                break
        if position == 0:
            for y in redo_traces:
                new = curr_trace + y
                if len(new) <= max_trace_length - min_do_trace - mr and num_loops + 1 <= max_loop_occ:
                    to_visit.append((new, 1, num_loops + 1))
                else:
                    break
        if position == 1:
            for y in do_traces:
                new = curr_trace + y
                if len(new) <= max_trace_length - mr:
                    to_visit.append((new, 0, num_loops))
                else:
                    break
    playout_dictio[node] = {TRACES: set(final_traces)}


def get_playout(node, playout_dictio, max_trace_length, max_loop_occ, min_rem_dict, max_limit_num_traces):
    """
    Performs a playout of an ode of the process tree, given the type
    """
    if len(node.children) == 0:
        get_playout_leaf(node, playout_dictio, max_trace_length, max_loop_occ, min_rem_dict, max_limit_num_traces)
    elif node.operator == Operator.XOR:
        get_playout_xor(node, playout_dictio, max_trace_length, max_loop_occ, min_rem_dict, max_limit_num_traces)
    elif node.operator == Operator.PARALLEL:
        get_playout_parallel(node, playout_dictio, max_trace_length, max_loop_occ, min_rem_dict, max_limit_num_traces)
    elif node.operator == Operator.SEQUENCE:
        get_playout_sequence(node, playout_dictio, max_trace_length, max_loop_occ, min_rem_dict, max_limit_num_traces)
    elif node.operator == Operator.LOOP:
        get_playout_loop(node, playout_dictio, max_trace_length, max_loop_occ, min_rem_dict, max_limit_num_traces)


def apply(tree, parameters=None):
    """
    Performs an extensive playout of the process tree

    Parameters
    -------------
    tree
        Process tree
    parameters
        Possible parameters, including:
        - Parameters.MAX_TRACE_LENGTH => maximum length of a trace (default: min_allowed_trace_length)
        - Parameters.MAX_LOOP_OCC => maximum number of occurrences for a loop (default: MAX_TRACE_LENGTH)
        - Parameters.ACTIVITY_KEY => activity key
        - Parameters.MAX_LIMIT_NUM_TRACES => maximum number to the limit of traces; the playout shall stop when the number is reached (default: sys.maxsize)
    Returns
    -------------
    log
        Event log
    """
    if parameters is None:
        parameters = {}

    min_allowed_trace_length = bottomup_discovery.get_min_trace_length(tree, parameters=parameters)
    max_trace_length = exec_utils.get_param_value(Parameters.MAX_TRACE_LENGTH, parameters, min_allowed_trace_length)
    max_loop_occ = exec_utils.get_param_value(Parameters.MAX_LOOP_OCC, parameters, max_trace_length)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    max_limit_num_traces = exec_utils.get_param_value(Parameters.MAX_LIMIT_NUM_TRACES, parameters, sys.maxsize)

    bottomup = bottomup_discovery.get_bottomup_nodes(tree, parameters=parameters)
    min_rem_dict = bottomup_discovery.get_min_rem_dict(tree, parameters=parameters)

    playout_dictio = {}
    for i in range(len(bottomup)):
        get_playout(bottomup[i], playout_dictio, max_trace_length, max_loop_occ, min_rem_dict, max_limit_num_traces)
    tree_playout_traces = playout_dictio[tree][TRACES]

    log = EventLog()
    for tr0 in tree_playout_traces:
        trace = Trace()
        for act in tr0:
            trace.append(Event({activity_key: act}))
        log.append(trace)

    return log

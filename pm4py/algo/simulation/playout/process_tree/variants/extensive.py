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
from enum import Enum

from pm4py.algo.discovery.footprints import algorithm as fp_discovery
from pm4py.objects.log.obj import EventLog, Trace, Event
from pm4py.objects.process_tree.utils import bottomup as bottomup_discovery
from pm4py.objects.process_tree.obj import Operator
from pm4py.util import constants, xes_constants
from pm4py.util import exec_utils

from typing import Optional, Dict, Any, Union
from pm4py.objects.log.obj import EventLog
from pm4py.objects.process_tree.obj import ProcessTree

TRACES = "traces"
SKIPPABLE = "skippable"


class Parameters(Enum):
    MIN_TRACE_LENGTH = "min_trace_length"
    MAX_TRACE_LENGTH = "max_trace_length"
    MAX_LOOP_OCC = "max_loop_occ"
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    MAX_LIMIT_NUM_TRACES = "max_limit_num_traces"
    RETURN_SET_STRINGS = "return_set_strings"


def get_playout_leaf(node, playout_dictio, min_trace_length, max_trace_length, max_loop_occ, min_rem_dict, max_rem_dict,
                     max_limit_num_traces):
    """
    Performs the playout of a leaf (activity or invisible), returning the traces  allowed by the tree
    """
    mr = min_rem_dict[node]
    mar = max_rem_dict[node]
    playout_dictio[node] = {TRACES: set()}
    if node.label is None:
        playout_dictio[node][TRACES].add(tuple([]))
    else:
        if mar + 1 >= min_trace_length and max_trace_length - mr >= 1:
            playout_dictio[node][TRACES].add((node.label,))


def get_playout_xor(node, playout_dictio, min_trace_length, max_trace_length, max_loop_occ, min_rem_dict, max_rem_dict,
                    max_limit_num_traces):
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


def get_max_remaining_length(traces):
    """
    Maximum remaining length (for sequential, parallel cut detection)

    Parameters
    --------------
    traces
        Traces
    """
    max_len_traces = []
    max_rem_length = []
    for x in traces:
        if len(x) == 0:
            max_len_traces.append(0)
        else:
            max_len_traces.append(len(x[-1]))
        max_rem_length.append(0)
    max_rem_length[-1] = 0
    max_rem_length[-2] = max_len_traces[-1]
    j = len(traces) - 3
    while j >= 0:
        max_rem_length[j] = max_rem_length[j + 1] + max_len_traces[j + 1]
        j = j - 1
    return max_len_traces, max_rem_length


def flatten(x):
    """
    Flattens a list of tuples
    """
    ret = []
    for y in x:
        for z in y:
            ret.append(z)
    return ret


def get_sequential_compositions_children(traces, min_trace_length, max_trace_length, mr, mar, max_limit_num_traces):
    """
    Returns alls the possible sequential combinations between
    the children of a tree
    """
    diff = max_trace_length - mr
    diff2 = min_trace_length - mar
    min_len_traces, min_rem_length = get_min_remaining_length(traces)
    max_len_traces, max_rem_length = get_max_remaining_length(traces)
    curr = list(traces[0])
    i = 1
    while i < len(traces):
        mrl = min_rem_length[i]
        marl = max_rem_length[i]
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
                val = sum(len(k) for k in xy)
                if val + mrl <= diff and val + marl >= diff2:
                    to_visit.append(xy)
                z = z + 1
            j = j + 1
        curr = to_visit
        i = i + 1
    return curr


def get_playout_parallel(node, playout_dictio, min_trace_length, max_trace_length, max_loop_occ, min_rem_dict,
                         max_rem_dict, max_limit_num_traces):
    """
    Performs the playout of an AND node, returning the traces allowed by the tree
    """
    mr = min_rem_dict[node]
    mar = max_rem_dict[node]
    traces = list(sorted(playout_dictio[x][TRACES], key=lambda x: len(x)) for x in node.children)
    sequential_compositions = get_sequential_compositions_children(traces, min_trace_length, max_trace_length, mr, mar, max_limit_num_traces)
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


def get_playout_sequence(node, playout_dictio, min_trace_length, max_trace_length, max_loop_occ, min_rem_dict,
                         max_rem_dict, max_limit_num_traces):
    """
    Performs the playout of a sequence node, returning the traces allowed by the tree
    """
    mr = min_rem_dict[node]
    mar = max_rem_dict[node]
    final_traces = set()
    traces = list(sorted(playout_dictio[x][TRACES], key=lambda x: len(x)) for x in node.children)
    sequential_compositions = get_sequential_compositions_children(traces, min_trace_length, max_trace_length, mr, mar, max_limit_num_traces)
    for x in sequential_compositions:
        final_traces.add(tuple(flatten(x)))
    playout_dictio[node] = {TRACES: final_traces}


def get_playout_loop(node, playout_dictio, min_trace_length, max_trace_length, max_loop_occ, min_rem_dict, max_rem_dict,
                     max_limit_num_traces):
    """
    Performs the playout of a loop node, returning the traces allowed by the tree
    """
    mr = min_rem_dict[node]
    mar = max_rem_dict[node]
    final_traces = set()
    do_traces = sorted(list(playout_dictio[node.children[0]][TRACES]), key=lambda x: len(x))
    redo_traces = sorted(list(playout_dictio[node.children[1]][TRACES]), key=lambda x: len(x))
    min_do_trace = min(len(x) for x in do_traces) if do_traces else 0
    to_visit = list((x, 0, 0) for x in do_traces)
    closed = set()
    diff1 = max_trace_length - mr
    diff2 = max_trace_length - min_do_trace - mr
    diff3 = min_trace_length - mar
    while to_visit:
        curr = to_visit.pop(0)
        curr_trace = curr[0]
        position = curr[1]
        num_loops = curr[2]
        if position == 0:
            if curr_trace in closed:
                continue
            closed.add(curr_trace)

            if diff3 <= len(curr_trace) <= diff1:
                final_traces.add(curr_trace)
                if len(final_traces) > max_limit_num_traces:
                    break

            for y in redo_traces:
                new = curr_trace + y
                if len(new) <= diff2 and num_loops + 1 <= max_loop_occ:
                    to_visit.append((new, 1, num_loops + 1))
                else:
                    break

        elif position == 1:
            for y in do_traces:
                new = curr_trace + y
                if len(new) <= diff1:
                    to_visit.append((new, 0, num_loops))
                else:
                    break
    playout_dictio[node] = {TRACES: final_traces}


def get_playout(node, playout_dictio, min_trace_length, max_trace_length, max_loop_occ, min_rem_dict, max_rem_dict,
                max_limit_num_traces):
    """
    Performs a playout of an ode of the process tree, given the type
    """
    if len(node.children) == 0:
        get_playout_leaf(node, playout_dictio, min_trace_length, max_trace_length, max_loop_occ, min_rem_dict,
                         max_rem_dict, max_limit_num_traces)
    elif node.operator == Operator.XOR:
        get_playout_xor(node, playout_dictio, min_trace_length, max_trace_length, max_loop_occ, min_rem_dict,
                        max_rem_dict, max_limit_num_traces)
    elif node.operator == Operator.PARALLEL:
        get_playout_parallel(node, playout_dictio, min_trace_length, max_trace_length, max_loop_occ, min_rem_dict,
                             max_rem_dict, max_limit_num_traces)
    elif node.operator == Operator.SEQUENCE:
        get_playout_sequence(node, playout_dictio, min_trace_length, max_trace_length, max_loop_occ, min_rem_dict,
                             max_rem_dict, max_limit_num_traces)
    elif node.operator == Operator.LOOP:
        get_playout_loop(node, playout_dictio, min_trace_length, max_trace_length, max_loop_occ, min_rem_dict,
                         max_rem_dict, max_limit_num_traces)


def apply(tree: ProcessTree, parameters : Optional[Dict[Union[str, Parameters], Any]] = None) -> EventLog:
    """
    Performs an extensive playout of the process tree

    Parameters
    -------------
    tree
        Process tree
    parameters
        Possible parameters, including:
        - Parameters.MIN_TRACE_LENGTH => minimum length of a trace (default: 1)
        - Parameters.MAX_TRACE_LENGTH => maximum length of a trace (default: min_allowed_trace_length)
        - Parameters.MAX_LOOP_OCC => maximum number of occurrences for a loop (default: MAX_TRACE_LENGTH)
        - Parameters.ACTIVITY_KEY => activity key
        - Parameters.MAX_LIMIT_NUM_TRACES => maximum number to the limit of traces; the playout shall stop when the number is reached (default: 100000)
    Returns
    -------------
    log
        Event log
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    # to save memory in the returned log, allocate each activity once. to know the list of activities of the
    # process tree, use the footprints module
    fp_tree = fp_discovery.apply(tree, parameters=parameters)
    activities = fp_tree["activities"]
    activities = {act: Event({activity_key: act}) for act in activities}

    min_allowed_trace_length = bottomup_discovery.get_min_trace_length(tree, parameters=parameters)
    min_trace_length = exec_utils.get_param_value(Parameters.MIN_TRACE_LENGTH, parameters, 1)
    max_trace_length = exec_utils.get_param_value(Parameters.MAX_TRACE_LENGTH, parameters, min_allowed_trace_length)
    max_loop_occ = exec_utils.get_param_value(Parameters.MAX_LOOP_OCC, parameters, int(max_trace_length / 2))
    max_limit_num_traces = exec_utils.get_param_value(Parameters.MAX_LIMIT_NUM_TRACES, parameters, 100000)
    return_set_strings = exec_utils.get_param_value(Parameters.RETURN_SET_STRINGS, parameters, False)

    bottomup = bottomup_discovery.get_bottomup_nodes(tree, parameters=parameters)
    min_rem_dict = bottomup_discovery.get_min_rem_dict(tree, parameters=parameters)
    max_rem_dict = bottomup_discovery.get_max_rem_dict(tree, parameters=parameters)

    playout_dictio = {}
    for i in range(len(bottomup)):
        get_playout(bottomup[i], playout_dictio, min_trace_length, max_trace_length, max_loop_occ, min_rem_dict,
                    max_rem_dict, max_limit_num_traces)
    tree_playout_traces = playout_dictio[tree][TRACES]

    if return_set_strings:
        return tree_playout_traces

    log = EventLog()
    for tr0 in tree_playout_traces:
        trace = Trace()
        for act in tr0:
            trace.append(activities[act])
        log.append(trace)

    return log

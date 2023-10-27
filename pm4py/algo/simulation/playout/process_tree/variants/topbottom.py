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
from pm4py.objects.process_tree.obj import Operator
from pm4py.util import exec_utils, constants, xes_constants
from pm4py.objects.log.obj import Trace, Event
from enum import Enum
import random
import time

from typing import Optional, Dict, Any, Union
from pm4py.objects.log.obj import EventLog
from pm4py.objects.process_tree.obj import ProcessTree


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    NO_TRACES = "num_traces"


def apply(tree: ProcessTree, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> EventLog:
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
    elif tree.operator is Operator.INTERLEAVING:
        random.shuffle(tree.children)
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

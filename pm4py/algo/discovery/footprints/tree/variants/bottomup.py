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
from pm4py.objects.process_tree.utils import bottomup as bottomup_disc
from copy import copy

from enum import Enum
from typing import Optional, Dict, Any
from pm4py.objects.process_tree.obj import ProcessTree


class Outputs(Enum):
    DFG = "dfg"
    SEQUENCE = "sequence"
    PARALLEL = "parallel"
    START_ACTIVITIES = "start_activities"
    END_ACTIVITIES = "end_activities"
    ACTIVITIES = "activities"
    SKIPPABLE = "skippable"
    ACTIVITIES_ALWAYS_HAPPENING = "activities_always_happening"
    MIN_TRACE_LENGTH = "min_trace_length"
    TRACE = "trace"


START_ACTIVITIES = Outputs.START_ACTIVITIES.value
END_ACTIVITIES = Outputs.END_ACTIVITIES.value
ACTIVITIES = Outputs.ACTIVITIES.value
SKIPPABLE = Outputs.SKIPPABLE.value
SEQUENCE = Outputs.SEQUENCE.value
PARALLEL = Outputs.PARALLEL.value
ACTIVITIES_ALWAYS_HAPPENING = Outputs.ACTIVITIES_ALWAYS_HAPPENING.value


def fix_fp(sequence, parallel):
    """
    Fix footprints

    Parameters
    --------------
    sequence
        Sequence
    parallel
        Parallel

    Returns
    -------------
    sequence
        Sequence
    parallel
        Parallel
    """
    sequence = sequence.difference(parallel)

    par_els = {(x[0], x[1]) for x in sequence if (x[1], x[0]) in sequence}
    for el in par_els:
        parallel.add(el)
        sequence.remove(el)

    return sequence, parallel


def get_footprints_leaf(node, footprints_dictio):
    """
    Gets the footprints for a leaf node

    Parameters
    ---------------
    node
        Node
    footprints_dictio
        Dictionary of footprints of the process tree

    Returns
    ---------------
    footprints
        Footprints of the leaf node
    """
    if node.label is None:
        return {START_ACTIVITIES: set(), END_ACTIVITIES: set(), ACTIVITIES: set(), SKIPPABLE: True, SEQUENCE: set(),
                PARALLEL: set(), ACTIVITIES_ALWAYS_HAPPENING: set()}
    else:
        return {START_ACTIVITIES: set([node.label]), END_ACTIVITIES: set([node.label]), ACTIVITIES: set([node.label]),
                SKIPPABLE: False, SEQUENCE: set(),
                PARALLEL: set(), ACTIVITIES_ALWAYS_HAPPENING: set([node.label])}


def get_footprints_xor(node, footprints_dictio):
    """
    Gets the footprints for the XOR node

    Parameters
    ---------------
    node
        Node
    footprints_dictio
        Dictionary of footprints of the process tree

    Returns
    ---------------
    footprints
        Footprints of the XOR node
    """
    start_activities = set()
    end_activities = set()
    activities = set()
    skippable = False
    sequence = set()
    parallel = set()
    activities_always_happening = set()

    if node.children:
        activities_always_happening = copy(footprints_dictio[node.children[0]][ACTIVITIES_ALWAYS_HAPPENING])

    for n0 in node.children:
        n = footprints_dictio[n0]
        start_activities = start_activities.union(n[START_ACTIVITIES])
        end_activities = end_activities.union(n[END_ACTIVITIES])
        activities = activities.union(n[ACTIVITIES])
        skippable = skippable or n[SKIPPABLE]
        sequence = sequence.union(n[SEQUENCE])
        parallel = parallel.union(n[PARALLEL])
        if not n[SKIPPABLE]:
            activities_always_happening = activities_always_happening.intersection(n[ACTIVITIES_ALWAYS_HAPPENING])
        else:
            activities_always_happening = set()

    sequence, parallel = fix_fp(sequence, parallel)

    return {START_ACTIVITIES: start_activities, END_ACTIVITIES: end_activities, ACTIVITIES: activities,
            SKIPPABLE: skippable, SEQUENCE: sequence, PARALLEL: parallel,
            ACTIVITIES_ALWAYS_HAPPENING: activities_always_happening}


def get_footprints_parallel(node, footprints_dictio):
    """
    Gets the footprints for the parallel node

    Parameters
    ---------------
    node
        Node
    footprints_dictio
        Dictionary of footprints of the process tree

    Returns
    ---------------
    footprints
        Footprints of the parallel node
    """
    start_activities = set()
    end_activities = set()
    activities = set()
    skippable = True
    sequence = set()
    parallel = set()
    activities_always_happening = set()

    for n0 in node.children:
        n = footprints_dictio[n0]
        start_activities = start_activities.union(n[START_ACTIVITIES])
        end_activities = end_activities.union(n[END_ACTIVITIES])
        activities = activities.union(n[ACTIVITIES])
        skippable = skippable and n[SKIPPABLE]
        sequence = sequence.union(n[SEQUENCE])
        parallel = parallel.union(n[PARALLEL])
        if not n[SKIPPABLE]:
            activities_always_happening = activities_always_happening.union(n[ACTIVITIES_ALWAYS_HAPPENING])

    i = 0
    while i < len(node.children):
        acti_i = list(footprints_dictio[node.children[i]][ACTIVITIES])
        j = i + 1
        while j < len(node.children):
            acti_j = list(footprints_dictio[node.children[j]][ACTIVITIES])
            for a1 in acti_i:
                for a2 in acti_j:
                    parallel.add((a1, a2))
                    parallel.add((a2, a1))
            j = j + 1
        i = i + 1

    sequence, parallel = fix_fp(sequence, parallel)

    return {START_ACTIVITIES: start_activities, END_ACTIVITIES: end_activities, ACTIVITIES: activities,
            SKIPPABLE: skippable, SEQUENCE: sequence, PARALLEL: parallel,
            ACTIVITIES_ALWAYS_HAPPENING: activities_always_happening}


def get_footprints_sequence(node, footprints_dictio):
    """
    Gets the footprints for the sequence

    Parameters
    ---------------
    node
        Node
    footprints_dictio
        Dictionary of footprints of the process tree

    Returns
    ---------------
    footprints
        Footprints of the sequence node
    """
    start_activities = set()
    end_activities = set()
    activities = set()
    skippable = True
    sequence = set()
    parallel = set()
    activities_always_happening = set()

    for n0 in node.children:
        n = footprints_dictio[n0]
        skippable = skippable and n[SKIPPABLE]
        sequence = sequence.union(n[SEQUENCE])
        parallel = parallel.union(n[PARALLEL])
        activities = activities.union(n[ACTIVITIES])
        if not n[SKIPPABLE]:
            activities_always_happening = activities_always_happening.union(n[ACTIVITIES_ALWAYS_HAPPENING])

    # adds the footprints
    i = 0
    while i < len(node.children) - 1:
        n0 = footprints_dictio[node.children[i]]
        j = i + 1
        while j < len(node.children):
            n1 = footprints_dictio[node.children[j]]
            n0_end_act = n0[END_ACTIVITIES]
            n1_start_act = n1[START_ACTIVITIES]
            for a1 in n0_end_act:
                for a2 in n1_start_act:
                    sequence.add((a1, a2))
            if not n1[SKIPPABLE]:
                break
            j = j + 1
        i = i + 1

    # adds the start activities
    i = 0
    while i < len(node.children):
        n = footprints_dictio[node.children[i]]
        start_activities = start_activities.union(n[START_ACTIVITIES])
        if not n[SKIPPABLE]:
            break
        i = i + 1

    # adds the end activities
    i = len(node.children) - 1
    while i >= 0:
        n = footprints_dictio[node.children[i]]
        end_activities = end_activities.union(n[END_ACTIVITIES])
        if not n[SKIPPABLE]:
            break
        i = i - 1

    sequence, parallel = fix_fp(sequence, parallel)

    return {START_ACTIVITIES: start_activities, END_ACTIVITIES: end_activities, ACTIVITIES: activities,
            SKIPPABLE: skippable, SEQUENCE: sequence, PARALLEL: parallel,
            ACTIVITIES_ALWAYS_HAPPENING: activities_always_happening}


def get_footprints_loop(node, footprints_dictio):
    """
    Gets the footprints for the loop

    Parameters
    ---------------
    node
        Node
    footprints_dictio
        Dictionary of footprints of the process tree

    Returns
    ---------------
    footprints
        Footprints of the loop node
    """
    start_activities = set()
    end_activities = set()
    activities = set()
    sequence = set()
    parallel = set()
    activities_always_happening = set()

    for n0 in node.children:
        n = footprints_dictio[n0]
        sequence = sequence.union(n[SEQUENCE])
        parallel = parallel.union(n[PARALLEL])
        activities = activities.union(n[ACTIVITIES])

    do = footprints_dictio[node.children[0]]
    redo = footprints_dictio[node.children[1]]

    skippable = do[SKIPPABLE]

    if not do[SKIPPABLE]:
        activities_always_happening = copy(do[ACTIVITIES_ALWAYS_HAPPENING])

    start_activities = start_activities.union(do[START_ACTIVITIES])
    if do[SKIPPABLE]:
        start_activities = start_activities.union(redo[START_ACTIVITIES])

    end_activities = end_activities.union(do[END_ACTIVITIES])
    if do[SKIPPABLE]:
        end_activities = end_activities.union(redo[END_ACTIVITIES])

    for a1 in do[END_ACTIVITIES]:
        for a2 in redo[START_ACTIVITIES]:
            sequence.add((a1, a2))

    for a1 in redo[END_ACTIVITIES]:
        for a2 in do[START_ACTIVITIES]:
            sequence.add((a1, a2))

    if do[SKIPPABLE]:
        for a1 in redo[END_ACTIVITIES]:
            for a2 in redo[START_ACTIVITIES]:
                sequence.add((a1, a2))

    if redo[SKIPPABLE]:
        for a1 in do[END_ACTIVITIES]:
            for a2 in do[START_ACTIVITIES]:
                sequence.add((a1, a2))

    sequence, parallel = fix_fp(sequence, parallel)

    return {START_ACTIVITIES: start_activities, END_ACTIVITIES: end_activities, ACTIVITIES: activities,
            SKIPPABLE: skippable, SEQUENCE: sequence, PARALLEL: parallel,
            ACTIVITIES_ALWAYS_HAPPENING: activities_always_happening}


def get_footprints(node, footprints_dictio):
    """
    Gets the footprints for a node (having the history of the child nodes)

    Parameters
    --------------
    node
        Node of the tree
    footprints_dictio
        Dictionary of footprints of the process tree

    Returns
    --------------
    footprints
        Footprints of the node  (having the history of the child nodes)
    """
    if len(node.children) == 0:
        return get_footprints_leaf(node, footprints_dictio)
    elif node.operator == Operator.XOR:
        return get_footprints_xor(node, footprints_dictio)
    elif node.operator == Operator.PARALLEL or node.operator == Operator.OR:
        return get_footprints_parallel(node, footprints_dictio)
    elif node.operator == Operator.SEQUENCE:
        return get_footprints_sequence(node, footprints_dictio)
    elif node.operator == Operator.LOOP:
        return get_footprints_loop(node, footprints_dictio)


def get_all_footprints(tree, parameters=None):
    """
    Gets all the footprints for the nodes of the tree

    Parameters
    -----------------
    tree
        Process tree
    parameters
        Parameters of the algorithm

    Returns
    ----------------
    dictio
        Dictionary that associates a footprint to each node of the tree
    """
    if parameters is None:
        parameters = {}

    # for each node of the bottom up, proceed to getting the footprints
    bottomup = bottomup_disc.get_bottomup_nodes(tree, parameters=parameters)
    footprints_dictio = {}
    for i in range(len(bottomup)):
        footprints_dictio[bottomup[i]] = get_footprints(bottomup[i], footprints_dictio)

    return footprints_dictio


def apply(tree: ProcessTree, parameters: Optional[Dict[Any, Any]] = None) -> Dict[str, Any]:
    """
    Footprints detection on process tree

    Parameters
    -----------------
    tree
        Process tree
    parameters
        Parameters of the algorithm

    Returns
    -----------------
    footprints
        Footprints
    """
    if parameters is None:
        parameters = {}

    all_footprints = get_all_footprints(tree, parameters=parameters)
    root_node_footprints = all_footprints[tree]

    min_trace_length = bottomup_disc.get_min_trace_length(tree, parameters=parameters)
    root_node_footprints[Outputs.MIN_TRACE_LENGTH.value] = min_trace_length

    return root_node_footprints

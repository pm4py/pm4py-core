from pm4py.objects.process_tree.pt_operator import Operator
from pm4py.algo.discovery.footprints.outputs import Outputs

START_ACTIVITIES = Outputs.START_ACTIVITIES.value
END_ACTIVITIES = Outputs.END_ACTIVITIES.value
ACTIVITIES = Outputs.ACTIVITIES.value
SKIPPABLE = Outputs.SKIPPABLE.value
SEQUENCE = Outputs.SEQUENCE.value
PARALLEL = Outputs.PARALLEL.value


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
                PARALLEL: set()}
    else:
        return {START_ACTIVITIES: set([node.label]), END_ACTIVITIES: set([node.label]), ACTIVITIES: set([node.label]),
                SKIPPABLE: False, SEQUENCE: set(),
                PARALLEL: set()}


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

    for n0 in node.children:
        n = footprints_dictio[n0]
        start_activities = start_activities.union(n[START_ACTIVITIES])
        end_activities = end_activities.union(n[END_ACTIVITIES])
        activities = activities.union(n[ACTIVITIES])
        skippable = skippable or n[SKIPPABLE]
        sequence = sequence.union(n[SEQUENCE])
        parallel = parallel.union(n[PARALLEL])

    sequence, parallel = fix_fp(sequence, parallel)

    return {START_ACTIVITIES: start_activities, END_ACTIVITIES: end_activities, ACTIVITIES: activities,
            SKIPPABLE: skippable, SEQUENCE: sequence, PARALLEL: parallel}


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
    skippable = False
    sequence = set()
    parallel = set()

    for n0 in node.children:
        n = footprints_dictio[n0]
        start_activities = start_activities.union(n[START_ACTIVITIES])
        end_activities = end_activities.union(n[END_ACTIVITIES])
        activities = activities.union(n[ACTIVITIES])
        skippable = skippable and n[SKIPPABLE]
        sequence = sequence.union(n[SEQUENCE])
        parallel = parallel.union(n[PARALLEL])

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
            SKIPPABLE: skippable, SEQUENCE: sequence, PARALLEL: parallel}


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

    for n0 in node.children:
        n = footprints_dictio[n0]
        skippable = skippable and n[SKIPPABLE]
        sequence = sequence.union(n[SEQUENCE])
        parallel = parallel.union(n[PARALLEL])
        activities = activities.union(n[ACTIVITIES])

    # adds the footprints
    i = 0
    while i < len(node.children)-1:
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
    i = len(node.children)-1
    while i >= 0:
        n = footprints_dictio[node.children[i]]
        end_activities = end_activities.union(n[END_ACTIVITIES])
        if not n[SKIPPABLE]:
            break
        i = i - 1

    sequence, parallel = fix_fp(sequence, parallel)

    return {START_ACTIVITIES: start_activities, END_ACTIVITIES: end_activities, ACTIVITIES: activities,
            SKIPPABLE: skippable, SEQUENCE: sequence, PARALLEL: parallel}


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
    skippable = True
    sequence = set()
    parallel = set()

    for n0 in node.children:
        n = footprints_dictio[n0]
        skippable = skippable and n[SKIPPABLE]
        sequence = sequence.union(n[SEQUENCE])
        parallel = parallel.union(n[PARALLEL])
        activities = activities.union(n[ACTIVITIES])

    do = footprints_dictio[node.children[0]]
    redo = footprints_dictio[node.children[1]]

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
            SKIPPABLE: skippable, SEQUENCE: sequence, PARALLEL: parallel}


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
    elif node.operator == Operator.PARALLEL:
        return get_footprints_parallel(node, footprints_dictio)
    elif node.operator == Operator.SEQUENCE:
        return get_footprints_sequence(node, footprints_dictio)
    elif node.operator == Operator.LOOP:
        return get_footprints_loop(node, footprints_dictio)


def apply(tree, parameters=None):
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
    to_visit = [tree]
    all_nodes = set()
    while len(to_visit) > 0:
        n = to_visit.pop(0)
        all_nodes.add(n)
        for child in n.children:
            to_visit.append(child)
    # starts to visit the tree from the leafs
    bottomup = [x for x in all_nodes if len(x.children) == 0]
    # then add iteratively the parent
    i = 0
    while i < len(bottomup):
        parent = bottomup[i].parent
        if parent is not None and parent not in bottomup:
            is_ok = True
            for child in parent.children:
                if not child in bottomup:
                    is_ok = False
                    break
            if is_ok:
                bottomup.append(parent)
        i = i + 1
    # for each node of the bottom up, proceed to getting the footprints
    footprints_dictio = {}
    for i in range(len(bottomup)):
        footprints_dictio[bottomup[i]] = get_footprints(bottomup[i], footprints_dictio)
    return footprints_dictio[tree]

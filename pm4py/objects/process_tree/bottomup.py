from pm4py.objects.process_tree.pt_operator import Operator


def get_min_trace_length(tree, parameters=None):
    """
    Get the minimum length of a trace allowed by the process tree

    Parameters
    ---------------
    tree
        Process tree
    parameters
        Possible parameters of the algorithm

    Returns
    --------------
    min_trace_length
        The minimum length of a trace
    """
    if parameters is None:
        parameters = {}

    bottomup = get_bottomup_nodes(tree, parameters=parameters)
    min_length_dict = {}
    for i in range(len(bottomup)):
        get_min_length_dict(bottomup[i], min_length_dict)

    return min_length_dict[tree]


def get_min_rem_dict(tree, parameters=None):
    """
    Gets for each node of the tree the minimum number of activities
    that are inserted to 'complete' a trace of the overall tree

    Parameters
    ----------------
    tree
        Process tree
    parameters
        Parameters of the algorithm

    Returns
    ---------------
    min_rem_dict
        Dictionary described in the docstring
    """
    if parameters is None:
        parameters = {}

    bottomup = get_bottomup_nodes(tree, parameters=parameters)
    min_length_dict = {}
    for i in range(len(bottomup)):
        get_min_length_dict(bottomup[i], min_length_dict)

    min_rem_dict = {}
    for i in range(len(bottomup)):
        min_rem_dict[bottomup[i]] = min_length_dict[tree] - min_length_dict[bottomup[i]]

    return min_rem_dict


def get_min_length_dict(node, min_length_dict):
    """
    Populates, given the nodes of a tree in a bottom-up order, the minimum length dictionary
    (every trace generated from that point of the tree has at least length N)

    Parameters
    ---------------
    node
        Node
    min_length_dict
        Dictionary that is populated in-place
    """
    if len(node.children) == 0:
        if node.label is None:
            min_length_dict[node] = 0
        else:
            min_length_dict[node] = 1
    elif node.operator == Operator.XOR:
        min_length_dict[node] = min(min_length_dict[x] for x in node.children)
    elif node.operator == Operator.PARALLEL or node.operator == Operator.SEQUENCE:
        min_length_dict[node] = sum(min_length_dict[x] for x in node.children)
    elif node.operator == Operator.LOOP:
        min_length_dict[node] = min_length_dict[node.children[0]]


def get_bottomup_nodes(tree, parameters=None):
    """
    Gets the nodes of a tree in a bottomup order (leafs come first, the master node comes after)

    Parameters
    --------------
    tree
        Process tree
    parameters
        Parameters of the algorithm

    Returns
    -------------
    bottomup_nodes
        Nodes of the tree in a bottomup order
    """
    if parameters is None:
        parameters = {}

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

    return bottomup

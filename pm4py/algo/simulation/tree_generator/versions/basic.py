import random
import string

from pm4py.objects.process_tree.process_tree import ProcessTree
from pm4py.objects.process_tree.pt_operator import Operator


def generate_random_string(N):
    """
    Generate a random string

    Parameters
    -------------
    N
        length of the string

    Returns
    -------------
    random_string
        Random string
    """
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))


def get_random_operator():
    """
    Gets a random operator

    Returns
    ------------
    operator
        Operator
    """
    r = random.random()
    if r < 0.25:
        return Operator.SEQUENCE
    elif r < 0.5:
        return Operator.LOOP
    elif r < 0.75:
        return Operator.XOR
    else:
        return Operator.PARALLEL


def apply(parameters=None):
    """
    Generate a process tree

    Parameters
    ------------
    parameters
        Paramters of the algorithm, including:
            rec_depth -> current recursion depth
            min_rec_depth -> minimum recursion depth
            max_rec_depth -> maximum recursion depth
            prob_leaf -> Probability to get a leaf

    Returns
    ------------
    tree
        Process tree
    """
    if parameters is None:
        parameters = {}

    rec_depth = parameters["rec_depth"] if "rec_depth" in parameters else 0
    min_rec_depth = parameters["min_rec_depth"] if "min_rec_depth" in parameters else 1
    max_rec_depth = parameters["max_rec_depth"] if "max_rec_depth" in parameters else 3
    prob_leaf = parameters["prob_leaf"] if "prob_leaf" in parameters else 0.25

    next_parameters = {"rec_depth": rec_depth + 1, "min_rec_depth": min_rec_depth, "max_rec_depth": max_rec_depth,
                       "prob_leaf": prob_leaf}

    is_leaf = False

    if min_rec_depth <= rec_depth <= max_rec_depth:
        r = random.random()
        if r < prob_leaf:
            is_leaf = True
    elif rec_depth > max_rec_depth:
        is_leaf = True

    if is_leaf:
        current_tree = ProcessTree(label=generate_random_string(6))
    elif rec_depth == 0:
        current_tree = ProcessTree(operator=Operator.SEQUENCE)
        start = ProcessTree(label=generate_random_string(6), parent=current_tree)
        current_tree.children.append(start)
        node = apply(parameters=next_parameters)
        node.parent = current_tree
        current_tree.children.append(node)
        end = ProcessTree(label=generate_random_string(6))
        end.parent = current_tree
        current_tree.children.append(end)
    else:
        o = get_random_operator()

        current_tree = ProcessTree(operator=o)
        if o == Operator.SEQUENCE:
            n_min = 2
            n_max = 6
            selected_n = random.randrange(n_min, n_max)
            for i in range(selected_n):
                child = apply(parameters=next_parameters)
                child.parent = current_tree
                current_tree.children.append(child)
        elif o == Operator.LOOP:
            do = apply(parameters=next_parameters)
            do.parent = current_tree
            current_tree.children.append(do)
            redo = apply(parameters=next_parameters)
            redo.parent = current_tree
            current_tree.children.append(redo)
            exit = ProcessTree(parent=current_tree)
            current_tree.children.append(exit)
        elif o == Operator.XOR:
            n_min = 2
            n_max = 5
            selected_n = random.randrange(n_min, n_max)
            for i in range(selected_n):
                child = apply(parameters=next_parameters)
                child.parent = current_tree
                current_tree.children.append(child)
        elif o == Operator.PARALLEL:
            n_min = 2
            n_max = 4
            selected_n = random.randrange(n_min, n_max)
            for i in range(selected_n):
                child = apply(parameters=next_parameters)
                child.parent = current_tree
                current_tree.children.append(child)
    return current_tree

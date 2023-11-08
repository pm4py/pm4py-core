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
import random
import string

from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.objects.process_tree.obj import Operator
from enum import Enum
from pm4py.util import exec_utils
from typing import Optional, Dict, Any, Union


class Parameters(Enum):
    REC_DEPTH = "rec_depth"
    MIN_REC_DEPTH = "min_rec_depth"
    MAX_REC_DEPTH = "max_rec_depth"
    PROB_LEAF = "prob_leaf"


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


def apply(parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> ProcessTree:
    """
    Generate a process tree

    Parameters
    ------------
    parameters
        Paramters of the algorithm, including:
            Parameters.REC_DEPTH -> current recursion depth
            Parameters.MIN_REC_DEPTH -> minimum recursion depth
            Parameters.MAX_REC_DEPTH -> maximum recursion depth
            Parameters.PROB_LEAF -> Probability to get a leaf

    Returns
    ------------
    tree
        Process tree
    """
    if parameters is None:
        parameters = {}

    rec_depth = exec_utils.get_param_value(Parameters.REC_DEPTH, parameters, 0)
    min_rec_depth = exec_utils.get_param_value(Parameters.MIN_REC_DEPTH, parameters, 1)
    max_rec_depth = exec_utils.get_param_value(Parameters.MAX_REC_DEPTH, parameters, 3)
    prob_leaf = exec_utils.get_param_value(Parameters.PROB_LEAF, parameters, 0.25)

    next_parameters = {Parameters.REC_DEPTH: rec_depth + 1, Parameters.MIN_REC_DEPTH: min_rec_depth,
                       Parameters.MAX_REC_DEPTH: max_rec_depth,
                       Parameters.PROB_LEAF: prob_leaf}

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

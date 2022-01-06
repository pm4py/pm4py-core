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
import copy
import sys
from typing import Dict, Tuple, Optional, List

from pm4py.objects.process_tree.utils import generic as ptu
from pm4py.objects.process_tree.obj import Operator
from pm4py.objects.process_tree.obj import ProcessTree

ProcessTreeState = Dict[Tuple[int, ProcessTree], ProcessTree.OperatorState]


def get_initial_state(tree: ProcessTree) -> ProcessTreeState:
    state = dict()
    state[(id(tree), tree)] = ProcessTree.OperatorState.FUTURE
    path = [(tree, ProcessTree.OperatorState.FUTURE)]
    e_path, state = enable_vertex(tree, state)
    path.extend(e_path)
    return state


def transform_tree(tree: ProcessTree, state_type: ProcessTree.OperatorState, state: ProcessTreeState) -> Tuple[
    List[Tuple[ProcessTree, ProcessTree.OperatorState]], ProcessTreeState]:
    state = copy.copy(state)
    path = list()
    if (id(tree), tree) not in state or state[(id(tree), tree)] != state_type:
        state[(id(tree), tree)] = state_type
        path = [(tree, state_type)]
    for c in tree.children:
        e_path, state = transform_tree(c, state_type, state)
        path.extend(e_path)
    return path, state


def can_enable(tree: ProcessTree, state: ProcessTreeState) -> bool:
    if ptu.is_in_state(tree, ProcessTree.OperatorState.FUTURE, state):
        if ptu.is_root(tree):
            return True
        if ptu.is_in_state(tree.parent, ProcessTree.OperatorState.OPEN, state):
            if ptu.is_any_operator_of(tree.parent, [Operator.PARALLEL, Operator.OR]):
                return True
            elif ptu.is_operator(tree.parent, Operator.XOR):
                return frozenset(map(lambda child: state[(id(child), child)], tree.parent.children)) == {
                    ProcessTree.OperatorState.FUTURE}
            elif ptu.is_operator(tree.parent, Operator.SEQUENCE):
                return True if tree.parent.children.index(tree) == 0 else ptu.is_in_state(
                    tree.parent.children[tree.parent.children.index(tree) - 1],
                    ProcessTree.OperatorState.CLOSED, state)
            elif ptu.is_operator(tree.parent, Operator.LOOP):
                return frozenset(map(lambda child: state[(id(child), child)], tree.parent.children)) == {
                    ProcessTree.OperatorState.FUTURE, ProcessTree.OperatorState.CLOSED}
    return False


def can_open(tree: ProcessTree, state: ProcessTreeState) -> bool:
    return ptu.is_in_state(tree, ProcessTree.OperatorState.ENABLED, state)


def can_close(tree: ProcessTree, state: ProcessTreeState) -> bool:
    if ptu.is_leaf(tree):
        return ptu.is_in_state(tree, ProcessTree.OperatorState.OPEN, state)
    elif ptu.is_any_operator_of(tree, [Operator.SEQUENCE, Operator.PARALLEL, Operator.XOR]):
        return frozenset(map(lambda child: state[(id(child), child)], tree.children)) == {
            ProcessTree.OperatorState.CLOSED}
    elif ptu.is_any_operator_of(tree, [Operator.OR]):
        return frozenset(map(lambda child: state[(id(child), child)], tree.children)) == {
            ProcessTree.OperatorState.CLOSED, ProcessTree.OperatorState.FUTURE}
    elif ptu.is_operator(tree, Operator.LOOP):
        return ptu.is_in_state(tree.children[0], ProcessTree.OperatorState.CLOSED, state) and ptu.is_in_state(
            tree.children[1], ProcessTree.OperatorState.FUTURE, state)


def close_vertex(tree: ProcessTree, state: ProcessTreeState) -> Tuple[Optional[
                                                                          List[Tuple[
                                                                              ProcessTree, ProcessTree.OperatorState]]],
                                                                      Optional[ProcessTreeState]]:
    if can_close(tree, state):
        current_state = state[(id(tree), tree)]
        path = list()
        state = copy.copy(state)
        for c in tree.children:
            if not ptu.is_in_state(c, ProcessTree.OperatorState.CLOSED, state):
                e_path, state = transform_tree(c, ProcessTree.OperatorState.CLOSED, state)
                path.extend(e_path)
        state[(id(tree), tree)] = ProcessTree.OperatorState.CLOSED
        path.append((tree, ProcessTree.OperatorState.CLOSED))
        # if tree is a redo, then we will always need to execute the do part of the surrounding loop
        if ptu.is_operator(tree.parent, Operator.LOOP) and id(tree) == id(tree.parent.children[
            1]) and current_state == ProcessTree.OperatorState.OPEN:
            e_path, state = enable_vertex(tree.parent.children[0], state)
            path.extend(e_path)
    else:
        state, path = None, None
    return path, state


def enable_vertex(tree: ProcessTree, state: ProcessTreeState) -> Tuple[Optional[
                                                                           List[Tuple[
                                                                               ProcessTree, ProcessTree.OperatorState]]],
                                                                       Optional[ProcessTreeState]]:
    if state[(id(tree), tree)] == ProcessTree.OperatorState.ENABLED:
        return list(), state
    if can_enable(tree, state):
        state = copy.copy(state)
        path = list()
        state[(id(tree), tree)] = ProcessTree.OperatorState.ENABLED
        path.append((tree, ProcessTree.OperatorState.ENABLED))
        if ptu.is_operator(tree.parent, Operator.LOOP):
            if id(tree) == id(tree.parent.children[0]):
                e_path, state = transform_tree(tree.parent.children[1], ProcessTree.OperatorState.FUTURE, state)
                path.extend(e_path)
            if id(tree) == id(tree.parent.children[1]):
                e_path, state = transform_tree(tree.parent.children[0], ProcessTree.OperatorState.FUTURE, state)
                path.extend(e_path)
        if ptu.is_operator(tree.parent, Operator.XOR):
            for c in tree.parent.children:
                if id(c) != id(tree):
                    e_path, state = transform_tree(c, ProcessTree.OperatorState.CLOSED, state)
                    path.extend(e_path)
        for c in tree.children:
            e_path, state = transform_tree(c, ProcessTree.OperatorState.FUTURE, state)
            path.extend(e_path)
        return path, state
    else:
        return None, None


def open_vertex(tree: ProcessTree, state: ProcessTreeState) -> Tuple[Optional[
                                                                         List[Tuple[
                                                                             ProcessTree, ProcessTree.OperatorState]]],
                                                                     Optional[ProcessTreeState]]:
    if can_open(tree, state):
        state = copy.copy(state)
        path = list()
        state[(id(tree), tree)] = ProcessTree.OperatorState.OPEN
        path.append((tree, ProcessTree.OperatorState.OPEN))
        if ptu.is_any_operator_of(tree, [Operator.XOR, Operator.OR, Operator.PARALLEL]):
            for c in tree.children:
                state[(id(c), c)] = ProcessTree.OperatorState.FUTURE
                path.append((c, ProcessTree.OperatorState.FUTURE))
        elif ptu.is_any_operator_of(tree, [Operator.SEQUENCE, Operator.LOOP]):
            state[(id(tree.children[0]), tree.children[0])] = ProcessTree.OperatorState.ENABLED
            path.append((tree.children[0], ProcessTree.OperatorState.ENABLED))
            for c in tree.children[1:]:
                state[(id(c), c)] = ProcessTree.OperatorState.FUTURE
                path.append((c, ProcessTree.OperatorState.FUTURE))
        return path, state
    else:
        return None, None


def shortest_path_to_open(tree: ProcessTree, state: ProcessTreeState) -> Tuple[
    List[Tuple[ProcessTree, ProcessTree.OperatorState]], ProcessTreeState]:
    if ptu.is_in_state(tree, ProcessTree.OperatorState.OPEN, state):
        return list(), state
    fast_path, fast_state = open_vertex(tree, state)
    if fast_state is not None:
        return fast_path, fast_state
    path, state = shortest_path_to_enable(tree, state)
    if path is not None:
        e_path, state = open_vertex(tree, state)
        path.extend(e_path)
    return path, state


def shortest_path_to_close(tree: ProcessTree, state: ProcessTreeState) -> Tuple[
    List[Tuple[ProcessTree, ProcessTree.OperatorState]], ProcessTreeState]:
    if ptu.is_in_state(tree, ProcessTree.OperatorState.CLOSED, state):
        return list(), state
    fast_path, fast_state = close_vertex(tree, state)
    if fast_state is not None:
        return fast_path, fast_state
    path, state = shortest_path_to_open(tree, state)
    if ptu.is_leaf(tree):
        e_path, state = close_vertex(tree, state)
        path.extend(e_path)
        return path, state
    elif ptu.is_any_operator_of(tree, [Operator.SEQUENCE, Operator.PARALLEL]):
        for c in tree.children:
            e_path, state = shortest_path_to_close(c, state)
            path.extend(e_path)
    elif ptu.is_operator(tree, Operator.LOOP):
        if state[(id(tree.children[0]), tree.children[0])] in {ProcessTree.OperatorState.ENABLED,
                                                               ProcessTree.OperatorState.OPEN}:
            e_path, state = shortest_path_to_close(tree.children[0], state)
            path.extend(e_path)
        elif state[(id(tree.children[1]), tree.children[1])] in {ProcessTree.OperatorState.ENABLED,
                                                                 ProcessTree.OperatorState.OPEN}:
            e_path, state = shortest_path_to_close(tree.children[1], state)
            path.extend(e_path)
            e_path, state = shortest_path_to_open(tree.children[0], state)
            path.extend(e_path)
            e_path, state = shortest_path_to_close(tree.children[0], state)
            path.extend(e_path)
    elif tree.operator in {Operator.XOR, Operator.OR}:
        busy = False
        for c in tree.children:
            if state[(id(c), c)] in {ProcessTree.OperatorState.ENABLED, ProcessTree.OperatorState.OPEN}:
                e_path, state = shortest_path_to_close(c, state)
                path.extend(e_path)
                busy = True
        if not busy:
            cur_path, cur_state, cur_path_costs = list(), copy.copy(state), sys.maxsize
            for c in tree.children:
                if state[(id(c), c)] != ProcessTree.OperatorState.CLOSED:
                    candidate_p, candidate_s = shortest_path_to_close(c, state)
                    candidate_costs = len(list(filter(lambda t: t[0].operator is None and t[0].label is not None and t[
                        1] == ProcessTree.OperatorState.OPEN, candidate_p)))
                    if candidate_costs < cur_path_costs:
                        cur_path, cur_state, cur_path_costs = candidate_p, candidate_s, candidate_costs
            path.extend(cur_path)
            state = cur_state
    e_path, state = close_vertex(tree, state)
    path.extend(e_path)
    return path, state


def shortest_path_to_enable(tree: ProcessTree, state: ProcessTreeState) -> Tuple[
    List[Tuple[ProcessTree, ProcessTree.OperatorState]], ProcessTreeState]:
    if state[(id(tree), tree)] == ProcessTree.OperatorState.ENABLED:
        return list(), state
    fast_path, fast_state = enable_vertex(tree, state)
    if fast_state is not None:
        return fast_path, fast_state
    if state[(id(tree), tree)] == ProcessTree.OperatorState.FUTURE:
        path, state = shortest_path_to_open(tree.parent, state)
        if tree.parent.operator in {Operator.XOR, Operator.PARALLEL, Operator.OR}:
            e_path, state = enable_vertex(tree, state)
            if state is not None:  # choice if another choice has already been taken!
                path.extend(e_path)
        if tree.parent.operator == Operator.SEQUENCE:
            for i, c in enumerate(tree.parent.children):
                if id(c) == id(tree):
                    if i > 0:
                        e_path, state = enable_vertex(tree, state)
                        path.extend(e_path)
                    break
                else:
                    e_path, state = shortest_path_to_close(c, state)
                    path.extend(e_path)
        elif tree.parent.operator == Operator.LOOP:
            if id(tree) == id(tree.parent.children[0]):
                if state[(id(tree.parent.children[1]), tree.parent.children[1])] not in {
                    ProcessTree.OperatorState.FUTURE,
                    ProcessTree.OperatorState.CLOSED}:
                    e_path, state = shortest_path_to_close(tree.parent.children[1], state)
                    path.extend(e_path)
                e_path, state = enable_vertex(tree, state)
                path.extend(e_path)
            else:
                e_path, state = shortest_path_to_close(tree.parent.children[0], state)
                path.extend(e_path)
                e_path, state = enable_vertex(tree, state)
                path.extend(e_path)
        return path, state
    else:
        path, state = shortest_path_to_close(tree, state)
        parent = tree.parent
        while parent is not None:
            if parent.operator == Operator.LOOP and state[(id(parent), parent)] == ProcessTree.OperatorState.OPEN:
                break
            parent = parent.parent
        if parent is not None and parent.operator == Operator.LOOP:
            if state[(id(parent.children[0]), parent.children[0])] == ProcessTree.OperatorState.OPEN:
                e_path, state = shortest_path_to_close(parent.children[0], state)
                path.extend(e_path)
                e_path, state = shortest_path_to_enable(parent.children[1], state)
                path.extend(e_path)
            elif state[(id(parent.children[1]), parent.children[1])] == ProcessTree.OperatorState.OPEN:
                e_path, state = shortest_path_to_close(parent.children[1], state)
                path.extend(e_path)
                e_path, state = shortest_path_to_enable(parent.children[0], state)
                path.extend(e_path)
            elif state[(id(parent.children[0]), parent.children[0])] == ProcessTree.OperatorState.FUTURE:
                e_path, state = shortest_path_to_enable(parent.children[0], state)
                path.extend(e_path)
            elif state[(id(parent.children[1]), parent.children[1])] == ProcessTree.OperatorState.FUTURE:
                e_path, state = shortest_path_to_enable(parent.children[1], state)
                path.extend(e_path)
            e_path, state = shortest_path_to_enable(tree, state)
            path.extend(e_path)
            return path, state
        else:
            return None, None

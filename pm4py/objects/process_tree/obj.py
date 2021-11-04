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


class Operator(Enum):
    # sequence operator
    SEQUENCE = '->'
    # exclusive choice operator
    XOR = 'X'
    # parallel operator
    PARALLEL = '+'
    # loop operator
    LOOP = '*'
    # or operator
    OR = 'O'

    '''
    SEQUENCE = u'\u2192'
    XOR = u'\u00d7'
    PARALLEL = u'\u002b'
    LOOP = u'\u27f2'
    '''

    def __str__(self):
        """
        Provides a string representation of the current operator

        Returns
        -----------
        stri
            String representation of the process tree
        """
        return self.value

    def __repr__(self):
        """
        Provides a string representation of the current operator

        Returns
        -----------
        stri
            String representation of the process tree
        """
        return self.value


class ProcessTree(object):

    class OperatorState(Enum):
        ENABLED = "enabled"
        OPEN = "open"
        CLOSED = "closed"
        FUTURE = "future"

    def __init__(self, operator=None, parent=None, children=None, label=None):
        """
        Constructor

        Parameters
        ------------
        operator
            Operator (of the current node) of the process tree
        parent
            Parent node (of the current node)
        children
            List of children of the current node
        label
            Label (of the current node)
        """
        self._operator = operator
        self._parent = parent
        self._children = list() if children is None else children
        self._label = label

    def __hash__(self):
        if self.label is not None:
            return hash(self.label)
        elif len(self.children) == 0:
            return 37
        else:
            h = 1337
            for i in range(len(self.children)):
                h += 41 * i * hash(self.children[i])
            if self.operator == Operator.SEQUENCE:
                h = h * 13
            elif self.operator == Operator.XOR:
                h = h * 17
            elif self.operator == Operator.OR:
                h = h * 23
            elif self.operator == Operator.PARALLEL:
                h = h * 29
            elif self.operator == Operator.LOOP:
                h = h * 37
            return h % 268435456

    def _set_operator(self, operator):
        self._operator = operator

    def _set_parent(self, parent):
        self._parent = parent

    def _set_label(self, label):
        self._label = label

    def _set_children(self, children):
        self._children = children

    def _get_children(self):
        return self._children

    def _get_parent(self):
        return self._parent

    def _get_operator(self):
        return self._operator

    def _get_label(self):
        return self._label

    def __eq__(self, other):
        if isinstance(other, ProcessTree):
            if self.label is not None:
                return True if other.label == self.label else False
            elif len(self.children) == 0:
                return other.label is None and len(other.children) == 0
            else:
                if self.operator == other.operator:
                    if len(self.children) != len(other.children):
                        return False
                    else:
                        for i in range(len(self.children)):
                            if self.children[i] != other.children[i]:
                                return False
                        return True
                else:
                    return False
        return False

    def __repr__(self):
        """
        Returns a string representation of the process tree

        Returns
        ------------
        stri
            String representation of the process tree
        """
        if self.operator is not None:
            rep = str(self._operator) + '( '
            for i in range(0, len(self._children)):
                child = self._children[i]
                if len(child.children) == 0:
                    if child.label is not None:
                        rep += '\'' + str(child) + '\'' + ', ' if i < len(self._children) - 1 else '\'' + str(
                            child) + '\''
                    else:
                        rep += str(child) + ', ' if i < len(self._children) - 1 else str(child)
                else:
                    rep += str(child) + ', ' if i < len(self._children) - 1 else str(child)
            return rep + ' )'
        elif self.label is not None:
            return self.label
        else:
            return '*tau*'

    def __str__(self):
        """
        Returns a string representation of the process tree

        Returns
        ------------
        stri
            String representation of the process tree
        """
        return self.__repr__()

    def _get_root(self):
        root = self
        while root._get_parent() is not None:
            root = root._get_parent()
        return root

    def _get_leaves(self):
        root = self._get_root()
        leaves = root
        if root._get_children != list():
            leaves = root._get_children()
            change_of_leaves = True
            while change_of_leaves:
                leaves_to_replace = list()
                new_leaves = list()
                for leaf in leaves:
                    if leaf._get_children() != list():
                        leaves_to_replace.append(leaf)
                    else:
                        new_leaves.append(leaf)
                if leaves_to_replace != list():
                    for leaf in leaves_to_replace:
                        for el in leaf.children:
                            new_leaves.append(el)
                    leaves = new_leaves
                else:
                    change_of_leaves = False
        return leaves

    def _print_tree(self):
        root = self._get_root()
        print(root)

    parent = property(_get_parent, _set_parent)
    children = property(_get_children, _set_children)
    operator = property(_get_operator, _set_operator)
    label = property(_get_label, _set_label)

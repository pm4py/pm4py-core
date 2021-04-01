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


def fix_parent_pointers(pt):
    """
    Ensures consistency to the parent pointers in the process tree

    Parameters
    --------------
    pt
        Process tree
    """
    for child in pt.children:
        child.parent = pt
        if child.children:
            fix_parent_pointers(child)


def fix_one_child_xor_flower(tree):
    """
    Fixes a 1 child XOR that is added when single-activities flowers are found

    Parameters
    --------------
    tree
        Process tree
    """
    if tree.parent is not None and tree.operator is Operator.XOR and len(tree.children) == 1:
        for child in tree.children:
            child.parent = tree.parent
            tree.parent.children.append(child)
            del tree.parent.children[tree.parent.children.index(tree)]
    else:
        for child in tree.children:
            fix_one_child_xor_flower(child)

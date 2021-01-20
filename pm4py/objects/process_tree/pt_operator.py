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

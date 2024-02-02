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
from pm4py.util import nx_utils
import sys


def exact_match_minimum_average(l1, l2):
    """
    Performs an exact matching, having minimum average,
    of two lists of times (a timestamp of the first list
    is matched with a timestamp of the second list that
    is greater or equal). Some timestamps in the two lists
    may be left out of the matching.

    Parameters
    ---------------
    l1
        First list of times
    l2
        Second list of times

    Returns
    ---------------
    exact_matching
        Exact matching (list of tuples having as first element
        an element of the first list, and as second element
        an element of the second list)
    """
    G = nx_utils.Graph()
    for i in range(len(l1)):
        G.add_node(i)
    for j in range(len(l2)):
        G.add_node(len(l1) + j)
    for i in range(len(l1)):
        for j in range(len(l2)):
            if l1[i] <= l2[j]:
                G.add_edge(i, len(l1) + j, weight=(l2[j] - l1[i]))
            else:
                G.add_edge(i, len(l1) + j, weight=sys.maxsize)
    matching0 = {x: y for x, y in nx_utils.minimum_weight_full_matching(G).items() if x < len(l1)}
    matching = []
    for k1, k2 in matching0.items():
        v1 = l1[k1]
        v2 = l2[k2 - len(l1)]
        if v2 >= v1:
            matching.append((v1, v2))
    return matching

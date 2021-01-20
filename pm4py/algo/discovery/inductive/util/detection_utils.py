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
from copy import copy
import numpy as np
import pkgutil
import logging


def get_connected_components(ingoing, outgoing, activities):
    """
    Get connected components in the DFG graph

    Parameters
    -----------
    ingoing
        Ingoing attributes
    outgoing
        Outgoing attributes
    activities
        Activities to consider
    """
    activities_considered = set()

    connected_components = []

    for act in ingoing:
        ingoing_act = set(ingoing[act].keys())
        if act in outgoing:
            ingoing_act = ingoing_act.union(set(outgoing[act].keys()))

        ingoing_act.add(act)

        if ingoing_act not in connected_components:
            connected_components.append(ingoing_act)
            activities_considered = activities_considered.union(set(ingoing_act))

    for act in outgoing:
        if act not in ingoing:
            outgoing_act = set(outgoing[act].keys())
            outgoing_act.add(act)
            if outgoing_act not in connected_components:
                connected_components.append(outgoing_act)
            activities_considered = activities_considered.union(set(outgoing_act))

    for activ in activities:
        if activ not in activities_considered:
            added_set = set()
            added_set.add(activ)
            connected_components.append(added_set)
            activities_considered.add(activ)

    max_it = len(connected_components)
    for it in range(max_it - 1):
        something_changed = False

        old_connected_components = copy(connected_components)
        connected_components = []

        for i in range(len(old_connected_components)):
            conn1 = old_connected_components[i]

            if conn1 is not None:
                for j in range(i + 1, len(old_connected_components)):
                    conn2 = old_connected_components[j]
                    if conn2 is not None:
                        inte = conn1.intersection(conn2)

                        if len(inte) > 0:
                            conn1 = conn1.union(conn2)
                            something_changed = True
                            old_connected_components[j] = None

            if conn1 is not None and conn1 not in connected_components:
                connected_components.append(conn1)

        if not something_changed:
            break

    return connected_components


def perform_list_union(lst):
    """
    Performs the union of a list of sets

    Parameters
    ------------
    lst
        List of sets

    Returns
    ------------
    un_set
        United set
    """
    ret = set()
    for s in lst:
        ret = ret.union(s)
    return ret


def get_connection_matrix(strongly_connected_components, dfg):
    """
    Gets the connection matrix between connected components

    Parameters
    ------------
    strongly_connected_components
        Strongly connected components
    dfg
        DFG

    Returns
    ------------
    connection_matrix
        Matrix reporting the connections
    """
    act_to_scc = {}
    for index, comp in enumerate(strongly_connected_components):
        for act in comp:
            act_to_scc[act] = index
    conn_matrix = np.zeros((len(strongly_connected_components), len(strongly_connected_components)))
    for el in dfg:
        comp_el_0 = act_to_scc[el[0][0]]
        comp_el_1 = act_to_scc[el[0][1]]
        if not comp_el_0 == comp_el_1:
            conn_matrix[comp_el_1][comp_el_0] = 1
            if conn_matrix[comp_el_0][comp_el_1] == 0:
                conn_matrix[comp_el_0][comp_el_1] = -1
    return conn_matrix

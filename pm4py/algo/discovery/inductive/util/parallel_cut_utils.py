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
def check_if_comp_is_completely_unconnected(conn1, conn2, ingoing, outgoing):
    """
    Checks if two connected components are completely unconnected each other

    Parameters
    -------------
    conn1
        First connected component
    conn2
        Second connected component
    ingoing
        Ingoing dictionary
    outgoing
        Outgoing dictionary

    Returns
    -------------
    boolean
        Boolean value that tells if the two connected components are completely unconnected
    """
    for act1 in conn1:
        for act2 in conn2:
            if ((act1 in outgoing and act2 in outgoing[act1]) and (
                    act1 in ingoing and act2 in ingoing[act1])):
                return False
    return True


def merge_connected_components(conn_components, ingoing, outgoing):
    """
    Merge the unconnected connected components

    Parameters
    -------------
    conn_components
        Connected components
    ingoing
        Ingoing dictionary
    outgoing
        Outgoing dictionary

    Returns
    -------------
    conn_components
        Merged connected components
    """
    i = 0
    while i < len(conn_components):
        conn1 = conn_components[i]
        j = i + 1
        while j < len(conn_components):
            conn2 = conn_components[j]
            if check_if_comp_is_completely_unconnected(conn1, conn2, ingoing, outgoing):
                conn_components[i] = set(conn_components[i]).union(set(conn_components[j]))
                del conn_components[j]
                continue
            j = j + 1
        i = i + 1
    return conn_components


def check_par_cut(conn_components, ingoing, outgoing):
    """
    Checks if in a parallel cut all relations are present

    Parameters
    -----------
    conn_components
        Connected components
    ingoing
        Ingoing dictionary
    outgoing
        Outgoing dictionary
    """
    conn_components = merge_connected_components(conn_components, ingoing, outgoing)
    conn_components = sorted(conn_components, key=lambda x: len(x))
    sthing_changed = True
    while sthing_changed:
        sthing_changed = False
        i = 0
        while i < len(conn_components):
            ok_comp_idx = []
            partly_ok_comp_idx = []
            not_ok_comp_idx = []
            conn1 = conn_components[i]
            j = i + 1
            while j < len(conn_components):
                count_good = 0
                count_notgood = 0
                conn2 = conn_components[j]
                for act1 in conn1:
                    for act2 in conn2:
                        if not ((act1 in outgoing and act2 in outgoing[act1]) and (
                                act1 in ingoing and act2 in ingoing[act1])):
                            count_notgood = count_notgood + 1
                            if count_good > 0:
                                break
                        else:
                            count_good = count_good + 1
                            if count_notgood > 0:
                                break
                if count_notgood == 0:
                    ok_comp_idx.append(j)
                elif count_good > 0:
                    partly_ok_comp_idx.append(j)
                else:
                    not_ok_comp_idx.append(j)
                j = j + 1
            if not_ok_comp_idx or partly_ok_comp_idx:
                if partly_ok_comp_idx:
                    conn_components[i] = set(conn_components[i]).union(set(conn_components[partly_ok_comp_idx[0]]))
                    del conn_components[partly_ok_comp_idx[0]]
                    sthing_changed = True
                    continue
                else:
                    return False
            if sthing_changed:
                break
            i = i + 1
    if len(conn_components) > 1:
        return conn_components
    return None


def check_sa_ea_for_each_branch(conn_components, start_activities, end_activities):
    """
    Checks if each branch of the parallel cut has a start
    and an end node of the subgraph

    Parameters
    --------------
    conn_components
        Parallel cut

    Returns
    -------------
    boolean
        True if each branch of the parallel cut has a start and an end node
    """
    if conn_components is None:
        return False

    for comp in conn_components:
        comp_sa_ok = False
        comp_ea_ok = False

        for sa in start_activities:
            if sa in comp:
                comp_sa_ok = True
                break
        for ea in end_activities:
            if ea in comp:
                comp_ea_ok = True
                break

        if not (comp_sa_ok and comp_ea_ok):
            return False

    return True

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
from collections import Counter
from copy import copy

import numpy as np

from pm4py.util import variants_util, nx_utils


def get_outgoing_edges(dfg):
    """
    Gets outgoing edges of the provided DFG graph
    """
    outgoing = {}
    for el in dfg:
        if type(el[0]) is str:
            if not el[0] in outgoing:
                outgoing[el[0]] = {}
            outgoing[el[0]][el[1]] = dfg[el]
        else:
            if not el[0][0] in outgoing:
                outgoing[el[0][0]] = {}
            outgoing[el[0][0]][el[0][1]] = el[1]
    return outgoing


def get_ingoing_edges(dfg):
    """
    Get ingoing edges of the provided DFG graph
    """
    ingoing = {}
    for el in dfg:
        if type(el[0]) is str:
            if not el[1] in ingoing:
                ingoing[el[1]] = {}
            ingoing[el[1]][el[0]] = dfg[el]
        else:
            if not el[0][1] in ingoing:
                ingoing[el[0][1]] = {}
            ingoing[el[0][1]][el[0][0]] = el[1]
    return ingoing


def infer_start_activities(dfg):
    """
    Infer start activities from a Directly-Follows Graph

    Parameters
    ----------
    dfg
        Directly-Follows Graph

    Returns
    ----------
    start_activities
        Start activities in the log
    """
    ingoing = get_ingoing_edges(dfg)
    outgoing = get_outgoing_edges(dfg)

    start_activities = []

    for act in outgoing:
        if act not in ingoing:
            start_activities.append(act)

    return start_activities


def infer_end_activities(dfg):
    """
    Infer end activities from a Directly-Follows Graph

    Parameters
    ----------
    dfg
        Directly-Follows Graph

    Returns
    ----------
    end_activities
        End activities in the log
    """
    ingoing = get_ingoing_edges(dfg)
    outgoing = get_outgoing_edges(dfg)

    end_activities = []

    for act in ingoing:
        if act not in outgoing:
            end_activities.append(act)

    return end_activities


def infer_start_activities_from_prev_connections_and_current_dfg(initial_dfg, dfg, activities, include_self=True):
    """
    Infer the start activities from the previous connections

    Parameters
    -----------
    initial_dfg
        Initial DFG
    dfg
        Directly-follows graph
    activities
        List of the activities contained in DFG
    """
    start_activities = set()
    for el in initial_dfg:
        if el[0][1] in activities and not el[0][0] in activities:
            start_activities.add(el[0][1])
    if include_self:
        start_activities = start_activities.union(
            set(infer_start_activities(dfg)))
    return start_activities


def infer_end_activities_from_succ_connections_and_current_dfg(initial_dfg, dfg, activities, include_self=True):
    """
    Infer the end activities from the previous connections

    Parameters
    -----------
    initial_dfg
        Initial DFG
    dfg
        Directly-follows graph
    activities
        List of the activities contained in DFG
    """
    end_activities = set()
    for el in initial_dfg:
        if el[0][0] in activities and not el[0][1] in activities:
            end_activities.add(el[0][0])
    if include_self:
        end_activities = end_activities.union(set(infer_end_activities(dfg)))
    return end_activities


def get_outputs_of_outside_activities_going_to_start_activities(initial_dfg, dfg, activities):
    """
    Get outputs of outside activities going to start activities

    Parameters
    ------------
    initial_dfg
        Initial DFG
    dfg
        Directly-follows graph
    activities
        Activities contained in the DFG
    """
    outputs = set()
    start_activities = infer_start_activities_from_prev_connections_and_current_dfg(initial_dfg, dfg, activities,
                                                                                    include_self=False)
    outside_activities_going_to_start_activities = set()
    for el in initial_dfg:
        if el[0][0] not in activities and el[0][1] in start_activities:
            outside_activities_going_to_start_activities.add(el[0][0])
    for el in initial_dfg:
        if el[0][0] in outside_activities_going_to_start_activities and not el[0][1] in activities:
            outputs.add(el[0][1])
    outputs = outputs - outside_activities_going_to_start_activities
    return outputs


def get_inputs_of_outside_activities_reached_by_end_activities(initial_dfg, dfg, activities):
    """
    Get inputs of outside activities going to start activities

    Parameters
    ------------
    initial_dfg
        Initial DFG
    dfg
        Directly-follows graph
    activities
        Activities contained in the DFG
    """
    inputs = set()
    end_activities = infer_end_activities_from_succ_connections_and_current_dfg(initial_dfg, dfg, activities,
                                                                                include_self=False)
    input_activities_reached_by_end_activities = set()
    for el in initial_dfg:
        if el[0][1] not in activities and el[0][0] in end_activities:
            input_activities_reached_by_end_activities.add(el[0][1])
    for el in initial_dfg:
        if el[0][1] in input_activities_reached_by_end_activities and not el[0][0] in activities:
            inputs.add(el[0][0])
    inputs = inputs - input_activities_reached_by_end_activities

    return inputs


def get_activities_from_dfg(dfg):
    """
    Get the list of attributes directly from DFG graph

    Parameters
    -----------
    dfg
        Directly-Follows graph

    Returns
    -----------
    list_activities
        List of activities that are present in the DFG graph
    """
    set_activities = set()
    for el in dfg:
        if type(el[0]) is str:
            set_activities.add(el[0])
            set_activities.add(el[1])
        else:
            set_activities.add(el[0][0])
            set_activities.add(el[0][1])
    list_activities = sorted(list(set_activities))

    return list_activities


def get_max_activity_count(dfg, act):
    """
    Get maximum count of an ingoing/outgoing edge related to an activity

    Parameters
    ------------
    dfg
        Directly-Follows graph
    act
        Activity

    Returns
    ------------
    max_value
        Maximum count of ingoing/outgoing edges to attributes
    """
    ingoing = get_ingoing_edges(dfg)
    outgoing = get_outgoing_edges(dfg)
    max_value = -1
    if act in ingoing:
        for act2 in ingoing[act]:
            if ingoing[act][act2] > max_value:
                max_value = ingoing[act][act2]
    if act in outgoing:
        for act2 in outgoing[act]:
            if outgoing[act][act2] > max_value:
                max_value = outgoing[act][act2]
    return max_value


def sum_ingoutg_val_activ(dictio, activity):
    """
    Gets the sum of ingoing/outgoing values of an activity

    Parameters
    -----------
    dictio
        Dictionary
    activity
        Current examined activity

    Returns
    -----------
    summ
    """
    summ = 0
    for act2 in dictio[activity]:
        summ += dictio[activity][act2]
    return summ


def max_occ_all_activ(dfg):
    """
    Get maximum ingoing/outgoing sum of values related to attributes in DFG graph
    """
    ingoing = get_ingoing_edges(dfg)
    outgoing = get_outgoing_edges(dfg)
    max_value = -1

    for act in ingoing:
        summ = sum_ingoutg_val_activ(ingoing, act)
        if summ > max_value:
            max_value = summ

    for act in outgoing:
        summ = sum_ingoutg_val_activ(outgoing, act)
        if summ > max_value:
            max_value = summ

    return max_value


def max_occ_among_specif_activ(dfg, activities):
    """
    Get maximum ingoing/outgoing sum of values related to attributes in DFG graph
    (here attributes to consider are specified)
    """
    ingoing = get_ingoing_edges(dfg)
    outgoing = get_outgoing_edges(dfg)
    max_value = -1

    for act in activities:
        if act in ingoing:
            summ = sum_ingoutg_val_activ(ingoing, act)
            if summ > max_value:
                max_value = summ
        if act in outgoing:
            summ = sum_ingoutg_val_activ(outgoing, act)
            if summ > max_value:
                max_value = summ

    return max_value


def sum_start_activities_count(dfg):
    """
    Gets the sum of start attributes count inside a DFG

    Parameters
    -------------
    dfg
        Directly-Follows graph

    Returns
    -------------
        Sum of start attributes count
    """
    ingoing = get_ingoing_edges(dfg)
    outgoing = get_outgoing_edges(dfg)

    sum_values = 0

    for act in outgoing:
        if act not in ingoing:
            for act2 in outgoing[act]:
                sum_values += outgoing[act][act2]

    return sum_values


def sum_end_activities_count(dfg):
    """
    Gets the sum of end attributes count inside a DFG

    Parameters
    -------------
    dfg
        Directly-Follows graph

    Returns
    -------------
        Sum of start attributes count
    """
    ingoing = get_ingoing_edges(dfg)
    outgoing = get_outgoing_edges(dfg)

    sum_values = 0

    for act in ingoing:
        if act not in outgoing:
            for act2 in ingoing[act]:
                sum_values += ingoing[act][act2]

    return sum_values


def sum_activities_count(dfg, activities, enable_halving=True):
    """
    Gets the sum of specified attributes count inside a DFG

    Parameters
    -------------
    dfg
        Directly-Follows graph
    activities
        Activities to sum
    enable_halving
        Halves the sum in specific occurrences

    Returns
    -------------
        Sum of start attributes count
    """
    ingoing = get_ingoing_edges(dfg)
    outgoing = get_outgoing_edges(dfg)

    sum_values = 0

    for act in activities:
        if act in outgoing:
            for act2 in outgoing[act]:
                sum_values += outgoing[act][act2]
        if act in ingoing:
            for act2 in ingoing[act]:
                sum_values += ingoing[act][act2]
        if enable_halving:
            if act in ingoing and act in outgoing:
                sum_values = int(sum_values / 2)

    return sum_values


def filter_dfg_on_act(dfg, listact):
    """
    Filter a DFG graph on a list of attributes
    (to produce a projected DFG graph)

    Parameters
    -----------
    dfg
        Current DFG graph
    listact
        List of attributes to filter on
    """
    new_dfg = []
    for el in dfg:
        if el[0][0] in listact and el[0][1] in listact:
            new_dfg.append(el)
    return new_dfg


def negate(dfg):
    """
    Negate relationship in the DFG graph

    Parameters
    ----------
    dfg
        Directly-Follows graph

    Returns
    ----------
    negated_dfg
        Negated Directly-Follows graph (for parallel cut detection)
    """
    negated_dfg = []

    outgoing = get_outgoing_edges(dfg)

    for el in dfg:
        if not (el[0][1] in outgoing and el[0][0] in outgoing[el[0][1]]):
            negated_dfg.append(el)

    return negated_dfg


def get_activities_direction(dfg, activities):
    """
    Calculate activities direction (in a similar way to Heuristics Miner)

    Parameters
    -----------
    dfg
        Directly-follows graph
    activities
        (if provided) activities of the subtree

    Returns
    -----------
    direction
        Dictionary that contains for each direction a number that goes from -1 (all ingoing edges)
        to 1 (all outgoing edges)
    """

    if activities is None:
        activities = get_activities_from_dfg(dfg)

    ingoing_list = get_ingoing_edges(dfg)
    outgoing_list = get_outgoing_edges(dfg)

    direction = {}
    for act in activities:
        outgoing = 0
        ingoing = 0
        if act in outgoing_list:
            outgoing = sum(list(outgoing_list[act].values()))
        if act in ingoing_list:
            ingoing = sum(list(ingoing_list[act].values()))
        dependency = (outgoing - ingoing) / (ingoing + outgoing + 1)
        direction[act] = dependency
    return direction


def get_activities_dirlist(activities_direction):
    """
    Form an ordered list out of a dictionary that contains for each activity
    the direction (going from -1 if all ingoing edges, to 1 if all outgoing edges)

    Parameters
    -----------
    activities_direction
        Dictionary that contains for each direction a number that goes from -1 (all ingoing edges)
        to 1 (all outgoing edges)

    Returns
    ----------
    dirlist
        Sorted list of couples of activity plus the direction
    """
    dirlist = []
    for act in activities_direction:
        dirlist.append([act, activities_direction[act]])
    dirlist = sorted(dirlist, key=lambda x: (x[1], x[0]), reverse=True)
    return dirlist


def get_activities_self_loop(dfg):
    """
    Get attributes that are in self-loop in this subtree

    Parameters
    ----------
    dfg
        Directly-follows graph

    Returns
    ----------
    self_loop_act
        Activities of the graph that are in subloop
    """
    self_loop_act = []

    outgoing = get_outgoing_edges(dfg)

    for act in outgoing:
        if act in list(outgoing[act].keys()):
            self_loop_act.append(act)
    return self_loop_act


def get_connected_components(ingoing, outgoing, activities, force_insert_missing_acti=True):
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
    force_insert_missing_acti
        Force the insertion of a missing activity
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
            activities_considered = activities_considered.union(
                set(ingoing_act))

    for act in outgoing:
        if act not in ingoing:
            outgoing_act = set(outgoing[act].keys())
            outgoing_act.add(act)
            if outgoing_act not in connected_components:
                connected_components.append(outgoing_act)
            activities_considered = activities_considered.union(
                set(outgoing_act))

    if force_insert_missing_acti:
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

    if len(connected_components) == 0:
        for activity in activities:
            connected_components.append([activity])

    return connected_components


def add_to_most_probable_component(comps, act2, ingoing, outgoing):
    """
    Adds a lost component in parallel cut detection to the most probable component

    Parameters
    -------------
    comps
        Connected components
    act2
        Activity that has been missed
    ingoing
        Map of ingoing attributes
    outgoing
        Map of outgoing attributes

    Returns
    -------------
    comps
        Fixed connected components
    """
    sums = []
    idx_max_sum = 0

    for comp in comps:
        summ = 0
        for act1 in comp:
            if act1 in ingoing and act2 in ingoing[act1]:
                summ = summ + ingoing[act1][act2]
            if act1 in outgoing and act2 in outgoing[act1]:
                summ = summ + outgoing[act1][act2]
        sums.append(summ)
        if sums[-1] > sums[idx_max_sum]:
            idx_max_sum = len(sums) - 1

    comps[idx_max_sum].add(act2)

    return comps


def get_all_activities_connected_as_output_to_activity(dfg, activity):
    """
    Gets all the activities that are connected as output to a given activity

    Parameters
    -------------
    dfg
        Directly-follows graph
    activity
        Activity

    Returns
    -------------
    all_activities
        All activities connected as output to a given activity
    """
    all_activities = set()

    for el in dfg:
        if el[0][0] == activity:
            all_activities.add(el[0][1])

    return all_activities


def get_all_activities_connected_as_input_to_activity(dfg, activity):
    """
    Gets all the activities that are connected as input to a given activity

    Parameters
    ------------
    dfg
        Directly-follows graph
    activity
        Activity

    Returns
    ------------
    all_activities
        All activities connected as input to a given activities
    """
    all_activities = set()
    for el in dfg:
        if el[0][1] == activity:
            all_activities.add(el[0][0])
    return all_activities


def get_dfg_np_matrix(dfg):
    """
    Gets a Numpy matrix describing the DFG graph, along with a dictionary
    making correspondence between indexes and activities names

    Parameters
    -------------
    dfg
        Directly-Follows graph

    Returns
    -------------
    matrix
        Matrix describing the DFG
    index_corresp
        Dictionary making correspondence between indexes and activities names
    """
    activities_in_dfg = get_activities_from_dfg(dfg)
    matrix = np.zeros((len(activities_in_dfg), len(activities_in_dfg)))

    for el in dfg:
        if type(el[0]) is str:
            # manage DFG expressed as dictionary (the key is a tuple)
            first_el = el[0]
            second_el = el[1]
            n_occ = dfg[el]
        else:
            # manage DFG expressed as list of: ((act0, act1), count)
            first_el = el[0][0]
            second_el = el[0][1]
            n_occ = el[1]
        act_ind_0 = activities_in_dfg.index(first_el)
        act_ind_1 = activities_in_dfg.index(second_el)
        matrix[act_ind_0, act_ind_1] = n_occ

    index_corresp = {}
    for index, act in enumerate(activities_in_dfg):
        index_corresp[index] = act

    return matrix, index_corresp


def get_dfg_sa_ea_act_from_variants(variants, parameters=None):
    """
    Gets the DFG, the start and end activities, and the activities
    from the dictionary/set/list of variants in the log

    Parameters
    ---------------
    variants
        Dictionary/set/list of variants
    parameters
        Parameters of the algorithm, including:
        - variants_sep: the delimiter splitting activities in a variant

    Returns
    --------------
    dfg
        DFG
    list_act
        List of different activities
    start_activities
        Start activities
    end_activities
        End activities
    """
    if parameters is None:
        parameters = {}
    variants = set(variants_util.get_activities_from_variant(v)
                   for v in variants)
    dfg = dict(Counter(list((x[i], x[i + 1])
               for x in variants for i in range(len(x) - 1))))
    list_act = list(set(y for x in variants for y in x))
    start_activities = dict(Counter(x[0] for x in variants if x))
    end_activities = dict(Counter(x[-1] for x in variants if x))
    return dfg, list_act, start_activities, end_activities


def transform_dfg_to_directed_nx_graph(dfg, activities=None):
    """
    Transform DFG to directed NetworkX graph

    Returns
    ------------
    G
        NetworkX digraph
    nodes_map
        Correspondence between digraph nodes and activities
    """
    if activities is None:
        activities = get_activities_from_dfg(dfg)

    G = nx_utils.DiGraph()
    for act in activities:
        G.add_node(act)
    for el in dfg:
        act1 = el[0][0]
        act2 = el[0][1]
        G.add_edge(act1, act2)
    return G


def get_successors(dfg, activities_model=None):
    """
    Gets the successors of any node of the DFG graph

    Parameters
    ----------------
    dfg
        DFG
    activities_model
        Activities of the process model (if None, it is inferred from the process model)

    Returns
    -----------------
    successors
        Dictionary associating to each node all the descendants
    """
    if activities_model is None:
        activities_model = set(x[0] for x in dfg).union(set(x[1] for x in dfg))
    prev = {x: set() for x in activities_model}
    curr = {x: set() for x in activities_model}
    changed = {x: True for x in activities_model}
    for x in dfg:
        curr[x[0]].add(x[1])
    sthing_diff = True
    while sthing_diff:
        sthing_diff = False
        diff = {}
        for x in prev:
            if changed[x]:
                this_diff = curr[x].difference(prev[x])
                if this_diff:
                    sthing_diff = True
                else:
                    changed[x] = False
                diff[x] = this_diff
        prev = copy(curr)
        for x in diff:
            if changed[x]:
                for y in diff[x]:
                    curr[x] = curr[x].union(curr[y])
    return curr


def get_predecessors(dfg, activities_model=None):
    """
    Gets the predecessors of any node of the DFG graph

    Parameters
    ----------------
    dfg
        DFG
    activities_model
        Activities of the process model (if None, it is inferred from the process model)

    Returns
    -----------------
    predecessors
        Dictionary associating to each node all the ascendants
    """
    if activities_model is None:
        activities_model = set(x[0] for x in dfg).union(set(x[1] for x in dfg))
    prev = {x: set() for x in activities_model}
    curr = {x: set() for x in activities_model}
    changed = {x: True for x in activities_model}
    for x in dfg:
        curr[x[1]].add(x[0])
    sthing_diff = True
    while sthing_diff:
        sthing_diff = False
        diff = {}
        for x in prev:
            if changed[x]:
                this_diff = curr[x].difference(prev[x])
                if this_diff:
                    sthing_diff = True
                else:
                    changed[x] = False
                diff[x] = this_diff
        prev = copy(curr)
        for x in diff:
            if changed[x]:
                for y in diff[x]:
                    curr[x] = curr[x].union(curr[y])
    return curr


def get_transitive_relations(dfg, alphabet):
    '''

    Parameters
    ----------
    dfg
        directly follows relation (counter describing activity pairs)

    Returns
    -------
        tuple with two dicts.
        first argument maps an activit on all other activities that are able to reach the activity ('transitive pre set')
        second argument maps an activity on all other activities that it can reach (transitively) ('transitive post set')

    '''
    pre = {a: set() for a in alphabet}
    post = {a: set() for a in alphabet}
    if len(dfg) > 0:
        q = [e for e in dfg]
        while len(q) > 0:
            s, t = q.pop(0)
            post[s].add(t)
            pre[t].add(s)
            post[s].update(post[t])
            pre[t].update(pre[s])
            for a, b in dfg:
                if b == s and not post[s].issubset(post[a]):
                    post[a].update(post[s])
                    q.append((a, b))
                if a == t and not pre[t].issubset(pre[b]):
                    pre[b].update(pre[t])
                    q.append((a, b))
    return pre, post


def get_alphabet(dfg):
    alpha = set()
    for a, b in dfg:
        alpha.add(a)
        alpha.add(b)
    return alpha

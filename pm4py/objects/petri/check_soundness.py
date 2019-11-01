from copy import deepcopy

import networkx as nx
import numpy as np

from pm4py.objects.petri import incidence_matrix
from pm4py.objects.petri import utils as petri_utils
from pm4py.objects.petri import petrinet
from pm4py.objects.petri.networkx_graph import create_networkx_undirected_graph
from pm4py.util.lp import factory as lp_solver_factory
from pm4py.objects.petri import explore_path

DEFAULT_LP_SOLVER_VARIANT = lp_solver_factory.PULP


def check_source_and_sink_reachability(net, unique_source, unique_sink):
    """
    Checks reachability of the source and the sink place from all simulation nodes (places/transitions)
    of the Petri net

    Parameters
    -------------
    net
        Petri net
    unique_source
        Unique source place of the Petri net
    unique_sink
        Unique sink place of the Petri net

    Returns
    -------------
    boolean
        Boolean value that is true if each node is in a path from the source place to the sink place
    """
    graph, unique_source_corr, unique_sink_corr, inv_dictionary = create_networkx_undirected_graph(net, unique_source,
                                                                                                   unique_sink)
    if unique_source_corr is not None and unique_sink_corr is not None:
        nodes_list = list(graph.nodes())
        finish_to_sink = list(nx.ancestors(graph, unique_sink_corr))
        connected_to_source = list(nx.descendants(graph, unique_source_corr))
        if len(finish_to_sink) == len(nodes_list) - 1 and len(connected_to_source) == len(nodes_list) - 1:
            return True
    return False


def check_source_place_presence(net):
    """
    Check if there is a unique source place with empty connections

    Parameters
    -------------
    net
        Petri net

    Returns
    -------------
    place
        Unique source place (or None otherwise)
    """
    count_empty_input = 0
    unique_source = None
    for place in net.places:
        if len(place.in_arcs) == 0:
            count_empty_input = count_empty_input + 1
            unique_source = place
    if count_empty_input == 1:
        return unique_source
    return None


def check_sink_place_presence(net):
    """
    Check if there is a unique sink place with empty connections

    Parameters
    -------------
    net
        Petri net

    Returns
    -------------
    place
        Unique source place (or None otherwise)
    """
    count_empty_output = 0
    unique_sink = None
    for place in net.places:
        if len(place.out_arcs) == 0:
            count_empty_output = count_empty_output + 1
            unique_sink = place
    if count_empty_output == 1:
        return unique_sink
    return None


def check_wfnet(net):
    """
    Check if the Petri net is a workflow net

    Parameters
    ------------
    net
        Petri net

    Returns
    ------------
    boolean
        Boolean value that is true when the Petri net is a workflow net
    """
    unique_source_place = check_source_place_presence(net)
    unique_sink_place = check_sink_place_presence(net)
    source_sink_reachability = check_source_and_sink_reachability(net, unique_source_place, unique_sink_place)

    return (unique_source_place is not None) and (unique_sink_place is not None) and source_sink_reachability


def check_loops_generating_tokens(net0):
    """
    Check if the Petri net contains loops generating tokens

    Parameters
    ------------
    net0
        Petri net

    Returns
    ------------
    boolean
        Boolean value (True if the net has loops generating tokens)
    """
    net = deepcopy(net0)
    petri_utils.decorate_transitions_prepostset(net)
    graph, inv_dictionary = petri_utils.create_networkx_directed_graph(net)
    dictionary = {y:x for x,y in inv_dictionary.items()}
    loops_trans = petri_utils.get_cycles_petri_net_transitions(net)
    for loop in loops_trans:
        m = petrinet.Marking()
        for index, trans in enumerate(loop):
            m = m + trans.add_marking

        visited_couples = set()
        while True:
            changed_something = False
            # if there are no places with positive marking replaying the loop, then we are fine
            neg_places = [p for p in m if m[p] < 0]
            pos_places = [p for p in m if m[p] > 0]
            for p1 in pos_places:
                # if there are no places with negative marking replaying the loop, then we are doomed
                for p2 in neg_places:
                    if not ((p1, p2)) in visited_couples:
                        visited_couples.add((p1, p2))
                        # otherwise, do a check if there is a path in the workflow net between the two places

                        # this exploration is based on heuristics; indeed, since we can enter the cycle multiple times
                        # it does not really matter if we reach suddenly the optimal path
                        #
                        # another option is to use the exploration provided in explore_path (that is based on alignments)
                        spath = None
                        try:
                            spath = nx.algorithms.shortest_paths.generic.shortest_path(graph, dictionary[p1], dictionary[p2])
                        except:
                            pass
                        if spath is not None:
                            trans = [inv_dictionary[x] for x in spath if type(inv_dictionary[x]) is petrinet.PetriNet.Transition]
                            sec_m0 = petrinet.Marking()
                            for t in trans:
                                sec_m0 = sec_m0 + t.add_marking
                            sec_m = petrinet.Marking()
                            for place in m:
                                if place in sec_m0:
                                    sec_m[place] = sec_m0[place]
                            m1 = m + sec_m
                            # the exploration is (in part) successful
                            if m1[p1] == 0:
                                m = m1
                                changed_something = True
                                break
                if not changed_something:
                    break
            if not changed_something:
                break

        # at this point, we have definitely created one token
        if sum(m[place] for place in m) > 0:
            return True

    return False


def check_non_blocking(net0):
    """
    Checks if a workflow net is non-blocking

    Parameters
    -------------
    net
        Petri net

    Returns
    -------------
    boolean
        Boolean value
    """
    net = deepcopy(net0)
    petri_utils.decorate_transitions_prepostset(net)
    graph, inv_dictionary = petri_utils.create_networkx_directed_graph(net)
    dictionary = {y:x for x,y in inv_dictionary.items()}
    source_place = [place for place in net.places if len(place.in_arcs) == 0][0]
    for trans in net.transitions:
        # transitions with 1 input arcs does not block
        if len(trans.in_arcs) > 1:
            places = [arc.source for arc in trans.in_arcs]
            # search the top-right intersection between a path connecting the initial marking and the input places
            # of such transition
            #
            # this exploration is based on heuristics; another option is to use the exploration provided in explore_path (that is based on alignments)
            spaths = [[inv_dictionary[y] for y in nx.algorithms.shortest_paths.generic.shortest_path(graph, dictionary[source_place], dictionary[x])] for x in places]
            spaths = [[y for y in x if type(y) is petrinet.PetriNet.Transition] for x in spaths]
            trans_dict = {}
            i = 0
            while i < len(places):
                p1 = places[i]
                spath1 = spaths[i]
                j = i + 1
                while j < len(places):
                    p2 = places[j]
                    spath2 = spaths[j]
                    s1, s2 = [x for x in spath1 if x in spath2], [x for x in spath2 if x in spath1]
                    if len(s1) > 0 and len(s2) > 0 and s1[-1] == s2[-1]:
                        # there is an intersection
                        t = s1[-1]
                        if len(t.out_arcs) <= 1:
                            return False
                        else:
                            if t not in trans_dict:
                                trans_dict[t] = set()
                                trans_dict[t].add(p1)
                                trans_dict[t].add(p2)
                    else:
                        return False
                    j = j + 1
                i = i + 1
            # after checking if the intersecting transition has at least one exit,
            # we check also that the number of outputs of the transition is at least the one expected
            for t in trans_dict:
                if len(t.out_arcs) < len(trans_dict[t]):
                    return False
    return True


def check_stability_wfnet(net):
    """
    Check if a workflow net is stable by using the incidence matrix

    Parameters
    -------------
    net
        Petri net

    Returns
    -------------
    boolean
        Boolean value (True if the WFNet is stable; False if it is not stable)
    """
    matrix = np.asmatrix(incidence_matrix.construct(net).a_matrix)
    matrix = np.transpose(matrix)
    id_matrix = np.identity(matrix.shape[1]) * -1
    vstack_matrix = np.vstack((matrix, id_matrix))
    c = np.ones(matrix.shape[1])
    bub = np.zeros(matrix.shape[0] + matrix.shape[1])
    i = matrix.shape[0]
    while i < matrix.shape[0] + matrix.shape[1]:
        bub[i] = -0.01
        i = i + 1

    try:
        sol = lp_solver_factory.apply(c, vstack_matrix, bub, None, None, variant=DEFAULT_LP_SOLVER_VARIANT)
        if sol:
            return True
    except:
        return False

    return False


def check_source_sink_place_conditions(net):
    """
    Check some conditions on the source/sink place important
    for a sound workflow net

    Parameters
    --------------
    net
        Petri net

    Returns
    --------------
    boolean
        Boolean value (True is good)
    """
    # check also that the transitions connected to the source/sink place have unique arcs
    unique_source_place = check_source_place_presence(net)
    unique_sink_place = check_sink_place_presence(net)
    if unique_source_place is not None:
        for arc in unique_source_place.out_arcs:
            trans = arc.target
            if len(trans.in_arcs) > 1:
                return False
    if unique_sink_place is not None:
        for arc in unique_sink_place.in_arcs:
            trans = arc.source
            if len(trans.out_arcs) > 1:
                return False
    return True


def check_relaxed_soundness_net_in_fin_marking(net, ini, fin):
    """
    Checks the relaxed soundness of a Petri net having the initial and the final marking

    Parameters
    -------------
    net
        Petri net
    ini
        Initial marking
    fin
        Final marking

    Returns
    -------------
    boolean
        Boolean value
    """
    try:
        alignment = explore_path.__search(net, ini, fin)
        if alignment is not None:
            return True
        return False
    except:
        return False


def check_relaxed_soundness_of_wfnet(net):
    """
    Checks the relaxed soundness of a workflow net

    Parameters
    -------------
    net
        Petri net

    Returns
    -------------
    boolean
        Boolean value
    """
    source = list(x for x in net.places if len(x.in_arcs) == 0)[0]
    sink = list(x for x in net.places if len(x.out_arcs) == 0)[0]

    ini = petrinet.Marking({source: 1})
    fin = petrinet.Marking({sink: 1})

    return check_relaxed_soundness_net_in_fin_marking(net, ini, fin)


def check_petri_wfnet_and_soundness(net, debug=False):
    """
    Check if the provided Petri net is a sound workflow net:
    - firstly, it is checked if it is a workflow net
    - secondly, it is checked if it is a sound workflow net

    Parameters
    -------------
    net
        Petri net
    debug
        Debug information

    Returns
    -------------
    boolean
        Boolean value (True if the Petri net is a sound workflow net)
    """
    is_wfnet = check_wfnet(net)
    if debug:
        print("is_wfnet=",is_wfnet)
    if is_wfnet:
        check_conditions_source_sink = check_source_sink_place_conditions(net)
        if debug:
            print("check_conditions_source_sink", check_conditions_source_sink)
        if check_conditions_source_sink:
            relaxed_soundness = check_relaxed_soundness_of_wfnet(net)
            if debug:
                print("relaxed_soundness",relaxed_soundness)
            if relaxed_soundness:
                is_stable = check_stability_wfnet(net)
                if debug:
                    print("is_stable=",is_stable)
                if is_stable:
                    is_non_blocking = check_non_blocking(net)
                    if debug:
                        print("is_non_blocking", is_non_blocking)
                    if is_non_blocking:
                        contains_loops_generating_tokens = check_loops_generating_tokens(net)
                        if debug:
                            print("contains_loops_generating_tokens",contains_loops_generating_tokens)
                        if not contains_loops_generating_tokens:
                            return True
    return False

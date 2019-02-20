from copy import copy, deepcopy

import networkx as nx

from pm4py.objects import petri
from pm4py.objects.log.util import xes as xes_util
from pm4py.objects.petri.check_soundness import check_petri_wfnet_and_soundness
from pm4py.objects.petri.networkx_graph import create_networkx_directed_graph


def remove_transition(net, trans):
    """
    Remove a transition from a Petri net

    Parameters
    ----------
    net
        Petri net
    trans
        Transition to remove

    Returns
    ----------
    net
        Petri net
    """
    if trans in net.transitions:
        in_arcs = trans.in_arcs
        for arc in in_arcs:
            place = arc.source
            place.out_arcs.remove(arc)
            net.arcs.remove(arc)
        out_arcs = trans.out_arcs
        for arc in out_arcs:
            place = arc.target
            place.in_arcs.remove(arc)
            net.arcs.remove(arc)
        net.transitions.remove(trans)
    return net


def remove_place(net, place):
    """
    Remove a place from a Petri net

    Parameters
    -------------
    net
        Petri net
    place
        Place to remove

    Returns
    -------------
    net
        Petri net
    """
    if place in net.places:
        in_arcs = place.in_arcs
        for arc in in_arcs:
            trans = arc.source
            trans.out_arcs.remove(arc)
            net.arcs.remove(arc)
        out_arcs = place.out_arcs
        for arc in out_arcs:
            trans = arc.target
            trans.in_arcs.remove(arc)
            net.arcs.remove(arc)
        net.places.remove(place)
    return net


def add_arc_from_to(fr, to, net, weight=1):
    """
    Adds an arc from a specific element to another element in some net. Assumes from and to are in the net!

    Parameters
    ----------
    fr: transition/place from
    to:  transition/place to
    net: net to use
    weight: weight associated to the arc

    Returns
    -------
    None
    """
    a = petri.petrinet.PetriNet.Arc(fr, to, weight)
    net.arcs.add(a)
    fr.out_arcs.add(a)
    to.in_arcs.add(a)

    return a


def construct_trace_net(trace, trace_name_key=xes_util.DEFAULT_NAME_KEY, activity_key=xes_util.DEFAULT_NAME_KEY):
    """
    Creates a trace net, i.e. a trace in Petri net form.

    Parameters
    ----------
    trace: :class:`list` input trace, assumed to be a list of events
    trace_name_key: :class:`str` key of the attribute that defines the name of the trace
    activity_key: :class:`str` key of the attribute of the events that defines the activity name

    Returns
    -------
    tuple: :class:`tuple` of the net, initial marking and the final marking

    """
    net = petri.petrinet.PetriNet(
        'trace net of %s' % trace.attributes[trace_name_key] if trace_name_key in trace.attributes else ' ')
    place_map = {0: petri.petrinet.PetriNet.Place('p_0')}
    net.places.add(place_map[0])
    for i in range(0, len(trace)):
        t = petri.petrinet.PetriNet.Transition('t_' + trace[i][activity_key] + '_' + str(i), trace[i][activity_key])
        net.transitions.add(t)
        place_map[i + 1] = petri.petrinet.PetriNet.Place('p_' + str(i + 1))
        net.places.add(place_map[i + 1])
        petri.utils.add_arc_from_to(place_map[i], t, net)
        petri.utils.add_arc_from_to(t, place_map[i + 1], net)
    return net, petri.petrinet.Marking({place_map[0]: 1}), petri.petrinet.Marking({place_map[len(trace)]: 1})


def construct_trace_net_cost_aware(trace, costs, trace_name_key=xes_util.DEFAULT_NAME_KEY,
                                   activity_key=xes_util.DEFAULT_NAME_KEY):
    """
    Creates a trace net, i.e. a trace in Petri net form.

    Parameters
    ----------
    trace: :class:`list` input trace, assumed to be a list of events
    costs: :class:`list` list of costs, length should be equal to the length of the input trace
    trace_name_key: :class:`str` key of the attribute that defines the name of the trace
    activity_key: :class:`str` key of the attribute of the events that defines the activity name

    Returns
    -------
    tuple: :class:`tuple` of the net, initial marking and the final marking

    """
    net = petri.petrinet.PetriNet(
        'trace net of %s' % trace.attributes[trace_name_key] if trace_name_key in trace.attributes else ' ')
    place_map = {0: petri.petrinet.PetriNet.Place('p_0')}
    net.places.add(place_map[0])
    cost_map = dict()
    for i in range(0, len(trace)):
        t = petri.petrinet.PetriNet.Transition('t_' + trace[i][activity_key] + '_' + str(i), trace[i][activity_key])
        cost_map[t] = costs[i]
        net.transitions.add(t)
        place_map[i + 1] = petri.petrinet.PetriNet.Place('p_' + str(i + 1))
        net.places.add(place_map[i + 1])
        petri.utils.add_arc_from_to(place_map[i], t, net)
        petri.utils.add_arc_from_to(t, place_map[i + 1], net)
    return net, petri.petrinet.Marking({place_map[0]: 1}), petri.petrinet.Marking({place_map[len(trace)]: 1}), cost_map


def variants(net, initial_marking, final_marking):
    """
    Given an acyclic workflow net, initial and final marking extracts a set of variants (list of event)
    replayable on the net.

    Parameters
    ----------
    net: An acyclic workflow net
    initial_marking: The initial marking of the net.
    final_marking: The final marking of the net.

    Returns
    -------
    variants: :class:`list` List of variants replayable in the net.

    """
    active = [(initial_marking, [])]
    visited = []
    this_variants = []
    for i in range(10000000):
        if not active:
            break
        curr_couple = active.pop(0)
        en_tr = petri.semantics.enabled_transitions(net, curr_couple[0])
        for t in en_tr:
            next_activitylist = list(curr_couple[1])
            next_activitylist.append(repr(t))
            next_couple = (petri.semantics.execute(t, net, curr_couple[0]), next_activitylist)
            if hash(next_couple[0]) == hash(final_marking):
                this_variants.append(next_couple[1])
            else:
                # If the next marking hash is not in visited, if the next marking+partial trace itself is
                # not already in active and if the next marking+partial trace is different from the
                # current one+partial trace
                if hash(next_couple[0]) not in visited and next((mark for mark in active if hash(mark[0]) == hash(
                        next_couple[0] and mark[1] == next_couple[1])), None) is None and (
                        hash(curr_couple[0]) != hash(next_couple[0]) or curr_couple[1] != next_couple[1]):
                    active.append(next_couple)
        visited.append(hash(curr_couple[0]))
    return this_variants


def get_transition_by_name(net, transition_name):
    """
    Get a transition by its name

    Parameters
    ------------
    net
        Petri net
    transition_name
        Transition name

    Returns
    ------------
    transition
        Transition object
    """
    for t in net.transitions:
        if t.name == transition_name:
            return t
    return None


def get_cycles_petri_net_places(net):
    """
    Get the cycles of a Petri net (returning only list of places belonging to the cycle)

    Parameters
    -------------
    net
        Petri net

    Returns
    -------------
    cycles
        Cycles (places) of the Petri net
    """
    graph, inv_dictionary = create_networkx_directed_graph(net)
    cycles = nx.simple_cycles(graph)
    cycles_places = []
    for cycle in cycles:
        cycles_places.append([])
        for el in cycle:
            if el in inv_dictionary and type(inv_dictionary[el]) is petri.petrinet.PetriNet.Place:
                cycles_places[-1].append(inv_dictionary[el])
    return cycles_places


def get_strongly_connected_subnets(net):
    """
    Get the strongly connected components subnets in the Petri net

    Parameters
    -------------
    net
        Petri net

    Returns
    -------------
    strongly_connected_transitions
        List of strongly connected transitions of the Petri net
    """
    graph, inv_dictionary = create_networkx_directed_graph(net)
    sccg = nx.strongly_connected_component_subgraphs(graph)
    strongly_connected_subnets = []
    for sg in list(sccg):
        if len(sg.nodes()) > 1:
            subnet = petri.petrinet.PetriNet()
            imarking = petri.petrinet.Marking()
            fmarking = petri.petrinet.Marking()
            corr = {}
            for node in sg.nodes():
                if node in inv_dictionary:
                    if type(inv_dictionary[node]) is petri.petrinet.PetriNet.Transition:
                        prev_trans = inv_dictionary[node]
                        new_trans = petri.petrinet.PetriNet.Transition(prev_trans.name, prev_trans.label)
                        corr[node] = new_trans
                        subnet.transitions.add(new_trans)
                    if type(inv_dictionary[node]) is petri.petrinet.PetriNet.Place:
                        prev_place = inv_dictionary[node]
                        new_place = petri.petrinet.PetriNet.Place(prev_place.name)
                        corr[node] = new_place
                        subnet.places.add(new_place)
            for edge in sg.edges():
                add_arc_from_to(corr[edge[0]], corr[edge[1]], subnet)
            strongly_connected_subnets.append([subnet, imarking, fmarking])

    return strongly_connected_subnets


def get_places_shortest_path(net, place_to_populate, current_place, places_shortest_path, actual_list, rec_depth):
    """
    Get shortest path between places lead by hidden transitions

    Parameters
    ----------
    net
        Petri net
    place_to_populate
        Place that we are populating the shortest map of
    current_place
        Current visited place (must explore its transitions)
    places_shortest_path
        Current dictionary
    actual_list
        Actual list of transitions to enable
    rec_depth
        Recursion depth
    """
    MAX_REC_DEPTH = 18
    if rec_depth > MAX_REC_DEPTH:
        return places_shortest_path
    if place_to_populate not in places_shortest_path:
        places_shortest_path[place_to_populate] = {}
    for t in current_place.out_arcs:
        if t.target.label is None:
            for p2 in t.target.out_arcs:
                if p2.target not in places_shortest_path[place_to_populate] or len(actual_list) + 1 < len(
                        places_shortest_path[place_to_populate][p2.target]):
                    new_actual_list = copy(actual_list)
                    new_actual_list.append(t.target)
                    places_shortest_path[place_to_populate][p2.target] = copy(new_actual_list)
                    places_shortest_path = get_places_shortest_path(net, place_to_populate, p2.target,
                                                                    places_shortest_path, new_actual_list,
                                                                    rec_depth + 1)
    return places_shortest_path


def get_places_shortest_path_by_hidden(net):
    """
    Get shortest path between places lead by hidden transitions

    Parameters
    ----------
    net
        Petri net
    """
    places_shortest_path = {}
    for p in net.places:
        places_shortest_path = get_places_shortest_path(net, p, p, places_shortest_path, [], 0)
    return places_shortest_path


def invert_spaths_dictionary(spaths):
    """
    Invert the shortest paths (between places) dictionary,
    from target-source to source-target

    Parameters
    -------------
    spaths
        Shortest paths dictionary

    Returns
    -------------
    inv_spaths
        Inverted shortest paths dictionary
    """
    inv_spaths = {}
    for target_place in spaths:
        for source_place in spaths[target_place]:
            if not source_place in inv_spaths:
                inv_spaths[source_place] = {}
            if not target_place in inv_spaths[source_place]:
                inv_spaths[source_place][target_place] = set()
            inv_spaths[source_place][target_place] = inv_spaths[source_place][target_place].union(
                spaths[target_place][source_place])
    return inv_spaths


def remove_unconnected_components(net):
    """
    Remove unconnected components from a Petri net

    Parameters
    -----------
    net
        Petri net

    Returns
    -----------
    net
        Cleaned Petri net
    """
    changed_something = True
    while changed_something:
        changed_something = False
        places = list(net.places)
        for place in places:
            if len(place.in_arcs) == 0 and len(place.out_arcs) == 0:
                remove_place(net, place)
                changed_something = True
        transitions = list(net.transitions)
        for trans in transitions:
            if len(trans.in_arcs) == 0 or len(trans.out_arcs) == 0:
                remove_transition(net, trans)
                changed_something = True
    return net


def get_s_components_from_petri(net, im, fm, rec_depth=0, curr_s_comp=None, visited_places=None,
                                list_s_components=None):
    """
    Gets the S-components from a Petri net

    Parameters
    -------------
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    curr_s_comp
        Current S component
    visited_places
        Visited places
    list_s_components
        List of S-components

    Returns
    --------------
    s_components
        List of S-components
    """
    MAX_REC_DEPTH = 6
    if list_s_components is None:
        list_s_components = []
    if len(im) > 1 or len(fm) > 1:
        return list_s_components
    if not check_petri_wfnet_and_soundness(net):
        return list_s_components
    source = list(im.keys())[0]
    if curr_s_comp is None:
        curr_s_comp = [source]
    if visited_places is None:
        visited_places = []
    something_changed = True
    while something_changed and rec_depth < MAX_REC_DEPTH:
        something_changed = False
        places_to_visit = sorted(list(set(curr_s_comp[len(visited_places):])), key=lambda x: len(x.out_arcs),
                                 reverse=True)
        for place_to_visit in places_to_visit:
            visited_places.append(place_to_visit)
            target_trans = sorted(list(set([arc.target for arc in place_to_visit.out_arcs])),
                                  key=lambda x: len(x.out_arcs))
            for trans in target_trans:
                visited_places_names = [x.name for x in visited_places]
                target_trans_target = list(
                    set([arc.target for arc in trans.out_arcs if arc.target.name not in visited_places_names]))
                if target_trans_target:
                    something_changed = True
                    if len(target_trans_target) == 1:
                        new_place = target_trans_target[0]
                        curr_s_comp.append(new_place)
                    else:
                        for new_place in target_trans_target:
                            [new_curr_s_comp, new_visited_places] = deepcopy([curr_s_comp, visited_places])
                            new_curr_s_comp.append(new_place)
                            list_s_components = get_s_components_from_petri(net, im, fm, rec_depth=rec_depth + 1,
                                                                            curr_s_comp=new_curr_s_comp,
                                                                            visited_places=new_visited_places,
                                                                            list_s_components=list_s_components)

    if not set([place.name for place in curr_s_comp]) in list_s_components:
        list_s_components.append(set([place.name for place in curr_s_comp]))

    return list_s_components

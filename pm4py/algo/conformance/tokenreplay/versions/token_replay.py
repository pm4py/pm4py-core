from copy import copy
from threading import Thread

from pm4py import util as pmutil
from pm4py.algo.filtering.tracelog.variants import variants_filter as variants_module
from pm4py.objects.log.util import xes as xes_util
from pm4py.objects.petri import semantics
from pm4py.util import constants

MAX_REC_DEPTH = 50
MAX_IT_FINAL = 10
MAX_REC_DEPTH_HIDTRANSENABL = 5
MAX_POSTFIX_SUFFIX_LENGTH = 20
MAX_NO_THREADS = 1000
ENABLE_POSTFIX_CACHE = True
ENABLE_MARKTOACT_CACHE = True


class NoConceptNameException(Exception):
    def __init__(self, message):
        self.message = message


def add_missing_tokens(t, marking):
    """
    Adds missing tokens needed to activate a transition

    Parameters
    ----------
    t
        Transition that should be enabled
    marking
        Current marking
    """
    missing = 0
    tokens_added = {}
    for a in t.in_arcs:
        if marking[a.source] < a.weight:
            missing = missing + (a.weight - marking[a.source])
            marking[a.source] = marking[a.source] + a.weight
            tokens_added[a.source] = a.weight - marking[a.source]
    return [missing, tokens_added]


def get_consumed_tokens(t):
    """
    Get tokens consumed firing a transition

    Parameters
    ----------
    t
        Transition that should be enabled
    """
    consumed = 0
    for a in t.in_arcs:
        consumed = consumed + a.weight
    return consumed


def get_produced_tokens(t):
    """
    Get tokens produced firing a transition

    Parameters
    ----------
    t
        Transition that should be enabled
    """
    produced = 0
    for a in t.out_arcs:
        produced = produced + a.weight
    return produced


def merge_dicts(x, y):
    """
    Merge two dictionaries keeping the least value

    Parameters
    ----------
    x
        First map (string, integer)
    y
        Second map (string, integer)
    """
    for key in y:
        if key not in x:
            x[key] = y[key]
        else:
            if y[key] < x[key]:
                x[key] = y[key]


def get_hidden_trans_reached_trans(t, net, rec_depth):
    """
    Get visible transitions reachable by enabling a hidden transition

    Parameters
    ----------
    t
        Transition that should be enabled
    net
        Petri net
    rec_depth
        Current recursion depth
    """
    reach_trans = {}
    if rec_depth > MAX_REC_DEPTH:
        return reach_trans
    for a1 in t.out_arcs:
        place = a1.target
        for a2 in place.out_arcs:
            t2 = a2.target
            if t2.label is not None:
                reach_trans[t2.label] = rec_depth
            if t2.label is None:
                merge_dicts(reach_trans, get_hidden_trans_reached_trans(t2, net, rec_depth + 1))
    return reach_trans


def get_places_with_missing_tokens(t, marking):
    """
    Get places with missing tokens

    Parameters
    ----------
    t
        Transition to enable
    marking
        Current marking
    """
    places_with_missing = set()
    for a in t.in_arcs:
        if marking[a.source] < a.weight:
            places_with_missing.add(a.source)
    return places_with_missing


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


def get_hidden_transitions_to_enable(marking, places_with_missing, places_shortest_path_by_hidden):
    """
    Calculate an ordered list of transitions to visit in order to enable a given transition

    Parameters
    ----------
    marking
        Current marking
    places_with_missing
        List of places with missing tokens
    places_shortest_path_by_hidden
        Minimal connection between places by hidden transitions
    """
    hidden_transitions_to_enable = []

    marking_places = [x for x in marking]
    marking_places = sorted(marking_places, key=lambda x: x.name)
    places_with_missing_keys = [x for x in places_with_missing]
    places_with_missing_keys = sorted(places_with_missing_keys, key=lambda x: x.name)
    for p1 in marking_places:
        for p2 in places_with_missing_keys:
            if p1 in places_shortest_path_by_hidden and p2 in places_shortest_path_by_hidden[p1]:
                hidden_transitions_to_enable.append(places_shortest_path_by_hidden[p1][p2])
    hidden_transitions_to_enable = sorted(hidden_transitions_to_enable, key=lambda x: len(x))

    return hidden_transitions_to_enable


def get_req_transitions_for_final_marking(marking, final_marking, places_shortest_path_by_hidden):
    """
    Gets required transitions for final marking

    Parameters
    ----------
    marking
        Current marking
    final_marking
        Final marking assigned to the Petri net
    places_shortest_path_by_hidden
        Minimal connection between places by hidden transitions
    """
    hidden_transitions_to_enable = []

    marking_places = [x for x in marking]
    marking_places = sorted(marking_places, key=lambda x: x.name)
    final_marking_places = [x for x in final_marking]
    final_marking_places = sorted(final_marking_places, key=lambda x: x.name)
    for p1 in marking_places:
        for p2 in final_marking_places:
            if p1 in places_shortest_path_by_hidden and p2 in places_shortest_path_by_hidden[p1]:
                hidden_transitions_to_enable.append(places_shortest_path_by_hidden[p1][p2])
    hidden_transitions_to_enable = sorted(hidden_transitions_to_enable, key=lambda x: len(x))

    return hidden_transitions_to_enable


def enable_hidden_transitions(net, marking, activated_transitions, visited_transitions, all_visited_markings,
                              hidden_transitions_to_enable, t):
    """
    Actually enable hidden transitions on the Petri net

    Parameters
    -----------
    net
        Petri net
    marking
        Current marking
    activated_transitions
        All activated transitions during the replay
    visited_transitions
        All visited transitions by the recursion
    all_visited_markings
        All visited markings
    hidden_transitions_to_enable
        List of hidden transition to enable
    t
        Transition against we should check if they are enabled
    """
    j_indexes = [0] * len(hidden_transitions_to_enable)
    for z in range(10000000):
        something_changed = False
        for k in range(j_indexes[z % len(hidden_transitions_to_enable)], len(
                hidden_transitions_to_enable[z % len(hidden_transitions_to_enable)])):
            t3 = hidden_transitions_to_enable[z % len(hidden_transitions_to_enable)][
                j_indexes[z % len(hidden_transitions_to_enable)]]
            if not t3 == t:
                if semantics.is_enabled(t3, net, marking):
                    if t3 not in visited_transitions:
                        marking = semantics.execute(t3, net, marking)
                        activated_transitions.append(t3)
                        visited_transitions.add(t3)
                        all_visited_markings.append(marking)
                        something_changed = True
            j_indexes[z % len(hidden_transitions_to_enable)] = j_indexes[z % len(hidden_transitions_to_enable)] + 1
            if semantics.is_enabled(t, net, marking):
                break
        if semantics.is_enabled(t, net, marking):
            break
        if not something_changed:
            break
    return [marking, activated_transitions, visited_transitions, all_visited_markings]


def apply_hidden_trans(t, net, marking, places_shortest_paths_by_hidden, act_tr, rec_depth,
                       visit_trans,
                       vis_mark):
    """
    Apply hidden transitions in order to enable a given transition

    Parameters
    ----------
    t
        Transition to eventually enable
    net
        Petri net
    marking
        Marking
    places_shortest_paths_by_hidden
        Shortest paths between places connected by hidden transitions
    act_tr
        All activated transitions
    rec_depth
        Current recursion depth
    visit_trans
        All visited transitions by hiddenTrans method
    vis_mark
        All visited markings
    """
    if rec_depth >= MAX_REC_DEPTH_HIDTRANSENABL or t in visit_trans:
        return [net, marking, act_tr, vis_mark]
    visit_trans.add(t)
    marking_at_start = copy(marking)
    places_with_missing = get_places_with_missing_tokens(t, marking)
    hidden_transitions_to_enable = get_hidden_transitions_to_enable(marking, places_with_missing,
                                                                    places_shortest_paths_by_hidden)

    if hidden_transitions_to_enable:
        [marking, act_tr, visit_trans, vis_mark] = enable_hidden_transitions(net,
                                                                             marking,
                                                                             act_tr,
                                                                             visit_trans,
                                                                             vis_mark,
                                                                             hidden_transitions_to_enable,
                                                                             t)
        if not semantics.is_enabled(t, net, marking):
            hidden_transitions_to_enable = get_hidden_transitions_to_enable(marking, places_with_missing,
                                                                            places_shortest_paths_by_hidden)
            for z in range(len(hidden_transitions_to_enable)):
                for k in range(len(hidden_transitions_to_enable[z])):
                    t4 = hidden_transitions_to_enable[z][k]
                    if not t4 == t:
                        if t4 not in visit_trans:
                            if not semantics.is_enabled(t4, net, marking):
                                [net, marking, act_tr, vis_mark] = apply_hidden_trans(t4,
                                                                                      net,
                                                                                      marking,
                                                                                      places_shortest_paths_by_hidden,
                                                                                      act_tr,
                                                                                      rec_depth + 1,
                                                                                      visit_trans,
                                                                                      vis_mark)
                            if semantics.is_enabled(t4, net, marking):
                                marking = semantics.execute(t4, net, marking)
                                act_tr.append(t4)
                                visit_trans.add(t4)
                                vis_mark.append(marking)
        if not semantics.is_enabled(t, net, marking):
            if not (marking_at_start == marking):
                [net, marking, act_tr, vis_mark] = apply_hidden_trans(t, net, marking,
                                                                      places_shortest_paths_by_hidden,
                                                                      act_tr,
                                                                      rec_depth + 1,
                                                                      visit_trans,
                                                                      vis_mark)

    return [net, marking, act_tr, vis_mark]


def get_visible_transitions_eventually_enabled_by_marking(net, marking):
    """
    Get visible transitions eventually enabled by marking (passing possibly through hidden transitions)

    Parameters
    ----------
    net
        Petri net
    marking
        Current marking
    """
    all_enabled_transitions = list(semantics.enabled_transitions(net, marking))
    visible_transitions = set()
    visited_transitions = set()

    for i in range(len(all_enabled_transitions)):
        t = all_enabled_transitions[i]
        if t not in visited_transitions:
            if t.label is not None:
                visible_transitions.add(t)
            else:
                marking_copy = copy(marking)
                if semantics.is_enabled(t, net, marking_copy):
                    new_marking = semantics.execute(t, net, marking_copy)
                    new_enabled_transitions = list(semantics.enabled_transitions(net, new_marking))
                    all_enabled_transitions = all_enabled_transitions + new_enabled_transitions
            visited_transitions.add(t)

    return visible_transitions


def break_condition_final_marking(marking, final_marking):
    """
    Verify break condition for final marking

    Parameters
    -----------
    marking
        Current marking
    final_marking
        Target final marking
    """
    final_marking_dict = dict(final_marking)
    marking_dict = dict(marking)
    final_marking_dict_keys = set(final_marking_dict.keys())
    marking_dict_keys = set(marking_dict.keys())

    return final_marking_dict_keys.issubset(marking_dict_keys)


def apply_trace(trace, net, initial_marking, final_marking, trans_map, enable_place_fitness, place_fitness,
                places_shortest_path_by_hidden, consider_remaining_in_fitness, activity_key="concept:name",
                try_to_reach_final_marking_through_hidden=True, stop_immediately_unfit=False,
                walk_through_hidden_trans=True, post_fix_caching=None,
                marking_to_activity_caching=None):
    """
    Apply the token replaying algorithm to a trace

    Parameters
    ----------
    trace
        Trace in the event log
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    trans_map
        Map between transitions labels and transitions
    enable_place_fitness
        Enable fitness calculation at place level
    place_fitness
        Current dictionary of places associated with unfit traces
    places_shortest_path_by_hidden
        Shortest paths between places by hidden transitions
    consider_remaining_in_fitness
        Boolean value telling if the remaining tokens should be considered in fitness evaluation
    activity_key
        Name of the attribute that contains the activity
    try_to_reach_final_marking_through_hidden
        Boolean value that decides if we shall try to reach the final marking through hidden transitions
    stop_immediately_unfit
        Boolean value that decides if we shall stop immediately when a non-conformance is detected
    walk_through_hidden_trans
        Boolean value that decides if we shall walk through hidden transitions in order to enable visible transitions
    post_fix_caching
        Stores the post fix caching object
    marking_to_activity_caching
        Stores the marking-to-activity cache
    """
    trace_activities = [event[activity_key] for event in trace]
    act_trans = []
    transitions_with_problems = []
    vis_mark = []
    activating_transition_index = {}
    activating_transition_interval = []
    used_postfix_cache = False
    marking = copy(initial_marking)
    vis_mark.append(marking)
    missing = 0
    consumed = 0
    produced = 0
    for i in range(len(trace)):
        if ENABLE_POSTFIX_CACHE and (str(trace_activities) in post_fix_caching.cache and
                                     hash(marking) in post_fix_caching.cache[str(trace_activities)]):
            trans_to_act = post_fix_caching.cache[str(trace_activities)][hash(marking)]["trans_to_activate"]
            for z in range(len(trans_to_act)):
                t = trans_to_act[z]
                act_trans.append(t)
            used_postfix_cache = True
            marking = post_fix_caching.cache[str(trace_activities)][hash(marking)]["final_marking"]
            break
        else:
            prev_len_activated_transitions = len(act_trans)
            if ENABLE_MARKTOACT_CACHE and (hash(marking) in marking_to_activity_caching.cache and
                                           trace[i][activity_key] in marking_to_activity_caching.cache[hash(marking)]
                                           and trace[i - 1][activity_key] ==
                                           marking_to_activity_caching.cache[hash(marking)][trace[i][activity_key]]
                                           ["previousActivity"]):
                this_end_marking = marking_to_activity_caching.cache[hash(marking)][trace[i][activity_key]][
                    "end_marking"]
                this_act_trans = marking_to_activity_caching.cache[hash(marking)][trace[i][activity_key]][
                    "this_activated_transitions"]
                this_vis_markings = marking_to_activity_caching.cache[hash(marking)][trace[i][activity_key]][
                    "this_visited_markings"]
                act_trans = act_trans + this_act_trans
                vis_mark = vis_mark + this_vis_markings
                marking = copy(this_end_marking)
            else:
                if trace[i][activity_key] in trans_map:
                    t = trans_map[trace[i][activity_key]]
                    if walk_through_hidden_trans and not semantics.is_enabled(t, net,
                                                                              marking):
                        visited_transitions = set()
                        prev_len_activated_transitions = len(act_trans)
                        [net, marking, act_trans, vis_mark] = apply_hidden_trans(t, net,
                                                                                 marking,
                                                                                 places_shortest_path_by_hidden,
                                                                                 act_trans,
                                                                                 0,
                                                                                 visited_transitions,
                                                                                 vis_mark)
                    if not semantics.is_enabled(t, net, marking):
                        transitions_with_problems.append(t)
                        if stop_immediately_unfit:
                            missing = missing + 1
                            break
                        [m, tokens_added] = add_missing_tokens(t, marking)
                        missing = missing + m
                        if enable_place_fitness:
                            for place in tokens_added.keys():
                                if place in place_fitness:
                                    place_fitness[place]["underfed_traces"].add(trace)
                    c = get_consumed_tokens(t)
                    p = get_produced_tokens(t)
                    consumed = consumed + c
                    produced = produced + p
                    if semantics.is_enabled(t, net, marking):
                        marking = semantics.execute(t, net, marking)
                        act_trans.append(t)
                        vis_mark.append(marking)
            del trace_activities[0]
            if len(trace_activities) < MAX_POSTFIX_SUFFIX_LENGTH:
                activating_transition_index[str(trace_activities)] = {"index": len(act_trans),
                                                                      "marking": hash(marking)}
            if i > 0:
                activating_transition_interval.append(
                    [trace[i][activity_key], prev_len_activated_transitions, len(act_trans),
                     trace[i - 1][activity_key]])
            else:
                activating_transition_interval.append(
                    [trace[i][activity_key], prev_len_activated_transitions, len(act_trans),
                     ""])

    if try_to_reach_final_marking_through_hidden and not used_postfix_cache:
        for i in range(MAX_IT_FINAL):
            if not break_condition_final_marking(marking, final_marking):
                hidden_transitions_to_enable = get_req_transitions_for_final_marking(marking, final_marking,
                                                                                     places_shortest_path_by_hidden)

                for group in hidden_transitions_to_enable:
                    for t in group:
                        if semantics.is_enabled(t, net, marking):
                            marking = semantics.execute(t, net, marking)
                            act_trans.append(t)
                            vis_mark.append(marking)
                    if break_condition_final_marking(marking, final_marking):
                        break
            else:
                break

        # try to reach the final marking in a different fashion, if not already reached
        if not break_condition_final_marking(marking, final_marking):
            if len(final_marking) == 1:
                sink_place = list(final_marking)[0]

                connections_to_sink = []
                for place in marking:
                    if place in places_shortest_path_by_hidden and sink_place in places_shortest_path_by_hidden[place]:
                        connections_to_sink.append([place, places_shortest_path_by_hidden[place][sink_place]])
                connections_to_sink = sorted(connections_to_sink, key=lambda x: len(x[1]))

                for i in range(MAX_IT_FINAL):
                    for j in range(len(connections_to_sink)):
                        for z in range(len(connections_to_sink[j][1])):
                            t = connections_to_sink[j][1][z]
                            if semantics.is_enabled(t, net, marking):
                                marking = semantics.execute(t, net, marking)
                                act_trans.append(t)
                                vis_mark.append(marking)
                                continue
                            else:
                                break

    marking_before_cleaning = copy(marking)

    remaining = 0
    for p in marking:
        if p in final_marking:
            marking[p] = max(0, marking[p] - final_marking[p])
            if enable_place_fitness:
                if marking[p] > 0:
                    if p in place_fitness:
                        if trace not in place_fitness[p]["underfed_traces"]:
                            place_fitness[p]["overfed_traces"].add(trace)
        remaining = remaining + marking[p]
    if consider_remaining_in_fitness:
        is_fit = (missing == 0) and (remaining == 0)
    else:
        is_fit = (missing == 0)

    if consumed > 0 and produced > 0:
        trace_fitness = (1.0 - float(missing) / float(consumed)) * (1.0 - float(remaining) / float(produced))
    else:
        trace_fitness = 1.0

    if is_fit:
        for suffix in activating_transition_index:
            if suffix not in post_fix_caching.cache:
                post_fix_caching.cache[suffix] = {}
            if activating_transition_index[suffix]["marking"] not in post_fix_caching.cache[suffix]:
                post_fix_caching.cache[suffix][activating_transition_index[suffix]["marking"]] = \
                    {"trans_to_activate": act_trans[activating_transition_index[suffix]["index"]:],
                     "final_marking": marking}
        for trans in activating_transition_interval:
            activity = trans[0]
            start_marking_index = trans[1]
            end_marking_index = trans[2]
            previous_activity = trans[3]
            if end_marking_index < len(vis_mark):
                start_marking_object = vis_mark[start_marking_index]
                start_marking_hash = hash(start_marking_object)
                end_marking_object = vis_mark[end_marking_index]
                if activity in trans_map:
                    this_activated_trans = act_trans[start_marking_index:end_marking_index]
                    this_visited_markings = vis_mark[start_marking_index + 1:end_marking_index + 1]

                    if start_marking_hash not in marking_to_activity_caching.cache:
                        marking_to_activity_caching.cache[start_marking_hash] = {}
                    if activity not in marking_to_activity_caching.cache[start_marking_hash]:
                        marking_to_activity_caching.cache[start_marking_hash][activity] = {
                            "start_marking": start_marking_object, "end_marking": end_marking_object,
                            "this_activated_transitions": this_activated_trans,
                            "this_visited_markings": this_visited_markings,
                            "previousActivity": previous_activity}

    return [is_fit, trace_fitness, act_trans, transitions_with_problems, marking_before_cleaning,
            get_visible_transitions_eventually_enabled_by_marking(net, marking_before_cleaning)]


class ApplyTraceTokenReplay(Thread):
    def __init__(self, trace, net, initial_marking, final_marking, trans_map, enable_place_fitness, place_fitness,
                 places_shortest_path_by_hidden, consider_remaining_in_fitness, activity_key="concept:name",
                 reach_mark_through_hidden=True, stop_immediately_when_unfit=False,
                 walk_through_hidden_trans=True, post_fix_caching=None,
                 marking_to_activity_caching=None):
        """
        Constructor
        """
        self.trace = trace
        self.net = net
        self.initial_marking = initial_marking
        self.final_marking = final_marking
        self.trans_map = trans_map
        self.enable_place_fitness = enable_place_fitness
        self.place_fitness = place_fitness
        self.places_shortest_path_by_hidden = places_shortest_path_by_hidden
        self.consider_remaining_in_fitness = consider_remaining_in_fitness
        self.activity_key = activity_key
        self.try_to_reach_final_marking_through_hidden = reach_mark_through_hidden
        self.stop_immediately_when_unfit = stop_immediately_when_unfit
        self.walk_through_hidden_trans = walk_through_hidden_trans
        self.post_fix_caching = post_fix_caching
        self.marking_to_activity_caching = marking_to_activity_caching
        self.t_fit = None
        self.t_value = None
        self.act_trans = None
        self.trans_probl = None
        self.reached_marking = None
        self.enabled_trans_in_mark = None

        Thread.__init__(self)

    def run(self):
        """
        Runs the thread and stores the results
        """
        self.t_fit, self.t_value, self.act_trans, self.trans_probl, self.reached_marking, self.enabled_trans_in_mark = \
            apply_trace(self.trace, self.net, self.initial_marking, self.final_marking, self.trans_map,
                        self.enable_place_fitness, self.place_fitness,
                        self.places_shortest_path_by_hidden, self.consider_remaining_in_fitness,
                        activity_key=self.activity_key,
                        try_to_reach_final_marking_through_hidden=self.try_to_reach_final_marking_through_hidden,
                        stop_immediately_unfit=self.stop_immediately_when_unfit,
                        walk_through_hidden_trans=self.walk_through_hidden_trans,
                        post_fix_caching=self.post_fix_caching,
                        marking_to_activity_caching=self.marking_to_activity_caching)


class PostFixCaching:
    """
    Post fix caching object
    """

    def __init__(self):
        self.cache = 0
        self.cache = {}


class MarkingToActivityCaching:
    """
    Marking to activity caching
    """

    def __init__(self):
        self.cache = 0
        self.cache = {}


"""
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    trans_map
        Map between transitions labels and transitions
    enable_place_fitness
        Enable fitness calculation at place level
    place_fitness
        Current dictionary of places associated with unfit traces
    places_shortest_path_by_hidden
        Shortest paths between places by hidden transitions
    consider_remaining_in_fitness
        Boolean value telling if the remaining tokens should be considered in fitness evaluation
    activity_key
        Name of the attribute that contains the activity
    try_to_reach_final_marking_through_hidden
        Boolean value that decides if we shall try to reach the final marking through hidden transitions
    stop_immediately_unfit
        Boolean value that decides if we shall stop immediately when a non-conformance is detected
    walk_through_hidden_trans
        Boolean value that decides if we shall walk through hidden transitions in order to enable visible transitions
    post_fix_caching
        Stores the post fix caching object
    marking_to_activity_caching
        Stores the marking-to-activity cache
        """


def apply_log(log, net, initial_marking, final_marking, enable_place_fitness=False, consider_remaining_in_fitness=False,
              activity_key="concept:name", reach_mark_through_hidden=True, stop_immediately_unfit=False,
              walk_through_hidden_trans=True, places_shortest_path_by_hidden=None,
              variants=None):
    """
    Apply token-based replay to a log

    Parameters
    ----------
    log
        Trace log
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    enable_place_fitness
        Enable fitness calculation at place level
    consider_remaining_in_fitness
        Boolean value telling if the remaining tokens should be considered in fitness evaluation
    activity_key
        Name of the attribute that contains the activity
    reach_mark_through_hidden
        Boolean value that decides if we shall try to reach the final marking through hidden transitions
    stop_immediately_unfit
        Boolean value that decides if we shall stop immediately when a non-conformance is detected
    walk_through_hidden_trans
        Boolean value that decides if we shall walk through hidden transitions in order to enable visible transitions
    places_shortest_path_by_hidden
        Shortest paths between places by hidden transitions
    variants
        List of variants contained in the event log
    """
    post_fix_cache = PostFixCaching()
    marking_to_activity_cache = MarkingToActivityCaching()
    if places_shortest_path_by_hidden is None:
        places_shortest_path_by_hidden = get_places_shortest_path_by_hidden(net)

    place_fitness_per_trace = {}

    aligned_traces = []

    if enable_place_fitness:
        for place in net.places:
            place_fitness_per_trace[place] = {"underfed_traces": set(), "overfed_traces": set()}
    trans_map = {}
    for t in net.transitions:
        trans_map[t.label] = t
    if len(log) > 0:
        if len(log[0]) > 0:
            if activity_key in log[0][0]:
                if variants is None:
                    parameters_variants = {constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}
                    variants = variants_module.get_variants(log, parameters=parameters_variants)
                vc = variants_module.get_variants_sorted_by_count(variants)
                threads = {}
                threads_results = {}

                for i in range(len(vc)):
                    variant = vc[i][0]
                    threads_keys = list(threads.keys())
                    if len(threads_keys) > MAX_NO_THREADS:
                        for j in range(len(threads_keys)):
                            t = threads[threads_keys[j]]
                            t.join()
                            threads_results[threads_keys[j]] = {"trace_is_fit": copy(t.t_fit),
                                                                "trace_fitness": copy(t.t_value),
                                                                "activated_transitions": copy(t.act_trans),
                                                                "reached_marking": copy(t.reached_marking),
                                                                "enabled_transitions_in_marking": copy(
                                                                    t.enabled_trans_in_mark),
                                                                "transitions_with_problems": copy(
                                                                    t.trans_probl)}
                            del threads[threads_keys[j]]
                        del threads_keys
                    threads[variant] = ApplyTraceTokenReplay(variants[variant][0], net, initial_marking, final_marking,
                                                             trans_map, enable_place_fitness, place_fitness_per_trace,
                                                             places_shortest_path_by_hidden,
                                                             consider_remaining_in_fitness,
                                                             activity_key=activity_key,
                                                             reach_mark_through_hidden=reach_mark_through_hidden,
                                                             stop_immediately_when_unfit=stop_immediately_unfit,
                                                             walk_through_hidden_trans=walk_through_hidden_trans,
                                                             post_fix_caching=post_fix_cache,
                                                             marking_to_activity_caching=marking_to_activity_cache)
                    threads[variant].start()
                threads_keys = list(threads.keys())
                for j in range(len(threads_keys)):
                    t = threads[threads_keys[j]]
                    t.join()
                    threads_results[threads_keys[j]] = {"trace_is_fit": copy(t.t_fit), "trace_fitness": copy(t.t_value),
                                                        "activated_transitions": copy(t.act_trans),
                                                        "reached_marking": copy(t.reached_marking),
                                                        "enabled_transitions_in_marking": copy(
                                                            t.enabled_trans_in_mark),
                                                        "transitions_with_problems": copy(t.trans_probl)}
                    del threads[threads_keys[j]]
                for trace in log:
                    trace_variant = ",".join([x[activity_key] for x in trace])
                    t = threads_results[trace_variant]

                    aligned_traces.append(t)
            else:
                raise NoConceptNameException("at least an event is without " + activity_key)

    if enable_place_fitness:
        return aligned_traces, place_fitness_per_trace
    else:
        return aligned_traces


def apply(log, net, initial_marking, final_marking, parameters=None):
    """
    Method to apply token-based replay

    Parameters
    -----------
    log
        Log
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    parameters
        Parameters of the algorithm
    """
    if parameters is None:
        parameters = {}

    enable_place_fitness = False
    consider_remaining_in_fitness = False
    try_to_reach_final_marking_through_hidden = True
    stop_immediately_unfit = False
    walk_through_hidden_trans = True
    places_shortest_path_by_hidden = None
    activity_key = xes_util.DEFAULT_NAME_KEY
    variants = None

    if "enable_place_fitness" in parameters:
        enable_place_fitness = parameters["enable_place_fitness"]
    if "consider_remaining_in_fitness" in parameters:
        consider_remaining_in_fitness = parameters["consider_remaining_in_fitness"]
    if "try_to_reach_final_marking_through_hidden" in parameters:
        try_to_reach_final_marking_through_hidden = parameters["try_to_reach_final_marking_through_hidden"]
    if "stop_immediately_unfit" in parameters:
        stop_immediately_unfit = parameters["stop_immediately_unfit"]
    if "walk_through_hidden_trans" in parameters:
        walk_through_hidden_trans = parameters[
            "walk_through_hidden_trans"]
    if "places_shortest_path_by_hidden" in parameters:
        places_shortest_path_by_hidden = parameters["places_shortest_path_by_hidden"]
    if "variants" in parameters:
        variants = parameters["variants"]
    if pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters:
        activity_key = parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY]

    return apply_log(log, net, initial_marking, final_marking, enable_place_fitness=enable_place_fitness,
                     consider_remaining_in_fitness=consider_remaining_in_fitness,
                     reach_mark_through_hidden=try_to_reach_final_marking_through_hidden,
                     stop_immediately_unfit=stop_immediately_unfit,
                     walk_through_hidden_trans=walk_through_hidden_trans,
                     places_shortest_path_by_hidden=places_shortest_path_by_hidden, activity_key=activity_key,
                     variants=variants)

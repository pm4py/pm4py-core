from copy import copy
from threading import Thread

from pm4py import util as pmutil
from pm4py.algo.filtering.log.variants import variants_filter as variants_module
from pm4py.objects.log.util import xes as xes_util
from pm4py.objects.petri import semantics
from pm4py.objects.petri.utils import get_places_shortest_path_by_hidden, get_s_components_from_petri
from pm4py.util import constants

MAX_REC_DEPTH = 18
MAX_IT_FINAL1 = 5
MAX_IT_FINAL2 = 5
MAX_REC_DEPTH_HIDTRANSENABL = 2
MAX_POSTFIX_SUFFIX_LENGTH = 20
MAX_NO_THREADS = 1024
MAX_DEF_THR_EX_TIME = 10
ENABLE_POSTFIX_CACHE = False
ENABLE_MARKTOACT_CACHE = False


class DebugConst:
    REACH_MRH = -1
    REACH_ITF1 = -1
    REACH_ITF2 = -1


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
    # if rec_depth > DebugConst.REACH_MRD:
    #    DebugConst.REACH_MRD = rec_depth
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
    # if rec_depth > DebugConst.REACH_MRH:
    #    DebugConst.REACH_MRH = rec_depth
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
    initial_all_enabled_transitions_marking_dictio = {}
    all_enabled_transitions_marking_dictio = {}
    for trans in all_enabled_transitions:
        all_enabled_transitions_marking_dictio[trans] = marking
        initial_all_enabled_transitions_marking_dictio[trans] = marking
    visible_transitions = set()
    visited_transitions = set()

    i = 0
    while i < len(all_enabled_transitions):
        t = all_enabled_transitions[i]
        marking_copy = copy(all_enabled_transitions_marking_dictio[t])

        if repr([t, marking_copy]) not in visited_transitions:
            if t.label is not None:
                visible_transitions.add(t)
            else:
                if semantics.is_enabled(t, net, marking_copy):
                    new_marking = semantics.execute(t, net, marking_copy)
                    new_enabled_transitions = list(semantics.enabled_transitions(net, new_marking))
                    for t2 in new_enabled_transitions:
                        all_enabled_transitions.append(t2)
                        all_enabled_transitions_marking_dictio[t2] = new_marking
            visited_transitions.add(repr([t, marking_copy]))
        i = i + 1

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


def apply_trace(trace, net, initial_marking, final_marking, trans_map, enable_pltr_fitness, place_fitness,
                transition_fitness, notexisting_activities_in_model,
                places_shortest_path_by_hidden, consider_remaining_in_fitness, activity_key="concept:name",
                try_to_reach_final_marking_through_hidden=True, stop_immediately_unfit=False,
                walk_through_hidden_trans=True, post_fix_caching=None,
                marking_to_activity_caching=None, is_reduction=False, thread_maximum_ex_time=MAX_DEF_THR_EX_TIME,
                enable_postfix_cache=False, enable_marktoact_cache=False, cleaning_token_flood=False,
                s_components=None):
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
    enable_pltr_fitness
        Enable fitness calculation at place/transition level
    place_fitness
        Current dictionary of places associated with unfit traces
    transition_fitness
        Current dictionary of transitions associated with unfit traces
    notexisting_activities_in_model
        Map that stores the notexisting activities in the model
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
    is_reduction
        Expresses if the token-based replay is called in a reduction attempt
    thread_maximum_ex_time
        Alignment threads maximum allowed execution time
    enable_postfix_cache
        Enables postfix cache
    enable_marktoact_cache
        Enables marking to activity cache
    cleaning_token_flood
        Decides if a cleaning of the token flood shall be operated
    s_components
        S-components of the Petri net (if workflow net)
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
    sum_tokens_im = 0
    for place in initial_marking:
        sum_tokens_im = sum_tokens_im + initial_marking[place]
    sum_tokens_fm = 0
    for place in final_marking:
        sum_tokens_fm = sum_tokens_fm + final_marking[place]
    produced = sum_tokens_im
    current_event_map = {}
    current_remaining_map = {}
    for i in range(len(trace)):
        if enable_postfix_cache and (str(trace_activities) in post_fix_caching.cache and
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
            if enable_marktoact_cache and (hash(marking) in marking_to_activity_caching.cache and
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
                    current_event_map.update(trace[i])
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
                    is_initially_enabled = True
                    old_marking_names = [x.name for x in list(marking.keys())]
                    if not semantics.is_enabled(t, net, marking):
                        is_initially_enabled = False
                        transitions_with_problems.append(t)
                        if stop_immediately_unfit:
                            missing = missing + 1
                            break
                        [m, tokens_added] = add_missing_tokens(t, marking)
                        missing = missing + m
                        if enable_pltr_fitness:
                            for place in tokens_added.keys():
                                if place in place_fitness:
                                    place_fitness[place]["underfed_traces"].add(trace)
                            if trace not in transition_fitness[t]["underfed_traces"]:
                                transition_fitness[t]["underfed_traces"][trace] = list()
                            transition_fitness[t]["underfed_traces"][trace].append(current_event_map)
                    elif enable_pltr_fitness:
                        if trace not in transition_fitness[t]["fit_traces"]:
                            transition_fitness[t]["fit_traces"][trace] = list()
                        transition_fitness[t]["fit_traces"][trace].append(current_event_map)
                    c = get_consumed_tokens(t)
                    p = get_produced_tokens(t)
                    consumed = consumed + c
                    produced = produced + p
                    if semantics.is_enabled(t, net, marking):
                        marking = semantics.execute(t, net, marking)
                        act_trans.append(t)
                        vis_mark.append(marking)
                    if not is_initially_enabled and cleaning_token_flood:
                        # here, a routine for cleaning token flood shall go
                        new_marking_names = [x.name for x in list(marking.keys())]
                        new_marking_names_diff = [x for x in new_marking_names if x not in old_marking_names]
                        new_marking_names_inte = [x for x in new_marking_names if x in old_marking_names]
                        for p1 in new_marking_names_inte:
                            for p2 in new_marking_names_diff:
                                for comp in s_components:
                                    if p1 in comp and p2 in comp:
                                        place_to_delete = [place for place in list(marking.keys()) if place.name == p1]
                                        if len(place_to_delete) == 1:
                                            del marking[place_to_delete[0]]
                                            if not place_to_delete[0] in current_remaining_map:
                                                current_remaining_map[place_to_delete[0]] = 0
                                            current_remaining_map[place_to_delete[0]] = current_remaining_map[
                                                                                            place_to_delete[0]] + 1
                        pass
                else:
                    if not trace[i][activity_key] in notexisting_activities_in_model:
                        notexisting_activities_in_model[trace[i][activity_key]] = {}
                    notexisting_activities_in_model[trace[i][activity_key]][trace] = current_event_map
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
        for i in range(MAX_IT_FINAL1):
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

        # if i > DebugConst.REACH_ITF1:
        #    DebugConst.REACH_ITF1 = i

        # try to reach the final marking in a different fashion, if not already reached
        if not break_condition_final_marking(marking, final_marking):
            if len(final_marking) == 1:
                sink_place = list(final_marking)[0]

                connections_to_sink = []
                for place in marking:
                    if place in places_shortest_path_by_hidden and sink_place in places_shortest_path_by_hidden[place]:
                        connections_to_sink.append([place, places_shortest_path_by_hidden[place][sink_place]])
                connections_to_sink = sorted(connections_to_sink, key=lambda x: len(x[1]))

                for i in range(MAX_IT_FINAL2):
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

                # if i > DebugConst.REACH_ITF2:
                #    DebugConst.REACH_ITF2 = i

    if break_condition_final_marking(marking, final_marking):
        consumed = consumed + sum_tokens_fm

    marking_before_cleaning = copy(marking)

    remaining = 0
    for p in marking:
        if p in final_marking:
            marking[p] = max(0, marking[p] - final_marking[p])
            if enable_pltr_fitness:
                if marking[p] > 0:
                    if p in place_fitness:
                        if trace not in place_fitness[p]["underfed_traces"]:
                            place_fitness[p]["overfed_traces"].add(trace)
        remaining = remaining + marking[p]

    for p in current_remaining_map:
        if enable_pltr_fitness:
            if p in place_fitness:
                if trace not in place_fitness[p]["underfed_traces"] and trace not in place_fitness[p]["overfed_traces"]:
                    place_fitness[p]["overfed_traces"].add(trace)
        remaining = remaining + current_remaining_map[p]

    if consider_remaining_in_fitness:
        is_fit = (missing == 0) and (remaining == 0)
    else:
        is_fit = (missing == 0)

    if consumed > 0 and produced > 0:
        #trace_fitness = (1.0 - float(missing) / float(consumed)) * (1.0 - float(remaining) / float(produced))
        trace_fitness = 0.5 * (1.0 - float(missing) / float(consumed)) + 0.5 * (1.0 - float(remaining) / float(produced))
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
            get_visible_transitions_eventually_enabled_by_marking(net, marking_before_cleaning), missing, consumed,
            remaining, produced]


class ApplyTraceTokenReplay(Thread):
    def __init__(self, trace, net, initial_marking, final_marking, trans_map, enable_pltr_fitness, place_fitness,
                 transition_fitness, notexisting_activities_in_model,
                 places_shortest_path_by_hidden, consider_remaining_in_fitness, activity_key="concept:name",
                 reach_mark_through_hidden=True, stop_immediately_when_unfit=False,
                 walk_through_hidden_trans=True, post_fix_caching=None,
                 marking_to_activity_caching=None, is_reduction=False, thread_maximum_ex_time=MAX_DEF_THR_EX_TIME,
                 cleaning_token_flood=False, s_components=None):
        """
        Constructor

        net
            Petri net
        initial_marking
            Initial marking
        final_marking
            Final marking
        trans_map
            Map between transitions labels and transitions
        enable_pltr_fitness
            Enable fitness calculation at place/transition level
        place_fitness
            Current dictionary of places associated with unfit traces
        transition_fitness
            Current dictionary of transitions associated with unfit traces
        notexisting_activities_in_model
            Map that stores the notexisting activities in the model
            triggered in the log
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
        is_reduction
            Expresses if the token-based replay is called in a reduction attempt
        thread_maximum_ex_time
            Alignment threads maximum allowed execution time
        cleaning_token_flood
            Decides if a cleaning of the token flood shall be operated
        s_components
            S-components of the Petri net
        """
        self.thread_is_alive = True
        self.trace = trace
        self.net = net
        self.initial_marking = initial_marking
        self.final_marking = final_marking
        self.trans_map = trans_map
        self.enable_pltr_fitness = enable_pltr_fitness
        self.place_fitness = place_fitness
        self.transition_fitness = transition_fitness
        self.notexisting_activities_in_model = notexisting_activities_in_model
        self.places_shortest_path_by_hidden = places_shortest_path_by_hidden
        self.consider_remaining_in_fitness = consider_remaining_in_fitness
        self.activity_key = activity_key
        self.try_to_reach_final_marking_through_hidden = reach_mark_through_hidden
        self.stop_immediately_when_unfit = stop_immediately_when_unfit
        self.walk_through_hidden_trans = walk_through_hidden_trans
        self.post_fix_caching = post_fix_caching
        self.marking_to_activity_caching = marking_to_activity_caching
        self.is_reduction = is_reduction
        self.thread_maximum_ex_time = thread_maximum_ex_time
        self.cleaning_token_flood = cleaning_token_flood
        self.enable_postfix_cache = ENABLE_POSTFIX_CACHE
        self.enable_marktoact_cache = ENABLE_MARKTOACT_CACHE
        if self.is_reduction:
            self.enable_postfix_cache = True
            self.enable_marktoact_cache = True
        self.t_fit = None
        self.t_value = None
        self.act_trans = None
        self.trans_probl = None
        self.reached_marking = None
        self.enabled_trans_in_mark = None
        self.missing = None
        self.consumed = None
        self.remaining = None
        self.produced = None
        self.s_components = s_components

        Thread.__init__(self)

    def run(self):
        """
        Runs the thread and stores the results
        """
        self.t_fit, self.t_value, self.act_trans, self.trans_probl, self.reached_marking, self.enabled_trans_in_mark, self.missing, self.consumed, self.remaining, self.produced = \
            apply_trace(self.trace, self.net, self.initial_marking, self.final_marking, self.trans_map,
                        self.enable_pltr_fitness, self.place_fitness, self.transition_fitness,
                        self.notexisting_activities_in_model,
                        self.places_shortest_path_by_hidden, self.consider_remaining_in_fitness,
                        activity_key=self.activity_key,
                        try_to_reach_final_marking_through_hidden=self.try_to_reach_final_marking_through_hidden,
                        stop_immediately_unfit=self.stop_immediately_when_unfit,
                        walk_through_hidden_trans=self.walk_through_hidden_trans,
                        post_fix_caching=self.post_fix_caching,
                        marking_to_activity_caching=self.marking_to_activity_caching,
                        is_reduction=self.is_reduction,
                        thread_maximum_ex_time=self.thread_maximum_ex_time,
                        enable_postfix_cache=self.enable_postfix_cache,
                        enable_marktoact_cache=self.enable_marktoact_cache,
                        cleaning_token_flood=self.cleaning_token_flood,
                        s_components=self.s_components)
        self.thread_is_alive = False


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


def check_threads(net, threads, threads_results, all_activated_transitions, is_reduction=False):
    """
    Check threads aliveness and terminate them accordingly

    Parameters
    ------------
    net
        Petri net
    threads
        Current opened threads
    threads_results
        Threads execution result (to be returned)
    all_activated_transitions
        List of activated transitions during the replay (to be returned)
    is_reduction
        Is this a reduction replay (boolean)

    Returns
    ------------
    threads
        Current opened threads
    threads_results
        Threads execution result
    all_activated_transitions
        List of activated transitions during the replay
    """
    threads_keys = list(threads.keys())
    terminated_threads_keys = [tk for tk in threads_keys if threads[tk].thread_is_alive is False]
    for tk in terminated_threads_keys:
        t = threads[tk]
        threads_results[tk] = {"trace_is_fit": copy(t.t_fit),
                               "trace_fitness": copy(t.t_value),
                               "activated_transitions": copy(t.act_trans),
                               "reached_marking": copy(t.reached_marking),
                               "enabled_transitions_in_marking": copy(
                                   t.enabled_trans_in_mark),
                               "transitions_with_problems": copy(
                                   t.trans_probl),
                               "missing_tokens": t.missing,
                               "consumed_tokens": t.consumed,
                               "remaining_tokens": t.remaining,
                               "produced_tokens": t.produced}
        all_activated_transitions.update(set(t.act_trans))

        del threads_keys[threads_keys.index(tk)]
        del threads[tk]

        if is_reduction and len(all_activated_transitions) == len(net.transitions):
            break
    return threads, threads_results, all_activated_transitions


def get_variant_from_trace(trace, activity_key, disable_variants=False):
    """
    Gets the variant from the trace (allow disabling)

    Parameters
    ------------
    trace
        Trace
    activity_key
        Attribute that is the activity
    disable_variants
        Boolean value that disable variants

    Returns
    -------------
    variant
        Variant describing the trace
    """
    if disable_variants:
        return str(hash(trace))
    return ",".join([x[activity_key] for x in trace])


def get_variants_from_log(log, activity_key, disable_variants=False):
    """
    Gets the variants from the log (allow disabling by giving each trace a different variant)

    Parameters
    -------------
    log
        Trace log
    activity_key
        Attribute that is the activity
    disable_variants
        Boolean value that disable variants

    Returns
    -------------
    variants
        Variants contained in the log
    """
    if disable_variants:
        variants = {}
        for trace in log:
            variants[str(hash(trace))] = [trace]
        return variants
    parameters_variants = {constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}
    variants = variants_module.get_variants(log, parameters=parameters_variants)
    return variants


def apply_log(log, net, initial_marking, final_marking, enable_pltr_fitness=False, consider_remaining_in_fitness=False,
              activity_key="concept:name", reach_mark_through_hidden=True, stop_immediately_unfit=False,
              walk_through_hidden_trans=True, places_shortest_path_by_hidden=None,
              variants=None, is_reduction=False, thread_maximum_ex_time=MAX_DEF_THR_EX_TIME,
              cleaning_token_flood=False, disable_variants=False):
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
    enable_pltr_fitness
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
    is_reduction
        Expresses if the token-based replay is called in a reduction attempt
    thread_maximum_ex_time
        Alignment threads maximum allowed execution time
    cleaning_token_flood
        Decides if a cleaning of the token flood shall be operated
    disable_variants
        Disable variants grouping
    """
    post_fix_cache = PostFixCaching()
    marking_to_activity_cache = MarkingToActivityCaching()
    if places_shortest_path_by_hidden is None:
        places_shortest_path_by_hidden = get_places_shortest_path_by_hidden(net)

    place_fitness_per_trace = {}
    transition_fitness_per_trace = {}

    aligned_traces = []

    if enable_pltr_fitness:
        for place in net.places:
            place_fitness_per_trace[place] = {"underfed_traces": set(), "overfed_traces": set()}
        for transition in net.transitions:
            if transition.label:
                transition_fitness_per_trace[transition] = {"underfed_traces": {}, "fit_traces": {}}

    s_components = []

    if cleaning_token_flood:
        s_components = get_s_components_from_petri(net, initial_marking, final_marking)

    notexisting_activities_in_model = {}

    trans_map = {}
    for t in net.transitions:
        trans_map[t.label] = t
    if len(log) > 0:
        if len(log[0]) > 0:
            if activity_key in log[0][0]:
                if variants is None:
                    variants = get_variants_from_log(log, activity_key, disable_variants=disable_variants)
                vc = variants_module.get_variants_sorted_by_count(variants)
                threads = {}
                threads_results = {}
                all_activated_transitions = set()

                for i in range(len(vc)):
                    variant = vc[i][0]
                    threads_keys = list(threads.keys())
                    while len(threads_keys) > MAX_NO_THREADS:
                        threads, threads_results, all_activated_transitions = check_threads(net, threads,
                                                                                            threads_results,
                                                                                            all_activated_transitions,
                                                                                            is_reduction=is_reduction)
                        if is_reduction and len(all_activated_transitions) == len(net.transitions):
                            break
                        threads_keys = list(threads.keys())
                    threads, threads_results, all_activated_transitions = check_threads(net, threads, threads_results,
                                                                                        all_activated_transitions,
                                                                                        is_reduction=is_reduction)
                    if is_reduction and len(all_activated_transitions) == len(net.transitions):
                        break
                    threads[variant] = ApplyTraceTokenReplay(variants[variant][0], net, initial_marking, final_marking,
                                                             trans_map, enable_pltr_fitness, place_fitness_per_trace,
                                                             transition_fitness_per_trace,
                                                             notexisting_activities_in_model,
                                                             places_shortest_path_by_hidden,
                                                             consider_remaining_in_fitness,
                                                             activity_key=activity_key,
                                                             reach_mark_through_hidden=reach_mark_through_hidden,
                                                             stop_immediately_when_unfit=stop_immediately_unfit,
                                                             walk_through_hidden_trans=walk_through_hidden_trans,
                                                             post_fix_caching=post_fix_cache,
                                                             marking_to_activity_caching=marking_to_activity_cache,
                                                             is_reduction=is_reduction,
                                                             thread_maximum_ex_time=thread_maximum_ex_time,
                                                             cleaning_token_flood=cleaning_token_flood,
                                                             s_components=s_components)
                    threads[variant].start()
                while len(threads) > 0:
                    threads_keys = list(threads.keys())
                    t = threads[threads_keys[0]]
                    t.join()
                    threads, threads_results, all_activated_transitions = check_threads(net, threads, threads_results,
                                                                                        all_activated_transitions,
                                                                                        is_reduction=is_reduction)
                    if is_reduction and len(all_activated_transitions) == len(net.transitions):
                        break

                for trace in log:
                    # trace_variant = ",".join([x[activity_key] for x in trace])
                    trace_variant = get_variant_from_trace(trace, activity_key, disable_variants=disable_variants)
                    if trace_variant in threads_results:
                        t = threads_results[trace_variant]
                        aligned_traces.append(t)
            else:
                raise NoConceptNameException("at least an event is without " + activity_key)

    if enable_pltr_fitness:
        return aligned_traces, place_fitness_per_trace, transition_fitness_per_trace, notexisting_activities_in_model
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

    enable_pltr_fitness = False
    consider_remaining_in_fitness = False
    try_to_reach_final_marking_through_hidden = True
    stop_immediately_unfit = False
    walk_through_hidden_trans = True
    is_reduction = False
    cleaning_token_flood = False
    disable_variants = False
    thread_maximum_ex_time = MAX_DEF_THR_EX_TIME
    places_shortest_path_by_hidden = None
    activity_key = xes_util.DEFAULT_NAME_KEY
    variants = None

    if "enable_place_fitness" in parameters:
        enable_pltr_fitness = parameters["enable_place_fitness"]
    if "enable_pltr_fitness" in parameters:
        enable_pltr_fitness = parameters["enable_pltr_fitness"]
    if "consider_remaining_in_fitness" in parameters:
        consider_remaining_in_fitness = parameters["consider_remaining_in_fitness"]
    if "try_to_reach_final_marking_through_hidden" in parameters:
        try_to_reach_final_marking_through_hidden = parameters["try_to_reach_final_marking_through_hidden"]
    if "stop_immediately_unfit" in parameters:
        stop_immediately_unfit = parameters["stop_immediately_unfit"]
    if "walk_through_hidden_trans" in parameters:
        walk_through_hidden_trans = parameters[
            "walk_through_hidden_trans"]
    if "is_reduction" in parameters:
        is_reduction = parameters["is_reduction"]
    if "cleaning_token_flood" in parameters:
        cleaning_token_flood = parameters["cleaning_token_flood"]
    if "disable_variants" in parameters:
        disable_variants = parameters["disable_variants"]
    if "thread_maximum_ex_time" in parameters:
        thread_maximum_ex_time = parameters["thread_maximum_ex_time"]
    if "places_shortest_path_by_hidden" in parameters:
        places_shortest_path_by_hidden = parameters["places_shortest_path_by_hidden"]
    if "variants" in parameters:
        variants = parameters["variants"]
    if pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters:
        activity_key = parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY]

    return apply_log(log, net, initial_marking, final_marking, enable_pltr_fitness=enable_pltr_fitness,
                     consider_remaining_in_fitness=consider_remaining_in_fitness,
                     reach_mark_through_hidden=try_to_reach_final_marking_through_hidden,
                     stop_immediately_unfit=stop_immediately_unfit,
                     walk_through_hidden_trans=walk_through_hidden_trans,
                     places_shortest_path_by_hidden=places_shortest_path_by_hidden, activity_key=activity_key,
                     variants=variants, is_reduction=is_reduction, thread_maximum_ex_time=thread_maximum_ex_time,
                     cleaning_token_flood=cleaning_token_flood, disable_variants=disable_variants)

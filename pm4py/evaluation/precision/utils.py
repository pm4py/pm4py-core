from collections import Counter
from pm4py.objects.log.log import EventLog, Event, Trace
from pm4py.objects.log.util import xes as xes_util
import heapq
from pm4py.objects.petri.utils import decorate_places_preset_trans, decorate_transitions_prepostset
from pm4py.objects.petri import align_utils as utils
from pm4py.objects import petri


def __search(sync_net, ini, fin, stop, cost_function, skip):
    decorate_transitions_prepostset(sync_net)
    decorate_places_preset_trans(sync_net)

    incidence_matrix = petri.incidence_matrix.construct(sync_net)
    ini_vec, fin_vec, cost_vec = utils.__vectorize_initial_final_cost(incidence_matrix, ini, fin, cost_function)

    closed = set()

    ini_state = utils.SearchTuple(0, 0, 0, ini, None, None, None, True)
    open_set = [ini_state]
    heapq.heapify(open_set)
    visited = 0
    queued = 0
    traversed = 0
    while not len(open_set) == 0:
        curr = heapq.heappop(open_set)

        current_marking = curr.m

        already_closed = current_marking in closed
        if already_closed:
            continue

        # 12/10/2019: the current marking can be equal to the final marking only if the heuristics
        # (underestimation of the remaining cost) is 0. Low-hanging fruits
        if stop <= current_marking:
            return current_marking
        closed.add(current_marking)
        visited += 1

        possible_enabling_transitions = set()
        for p in current_marking:
            for t in p.ass_trans:
                possible_enabling_transitions.add(t)

        enabled_trans = [t for t in possible_enabling_transitions if t.sub_marking <= current_marking]

        trans_to_visit_with_cost = [(t, cost_function[t]) for t in enabled_trans if
                                    not (t is None or utils.__is_log_move(t, skip) or (
                                            utils.__is_model_move(t, skip) and not t.label[1] is None))]

        for t, cost in trans_to_visit_with_cost:
            traversed += 1
            new_marking = utils.add_markings(current_marking, t.add_marking)

            if new_marking in closed:
                continue
            g = curr.g + cost

            queued += 1
            new_f = g

            tp = utils.SearchTuple(new_f, g, 0, new_marking, curr, t, None, True)
            heapq.heappush(open_set, tp)


def get_log_prefixes(log, activity_key=xes_util.DEFAULT_NAME_KEY):
    """
    Get log prefixes

    Parameters
    ----------
    log
        Trace log
    activity_key
        Activity key (must be provided if different from concept:name)
    """
    prefixes = {}
    prefix_count = Counter()
    for trace in log:
        for i in range(1, len(trace)):
            red_trace = trace[0:i]
            prefix = ",".join([x[activity_key] for x in red_trace])
            next_activity = trace[i][activity_key]
            if prefix not in prefixes:
                prefixes[prefix] = set()
            prefixes[prefix].add(next_activity)
            prefix_count[prefix] += 1
    return prefixes, prefix_count


def form_fake_log(prefixes_keys, activity_key=xes_util.DEFAULT_NAME_KEY):
    """
    Form fake log for replay (putting each prefix as separate trace to align)

    Parameters
    ----------
    prefixes_keys
        Keys of the prefixes (to form a log with a given order)
    activity_key
        Activity key (must be provided if different from concept:name)
    """
    fake_log = EventLog()
    for prefix in prefixes_keys:
        trace = Trace()
        prefix_activities = prefix.split(",")
        for activity in prefix_activities:
            event = Event()
            event[activity_key] = activity
            trace.append(event)
        fake_log.append(trace)
    return fake_log
